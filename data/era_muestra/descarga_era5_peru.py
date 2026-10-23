"""Descarga real de ERA5 (single-levels, ~31 km, NO Land) para la misma
área y el mismo día que descarga_era5land_peru.py (~9 km) -- el par sirve
para comparar 'added value' de resolución entre dos reanálisis del mismo
origen, ya que el dominio del WRF no cubre Perú y no se puede usar WRF
como en el resto del curso. Extensión opcional Módulo 3 (Día 5) / Módulo 5
(Día 9).
"""
import os
import shutil
import tempfile
import zipfile

import cdsapi
import xarray as xr

dataset = "reanalysis-era5-single-levels"
request = {
    "product_type": "reanalysis",
    "variable": [
        "2m_temperature",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "total_precipitation",
    ],
    "year": "2024",
    "month": "12",
    "day": ["13"],
    "time": [f"{h:02d}:00" for h in range(24)],
    "data_format": "netcdf",
    "download_format": "unarchived",
    # mismo recorte que descarga_era5land_peru.py
    "area": [0, -82, -19, -68],
}

destino = "era5_peru_20241213.nc"

client = cdsapi.Client()
client.retrieve(dataset, request, destino)

# CDS entrega este dataset como un zip con dos archivos (uno para variables
# instantaneas -- t2m/u10/v10 -- y otro para la acumulada -- tp), incluso
# con download_format="unarchived", porque mezcla dos "stream/stepType"
# distintos. Se descomprime y se fusiona en un unico NetCDF real, mismo
# nombre final, para que el resto de la extension lo abra igual que a
# era5_land_peru_20241213.nc (que si vino como NetCDF directo, sin zip).
if zipfile.is_zipfile(destino):
    tmpdir = tempfile.mkdtemp()
    with zipfile.ZipFile(destino) as z:
        z.extractall(tmpdir)
    partes = [xr.open_dataset(os.path.join(tmpdir, f)) for f in os.listdir(tmpdir)]
    fusionado = xr.merge(partes)
    os.remove(destino)
    fusionado.to_netcdf(destino)
    shutil.rmtree(tmpdir)
    print(f"Descarga real completada y fusionada (zip -> NetCDF unico): {destino}")
else:
    print(f"Descarga real completada: {destino}")
