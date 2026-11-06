# Metricas complementarias, control de calidad y emparejamiento (Modulo 5)
#
# Completa metricas.py (Dia 8) para validar con datos reales:
# - pares validos (ignora NaN) y resumen de metricas con IOA
# - humedad relativa y razon de mezcla desde el wrfout y desde la estacion
# - velocidad y direccion del viento, con estadistica circular para la direccion
# - control de calidad de las observaciones
# - revision del punto de grilla (distancia y altura)
# - comparacion con criterios de desempeno de la literatura
import numpy as np
import pandas as pd
import xarray as xr

from metricas import calcular_mae, calcular_rmse, calcular_bias, calcular_r, calcular_kge


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------

def abrir_wrfout(ruta, variables):
    """Abre un wrfout y deja solo las variables pedidas (mas sus coordenadas).

    open_dataset no carga los datos a memoria hasta que se usan, asi que
    funciona igual con archivos de varios GB que traen cientos de variables.
    """
    ds = xr.open_dataset(ruta)
    faltan = [v for v in variables if v not in ds]
    if faltan:
        raise KeyError(f"{ruta} no trae {faltan}")
    return ds[variables]


# ---------------------------------------------------------------------------
# Metricas
# ---------------------------------------------------------------------------

def pares_validos(s, o):
    """Devuelve s y o solo donde ambos tienen dato (sin NaN)."""
    s = np.asarray(s, dtype=float)
    o = np.asarray(o, dtype=float)
    ok = np.isfinite(s) & np.isfinite(o)
    return s[ok], o[ok]


def calcular_ioa(s, o):
    """Indice de concordancia de Willmott (1981): 1 es perfecto, 0 no concuerda."""
    o_media = np.mean(o)
    denominador = np.sum((np.abs(s - o_media) + np.abs(o - o_media)) ** 2)
    return float(1 - np.sum((s - o) ** 2) / denominador)


def resumen_metricas(s, o, n_min=10):
    """Todas las metricas sobre los pares validos.

    Si quedan menos de n_min pares, devuelve NaN en vez de un numero que
    no significa nada.
    """
    s, o = pares_validos(s, o)
    fila = {"n": len(o)}
    nombres = ["bias", "MAE", "RMSE", "r", "IOA", "KGE"]
    if len(o) < n_min:
        return {**fila, **{m: np.nan for m in nombres}}
    kge, _ = calcular_kge(s, o)
    return {**fila,
            "bias": calcular_bias(s, o), "MAE": calcular_mae(s, o),
            "RMSE": calcular_rmse(s, o), "r": calcular_r(s, o),
            "IOA": calcular_ioa(s, o), "KGE": float(kge)}


# ---------------------------------------------------------------------------
# Humedad
# ---------------------------------------------------------------------------

def presion_vapor_saturacion(t_c):
    """Presion de vapor de saturacion (hPa) sobre agua, formula de Bolton (1980)."""
    return 6.112 * np.exp(17.67 * t_c / (t_c + 243.5))


def humedad_relativa_wrf(t2_k, q2, psfc_pa):
    """HR a 2 m (%) desde T2 (K), Q2 (kg/kg, razon de mezcla) y PSFC (Pa)."""
    p_hpa = psfc_pa / 100
    e = q2 * p_hpa / (0.622 + q2)
    return np.clip(100 * e / presion_vapor_saturacion(t2_k - 273.15), 0, 100)


def presion_por_altura(alt_m):
    """Presion estandar (hPa) a una altura, para estaciones que no miden presion."""
    return 1013.25 * (1 - 2.25577e-5 * np.asarray(alt_m, dtype=float)) ** 5.25588


def razon_mezcla(t_c, hr, p_hpa):
    """Razon de mezcla (g/kg) desde temperatura (C), HR (%) y presion (hPa).

    Es la humedad que usan los criterios de Emery et al. (2001). Del wrfout
    sale directo: Q2 * 1000.
    """
    e = hr / 100 * presion_vapor_saturacion(t_c)
    return 1000 * 0.622 * e / (p_hpa - e)


# ---------------------------------------------------------------------------
# Viento
# ---------------------------------------------------------------------------

