"""
Script 3: junta los CSV horarios diarios generados por 2_procesa_horario.py
(uno por estación y por día, ej. Arequipa_2025_03_01_horario.csv) en UN
CSV MENSUAL COMPACTO POR ESTACIÓN, con todas sus variables meteorológicas.

Formato de salida (uno por estación, ej. obs/Arequipa_2025_03_horario.csv):

    tiempo,temp_C,precip_mm,dir_viento_deg,vel_viento_ms
    2025-03-01 00:00:00,13.4,,280,4.63
    2025-03-01 03:00:00,13.4,,270,1.54
    ...

La columna `tiempo` se procesa como datetime64[ns] con pandas (se ordena
cronológicamente y se eliminan duplicados exactos). Al escribirse a CSV
queda en formato ISO (YYYY-MM-DD HH:MM:SS); pd.read_csv(..., parse_dates=
['tiempo']) la vuelve a leer como datetime64 sin problema (un CSV no
puede "guardar" el dtype nativo, solo texto -- si en algún momento
querés preservar el dtype binario, se puede exportar a .parquet).

Recorre automáticamente todos los días para los que exista archivo
--anio/--mes (los mismos que controla h0_datos_ogimet.sh), sin necesidad
de indicar los días manualmente. Genera un archivo de salida por cada
estación definida en estaciones.json.

Uso:
    python h3_junta_mensual.py --anio 2025 --mes 3
"""
import argparse
import json
from pathlib import Path

import pandas as pd

AREA_P = 'peru'  # 'area_wrf'
CONFIG_FILE = Path('ogimet/estaciones_%s.json' % AREA_P)
SALIDA_DIR = Path('obs')

CAMPOS = ['tiempo', 'temp_C', 'precip_mm', 'dir_viento_deg', 'vel_viento_ms']


def cargar_estaciones() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"No se encontró {CONFIG_FILE}.")
    return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))


def archivos_diarios(nombre: str, anio: int, mes: int) -> list[Path]:
    """Devuelve, ordenados, todos los CSV horarios diarios ya generados
    para una estación y mes dados (uno por cada día procesado por
    h0_datos_ogimet.sh -- no hace falta indicar los días a mano)."""
    patron = f"{nombre}_{anio}_{mes:02d}_*_horario.csv"
    return sorted(SALIDA_DIR.glob(patron))


def juntar_estacion(nombre: str, anio: int, mes: int):
    """Junta todos los CSV diarios de una estación en un único DataFrame
    mensual, con `tiempo` como datetime64 y sin duplicados.
    Devuelve (df_est, archivos_usados) o (None, []) si no hay datos."""
    archivos = archivos_diarios(nombre, anio, mes)
    if not archivos:
        print(f"  [falta] {nombre}: no hay archivos horarios para {anio}-{mes:02d}")
        return None, []

    partes = []
    for archivo in archivos:
        df = pd.read_csv(archivo, dtype={
            'temp_C': 'float64',
            'precip_mm': 'float64',
            'dir_viento_deg': 'float64',
            'vel_viento_ms': 'float64',
        })
        partes.append(df)

    df_est = pd.concat(partes, ignore_index=True)
    df_est['tiempo'] = pd.to_datetime(df_est['tiempo'])
    df_est = df_est.drop_duplicates(subset='tiempo').sort_values('tiempo')
    df_est = df_est[CAMPOS]
    print(f"  -> {nombre}: {len(archivos)} archivo(s) diario(s) -> {len(df_est)} filas")
    return df_est, archivos


def main():
    ap = argparse.ArgumentParser(
        description="Junta los CSV horarios diarios en un CSV mensual compacto, uno por estación."
    )
    ap.add_argument('--anio', type=int, required=True)
    ap.add_argument('--mes', type=int, required=True)
    ap.add_argument('--borrar_diarios', action='store_true',
                     help="Borra los CSV diarios de obs/ ya usados para armar el "
                          "consolidado, uno por uno, y solo después de haber "
                          "guardado el consolidado de esa estación con éxito.")
    args = ap.parse_args()

    estaciones = cargar_estaciones()
    print(f"Estaciones configuradas ({len(estaciones)}): {list(estaciones.keys())}\n")

    SALIDA_DIR.mkdir(exist_ok=True)
    faltantes = []
    ok = []
    for nombre in estaciones:
        df_est, archivos = juntar_estacion(nombre, args.anio, args.mes)
        if df_est is None:
            faltantes.append(nombre)
            continue
        salida = SALIDA_DIR / f"{nombre}_{args.anio}_{args.mes:02d}_horario.csv"
        df_est.to_csv(salida, index=False)
        print(f"         guardado en {salida}")
        ok.append(nombre)

        if args.borrar_diarios:
            # Verificación mínima antes de borrar: el consolidado tiene que
            # haber quedado escrito en disco y con filas.
            if salida.exists() and len(df_est) > 0:
                for archivo in archivos:
                    archivo.unlink()
                print(f"         borrados {len(archivos)} CSV diario(s) de {nombre}")
            else:
                print(f"         [aviso] no se borraron los diarios de {nombre} "
                      f"(el consolidado no quedó como se esperaba)")

    print("\n=== Resumen ===")
    print(f"OK: {len(ok)}/{len(estaciones)}")
    if faltantes:
        print(f"Sin datos: {faltantes}")


if __name__ == '__main__':
    main()