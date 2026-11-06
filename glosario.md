# Glosario

Términos de Python y de datos que aparecen en el curso, explicados para
quien nunca programó. Entre paréntesis, el día en que aparecen por primera
vez.

## Herramientas y entorno

| Término | Qué es |
|---|---|
| **Terminal** (antes del curso) | La ventana donde se escriben órdenes (`cd`, `ls`, `conda`, `git`). |
| **Conda / entorno** (antes del curso) | Conda instala librerías. Un *entorno* es una «caja» con sus propias librerías y versiones; el del curso se llama `wrf2026` y se activa con `conda activate wrf2026` en cada terminal nueva. |
| **`environment.yml`** (antes del curso) | La lista de librerías del entorno, con sus versiones fijadas, para que todos tengan lo mismo. |
| **Jupyter / notebook (`.ipynb`)** (Día 1) | Documento que mezcla texto y código en **celdas**. Una celda se ejecuta con Shift+Enter. |
| **Kernel** (antes del curso) | El «motor» de Python que ejecuta las celdas de un notebook. En el curso se usa `Python (wrf2026)`. Si algo se comporta raro, *Kernel → Restart* empieza de cero. |
| **Script (`.py`)** (Día 1) | Archivo de texto con código Python que se ejecuta desde la terminal: `python3 archivo.py`. |
| **Librería / `import`** (Día 1) | Código que otros ya escribieron (NumPy, Pandas…). `import numpy as np` la deja disponible con el nombre corto `np`. |
| **Git** (antes del curso) | Programa que guarda la historia de una carpeta. `git pull` trae lo nuevo del curso; `git commit` guarda una versión; `git stash` aparta cambios propios. |
| **`.gitignore`** (Día 10) | Lista de archivos que Git no debe guardar (datos pesados, resultados, `__pycache__/`). |

## Python básico (Días 1 y 2)

| Término | Qué es |
|---|---|
| **Variable** | Un nombre que apunta a un valor: `temperatura = 27.8`. |
| **Tipo** | La clase de valor: número entero (`int`), decimal (`float`), texto (`str`), verdadero/falso (`bool`). `"27.8"` (texto) no es lo mismo que `27.8` (número). |
| **`None`** | «Nada», «sin valor». En el curso representa una hora `S/D` (sin dato) de SENAMHI. |
| **Lista** | Colección ordenada: `[21.7, 21.5, 22.0]`. Se accede por posición, empezando en 0: `lista[0]`. |
| **Diccionario** | Colección de pares nombre → valor: `{"lat": -12.08, "lon": -76.94}`. Se accede por nombre: `d["lat"]`. |
| **Bucle `for`** | Repite un bloque para cada elemento: `for t in temperaturas: ...`. |
| **Condicional `if / elif / else`** | Ejecuta un bloque solo si se cumple una condición. |
| **Función** | Bloque de código con nombre que recibe datos (**argumentos**) y devuelve un resultado (`return`). Se escribe una vez y se usa muchas. |
| **Error / traceback** | El mensaje en rojo cuando algo falla. La **última línea** dice qué pasó (`KeyError`, `TypeError`, `FileNotFoundError`…). |

## Datos con NumPy, Pandas y Xarray (Días 2 y 3)

| Término | Qué es |
|---|---|
| **Arreglo (array) de NumPy** | Tabla de números de cualquier número de dimensiones, sobre la que se opera sin bucles: `arreglo.mean()`. |
| **`NaN`** | «No es un número»: el hueco de un dato faltante en NumPy/Pandas. `np.mean` con un `NaN` da `nan`; `np.nanmean` lo ignora. |
| **Broadcasting** | Regla de NumPy para operar arreglos de formas distintas (p. ej. sumar un perfil vertical a toda una grilla 3D). |
| **`Series` / `DataFrame` (Pandas)** | Una columna de datos con índice (`Series`) o una tabla de varias columnas (`DataFrame`). |
| **`DatetimeIndex` / `resample`** | Índice de fechas de Pandas. Con él, `resample("1D").mean()` pasa de datos horarios a promedios diarios. |
| **`DataArray` / `Dataset` (Xarray)** | Un arreglo con nombres de dimensiones y coordenadas (`DataArray`), o varios de ellos juntos (`Dataset`), como un NetCDF en memoria. |
| **Dimensión / coordenada** | La dimensión es el nombre de un eje (`time`, `latitude`); la coordenada, sus valores (las fechas, las latitudes). |
| **`.sel` / `.isel`** | Seleccionar por valor de coordenada (`.sel(estacion="Ceres")`) o por posición (`.isel(estacion=3)`). |
| **`slice`** | Un rango para recortar: `slice(-8, -14)`. Con latitud descendente, el orden es de norte a sur. |
| **`nearest` / `interp`** | Tomar el punto de grilla más cercano, o calcular un valor intermedio entre los vecinos (interpolación bilineal). |
| **Apertura perezosa (*lazy loading*)** | Xarray abre un archivo leyendo solo su descripción; los números se leen cuando hacen falta (o con `.load()`). |

## Formatos y fuentes (Días 3 a 5)

| Término | Qué es |
|---|---|
| **NetCDF (`.nc`)** | Formato de archivo autodescriptivo para datos en grilla; el de ERA5 y el `wrfout`. |
| **GRIB2 (`.grib2`)** | Formato compacto de los centros operativos (GFS, FNL). Se abre con `cfgrib`. |
| **Convenciones CF** | Reglas para nombres y unidades de variables en NetCDF (`units`, `standard_name`). |
| **ERA5 / GFS / FNL** | Reanálisis de ECMWF (pasado) / pronóstico global de NOAA (futuro) / análisis final de NCEP (pasado reciente). |
| **`cdsapi`** | Librería para pedir ERA5 al Copernicus Climate Data Store; necesita la clave en `~/.cdsapirc`. |
| **Herbie** | Librería para descargar GFS y otros modelos desde la nube, sin cuenta. |
| **Vtable** | Tabla del WPS que dice qué variables y niveles toma `ungrib` de un GRIB; define qué hay que descargar. |

## WRF y validación (Días 6 a 10)

| Término | Qué es |
|---|---|
| **`wrfout`** | Archivo NetCDF de salida del WRF. |
| **Grilla escalonada (Arakawa-C) / *destagger*** | En el WRF, U y V están medio punto desplazados respecto a T2; *destagger* los lleva a los mismos puntos. |
| **`xwrf`** | Librería que prepara el `wrfout` para Xarray (coordenadas, proyección, *destagger*). |
| **Proyección / CRS / `transform`** | Cómo se dibuja la Tierra en un plano. En Cartopy, `transform` dice en qué sistema están los datos y `projection` cómo se dibuja el mapa. |
| **bias, MAE, RMSE** | Error medio con signo, error absoluto medio y raíz del error cuadrático medio. |
| **r, KGE** | Correlación (¿sigue el patrón?) y Kling-Gupta (combina correlación, sesgo `beta` y variabilidad `alpha`). |
| **Diagrama de Taylor** | Gráfico que resume r, desviación estándar y RMSD de varios modelos frente a la observación. |
| ***Added value*** | Si el modelo regional (WRF) mejora frente al modelo global que lo forzó, contra la misma observación. |
| **Pipeline** | El flujo completo encadenado (entrada → salida → validación) que corre con un solo comando o notebook. |
