# Pipeline de Trabajo — Curso de Python Aplicado al WRF

> Documento explicativo. Consolida el flujo técnico enseñado en el curso a partir del
> análisis de las versiones de la propuesta técnica del curso.
> No es código ni un cronograma: describe **qué problema resuelve cada etapa, con qué
> herramientas y qué produce como salida**, para tenerlo como referencia única del curso.

## 1. Visión general

El curso enseña a automatizar en Python el ciclo completo de trabajo de un modelador
que usa WRF (*Weather Research and Forecasting model*). Ese ciclo tiene tres grandes
momentos —**entrada, salida y validación**— y todas las versiones de la propuesta
coinciden en ese mismo eje, aunque difieren en profundidad y herramientas:

```mermaid
flowchart LR
    A[Datos de entrada\nERA5 / GFS / FNL] --> B[Preprocesamiento\nGRIB2 → NetCDF]
    B --> C[WRF\n(fuera del alcance del curso)]
    C --> D[Salidas wrfout]
    D --> E[Visualización\nmapas, series, animaciones]
    D --> F[Validación\nvs. observaciones]
    E --> G[Resultados / reporte]
    F --> G
```

El curso **no ejecuta el WRF**: toma sus insumos (para prepararlos) y sus salidas
(para leerlas, graficarlas y validarlas). Python es la capa que envuelve al modelo,
no el modelo en sí.

## 2. Fundamentos comunes a todo el pipeline

Antes de tocar datos atmosféricos, todas las versiones dedican un bloque a nivelar
herramientas de Python que se usan transversalmente en las etapas siguientes:

| Herramienta | Rol en el pipeline |
|---|---|
| Miniconda / entornos virtuales | Aislar dependencias científicas (netCDF4, cartopy, etc.). `environment.yml` fija la versión de cada librería, para que todas las máquinas tengan lo mismo |
| Jupyter Notebook | Entorno de ejecución interactivo para cada práctica, con el kernel `Python (wrf2026)` registrado antes del curso |
| Git | Recibir las actualizaciones del curso (`git pull`) y, al cierre, versionar el proyecto propio |
| NumPy | Operaciones numéricas vectorizadas sobre arreglos |
| Pandas | Manejo de series temporales y datos tabulares (observaciones) |
| Xarray | Estructura central del curso: maneja NetCDF como arreglos etiquetados (N-D) |
| Matplotlib | Motor de graficado base para todas las visualizaciones |

Xarray es la pieza que conecta las tres etapas: se usa igual para leer datos de
entrada, leer salidas `wrfout` y para interpolar contra observaciones.

La preparación previa (instalar el entorno, registrar el kernel, configurar la
identidad de Git y las credenciales de Copernicus) está en `antes_del_curso.md`.
Los términos de Python y de datos, explicados para quien nunca programó, están en
`glosario.md`.

### Metodología de las prácticas

El curso está pensado para participantes con formación en meteorología y WRF,
pero sin experiencia en programación. Por eso:

- **Días 1 a 3 (Python básico y formatos):** cada ejercicio tiene tres celdas
  seguidas:
  1. **Ejemplo resuelto**, que el participante ejecuta y lee.
  2. **Tu turno**, con el mismo problema para otra estación, otro día u otra
     variable. Las líneas a completar están marcadas con ✍️. La celda corre sin
     error aunque esté incompleta, así que «ejecutar todo» nunca se rompe.
  3. **Comprobar**, que responde ✅ si el resultado es correcto, ❌ con una pista,
     o ⏳ si todavía no se completó.
- **Desde el Día 3, datos reales:** los ejemplos pueden usar datos sintéticos
  (rotulados como tales). Los «tu turno» usan los datos reales del repositorio:
  SENAMHI en `data/senamhi/` y ERA5 en `data/era_muestra/`.
- **Preguntas de interpretación:** el participante escribe su respuesta en una
  celda propia. La respuesta modelo está oculta en una sección desplegable,
  para abrirla después de responder.
