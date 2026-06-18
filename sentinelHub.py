"""Sentinel-2 L2A data adapter via Sentinel Hub Process API.

Uses sentinelhub-py to request NDVI, LAI, and FAPAR biophysical
parameters computed server-side via Evalscripts.  Data is returned
as MimeType.TIFF numpy arrays and converted to an Apache Arrow Table.

Workflow
--------
1. Accept a ``BoundingBox`` in EPSG:3763 and a ``TimeRange``.
2. Reproject to WGS84; build a ``BBox`` and compute output dimensions
   from the requested resolution (auto-capped at 2500 px to respect
   the Sentinel Hub Process API limit).
3. For each of the three biophysical products (NDVI, LAI, FAPAR),
   build a ``SentinelHubRequest`` with the product's Evalscript,
   ``DataCollection.SENTINEL2_L2A``, and ``MosaickingOrder.LEAST_CC``.
4. Execute all three requests (each returns a single-band FLOAT32
   GeoTIFF via MimeType.TIFF).
5. Merge the resulting numpy arrays into a single Arrow Table with
   WGS84 (lon, lat) pixel-centre coordinates.

References
----------
* Sentinel Hub Process API: https://docs.sentinel-hub.com/api/latest/api/process/
* sentinelhub-py docs: https://sentinelhub-py.readthedocs.io/
* Evalscripts: Sentinel Hub Custom Scripts repository
  - NDVI : https://custom-scripts.sentinel-hub.com/sentinel-2/ndvi/
  - LAI  : https://custom-scripts.sentinel-hub.com/sentinel-2/lai/
  - FAPAR: https://custom-scripts.sentinel-hub.com/sentinel-2/fapar/
"""

# ruff: noqa: E501  (evalscripts are embedded JavaScript)

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import numpy as np
import pyarrow as pa
from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    MimeType,
    MosaickingOrder,
    SentinelHubRequest,
    SHConfig,
    bbox_to_dimensions,
)

from src.adapters.base import IDynamicDataProvider
from src.adapters.config import get_sh_credentials
from src.adapters.registry import register
from src.adapters.types import BoundingBox, TimeRange
from src.utils.coordinates import bbox_3763_to_wgs84
from src.utils.utils import retry_with_backoff

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_RESOLUTION_M = 10                       # target pixel resolution (m)
_MAX_CLOUD_PCT = 30                      # mosaicking max cloud cover
_MAX_PIXELS_PER_SIDE = 2500              # Sentinel Hub Process API limit

# ---------------------------------------------------------------------------
# Evalscripts (V3) — Sentinel Hub Custom Scripts
# ---------------------------------------------------------------------------
# Each evalscript returns a single FLOAT32 band.
# NDVI uses a simple normalised-difference index on B04+B08.
# LAI and FAPAR use a 5-neuron neural network with 11 Sentinel-2 bands
# plus angular (sun/view zenith/azimuth) inputs, following the SNAP
# biophysical processor implementation.  Cloud/shadow pixels (SCL classes
# 3, 8, 9, 10, 11) are masked to NaN.
#
# The evalscripts are embedded here for self-contained reproducibility.
# Source: https://custom-scripts.sentinel-hub.com/

_EVALSCRIPT_NDVI = """
//VERSION=3
function setup() {
    return {
        input: ["B04", "B08", "dataMask"],
        output: { bands: 1, sampleType: "FLOAT32" }
    };
}
function evaluatePixel(sample) {
    if (sample.dataMask !== 1 || [3, 8, 9, 10, 11].includes(sample.SCL)) {
        return [NaN];
    }
    let val = index(sample.B08, sample.B04);
    return [val];
}
"""

