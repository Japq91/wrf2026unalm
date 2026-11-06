# Datos del curso

En esta carpeta hay dos tipos de datos. Unos son pequeños y vienen en el
repositorio. Otros pesan demasiado para GitHub y aparecen solo cuando se
descargan o se generan en clase (están en el `.gitignore`).

## Incluidos en el repositorio

| Ruta | Qué es | Dónde se usa |
|---|---|---|
| `Vtable.GFS`, `Vtable.GDAS`, `Vtable.ERA5` | Tablas de `ungrib.exe` del WPS | M3, Día 4 |
| `grid_muestra/wrfout_real_muestra.nc`, `wrfpress_muestra.nc`, `wrfout_muestra.nc` | Recorte del `wrfout` del proyecto bigua (Argentina, Uruguay y sur de Brasil) | M4, M5 |
| `era_muestra/era5_land_20241213.nc` | ERA5-Land sobre el dominio del WRF | M5 |
| `era_muestra/era5_land_peru_20241213.nc`, `era5_peru_20241213.nc` | ERA5-Land y ERA5 sobre Perú | M2, M3 y M5 (extensión) |
| `obs/*_horario.csv` | Observaciones SYNOP ya decodificadas, cada 3 h | M5; `Lima_2025_03` en M6 |
| `senamhi/*_2025_03.csv`, `senamhi/estaciones_lima.json` | 5 estaciones automáticas de SENAMHI en Lima, cada hora, marzo de 2025, en el formato en que las entrega SENAMHI (ver `senamhi/README.md`) | M1, M3, M6 (caso Lima) |
| `modelos/gfs_lima_20250314_00z.csv` | Pronóstico de GFS (ciclo del 14/03/2025, 00 UTC, de 0 a 72 h) en el punto más cercano a Lima-Callao y a cada estación de SENAMHI. Es una copia de respaldo por si no hay internet | M6 (caso Lima) |
| `ogimet/coords_*.json`, `estaciones_*.json` | Coordenadas e indicativos OMM de las estaciones | M3, M5 |

## No incluidos: se descargan o se generan en clase

| Ruta (patrón en `.gitignore`) | Por qué no está | Cómo se obtiene |
|---|---|---|
| `gdas1.fnl*.grib2` (y su `.idx`) | Cada archivo pesa unos 450–480 MB (4 archivos, 1,9 GB en total) y GitHub no acepta archivos de más de 100 MB | `tcsh descarga_FNL.csh AAAAMMDD` (M3, Día 4); no pide cuenta |
| `grid/` | La corrida completa del WRF, unos 4,5 GB | No hace falta: el recorte está en `grid_muestra/` |
| `ogimet/peru/`, `ogimet/area_wrf/` | Descargas intermedias de OGIMET (HTML y CSV diarios) | `data/h0_datos_ogimet.sh`, que llama a `h1_ogimet.py`, `h2_procesa_horario.py` y `h3_junta_mensual.py`. Solo si quieres reprocesar desde cero; el resultado ya está en `obs/` |
| Lo que crean los notebooks (`src/**/*.nc`, `*.grib`, `*.grib2`, `*.gif`) | Se generan al correr los notebooks, sobre todo las descargas del Módulo 3 (con tu `.cdsapirc`) | Aparecen al ejecutar los notebooks |

Si un notebook falla con `FileNotFoundError` por un archivo de esta
segunda tabla, falta descargarlo o generarlo: la última columna dice cómo.
