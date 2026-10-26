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

En los Días 1 a 3, cada ejercicio de práctica tiene tres partes:

- **📘 Ejemplo resuelto:** se ejecuta y se lee; es el modelo a imitar.
- **✍️ Tu turno:** un problema parecido que escribe el participante. La
  celda corre sin errores aunque esté incompleta; hay que completar las
  líneas marcadas con `✍️`.
- **✔️ Comprobar:** responde `✅`, `❌` con una pista, o `⏳` si todavía
  no se completó nada.

Los notebooks se ejecutaron de punta a punta con el entorno `wrf2026` de
[`environment.yml`](../environment.yml) (versiones fijadas). **Qué datos usa
cada módulo:**

| Módulo | Datos |
|---|---|
| 1 | Reales: estaciones de SENAMHI en `data/senamhi/` |
| 2 | Ejemplos resueltos **sintéticos** (`synth_data.py`); los «tu turno», ERA5 **real** de `data/era_muestra/` |
| 3 | **Descargas reales** por internet: GFS (Herbie, sin cuenta), ERA5 (`cdsapi`, con la cuenta de Copernicus de `antes_del_curso.md`) y FNL (`data/descarga_FNL.csh`) |
| 4 y 5 | Reales: `wrfout` recortado (`data/grid_muestra/`), ERA5-Land y observaciones SYNOP incluidos en `data/` |
| 6 | Etapa 3 (validación) real: GFS (Herbie, con copia en `data/modelos/`) y estaciones. Etapas 1 y 2 **sintéticas** (`synth_data_*.py`), avisado en cada notebook |

Para trabajar sin perder cambios ni bloquear `git pull`, cada participante
guarda su copia con el sufijo `_mio` (ver
[`antes_del_curso.md`](../antes_del_curso.md), sección 5).

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
  recortados) vienen en la carpeta [`data/`](../data/) de este mismo
  repositorio (ver su `README.md`). Lo único que no viene es lo que se
  descarga en el Módulo 3.