# LAI and FAPAR share helper functions (normalize, tansig, setup).
# Only the neural-network weights and denormalisation bounds differ.
_LAI_FAPAR_HELPERS = """
function normalize(u, min, max) { return 2*(u-min)/(max-min)-1; }
function tansig(x) { return 2/(1+Math.exp(-2*x))-1; }

function setup() {
    return {
        input: [{
            bands: ["B03","B04","B05","B06","B07","B8A","B11","B12",
                    "viewZenithMean","viewAzimuthMean",
                    "sunZenithAngles","sunAzimuthAngles","dataMask"]
        }],
        output: { bands: 1, sampleType: "FLOAT32" }
    };
}
"""

_EVALSCRIPT_LAI = (
    "//VERSION=3\nvar degToRad = Math.PI / 180;\n"
    + _LAI_FAPAR_HELPERS
    + """
function evaluatePixel(sample) {
    if (sample.dataMask !== 1 || [3, 8, 9, 10, 11].includes(sample.SCL)) {
        return [NaN];
    }
    var b03=norm(sample.B03,0,0.253061520471542);
    var b04=norm(sample.B04,0,0.290393577911328);
    var b05=norm(sample.B05,0,0.305398915248555);
    var b06=norm(sample.B06,0.006637972542253,0.608900395797889);
    var b07=norm(sample.B07,0.013972727018939,0.753827384322927);
    var b8a=norm(sample.B8A,0.026690138082061,0.782011770669178);
    var b11=norm(sample.B11,0.016388074192258,0.493761397883092);
    var b12=norm(sample.B12,0,0.493025984460231);
    var vZ=norm(Math.cos(sample.viewZenithMean*degToRad),0.918595400582046,1);
    var sZ=norm(Math.cos(sample.sunZenithAngles*degToRad),0.342022871159208,0.936206429175402);
    var rA=Math.cos((sample.sunAzimuthAngles-sample.viewAzimuthMean)*degToRad);
    var n1=t( 4.96238030555279-0.023406878966470*b03+0.921655164636366*b04+0.135576544080099*b05-1.938331472397950*b06-3.342495816122680*b07+0.902277648009576*b8a+0.205363538258614*b11-0.040607844721716*b12-0.083196409727092*vZ+0.260029270773809*sZ+0.284761567218845*rA);
    var n2=t( 1.416008443981500-0.132555480856684*b03-0.139574837333540*b04-1.014606016898920*b05-1.330890038649270*b06+0.031730624503341*b07-1.433583541317050*b8a-0.959637898574699*b11+1.133115706551000*b12+0.216603876541632*vZ+0.410652303762839*sZ+0.064760155543506*rA);
    var n3=t( 1.075897047213310+0.086015977724868*b03+0.616648776881434*b04+0.678003876446556*b05+0.141102398644968*b06-0.096682206883546*b07-1.128832638862200*b8a+0.302189102741375*b11+0.434494937299725*b12-0.021903699490589*vZ-0.228492476802263*sZ-0.039460537589826*rA);
    var n4=t( 1.533988264655420-0.109366593670404*b03-0.071046262972729*b04+0.064582411478320*b05+2.906325236823160*b06-0.673873108979163*b07-3.838051868280840*b8a+1.695979344531530*b11+0.046950296081713*b12-0.049709652688365*vZ+0.021829545430994*sZ+0.057483827104091*rA);
    var n5=t( 3.024115930757230-0.089939416159969*b03+0.175395483106147*b04-0.081847329172620*b05+2.219895367487790*b06+1.713873975136850*b07+0.713069186099534*b8a+0.138970813499201*b11-0.060771761518025*b12+0.124263341255473*vZ+0.210086140404351*sZ-0.183878138700341*rA);
    var l2=1.096963107077220-1.500135489728730*n1-0.096283269121503*n2-0.194935930577094*n3-0.352305895755591*n4+0.075107415847473*n5;
    return [0.5*(l2+1)*(14.4675094548151-0.000319182538301)+0.000319182538301];
}
""".replace("norm(", "normalize(").replace("t(", "tansig(")
)

