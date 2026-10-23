# Datos del curso — qué está versionado y qué no

Esta carpeta mezcla datos reales pequeños que **sí viajan en el repositorio**
con datos reales pesados que **no existen acá** hasta que se descargan o se
generan en clase (ver `.gitignore`). Antes de dictar el curso, conviene saber
cuál es cuál.

## Sí versionado (real, pequeño, listo para usar)

| Ruta | Qué es | Módulo/Día |
|---|---|---|
| `Vtable.GFS`, `Vtable.GDAS`, `Vtable.ERA5` | Tablas reales de `ungrib.exe`/WPS | M3, Día 4 |
| `grid_muestra/wrfout_real_muestra.nc`, `wrfpress_muestra.nc`, `wrfout_muestra.nc` | Subconjunto real, recortado, del `wrfout` del proyecto bigua (Argentina/Uruguay/sur de Brasil) | M4, M5 |
| `era_muestra/era5_land_20241213.nc` | ERA5-Land real, dominio del WRF | M5 |
| `era_muestra/era5_land_peru_20241213.nc`, `era5_peru_20241213.nc` | ERA5-Land y ERA5 estándar reales, área de Perú (extensión opcional) | M3/M5, extensión |
| `obs/*_horario.csv` | Observaciones SYNOP reales ya decodificadas (cada 3 h) | M5; `Lima_2025_03` en M6 |
| `senamhi/*_2025_03.csv`, `senamhi/estaciones_lima.json` | 5 estaciones automáticas reales de SENAMHI en Lima, cada hora, marzo de 2025, en el formato original (ver `senamhi/README.md`) | M1 (ejercicios), M3 (cuarta fuente, integridad), M6 (caso Lima) |
| `modelos/gfs_lima_20250314_00z.csv` | Pronóstico real de GFS (ciclo 14/03/2025 00 UTC, 0–72 h) en el punto más cercano a Lima-Callao y a cada estación de SENAMHI; copia de respaldo por si no hay internet | M6 (caso Lima) |
| `ogimet/coords_*.json`, `estaciones_*.json` | Coordenadas e indicativos OMM reales | M3, M5 |

## NO versionado — no existe hasta que se descargue/genere en clase

| Ruta (patrón en `.gitignore`) | Por qué no viaja | Cómo se obtiene |
|---|---|---|
| `gdas1.fnl*.grib2` (+ `.idx`) | ~450-480 MB **cada archivo** (4 archivos, ~1.9 GB) — excede el límite duro de GitHub (100 MB/archivo) | `tcsh descarga_FNL.csh AAAAMMDD` (M3, Día 4) — no requiere credenciales |
| `grid/` | ~4.5 GB, corrida real completa del WRF sin recortar; superseded por `grid_muestra/` (sí versionado) | No hace falta regenerarlo — el recorte ya está en `grid_muestra/` |
| `ogimet/peru/`, `ogimet/area_wrf/` | Scrapes crudos/intermedios de OGIMET (HTML, CSV diarios sin consolidar) | `data/h0_datos_ogimet.sh` (orquesta `h1_ogimet.py` → `h2_procesa_horario.py` → `h3_junta_mensual.py`) — solo necesario si se quiere reprocesar desde cero; el resultado final (`obs/*_horario.csv`) ya está versionado |
| Descargas que hacen los propios notebooks (`src/**/*.nc`, `*.grib`, `*.grib2`, `*.gif`) | Se generan real y en vivo al correr el Módulo 3 en clase (requiere `.cdsapirc` propio) | Se crean solos al ejecutar los notebooks — no se preparan de antemano |

**Regla práctica para quien clone el repositorio:** si un notebook falla con
`FileNotFoundError` sobre algo de esta segunda tabla, no es un error del
repositorio — es un dato que hay que descargar o generar primero, siguiendo
la referencia de la columna "Cómo se obtiene".