def velocidad_direccion(u, v, sinalpha=None, cosalpha=None):
    """Velocidad (m/s) y direccion meteorologica (grados, de donde viene).

    U10/V10 del wrfout siguen los ejes de la grilla. En Mercator coinciden
    con este-norte; en Lambert hay que pasar SINALPHA y COSALPHA para
    girarlos (Modulo 4).
    """
    u = np.asarray(u, dtype=float)
    v = np.asarray(v, dtype=float)
    if sinalpha is not None:
        u, v = u * cosalpha - v * sinalpha, v * cosalpha + u * sinalpha
    velocidad = np.hypot(u, v)
    direccion = (270 - np.degrees(np.arctan2(v, u))) % 360
    return velocidad, direccion


def diferencia_angular(s, o):
    """Diferencia s - o en grados, llevada al rango [-180, 180)."""
    return (np.asarray(s, dtype=float) - np.asarray(o, dtype=float) + 180) % 360 - 180


def metricas_direccion(s, o, vel_obs=None, umbral_calma=1.0, n_min=10):
    """Sesgo y error medio de la direccion del viento (grados).

    Con viento flojo la direccion no esta bien definida: se descartan las
    horas con vel_obs < umbral_calma (m/s).
    """
    d = diferencia_angular(s, o)
    ok = np.isfinite(d)
    if vel_obs is not None:
        ok &= np.asarray(vel_obs, dtype=float) >= umbral_calma
    d = d[ok]
    if len(d) < n_min:
        return {"n": len(d), "bias": np.nan, "MAE": np.nan}
    return {"n": len(d), "bias": float(np.mean(d)), "MAE": float(np.mean(np.abs(d)))}


# ---------------------------------------------------------------------------
# Control de calidad de observaciones
# ---------------------------------------------------------------------------

# Rangos fisicamente posibles y salto maximo entre dos registros seguidos.
LIMITES = {
    "temp_C": (-30, 50),
    "hr": (1, 100),
    "vel_viento_ms": (0, 50),
    "dir_viento_deg": (0, 360),
    "precip_mm": (0, 150),
}
SALTO_MAX = {"temp_C": 6.0, "hr": 40.0, "vel_viento_ms": 15.0}
# Registros iguales seguidos para sospechar de un sensor trabado. La HR se
# registra en enteros, asi que se repite mas facil: se le exige mas.
REPETIDOS = {"temp_C": 6, "hr": 12, "vel_viento_ms": 6, "dir_viento_deg": 6, "precip_mm": 6}
# Valores que pueden repetirse muchas horas sin que nada este mal: sin
# lluvia, calma, y aire saturado (neblina o garua de noche en la costa).
VALOR_NORMAL_REPETIDO = {"precip_mm": 0, "vel_viento_ms": 0, "hr": 100}


def control_calidad(serie, variable, salto_max=None, n_repetidos=None):
    """Marca datos dudosos de una serie de estacion.

    Devuelve (serie_limpia, marcas): la serie con NaN en los datos dudosos
    y una tabla con el motivo de cada marca:
    - fuera_rango: fuera de LIMITES
    - pico: se aleja mas de salto_max del anterior Y del siguiente, en la
      misma direccion (un dato aislado que sube o baja de golpe)
    - repetido: el mismo valor n_repetidos veces seguidas (sensor trabado);
      no se aplica a VALOR_NORMAL_REPETIDO
    """
    serie = serie.astype(float)
    lo, hi = LIMITES[variable]
    marcas = pd.DataFrame(index=serie.index)
    marcas["fuera_rango"] = (serie < lo) | (serie > hi)

    salto_max = SALTO_MAX.get(variable) if salto_max is None else salto_max
    if salto_max is not None:
        d_ant = serie - serie.shift(1)
        d_sig = serie - serie.shift(-1)
        marcas["pico"] = ((d_ant.abs() > salto_max) & (d_sig.abs() > salto_max)
                          & (np.sign(d_ant) == np.sign(d_sig)))
    else:
        marcas["pico"] = False

    n_repetidos = REPETIDOS[variable] if n_repetidos is None else n_repetidos
    grupo = (serie != serie.shift()).cumsum()
    largo = serie.groupby(grupo).transform("size")
    repetido = (largo >= n_repetidos) & serie.notna()
    if variable in VALOR_NORMAL_REPETIDO:
        repetido &= serie != VALOR_NORMAL_REPETIDO[variable]
    marcas["repetido"] = repetido

    dudoso = marcas.any(axis=1)
    return serie.where(~dudoso), marcas[dudoso]