_EVALSCRIPT_FAPAR = (
    "//VERSION=3\nvar degToRad = Math.PI / 180;\n"
    + _LAI_FAPAR_HELPERS
    + """
function evaluatePixel(sample) {
    if (sample.dataMask !== 1 || [3, 8, 9, 10, 11].includes(sample.SCL)) return [NaN];
    var b03=norm(sample.B03,0,0.253061520471542);
    var b04=norm(sample.B04,0,0.290393577911328);
    var b05=norm(sample.B05,0,0.305398915248555);
    var b06=norm(sample.B06,0.006637972542253,0.608900395797889);
    var b07=norm(sample.B07,0.013972727018939,0.753827384322927);
    var b8a=norm(sample.B8A,0.026690138082061,0.782011770669178);
    var b11=norm(sample.B11,0.016388074192258,0.493761397883092);
    var b12=norm(sample.B12,0,0.493025984460231);
    var vZ=norm(Math.cos(sample.viewZenithMean*degToRad),0.918595400582046,1);
    var sZ=norm(Math.cos(sample.sunZenithAngles*degToRad),0.342022871159208,0.936206429175402);
    var rA=Math.cos((sample.sunAzimuthAngles-sample.viewAzimuthMean)*degToRad);
    var n1=t(-0.887068364040280+0.268714454733421*b03-0.205473108029835*b04+0.281765694196018*b05+1.337443412255980*b06+0.390319212938497*b07-3.612714342203350*b8a+0.222530960987244*b11+0.821790549667255*b12-0.093664567310731*vZ+0.019290146147447*sZ+0.037364446377188*rA);
    var n2=t( 0.320126471197199-0.248998054599707*b03-0.571461305473124*b04-0.369957603466673*b05+0.246031694650909*b06+0.332536215252841*b07+0.438269896208887*b8a+0.819000551890450*b11-0.934931499059310*b12+0.082716247651866*vZ-0.286978634108328*sZ-0.035890968351662*rA);
    var n3=t( 0.610523702500117-0.164063575315880*b03-0.126303285737763*b04-0.253670784366822*b05-0.321162835049381*b06+0.067082287973580*b07+2.029832288655260*b8a-0.023141228827722*b11-0.553176625657559*b12+0.059285451897783*vZ-0.034334454541432*sZ-0.031776704097009*rA);
    var n4=t(-0.379156190833946+0.130240753003835*b03+0.236781035723321*b04+0.131811664093253*b05-0.250181799267664*b06-0.011364149953286*b07-1.857573214633520*b8a-0.146860751013916*b11+0.528008831372352*b12-0.046230769098303*vZ-0.034509608392235*sZ+0.031884395036004*rA);
    var n5=t( 1.353023396690570-0.029929946166941*b03+0.795804414040809*b04+0.348025317624568*b05+0.943567007518504*b06-0.276341670431501*b07-2.946594180142590*b8a+0.289483073507500*b11+1.044006950440180*b12-0.000413031960419*vZ+0.403331114840215*sZ+0.068427130526696*rA);
    var l2=-0.336431283973339+2.126038811064490*n1-0.632044932794919*n2+5.598995787206250*n3+1.770444140578970*n4-0.267879583604849*n5;
    return [0.5*(l2+1)*(0.977135096979553-0.000153013463222)+0.000153013463222];
}
""".replace("norm(", "normalize(").replace("t(", "tansig(")
)

