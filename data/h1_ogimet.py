"""
Script 1: descarga (con caché) los reportes SYNOP crudos (sin decodificar)
de OGIMET usando el binario cgi-bin/getsynop, para las estaciones
definidas en estaciones.json.

A diferencia de gsynres.php (resumen diario) y display_synops2.php
(página HTML pesada, propensa a cortarse), getsynop es un binario CGI
liviano que devuelve directamente un CSV:

    WMO_IND,ANO,MES,DIA,HORA,MINUTO,SYNOP

La columna SYNOP trae el mensaje SYNOP sin decodificar -- hace falta
un decodificador (ej. pymetdecoder) para sacar temperatura y demás
variables; eso lo resolvemos en el script 2.

Uso:    
    python h1_ogimet.py --anio 2024 --mes 12 --dia 13   # un solo día
"""
import argparse
import json
import time
import calendar
from pathlib import Path
import requests

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    )
}
AREA_P = 'peru' #'area_wrf'
CACHE_DIR = Path('ogimet/%s' % AREA_P)
CONFIG_FILE = Path('ogimet/estaciones_%s.json' % AREA_P)

ESPERA_ENTRE_PEDIDOS = 21  # segundos, entre estaciones para no forzar el servidor


def cargar_estaciones() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró {CONFIG_FILE}. Creá un JSON con formato "
            '{"Nombre": "wigos_id", ...}'
        )
    return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))


def descargar_csv(nombre: str, wigos: str, anio: int, mes: int, dia: int = None,
                   timeout: int = 90) -> Path:
    """Descarga (o reutiliza del caché) el CSV de reportes SYNOP crudos de
    una estación para el mes completo, o para un día puntual si se pasa `dia`."""
    CACHE_DIR.mkdir(exist_ok=True)

    if dia is not None:
        cache_file = CACHE_DIR / f"{nombre}_{anio}_{mes:02d}_{dia:02d}.csv"
        begin = f"{anio}{mes:02d}{dia:02d}0000"
        end = f"{anio}{mes:02d}{dia:02d}2359"
    else:
        cache_file = CACHE_DIR / f"{nombre}_{anio}_{mes:02d}.csv"
        ndias = calendar.monthrange(anio, mes)[1]
        begin = f"{anio}{mes:02d}010000"
        end = f"{anio}{mes:02d}{ndias:02d}2359"

    if cache_file.exists():
        print(f"  [cache] {nombre}: ya existe {cache_file}, no se pide al servidor")
        return cache_file

    url = "http://www.ogimet.com/cgi-bin/getsynop"
    params = {
        'wigos': wigos,
        'begin': begin,
        'end': end,
        'lang': 'eng',
        'header': 'yes',
    }
    time.sleep(ESPERA_ENTRE_PEDIDOS)
    print(f"  [red] Pidiendo {nombre} ({wigos}) {begin}-{end}...")
    t0 = time.time()
    r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
    elapsed = time.time() - t0
    r.raise_for_status()
    texto = r.text
    print(f"         {elapsed:.1f}s | status={r.status_code} | {len(texto)} caracteres "
          f"| {texto.count(chr(10))} líneas")

    if 'Forbidden' in texto[:200]:
        raise PermissionError(
            f"OGIMET devolvió 403 en el cuerpo para {nombre}. "
            "Esperá unos minutos antes de reintentar."
        )
    if not texto.strip():
        raise RuntimeError(f"OGIMET devolvió una respuesta vacía para {nombre}.")

    cache_file.write_text(texto, encoding='utf-8')
    print(f"         guardado en {cache_file}")
    return cache_file


def main():
    ap = argparse.ArgumentParser(description="Descarga reportes SYNOP crudos de OGIMET (getsynop) por estación (con caché).")
    ap.add_argument('--anio', type=int, required=True)
    ap.add_argument('--mes', type=int, required=True)
    ap.add_argument('--dia', type=int, default=None,
                     help="Día puntual (1-31). Si no se pasa, se descarga el mes completo en un solo pedido por estación.")
    args = ap.parse_args()

    estaciones = cargar_estaciones()
    print(f"Estaciones configuradas ({len(estaciones)}): {list(estaciones.keys())}\n")

    fallidas = []
    for nombre, wigos in estaciones.items():
        try:
            descargar_csv(nombre, wigos, args.anio, args.mes, args.dia)
        except Exception as e:
            print(f"  [ERROR] {nombre}: {e}")
            fallidas.append(nombre)

    print("\n=== Resumen ===")
    print(f"OK: {len(estaciones) - len(fallidas)}/{len(estaciones)}")
    if fallidas:
        print(f"Fallaron: {fallidas} -- volvé a correr este script para reintentar solo esas.")


if __name__ == '__main__':
    main()