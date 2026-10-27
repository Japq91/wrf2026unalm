# Material del curso

Hay una carpeta por módulo. El `README.md` de cada una tiene la teoría
(2 h por día) y la práctica (3 h por día) de ese módulo. Las diapositivas
de teoría están en [`../slides/`](../slides/), una por clase, y el flujo
completo del curso se resume en
[`../pipeline_curso_python_wrf.md`](../pipeline_curso_python_wrf.md).

El entorno `wrf2026` se instala antes de la primera clase, a partir de
[`../environment.yml`](../environment.yml), siguiendo
[`../antes_del_curso.md`](../antes_del_curso.md).

## Días y módulos

| Días | Módulo | Contenido | Notebooks |
|---|---|---|---|
| 1–2 | [Módulo 1 — Python básico](modulo_01_python_basico/README.md) | Sintaxis, funciones, NumPy, introducción a Xarray, Pandas, Matplotlib | [`notebooks/`](modulo_01_python_basico/notebooks/) |
| 3 | [Módulo 2 — Formatos de datos atmosféricos](modulo_02_formatos_datos_atmosfericos/README.md) | NetCDF, GRIB/GRIB2, convenciones CF, selección, recorte e interpolación | [`notebooks/`](modulo_02_formatos_datos_atmosfericos/notebooks/) |
| 4–5 | [Módulo 3 — Descarga de datos de entrada](modulo_03_descarga_datos_entrada/README.md) | ERA5, GFS y FNL; `cdsapi`, `Herbie`; verificación de integridad y preprocesamiento | [`notebooks/`](modulo_03_descarga_datos_entrada/notebooks/) |
| 6–7 | [Módulo 4 — Lectura y visualización de salidas WRF](modulo_04_lectura_visualizacion_wrf/README.md) | Estructura del `wrfout`, `xwrf`, mapas con `cartopy`, series, animaciones | [`notebooks/`](modulo_04_lectura_visualizacion_wrf/notebooks/) |
| 8–9 | [Módulo 5 — Validación de resultados](modulo_05_validacion_resultados/README.md) | RMSE, MAE, r, KGE, *added value*, diagramas de Taylor | [`notebooks/`](modulo_05_validacion_resultados/notebooks/) |
| 10 | [Módulo 6 — Pipeline integrado](modulo_06_pipeline_integrado/README.md) | Pipeline reproducible y proyecto final | [`notebooks/`](modulo_06_pipeline_integrado/notebooks/) |

## Notebooks

Cada módulo tiene cuatro notebooks en `notebooks/`:

1. `01_teoria_demos.ipynb`: las demostraciones que se muestran en la teoría.
2. `02_..._practica...ipynb`: primera parte de la práctica.
3. `03_..._practica...ipynb`: segunda parte de la práctica.
4. `04_entregable_...ipynb`: el entregable del módulo.

En los Días 1 a 3, cada ejercicio tiene tres celdas seguidas:

- **📘 Ejemplo resuelto:** lo ejecutas y lo lees.
- **✍️ Tu turno:** un problema parecido que resuelves tú, completando las
  líneas marcadas con `✍️`. La celda corre aunque esté incompleta.
- **✔️ Comprobar:** te dice `✅` si está bien, `❌` con una pista si no, o
  `⏳` si todavía no completaste nada.

Guarda tu trabajo como una copia con `_mio` al final del nombre. Así no
pierdes cambios y `git pull` sigue funcionando (más detalles en
[`antes_del_curso.md`](../antes_del_curso.md), sección 5).

## Qué datos usa cada módulo

| Módulo | Datos |
|---|---|
| 1 | Estaciones de SENAMHI en `data/senamhi/` |
| 2 | Los ejemplos resueltos usan datos sintéticos (`synth_data.py`); los «tu turno», el ERA5 de `data/era_muestra/` |
| 3 | Lo que se descarga en clase: GFS (Herbie, sin cuenta), ERA5 (`cdsapi`, con tu cuenta de Copernicus) y FNL (`data/descarga_FNL.csh`) |
| 4 y 5 | El `wrfout` recortado de `data/grid_muestra/`, ERA5-Land y observaciones SYNOP de `data/` |
| 6 | La validación usa GFS (Herbie, con copia en `data/modelos/`) y estaciones; la descarga de entrada y la salida del WRF son sintéticas (`synth_data_*.py`), y cada notebook lo indica |

Todos los notebooks se probaron de principio a fin con el entorno
`wrf2026`.

## Cómo está organizado cada módulo

- Al inicio, qué hace falta de los módulos anteriores y cómo activar el
  entorno (`conda activate wrf2026` y luego `jupyter lab`). La activación
  se repite cada vez que abres una terminal nueva.
- La teoría de cada día, con la física o la matemática necesaria para
  entender el código.
- La práctica de cada día, con un tiempo aproximado por ejercicio y el
  entregable.
- Al final, preguntas frecuentes y una pregunta de cierre del módulo.

Los datos de muestra están en [`data/`](../data/) (ver su `README.md`).
Solo falta lo que se descarga en el Módulo 3.
