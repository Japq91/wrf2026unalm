"""Descarga real de ERA5-Land para el área de las 7 estaciones de Perú
usadas en el curso (data/ogimet/coords_peru.json), mismo día y mismas
variables que ya se descargaron para el dominio del WRF en
descarga_20241213.py -- para poder comparar ambos dominios con el mismo
criterio. Extensión opcional del Módulo 3 (Día 5) / Módulo 5 (Día 9).
"""
import cdsapi

dataset = "reanalysis-era5-land"
request = {
    "variable": [
        "2m_temperature",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "total_precipitation"
    ],
    "year": "2024",
    "month": "12",
    "day": ["13"],
    "time": [
        "00:00", "01:00", "02:00",
        "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00",
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00",
        "21:00", "22:00", "23:00"
    ],
    "data_format": "netcdf",
    "download_format": "unarchived",
    # [norte, oeste, sur, este] -- cubre las 7 estaciones de coords_peru.json
    # (Tumbes -3.55 a Tacna -18.05 en latitud; Piura -80.6 a Cuzco -71.9 en longitud)
    "area": [0, -82, -19, -68],
}

client = cdsapi.Client()
client.retrieve(dataset, request, "era5_land_peru_20241213.nc")
print("Descarga real completada: era5_land_peru_20241213.nc")
