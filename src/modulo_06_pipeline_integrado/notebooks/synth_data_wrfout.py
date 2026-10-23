"""Generador de un archivo wrfout sintetico pero estructuralmente real:
grilla Arakawa-C (staggered), proyeccion Lambert Conformal genuina (via
pyproj), variables acumuladas, y atributos globales equivalentes a los de
un archivo WRF real. Pensado como sustituto reproducible de un wrfout real
(que requeriria haber corrido el modelo, fuera del alcance del curso)."""
import numpy as np
import pandas as pd
import xarray as xr
import pyproj


def wrfout_sintetico(
    nx=35, ny=25, nz=6, ntime=13,
    cen_lat=-9.5, cen_lon=-76.0,
    truelat1=-8.0, truelat2=-12.0,
    dx=15000.0, dy=15000.0,
    start="2026-03-15T00:00:00", freq="1h",
    seed=0,
):
    """Devuelve un xr.Dataset con la estructura cruda de un wrfout (antes de
    xwrf.postprocess()): grilla staggered, XLAT/XLONG 2D, Times como bytes,
    RAINC/RAINNC acumulados de forma estrictamente creciente."""
    rng = np.random.default_rng(seed)

    pargs = dict(proj="lcc", lat_1=truelat1, lat_2=truelat2, lat_0=cen_lat,
                 lon_0=cen_lon, x_0=0, y_0=0, a=6370000, b=6370000)
    crs = pyproj.CRS(pargs)
    wgs84 = pyproj.CRS(4326)
    fwd = pyproj.Transformer.from_crs(wgs84, crs, always_xy=True)
    inv = pyproj.Transformer.from_crs(crs, wgs84, always_xy=True)

    e, n = fwd.transform(cen_lon, cen_lat)
    x0 = -(nx - 1) / 2.0 * dx + e
    y0 = -(ny - 1) / 2.0 * dy + n
    x = x0 + np.arange(nx) * dx
    y = y0 + np.arange(ny) * dy
    X, Y = np.meshgrid(x, y)  # forma (ny, nx) = (south_north, west_east)
    lon2d, lat2d = inv.transform(X, Y)

    times = pd.date_range(start, periods=ntime, freq=freq)
    times_bytes = np.array([t.strftime("%Y-%m-%d_%H:%M:%S") for t in times], dtype="S19")

    # --- T2: mas frio hacia el oeste (cordillera) + ciclo diurno + ruido
    dist_oeste = (X - X.min()) / (X.max() - X.min())
    base_t2 = 295.0 - 6.0 * (1 - dist_oeste)
    ciclo = 4.0 * np.sin((times.hour.values - 9) / 24 * 2 * np.pi)
    t2 = (base_t2[None, :, :] + ciclo[:, None, None]
          + rng.normal(0, 0.3, (ntime, ny, nx))).astype("float32")

    # --- viento: U en puntos staggered (nx+1), V en puntos staggered (ny+1)
    factor_z = np.linspace(1.0, 2.5, nz)  # el viento aumenta con la altura
    U = (3.0 * factor_z[None, :, None, None]
         + rng.normal(0, 0.5, (ntime, nz, ny, nx + 1))).astype("float32")
    V = (1.0 * factor_z[None, :, None, None]
         + rng.normal(0, 0.5, (ntime, nz, ny + 1, nx))).astype("float32")
    U10 = (3.0 + rng.normal(0, 0.7, (ntime, ny, nx))).astype("float32")
    V10 = (1.0 + rng.normal(0, 0.7, (ntime, ny, nx))).astype("float32")

    # --- precipitacion ACUMULADA (cada componente es su propio cumsum no-negativo,
    #     para que RAINC+RAINNC tambien sea siempre no-decreciente, como en WRF real)
    modulacion = 1 + 0.5 * np.sin(np.linspace(0, 3 * np.pi, ntime))
    tasa_nc = rng.uniform(0, 0.6, (ny, nx))
    tasa_c = rng.uniform(0, 0.2, (ny, nx))
    rainnc = np.cumsum(np.repeat(tasa_nc[None, :, :], ntime, axis=0) * modulacion[:, None, None], axis=0).astype("float32")
    rainc = np.cumsum(np.repeat(tasa_c[None, :, :], ntime, axis=0) * modulacion[:, None, None], axis=0).astype("float32")

    sinalpha = np.zeros((ny, nx), dtype="float32")
    cosalpha = np.ones((ny, nx), dtype="float32")

    ds = xr.Dataset(
        data_vars={
            "T2": (["Time", "south_north", "west_east"], t2,
                   {"units": "K", "description": "TEMP at 2 M"}),
            "U": (["Time", "bottom_top", "south_north", "west_east_stag"], U,
                  {"units": "m s-1", "stagger": "X"}),
            "V": (["Time", "bottom_top", "south_north_stag", "west_east"], V,
                  {"units": "m s-1", "stagger": "Y"}),
            "U10": (["Time", "south_north", "west_east"], U10, {"units": "m s-1"}),
            "V10": (["Time", "south_north", "west_east"], V10, {"units": "m s-1"}),
            "RAINC": (["Time", "south_north", "west_east"], rainc,
                      {"units": "mm", "description": "ACCUMULATED CUMULUS PRECIPITATION"}),
            "RAINNC": (["Time", "south_north", "west_east"], rainnc,
                      {"units": "mm", "description": "ACCUMULATED GRID SCALE PRECIPITATION"}),
            "SINALPHA": (["south_north", "west_east"], sinalpha),
            "COSALPHA": (["south_north", "west_east"], cosalpha),
            "Times": (["Time"], times_bytes),
        },
        coords={
            "XLAT": (["Time", "south_north", "west_east"],
                     np.repeat(lat2d[None, :, :], ntime, axis=0).astype("float32")),
            "XLONG": (["Time", "south_north", "west_east"],
                      np.repeat(lon2d[None, :, :], ntime, axis=0).astype("float32")),
        },
        attrs={
            "TITLE": " OUTPUT FROM WRF (sintetico, curso Python-WRF)",
            "START_DATE": str(times[0]).replace(" ", "_"),
            "SIMULATION_START_DATE": str(times[0]).replace(" ", "_"),
            "MAP_PROJ": 1,
            "CEN_LAT": np.float32(cen_lat),
            "CEN_LON": np.float32(cen_lon),
            "TRUELAT1": np.float32(truelat1),
            "TRUELAT2": np.float32(truelat2),
            "MOAD_CEN_LAT": np.float32(cen_lat),
            "STAND_LON": np.float32(cen_lon),
            "DX": np.float32(dx),
            "DY": np.float32(dy),
            "WEST-EAST_GRID_DIMENSION": nx + 1,
            "SOUTH-NORTH_GRID_DIMENSION": ny + 1,
            "BOTTOM-TOP_GRID_DIMENSION": nz + 1,
        },
    )
    return ds
