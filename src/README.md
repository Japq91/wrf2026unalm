# Curso Intermedio de Python Aplicado para el WRF — Material del curso

Material de los 6 módulos del curso, organizado en una carpeta por módulo.
Cada `README.md` contiene el desarrollo extenso de teoría (2 h/día) y
práctica (3 h/día) del módulo, pensado para dictarse en 10 días (50 horas
totales). Ver el
pipeline técnico consolidado en
[`../pipeline_curso_python_wrf.md`](../pipeline_curso_python_wrf.md), y el
entorno reproducible del curso en
[`../environment.yml`](../environment.yml) (entorno conda `wrf2026`, se
instala en la práctica del Día 1 del Módulo 1 clonando este repositorio), y
las [`../slides/`](../slides/) — 10 presentaciones HTML, una por clase,
para la parte de teoría de cada día.

## Mapa de días y módulos

| Días | Módulo | Contenido central | Notebooks |
|---|---|---|---|
| 1–2 | [Módulo 1 — Python básico](modulo_01_python_basico/README.md) | Sintaxis, funciones, NumPy, introducción a Xarray, Pandas, Matplotlib | [`notebooks/`](modulo_01_python_basico/notebooks/) |
| 3 | [Módulo 2 — Formatos de datos atmosféricos](modulo_02_formatos_datos_atmosfericos/README.md) | NetCDF, GRIB/GRIB2, convenciones CF, selección/recorte/interpolación | [`notebooks/`](modulo_02_formatos_datos_atmosfericos/notebooks/) |
| 4–5 | [Módulo 3 — Descarga de datos de entrada](modulo_03_descarga_datos_entrada/README.md) | ERA5/GFS/FNL, `cdsapi`, `Herbie`, verificación de integridad, preprocesamiento | [`notebooks/`](modulo_03_descarga_datos_entrada/notebooks/) |
| 6–7 | [Módulo 4 — Lectura y visualización de salidas WRF](modulo_04_lectura_visualizacion_wrf/README.md) | Estructura `wrfout`, `xwrf`, mapas con `cartopy`, series, animaciones | [`notebooks/`](modulo_04_lectura_visualizacion_wrf/notebooks/) |
| 8–9 | [Módulo 5 — Validación de resultados](modulo_05_validacion_resultados/README.md) | RMSE, MAE, r, KGE, *added value*, diagramas de Taylor | [`notebooks/`](modulo_05_validacion_resultados/notebooks/) |
| 10 | [Módulo 6 — Pipeline integrado](modulo_06_pipeline_integrado/README.md) | Pipeline reproducible, proyecto integrador final | [`notebooks/`](modulo_06_pipeline_integrado/notebooks/) |

## Notebooks (`.ipynb`)

Cada módulo tiene 4 notebooks ejecutables en `notebooks/`, con esta
estructura fija:

1. `01_teoria_demos.ipynb` — demostraciones cortas de cada idea de la teoría.
2. `02_..._practica...ipynb` — primer bloque de ejercicios de práctica.
3. `03_..._practica...ipynb` — segundo bloque de ejercicios de práctica.
4. `04_entregable_...ipynb` — ejercicio integrador/entregable del módulo.

Todos los notebooks están **ejecutados de punta a punta y sin errores**
(entorno `jap`, ver detalle de versiones en cada notebook) y usan **datos
sintéticos autocontenidos**: no requieren credenciales de Copernicus CDS ni
conexión a internet para correr. Donde el curso real usa una librería que sí
necesita credenciales (`cdsapi`) o una fuente remota (`Herbie`), el código
real se muestra igual como referencia (comentado o en un bloque de código
en el README/notebook), y la ejecución efectiva usa un generador local
equivalente en estructura y formato de archivo.

## Convenciones usadas en todos los módulos

- Cada módulo indica explícitamente sus **prerrequisitos** (de qué módulo
  anterior depende) y qué **entregable** produce cada día.
- Cada módulo abre con un bloque **"Antes de empezar: activar el
  entorno"** (`conda activate wrf2026` antes de `jupyter lab`), porque la
  activación de Conda no persiste entre sesiones de terminal nuevas —el
  entorno se crea una sola vez en el Módulo 1, pero se activa en cada
  sesión de trabajo.
- Cada módulo cierra con una sección **"Preguntas frecuentes"** que
  anticipa dudas concretas de los participantes (errores comunes,
  decisiones de diseño, límites de cada técnica), además del checkpoint de
  cierre.
- La teoría de cada día incluye el fundamento lógico, físico o matemático
  mínimo necesario para justificar la técnica, no solo la receta de código.
- La práctica de cada día está dimensionada para 3 horas, con tiempos
  orientativos por ejercicio.
- Los datasets de muestra (`wrfout`, datos de estaciones, reanálisis
  recortados) referidos en los módulos se distribuyen aparte, en el
  repositorio de material del curso.
