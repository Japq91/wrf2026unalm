"""Generadores de datos sintéticos reutilizados por varios notebooks del curso."""
import numpy as np
import pandas as pd
import xarray as xr


def era5_like_dataset(lat_first=10.0, lat_last=-20.0, lon_first=-82.0, lon_last=-66.0,
                       nlat=31, nlon=17, start="2026-01-15", periods=7 * 24, freq="h",
                       seed=0):
    """Crea un Dataset sintético con la MISMA convención que ERA5 real:
    latitud DESCENDENTE, longitud en grados este, variables con nombre/unidades CF.
    Pensado como sustituto reproducible de un archivo ERA5 real descargado con cdsapi.
    """
    rng = np.random.default_rng(seed)
    latitude = np.linspace(lat_first, lat_last, nlat)  # descendente, como ERA5 real
    longitude = np.linspace(lon_first, lon_last, nlon)
    time = pd.date_range(start, periods=periods, freq=freq)

    lat2d, lon2d = np.meshgrid(latitude, longitude, indexing="ij")
    # Campo base de temperatura: mas frio hacia el sur y hacia la cordillera (oeste)
    base = 295 - 0.3 * (lat_first - lat2d) - 0.15 * (lon2d - lon_first)
    ciclo_diurno = 3 * np.sin((time.hour.values - 9) / 24 * 2 * np.pi)

    t2m = (
        base[None, :, :]
        + ciclo_diurno[:, None, None]
        + rng.normal(0, 0.4, size=(len(time), nlat, nlon))
    ).astype("float32")

    msl = (101300 + rng.normal(0, 150, size=(len(time), nlat, nlon))).astype("float32")

    ds = xr.Dataset(
        data_vars={
            "t2m": (
                ["time", "latitude", "longitude"], t2m,
                {"units": "K", "long_name": "2 metre temperature", "standard_name": "air_temperature"},
            ),
            "msl": (
                ["time", "latitude", "longitude"], msl,
                {"units": "Pa", "long_name": "Mean sea level pressure", "standard_name": "air_pressure_at_mean_sea_level"},
            ),
        },
        coords={
            "time": time,
            "latitude": ("latitude", latitude, {"units": "degrees_north", "standard_name": "latitude"}),
            "longitude": ("longitude", longitude, {"units": "degrees_east", "standard_name": "longitude"}),
        },
        attrs={
            "Conventions": "CF-1.7",
            "institution": "Datos sinteticos (curso Python-WRF) - NO son ERA5 real",
            "history": "Generado localmente sin conexion a Copernicus CDS",
        },
    )
    return ds


def escribir_grib2_sintetico(ruta, ni=8, nj=6, lat_first=10.0, lat_last=-5.0,
                              lon_first=-80.0, lon_last=-65.0, seed=0,
                              short_name="2t", fecha=20260315, hora=0):
    """Escribe un archivo GRIB2 real (formato binario válido) usando eccodes,
    sin necesidad de conexión a internet. Sustituto reproducible de un
    archivo GFS/ECMWF real descargado con Herbie."""
    import eccodes

    gid = eccodes.codes_grib_new_from_samples("regular_ll_sfc_grib2")
    eccodes.codes_set(gid, "Ni", ni)
    eccodes.codes_set(gid, "Nj", nj)
    eccodes.codes_set(gid, "latitudeOfFirstGridPointInDegrees", lat_first)
    eccodes.codes_set(gid, "longitudeOfFirstGridPointInDegrees", lon_first % 360)
    eccodes.codes_set(gid, "latitudeOfLastGridPointInDegrees", lat_last)
    eccodes.codes_set(gid, "longitudeOfLastGridPointInDegrees", lon_last % 360)
    eccodes.codes_set(gid, "iDirectionIncrementInDegrees", (lon_last - lon_first) / (ni - 1))
    eccodes.codes_set(gid, "jDirectionIncrementInDegrees", abs((lat_last - lat_first) / (nj - 1)))

    rng = np.random.default_rng(seed)
    valores = 293 + rng.normal(0, 2, ni * nj)
    eccodes.codes_set(gid, "shortName", short_name)
    eccodes.codes_set_values(gid, valores)
    eccodes.codes_set(gid, "dataDate", fecha)
    eccodes.codes_set(gid, "dataTime", hora)

    with open(ruta, "wb") as f:
        eccodes.codes_write(gid, f)
    eccodes.codes_release(gid)
