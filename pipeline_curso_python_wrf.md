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
| Miniconda / entornos virtuales | Aislar dependencias científicas (netCDF4, cartopy, etc.) |
| Jupyter Notebook | Entorno de ejecución interactivo para cada práctica |
| NumPy | Operaciones numéricas vectorizadas sobre arreglos |
| Pandas | Manejo de series temporales y datos tabulares (observaciones) |
| Xarray | Estructura central del curso: maneja NetCDF como arreglos etiquetados (N-D) |
| Matplotlib | Motor de graficado base para todas las visualizaciones |

Xarray es la pieza que conecta las tres etapas: se usa igual para leer datos de
entrada, leer salidas `wrfout` y para interpolar contra observaciones.

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
   vez que se lanza una nueva simulación).
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
2. **Interpolar la salida del WRF** a los puntos exactos de observación (para
   poder comparar punto a punto).
3. **Calcular métricas estadísticas:**
   - RMSE (error cuadrático medio)
   - MAE (error absoluto medio)
   - Correlación de Pearson (r)
   - KGE (Kling–Gupta), que descompone el error en correlación, sesgo y
     variabilidad — métrica más completa, presente desde la v2 en adelante.
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
   final del curso.

## 7. Cómo evolucionó el pipeline entre versiones (resumen técnico)

| Aspecto | v1 | v2 | v3 | v4 |
|---|---|---|---|---|
| Nº de módulos | 5 | 6 | 6 | 6 (formato condensado) |
| Descarga de entrada | Solo `cdsapi` (ERA5) | + `Herbie` (GFS/ECMWF multi-fuente) | Igual que v2 | Igual que v2 |
| Lectura de `wrfout` | `xarray` directo | + `xwrf` (extracción de variables físicas) | Igual que v2 | Igual que v2 |
| Métricas de validación | RMSE, MAE, correlación | + KGE, *added value*, diagrama de Taylor | Igual que v2 | Igual que v2 |
| Módulo de integración/pipeline | No (solo práctica final) | Sí, módulo 6 explícito | Sí | Sí |
| Animaciones de salidas | No | Sí | Sí | Sí |

**Lectura del cambio:** v1 cubre el pipeline mínimo viable (descarga → mapa →
métrica básica). A partir de v2 el pipeline se profesionaliza: se añade una
segunda fuente de datos de entrada (`Herbie`), una capa de traducción de variables
nativas del WRF (`xwrf`), métricas de validación más rigurosas (KGE, *added
value*, Taylor) y un módulo dedicado a convertir todo en un pipeline reproducible
en vez de una secuencia de notebooks independientes. v3 y v4 mantienen ese mismo
pipeline técnico; sus diferencias son de nivel de entrada del curso y de formato
del documento, no del flujo de trabajo en sí.