- **Copias personales:** cada participante guarda sus notebooks como
  `*_mio.ipynb`. Git ignora esos archivos, así que `git pull` no choca con el
  trabajo propio.
- **Verificación automática:** en cada cambio, GitHub Actions ejecuta de punta
  a punta los notebooks que no dependen de descargas (Módulos 1, 2, 4, 5 y 6).
  Así se comprueba que el material corre con el entorno fijado. Las descargas
  del Módulo 3 (CDS, FNL, GFS) se prueban en las máquinas de los
  participantes, porque dependen de credenciales y de servicios externos.

## 3. Etapa 1 — Formatos y adquisición de datos de entrada

**Problema que resuelve:** el WRF necesita condiciones iniciales y de frontera
(temperatura, viento, humedad, presión) provenientes de un modelo global o reanálisis.
Descargar y preparar estos datos manualmente es lento y propenso a error.

**Flujo:**

1. **Entender los formatos fuente** — NetCDF (con convenciones CF) y GRIB/GRIB2, el
   formato binario estándar en meteorología operativa.
   - Lectura NetCDF → `xarray`
   - Lectura GRIB/GRIB2 → `cfgrib`
2. **Ubicar el repositorio correcto** según la necesidad:
   - **ERA5** (reanálisis, Copernicus/CDS) — mejor para climatología o casos pasados.
   - **GFS** (NOAA/NCEP, vía NOMADS/AWS/Google Cloud) — para pronóstico operativo.
   - **FNL** (RDA-NCAR) — alternativa de reanálisis operativo.
3. **Descargar de forma automatizada**, no manual:
   - `cdsapi` → ERA5 (requiere credenciales de cuenta CDS configuradas antes del curso).
   - `Herbie` → acceso unificado a GFS/ECMWF desde múltiples fuentes, con selección
     programática de modelo, fecha y variable.
4. **Parametrizar la descarga** — scripts que reciben fecha, área geográfica y
   variables como argumentos, pensados para correr de forma recurrente (p. ej. cada
   vez que se lanza una nueva simulación). Los parámetros se validan antes de
   contactar al servidor. Por ejemplo, si las fechas están invertidas o el periodo
   cruza de un mes a otro (CDS pide un pedido por mes), el script avisa con un
   mensaje claro en vez de fallar más adelante.
5. **Verificar integridad** de lo descargado antes de alimentarlo al WRF.
6. **Preprocesar** — convertir GRIB2 a NetCDF, recortar dominio, interpolar a la
   grilla necesaria (`xarray` + `scipy`).

**Salida de la etapa:** archivos de entrada verificados y en el formato correcto,
listos para el preprocesador del WRF (WPS/real.exe, fuera del alcance del curso).

## 4. Etapa 2 — Lectura y visualización de salidas del WRF

**Problema que resuelve:** los archivos `wrfout` usan coordenadas nativas (grilla
Arakawa-C, niveles eta) poco intuitivas; hay que extraerlas, transformarlas a
variables físicas legibles y comunicar el resultado visualmente.

**Flujo:**

1. **Entender la estructura de `wrfout`** — variables nativas, dimensiones,
   coordenadas y metadatos propios del WRF.
2. **Extraer variables físicas** con `xwrf`, que traduce las variables nativas a
   variables estándar (temperatura, viento, presión, humedad, precipitación) sobre
   una estructura `xarray`.
3. **Generar mapas georreferenciados** con `cartopy` + `matplotlib`:
   temperatura en superficie, campos de viento, precipitación acumulada.
   Opcionalmente `geopandas` para superponer límites administrativos (shapefiles).
4. **Series temporales y promedios espaciales** — reducir la dimensión espacial o
   temporal según el análisis que se necesite.
5. **Animaciones** — combinar múltiples `wrfout` (distintos tiempos) en una
   secuencia animada.
6. **Exportar resultados** de vuelta a NetCDF, para reutilizarlos o compartirlos.

