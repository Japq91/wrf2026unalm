"""
Script 2: procesa (decodifica) los reportes SYNOP crudos descargados por
1_descargar_ogimet.py (formato getsynop / CSV con columna PARTE) y extrae
una serie horaria simple: tiempo, temperatura, precipitación, dirección y
velocidad de viento.

Requiere: pip install pymetdecoder

Notas sobre precipitación:
    En SYNOP la precipitación se reporta en grupos con distintos períodos
    de acumulación (1, 6, 24 h, etc.). Para no mezclar acumulados de
    varias horas con datos horarios reales, este script SOLO toma el
    grupo cuyo período de acumulación es exactamente 1 hora
    (precipitation_s3 con time_before_obs == 1). Si esa hora no trae ese
    grupo puntual, precip_mm queda vacío (no se rellena con un acumulado
    de 6h ni con 0).

Uso:    
    python h2_procesa_horario.py --anio 2024 --mes 12 --dia 13
"""
import argparse
import csv
import json
from pathlib import Path
import sys
from pymetdecoder import synop as s

AREA_P = 'peru' #'area_wrf'
CACHE_DIR = Path('ogimet/%s' % AREA_P)
CONFIG_FILE = Path('ogimet/estaciones_%s.json' % AREA_P)
SALIDA_DIR = Path('obs')

KT_A_MS = 0.514444


def cargar_estaciones() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"No se encontró {CONFIG_FILE}.")
    return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))


def precip_1h(decoded: dict):
    """Devuelve el monto en mm SOLO si el grupo de precipitación de
    sección 3 corresponde exactamente a una acumulación de 1 hora.
    Descarta cualquier otro período (6h, 24h, etc.) para no mezclar
    acumulados con datos horarios reales."""
    grupo = decoded.get('precipitation_s3')
    if not grupo:
        return None
    periodo = grupo.get('time_before_obs', {}).get('value')
    if periodo != 1:
        return None
    return grupo.get('amount', {}).get('value')


def parsear_synop(msg: str) -> dict:
    """Decodifica un mensaje SYNOP crudo y devuelve las variables de interés."""
    decoded = s.SYNOP().decode(msg)

    temp = decoded.get('air_temperature')
    temp_c = temp['value'] if temp else None

    viento = decoded.get('surface_wind') or {}
    dir_info = viento.get('direction') or {}
    vel_info = viento.get('speed') or {}
    dir_deg = dir_info.get('value')
    vel_valor = vel_info.get('value')
    vel_unidad = vel_info.get('unit')
    vel_ms = None
    if vel_valor is not None:
        vel_ms = vel_valor * KT_A_MS if vel_unidad == 'KT' else vel_valor

    return {
        'temp_C': temp_c,
        'precip_mm': precip_1h(decoded),
        'dir_viento_deg': dir_deg,
        'vel_viento_ms': round(vel_ms, 2) if vel_ms is not None else None,
    }


def procesar_archivo(cache_file: Path, salida_file: Path):
    filas_salida = []
    n_error = 0
    with cache_file.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            msg = row['PARTE'].strip()
            tiempo = (f"{row['ANO']}-{int(row['MES']):02d}-{int(row['DIA']):02d} "
                      f"{int(row['HORA']):02d}:{int(row['MINUTO']):02d}:00")
            try:
                variables = parsear_synop(msg)
            except Exception:
                n_error += 1
                continue  # fila no decodificable: se omite de la serie horaria
            filas_salida.append({'tiempo': tiempo, **variables})

    SALIDA_DIR.mkdir(exist_ok=True)
    campos = ['tiempo', 'temp_C', 'precip_mm', 'dir_viento_deg', 'vel_viento_ms']
    with salida_file.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(filas_salida)

    print(f"  -> {salida_file} ({len(filas_salida)} filas, {n_error} descartadas por error)")


def main():
    ap = argparse.ArgumentParser(description="Decodifica los SYNOP crudos descargados y extrae variables por hora.")
    ap.add_argument('--anio', type=int, required=True)
    ap.add_argument('--mes', type=int, required=True)
    ap.add_argument('--dia', type=int, default=None,
                     help="Día puntual (1-31)")
    args = ap.parse_args()

    estaciones = cargar_estaciones()

    faltantes = []
    for nombre in estaciones:
        if args.dia is not None:
            cache_file = CACHE_DIR / f"{nombre}_{args.anio}_{args.mes:02d}_{args.dia:02d}.csv"
            salida_file = SALIDA_DIR / f"{nombre}_{args.anio}_{args.mes:02d}_{args.dia:02d}_horario.csv"
        else:
            cache_file = CACHE_DIR / f"{nombre}_{args.anio}_{args.mes:02d}.csv"
            salida_file = SALIDA_DIR / f"{nombre}_{args.anio}_{args.mes:02d}_horario.csv"

        if not cache_file.exists():
            print(f"  [falta] {cache_file} no existe -- corré primero 1_descargar_ogimet.py")
            faltantes.append(nombre)
            continue

        print(f"Procesando {nombre} ({cache_file.name})...")
        procesar_archivo(cache_file, salida_file)

    if faltantes:
        print(f"\nEstaciones sin archivo de entrada: {faltantes}")


if __name__ == '__main__':
    main()