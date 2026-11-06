# Funciones reales de descarga y verificacion (Modulo 3)
import calendar
import os
import cdsapi
import xarray as xr
import pandas as pd


def verificar_integridad(archivo, cobertura_esperada=None, tamano_minimo_kb=1, filtro_grib=None):
    if not os.path.exists(archivo):
        return False, f"El archivo {archivo} no existe."
    tamano_kb = os.path.getsize(archivo) / 1024
    if tamano_kb < tamano_minimo_kb:
        return False, f"Archivo sospechosamente pequeno ({tamano_kb:.1f} KB)."
    try:
        if archivo.endswith((".grib", ".grib2")):
            kwargs = {"filter_by_keys": filtro_grib} if filtro_grib else {}
            ds = xr.open_dataset(archivo, engine="cfgrib", backend_kwargs=kwargs)
        else:
            ds = xr.open_dataset(archivo)
    except Exception as e:
        return False, f"No se pudo abrir el archivo: {type(e).__name__}: {e}"
    if cobertura_esperada and "time_min_horas" in cobertura_esperada:
        n_tiempos = ds.sizes.get("valid_time", ds.sizes.get("time", 1))
        minimo = cobertura_esperada["time_min_horas"]
        if n_tiempos < minimo:
            return False, f"Cobertura insuficiente: {n_tiempos} < {minimo}."
    return True, "OK"


NIVELES_PRESION_ERA5 = [1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 100, 125, 150, 175,
                         200, 225, 250, 300, 350, 400, 450, 500, 550, 600,
                         650, 700, 750, 775, 800, 825, 850, 875, 900, 925,
                         950, 975, 1000]
VARIABLES_PRESION_ERA5 = ["temperature", "u_component_of_wind",
                           "v_component_of_wind", "specific_humidity", "geopotential"]
VARIABLES_SUPERFICIE_ERA5 = [
    "2m_temperature", "2m_dewpoint_temperature",
    "10m_u_component_of_wind", "10m_v_component_of_wind",
    "surface_pressure", "mean_sea_level_pressure",
    "skin_temperature", "sea_ice_cover", "snow_depth", "land_sea_mask",
    "geopotential",
    "soil_temperature_level_1", "soil_temperature_level_2",
    "soil_temperature_level_3", "soil_temperature_level_4",
    "volumetric_soil_water_layer_1", "volumetric_soil_water_layer_2",
    "volumetric_soil_water_layer_3", "volumetric_soil_water_layer_4",
]
NOMBRES_CORTOS_PRESION = ["t", "u", "v", "q", "z"]
NOMBRES_CORTOS_SUPERFICIE = ["t2m", "d2m", "u10", "v10", "sp", "msl", "skt",
                              "siconc", "sd", "lsm", "z",
                              "stl1", "stl2", "stl3", "stl4",
                              "swvl1", "swvl2", "swvl3", "swvl4"]


def _pedido_era5(fecha_inicio, fecha_fin, area, variables, extra, destino):
    if os.path.exists(destino):
        return destino
    dias = pd.date_range(fecha_inicio, fecha_fin, freq="D")
    if len(dias) == 0:
        raise ValueError(f"fecha_fin ({fecha_fin}) es anterior a fecha_inicio ({fecha_inicio}).")
    if (dias[0].year, dias[0].month) != (dias[-1].year, dias[-1].month):
        raise ValueError("El periodo cruza de un mes a otro: CDS necesita un pedido por mes.")
    horas = [f"{h:02d}:00" for h in range(0, 24, 6)]
    peticion = {
        "product_type": "reanalysis",
        "variable": variables,
        "year": dias[0].strftime("%Y"),
        "month": dias[0].strftime("%m"),
        "day": sorted({d.strftime("%d") for d in dias}),
        "time": horas,
        "area": area,
        "format": "netcdf",
    }
    peticion.update(extra)
    dataset = "reanalysis-era5-pressure-levels" if "pressure_level" in extra else "reanalysis-era5-single-levels"
    cdsapi.Client().retrieve(dataset, peticion, destino)
    return destino


