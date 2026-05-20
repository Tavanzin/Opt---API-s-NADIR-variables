import requests
import io
import zipfile

def get():
  response = requests.get("http://127.0.0.1:8000/Copernicus/ndvi?start_date=2025-01&end_date=2025-12", timeout=60.0)

  zip_buffer = io.BytesIO(response.content)

  with zipfile.ZipFile(zip_buffer) as zf:
    files_list = zf.namelist()

    for i, filename in enumerate(files_list, start=1):
      tiff_bytes = zf.read(filename)
      print(f"{i}. Ficheiro: {filename} | Tamanho real: {len(tiff_bytes)} bytes")

if __name__ == '__main__':
  get()