**Salida de la etapa:** mapas, series temporales, animaciones y productos
derivados en NetCDF, listos para inspección visual o para alimentar la etapa de
validación.

## 5. Etapa 3 — Validación de resultados

**Problema que resuelve:** una simulación sin comparar contra observaciones no
tiene valor científico demostrado; hay que cuantificar qué tan bien reproduce la
realidad y si aporta algo frente a sus propios datos de entrada.

**Flujo:**

1. **Reunir observaciones** — estaciones meteorológicas superficiales, datos
   satelitales o reanálisis usados como referencia "verdad terreno". En el
   curso, estas observaciones son reales: mensajes SYNOP crudos de
   estaciones de superficie, descargados y decodificados hora por hora (ver
   "Herramientas auxiliares" más abajo) — nunca coordenadas ni valores
   inventados. Toda estación usada para comparar contra el WRF o el modelo
   global está verificada dentro del dominio real de la simulación; las
   estaciones fuera de ese dominio (p. ej. Perú, para el caso de muestra
   del curso, cuyo dominio real cubre Argentina/Uruguay/sur de Brasil) se
   usan solo para práctica de carga y análisis puramente observacional,
   nunca para "inventar" una correspondencia espacial que no existe.
2. **Llevar la salida del WRF al punto de observación** (para poder comparar
   punto a punto). Con el `wrfout` se toma el **punto de grilla más cercano** a la
   estación, porque su latitud y su longitud son tablas 2D y `.interp()` de
   Xarray solo interpola sobre coordenadas 1D. Con celdas de pocos km, la
   diferencia con una interpolación bilineal es pequeña. La interpolación
   (`.interp()`) se practica en el Módulo 2 con ERA5, que sí tiene coordenadas
   1D. La diferencia entre ambos métodos se compara allí.
3. **Calcular métricas estadísticas:**
   - RMSE (error cuadrático medio)
   - MAE (error absoluto medio)
   - Correlación de Pearson (r)
   - KGE (Kling–Gupta), que descompone el error en correlación, sesgo y
     variabilidad — métrica más completa, presente desde la v2 en adelante.
   - Las métricas se calculan **estación por estación**, además de en forma
     agregada. Juntar todas las estaciones en una sola serie infla `r` y el
     KGE, porque la diferencia de temperatura entre estaciones es fácil de
     reproducir para cualquier modelo.
4. **Evaluar el "added value"** — comparar las métricas del WRF contra las de su
   propio dato de forzamiento (p. ej. ERA5) frente a las observaciones, para
   verificar si la simulación de alta resolución realmente mejora algo.
5. **Visualizar la validación** — diagramas de dispersión, diagramas de Taylor
   (resumen de correlación, desviación estándar y RMSE en un solo gráfico,
   construidos con el paquete `SkillMetrics`), y tablas comparativas.
6. **Automatizar el cálculo** para múltiples variables y períodos, en vez de
   repetirlo manualmente por cada caso.

**Salida de la etapa:** métricas cuantitativas y gráficos de validación que
respaldan (o cuestionan) la calidad de la simulación.

**Herramientas auxiliares desarrolladas/usadas para esta etapa (no son el
foco de enseñanza del curso, solo el medio para tener datos reales con
que validar):**
- Scripts propios de descarga y decodificación de reportes SYNOP de
  OGIMET (`requests` para la descarga, `pymetdecoder` para decodificar el
  mensaje crudo a temperatura/viento/precipitación por hora) — el
  resultado (observación real, hora real, punto real) es lo que entra al
  resto del pipeline; el scraping en sí no se enseña como contenido del
  curso. `data/h0_datos_ogimet.sh` orquesta los tres pasos
  (`h1_ogimet.py` descarga → `h2_procesa_horario.py` decodifica →
  `h3_junta_mensual.py` consolida el mes) para un rango de fechas; no es
  foco de clase, pero se muestra como ejemplo de herramienta ya lista
  para conseguir datos observados reales.