# Product name → evalscript mapping (iteration order is the column order).
_PRODUCTS = {
    "NDVI": _EVALSCRIPT_NDVI,
    "LAI": _EVALSCRIPT_LAI,
    "FAPAR": _EVALSCRIPT_FAPAR,
}


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------
@register("sentinel2")
class Sentinel2Adapter(IDynamicDataProvider):
    """Sentinel-2 L2A adapter via Sentinel Hub Process API (sentinelhub-py).

    Computes NDVI, LAI, and FAPAR server-side using Evalscripts.
    The Sentinel Hub mosaicking engine handles cloud-free compositing
    automatically via ``MosaickingOrder.LEAST_CC``.

    Each product is requested independently (3 API calls), then the
    resulting rasters are merged into a single Arrow Table.

    .. rubric:: Output columns

    ========  ======  =========================================
    Column    Type    Description
    ========  ======  =========================================
    time      ts(ns)  Centre of the requested time window
    x         f64     WGS84 longitude  (decimal degrees)
    y         f64     WGS84 latitude   (decimal degrees)
    NDVI      f32     Normalised Difference Vegetation Index
    LAI       f32     Leaf Area Index  (m²/m²)
    FAPAR     f32     Fraction of Absorbed PAR  (0–1)
    ========  ======  =========================================
    """

    def __init__(self, resolution_m: int = _RESOLUTION_M) -> None:
        """Initialise with Sentinel Hub OAuth credentials.

        Parameters
        ----------
        resolution_m : int
            Target pixel resolution in metres.  Automatically capped
            if the output would exceed 2500 px per side.
        """
        client_id, client_secret = get_sh_credentials()
        self._config = SHConfig()
        self._config.sh_client_id = client_id
        self._config.sh_client_secret = client_secret
        self._resolution_m = resolution_m

    # ------------------------------------------------------------------
    # fetch() — main entry point
    # ------------------------------------------------------------------
    def fetch(self, bbox: BoundingBox, time_range: TimeRange) -> pa.Table:
        """Retrieve NDVI, LAI, and FAPAR for *bbox* and *time_range*.

        Parameters
        ----------
        bbox : BoundingBox
            Spatial extent in EPSG:3763.
        time_range : TimeRange
            Temporal window — Sentinel Hub mosaicks all available
            cloud-free scenes within this interval via LEAST_CC.

        Returns
        -------
        pa.Table
            6-column table (see class docstring).  Returns an empty
            table if all three product requests fail.
        """
        # --- 1. Reproject to WGS84 and build Sentinel Hub BBox ---
        wgs84 = bbox_3763_to_wgs84(
            bbox.min_x, bbox.min_y, bbox.max_x, bbox.max_y,
        )
        wgs84_bbox = (wgs84["west"], wgs84["south"], wgs84["east"], wgs84["north"])
        sh_bbox = BBox(bbox=wgs84_bbox, crs=CRS.WGS84)

        # --- 2. Compute output dimensions; cap if needed ---
        size = bbox_to_dimensions(sh_bbox, resolution=self._resolution_m)
        if size[0] > _MAX_PIXELS_PER_SIDE or size[1] > _MAX_PIXELS_PER_SIDE:
            capped_res = (
                max(size) * self._resolution_m / _MAX_PIXELS_PER_SIDE
            )
            size = bbox_to_dimensions(sh_bbox, resolution=capped_res)
            logger.info(
                "Resolution capped from %d m to %.0f m (size: %d×%d px)",
                self._resolution_m, capped_res, size[0], size[1],
            )

        # --- 3. Build time interval string ---
        time_interval = (
            time_range.start.strftime("%Y-%m-%d"),
            time_range.end.strftime("%Y-%m-%d"),
        )

        # --- 4. Request each product independently ---
        arrays: dict[str, np.ndarray] = {}
        for product, evalscript in _PRODUCTS.items():
            try:
                arr = self._request_product(
                    evalscript, sh_bbox, size, time_interval, product
                )
                if arr is not None and arr.size > 0:
                    arrays[product] = arr
            except Exception:
                # A single product failure should not block the others.
                logger.debug(
                    "Failed to retrieve %s", product, exc_info=True,
                )

        if not arrays:
            return self._empty_table()

        # --- 5. Merge into Arrow Table ---
        return self._merge_arrays(arrays, wgs84_bbox, time_range.start)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _request_product(
        self,
        evalscript: str,
        sh_bbox: BBox,
        size: tuple[int, int],
        time_interval: tuple[str, str],
        product_name: str,
    ) -> np.ndarray | None:
        """Execute a single Sentinel Hub Process API request.

        Builds a ``SentinelHubRequest`` with the product's evalscript,
        requests a single-band FLOAT32 GeoTIFF response from the
        ``SENTINEL2_L2A`` collection, and returns the resulting numpy
        array.

        Parameters
        ----------
        evalscript : str
            V3 JavaScript evalscript for the product.
        sh_bbox : BBox
            Sentinel Hub bounding box (WGS84).
        size : tuple[int, int]
            Output dimensions in pixels (width, height).
        time_interval : tuple[str, str]
            ``(start_date, end_date)`` strings in ``YYYY-MM-DD`` format.

        Returns
        -------
        np.ndarray or None
            2-D float32 array, or ``None`` if the request fails.
        """
        request = SentinelHubRequest(
            evalscript=evalscript,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=time_interval,
                    mosaicking_order=MosaickingOrder.LEAST_CC,
                    maxcc=_MAX_CLOUD_PCT / 100.0,
                )
            ],
            responses=[
                SentinelHubRequest.output_response("default", MimeType.TIFF),
            ],
            bbox=sh_bbox,
            size=size,
            config=self._config,
        )
        def _do_get():
            return request.get_data()

        # Safely attempt the download up to 3 times
        try:
            data = retry_with_backoff(
                _do_get, max_retries=3, task_name=f"SH API {product_name}"
            )
            if not data:
                return None
            return data[0]
        except Exception as exc:
            logger.warning(f"Sentinel Hub failed to download {product_name}: {exc}")
            return None

    def _merge_arrays(
        self,
        arrays: dict[str, np.ndarray],
        wgs84_bbox: tuple[float, float, float, float],
        time_val: datetime,
    ) -> pa.Table:
        """Merge NDVI/LAI/FAPAR arrays into a single Arrow Table."""
        # Reference array for shape (assume 2D arrays).
        ref = next(iter(arrays.values()))
        
        # Squeeze in case Sentinel Hub returns shape (rows, cols, 1)
        ref = np.squeeze(ref)
        rows, cols = ref.shape

        # 1. Generate 1D arrays for lons and lats
        lons = np.linspace(wgs84_bbox[0], wgs84_bbox[2], cols)
        lats = np.linspace(wgs84_bbox[3], wgs84_bbox[1], rows)

        # 2. Let NumPy build the 2D coordinate grid instantly
        lon_grid, lat_grid = np.meshgrid(lons, lats)

        # 3. Flatten the grids into 1D arrays
        lon_flat = lon_grid.flatten()
        lat_flat = lat_grid.flatten()
        num_pixels = len(lon_flat)

        # 4. Prepare the base dictionary for PyArrow
        time_arr = pa.array([time_val] * num_pixels, type=pa.timestamp("ns"))
        table_data = {
            "time": time_arr,
            "x": pa.array(lon_flat, type=pa.float64()),
            "y": pa.array(lat_flat, type=pa.float64()),
        }

        # 5. Inject the vectorized product arrays directly
        for product in _PRODUCTS:
            if product in arrays:
                # Squeeze, flatten, and ensure FLOAT32
                arr_flat = np.squeeze(arrays[product]).flatten().astype(np.float32)
                table_data[product] = pa.array(arr_flat, type=pa.float32())
            else:
                # If a product failed to download, fill its column with NaNs
                nan_arr = np.full(num_pixels, np.nan, dtype=np.float32)
                table_data[product] = pa.array(nan_arr, type=pa.float32())

        # 6. Build the table with zero Python iteration overhead
        return pa.table(table_data)

    @staticmethod
    def _empty_table() -> pa.Table:
        """Return an empty Arrow Table with the full 6-column schema."""
        return pa.table(
            {
                "time": pa.array([], type=pa.timestamp("ns")),
                "x": pa.array([], type=pa.float64()),
                "y": pa.array([], type=pa.float64()),
                "NDVI": pa.array([], type=pa.float32()),
                "LAI": pa.array([], type=pa.float32()),
                "FAPAR": pa.array([], type=pa.float32()),
            }
        )