def descargar_era5_completo(fecha_inicio, fecha_fin, area, carpeta_destino):
    os.makedirs(carpeta_destino, exist_ok=True)
    nombre = f"{fecha_inicio}_{fecha_fin}"
    ruta_niveles = os.path.join(carpeta_destino, f"{nombre}_niveles_presion.nc")
    ruta_superficie = os.path.join(carpeta_destino, f"{nombre}_superficie.nc")
    _pedido_era5(fecha_inicio, fecha_fin, area, VARIABLES_PRESION_ERA5,
                 {"pressure_level": [str(p) for p in NIVELES_PRESION_ERA5]}, ruta_niveles)
    _pedido_era5(fecha_inicio, fecha_fin, area, VARIABLES_SUPERFICIE_ERA5, {}, ruta_superficie)
    return ruta_niveles, ruta_superficie


def verificar_cobertura_vtable(archivo, nombres_cds_esperados):
    ds = xr.open_dataset(archivo)
    faltan = set(nombres_cds_esperados) - set(ds.data_vars)
    if faltan:
        return False, f"Faltan variables del Vtable: {sorted(faltan)}"
    return True, "OK"


def obtener_entrada_wrf(fecha_inicio, fecha_fin, area, carpeta_destino):
    try:
        ruta_niveles, ruta_superficie = descargar_era5_completo(fecha_inicio, fecha_fin, area, carpeta_destino)
    except Exception as e:
        return False, f"Fallo en la descarga: {type(e).__name__}: {e}"
    n_dias = (pd.Timestamp(fecha_fin) - pd.Timestamp(fecha_inicio)).days + 1
    horas_esperadas = n_dias * 4
    for ruta, nombres_cortos in [(ruta_niveles, NOMBRES_CORTOS_PRESION),
                                  (ruta_superficie, NOMBRES_CORTOS_SUPERFICIE)]:
        ok, msg = verificar_integridad(ruta, {"time_min_horas": horas_esperadas})
        if not ok:
            return False, f"Fallo en la verificación de {ruta}: {msg}"
        ok, msg = verificar_cobertura_vtable(ruta, nombres_cortos)
        if not ok:
            return False, f"Fallo en la cobertura Vtable de {ruta}: {msg}"
    return True, (ruta_niveles, ruta_superficie)


def verificar_csv_senamhi(ruta, anio, mes, max_horas_faltantes=0, tamano_minimo_kb=1):
    """Los mismos 3 controles, adaptados a un CSV de estacion de SENAMHI.
    Devuelve (ok: bool, mensaje: str)."""
    # Control 1: existencia y tamano
    if not os.path.exists(ruta):
        return False, f"El archivo {ruta} no existe."
    if os.path.getsize(ruta) / 1024 < tamano_minimo_kb:
        return False, "Archivo sospechosamente pequeno."

    # Control 2: se puede leer BIEN -- cada fila tiene tantos valores como
    # nombres tiene el encabezado (si no, las columnas quedan corridas)
    with open(ruta, encoding="utf-8") as f:
        n_encabezado = len(f.readline().strip().split(";"))
        n_por_fila = {len(linea.strip().split(";")) for linea in f if linea.strip()}
    if n_por_fila != {n_encabezado}:
        return False, (f"Columnas corridas: el encabezado tiene {n_encabezado} nombres "
                       f"y las filas tienen {sorted(n_por_fila)} valores.")

    # Control 3: cobertura -- estan todas las horas del mes?
    d = pd.read_csv(ruta, sep=";", dtype=str)
    horas_esperadas = calendar.monthrange(anio, mes)[1] * 24
    faltan = horas_esperadas - len(d)
    sin_dato = int((d["Temperatura (°C)"] == "S/D").sum())
    if faltan > max_horas_faltantes:
        return False, (f"Faltan {faltan} de {horas_esperadas} horas "
                       f"(y {sin_dato} horas con S/D en temperatura).")
    return True, f"OK: faltan {faltan} horas, {sin_dato} con S/D en temperatura."