- `SkillMetrics` (paquete existente, no desarrollado en el curso) para
  construir los diagramas de Taylor, en vez de reimplementar la geometría
  polar a mano — mismo principio de "usar la herramienta estándar del
  ecosistema" que ya aplica `xwrf` en la Etapa 2.

## 6. Etapa de cierre — Integración en un pipeline reproducible

Presente como módulo explícito desde la v2 en adelante. No añade una técnica
nueva: consolida las tres etapas anteriores en un flujo único, reproducible y
parametrizado.

**Flujo:**

1. Definir una **estructura de directorios** estándar (entrada / salida / validación
   / resultados).
2. Aplicar **buenas prácticas de código** (parametrización, funciones reutilizables
   en vez de notebooks sueltos).
3. Ejecutar el **flujo completo de punta a punta** — descarga → preprocesamiento →
   visualización → validación — sobre un caso de muestra, como práctica integradora
   final del curso. En clase, la descarga de ERA5 de esta etapa es **sintética**
   (genera un archivo con la misma estructura que el real), para que el pipeline
   corra sin esperar la cola de Copernicus. La descarga real ya se practicó en la
   Etapa 1, y en un proyecto propio se reemplaza sin cambiar el resto del
   pipeline.
4. **Versionar el proyecto con Git** — `git init`, un `.gitignore` que excluye
   datos, resultados y `__pycache__/`, y un primer commit que incluye el código,
   la configuración, el `environment.yml` y el notebook final.

## 7. Cómo evolucionó el pipeline entre versiones (resumen técnico)

| Aspecto | v1 | v2 | v3 | v4 | Repositorio 2026 |
|---|---|---|---|---|---|
| Nº de módulos | 5 | 6 | 6 | 6 (formato condensado) | 6 (10 días) |
| Descarga de entrada | Solo `cdsapi` (ERA5) | + `Herbie` (GFS/ECMWF multi-fuente) | Igual que v2 | Igual que v2 | Igual que v2 (GFS con Herbie, ERA5 con `cdsapi`, FNL), con validación de fechas antes de descargar |
| Lectura de `wrfout` | `xarray` directo | + `xwrf` (extracción de variables físicas) | Igual que v2 | Igual que v2 | Igual que v2 |
| Métricas de validación | RMSE, MAE, correlación | + KGE, *added value*, diagrama de Taylor | Igual que v2 | Igual que v2 | + métricas por estación |
| Módulo de integración/pipeline | No (solo práctica final) | Sí, módulo 6 explícito | Sí | Sí | Sí, con versionado en Git |
| Animaciones de salidas | No | Sí | Sí | Sí | Sí |
| Prácticas de los primeros días | — | — | — | — | Ejemplo resuelto + tu turno + comprobación |
| Reproducibilidad del entorno | — | — | — | — | Versiones fijadas, kernel propio y CI |

**Lectura del cambio:** v1 cubre el pipeline mínimo viable (descarga → mapa →
métrica básica). A partir de v2 el pipeline se profesionaliza: se añade una
segunda fuente de datos de entrada (`Herbie`), una capa de traducción de variables
nativas del WRF (`xwrf`), métricas de validación más rigurosas (KGE, *added
value*, Taylor) y un módulo dedicado a convertir todo en un pipeline reproducible
en vez de una secuencia de notebooks independientes. v3 y v4 mantienen ese mismo
pipeline técnico; sus diferencias son de nivel de entrada del curso y de formato
del documento, no del flujo de trabajo en sí.

El repositorio 2026 mantiene el pipeline de v2 a v4 y cambia sobre todo la forma
de enseñarlo. Las prácticas de los primeros días alternan un ejemplo resuelto con
uno que el participante completa y comprueba solo. El entorno queda fijado y se
verifica automáticamente. Además:
- las descargas validan sus parámetros antes de contactar al servidor;
- la validación se reporta también estación por estación;
- el pipeline final se versiona con Git.