def completitud(serie, inicio, fin, freq="h"):
    """Fraccion de tiempos esperados (entre inicio y fin) que tienen dato."""
    esperados = pd.date_range(inicio, fin, freq=freq)
    return float(serie.reindex(esperados).notna().mean())


# ---------------------------------------------------------------------------
# Emparejamiento modelo-estacion
# ---------------------------------------------------------------------------

def distancia_km(lat1, lon1, lat2, lon2):
    """Distancia sobre la esfera (km) entre dos puntos."""
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return float(6371 * 2 * np.arcsin(np.sqrt(a)))


def revisar_emparejamiento(lat_est, lon_est, lat_mod, lon_mod, dx_km,
                           alt_est=None, alt_mod=None, max_dz=100):
    """Revisa que el punto de grilla elegido represente a la estacion.

    - El punto mas cercano nunca deberia estar a mas de ~0.7 dx (media
      diagonal de la celda). Si esta mas lejos, la estacion cae fuera del
      dominio o lat/lon estan al reves.
    - Si la altura del modelo (HGT) difiere mucho de la de la estacion, la
      temperatura del modelo es la de otra altura (en Lima, de la costa al
      valle hay mas de 500 m).
    """
    dist = distancia_km(lat_est, lon_est, lat_mod, lon_mod)
    resultado = {"dist_km": round(dist, 2), "dz_m": None, "avisos": []}
    if dist > 0.75 * dx_km:
        resultado["avisos"].append(
            f"punto a {dist:.1f} km (celda de {dx_km} km): ¿fuera del dominio o lat/lon al revés?")
    if alt_est is not None and alt_mod is not None:
        dz = float(alt_mod - alt_est)
        resultado["dz_m"] = round(dz, 1)
        if abs(dz) > max_dz:
            resultado["avisos"].append(
                f"el modelo está {dz:+.0f} m respecto de la estación: corregir T2 por altura")
    return resultado


def corregir_t2_altura(t2_c, alt_mod, alt_est, gradiente=-6.5):
    """Lleva T2 del modelo a la altura de la estacion con un gradiente (C/km)."""
    return t2_c + gradiente / 1000 * (alt_est - alt_mod)


# ---------------------------------------------------------------------------
# Criterios de desempeno
# ---------------------------------------------------------------------------

# Umbrales de referencia para modelos meteorologicos.
# "simple": Emery et al. (2001). "complejo" (terreno complejo, como Lima):
# Kemball-Cook et al. (2005). Revisar los valores contra la fuente antes de
# citarlos en un informe. bias en valor absoluto; MAE = "gross error".
# temp en C, vel en m/s, dir en grados, q (razon de mezcla) en g/kg.
BENCHMARKS = {
    "simple": {
        "temp": {"bias": 0.5, "MAE": 2.0, "IOA": 0.8},
        "q": {"bias": 1.0, "MAE": 2.0, "IOA": 0.6},
        "vel": {"bias": 0.5, "RMSE": 2.0, "IOA": 0.6},
        "dir": {"bias": 10, "MAE": 30},
    },
    "complejo": {
        "temp": {"bias": 2.0, "MAE": 3.5},
        "q": {"bias": 0.8, "MAE": 2.0},
        "vel": {"bias": 1.5, "RMSE": 2.5},
        "dir": {"bias": 10, "MAE": 55},
    },
}


def evaluar_benchmarks(resumen, variable, terreno="simple"):
    """Compara un resumen de metricas con los umbrales de BENCHMARKS.

    Devuelve una tabla con el valor, el umbral y si cumple. IOA debe ser
    mayor o igual al umbral; las demas, menores o iguales (bias en valor
    absoluto).
    """
    filas = []
    for metrica, umbral in BENCHMARKS[terreno][variable].items():
        valor = resumen[metrica]
        if metrica == "IOA":
            cumple = valor >= umbral
        elif metrica == "bias":
            cumple = abs(valor) <= umbral
        else:
            cumple = valor <= umbral
        filas.append({"metrica": metrica, "valor": valor,
                      "umbral": f"≥ {umbral}" if metrica == "IOA" else f"≤ {umbral}",
                      "cumple": bool(cumple) if np.isfinite(valor) else None})
    return pd.DataFrame(filas).set_index("metrica")
