# Módulo 3 — Descarga automatizada de datos de entrada para el WRF

[Índice del curso](../README.md)

**Ubicación en el curso:** Días 4–5 de 10 · **Carga horaria:** 10 h (2 h teoría + 3 h práctica por día)
**Precede a:** [Módulo 4 — Lectura y visualización de salidas WRF](../modulo_04_lectura_visualizacion_wrf/README.md)
**Requiere:** [Módulo 2 — Formatos de datos atmosféricos](../modulo_02_formatos_datos_atmosfericos/README.md)

## Objetivo del módulo

Al finalizar el módulo, el participante podrá automatizar —mediante scripts
parametrizados, no descargas manuales— la obtención de datos meteorológicos
globales (ERA5 y GFS) que sirven como condición inicial y de frontera para el
WRF, verificar que lo descargado esté íntegro y completo, y dejarlo
normalizado en un formato consistente para el resto del pipeline.

## Por qué este módulo importa para el WRF

El WRF simula el tiempo en una región (por ejemplo, el Perú). Para
arrancar necesita dos cosas que vienen de un modelo global:

- **Condición inicial:** cómo está la atmósfera en toda la región en el
  momento en que empieza la simulación.
- **Condiciones de frontera:** qué entra por los bordes de la región
  mientras la simulación avanza (el aire que llega del Pacífico, de la
  Amazonía, etc.).

Bajar esos datos a mano desde un portal web sirve una vez, pero no para 30
fechas ni para repetir el trabajo cuando cambia el caso. Este módulo
convierte esa descarga en funciones que se reutilizan.

## Prerrequisitos específicos

Haber completado el Módulo 2 (apertura de NetCDF/GRIB con Xarray/`cfgrib`,
necesario para la verificación de integridad del Día 5). Se requiere además
tener creada, **antes de esta sesión**, una cuenta activa en el Copernicus
Climate Data Store (CDS) con las licencias de ERA5 aceptadas, ya que la
validación de credenciales puede tardar en aprobarse (paso 5 de
[`antes_del_curso.md`](../../antes_del_curso.md)).

## Antes de empezar: activar el entorno

En cada terminal nueva, activa el entorno **antes** de abrir Jupyter:
```bash
conda activate wrf2026
jupyter lab
```
`herbie-data` y `cdsapi` ya vienen en `wrf2026`. Lo único nuevo en este
módulo es configurar tus credenciales del CDS (`.cdsapirc`), en la práctica
del Día 4.

---

## Día 4 — Repositorios globales, Herbie y cdsapi

### Teoría (2 h)

**1. Reanálisis o pronóstico: dos tipos de dato (~20 min)**
Elegir mal la fuente es un error común. Hay tres fuentes de modelo en el
curso, y una cuarta de observaciones:
- **ERA5 (Copernicus) es un reanálisis:** una reconstrucción del tiempo que
  **ya pasó**, hecha mezclando un modelo con millones de observaciones
  reales (estaciones, satélites, globos). Usa el mismo método para todo el
  registro desde 1940, así que sirve para estudiar el clima o para
  reproducir un evento pasado.
- **GFS (NOAA, EE. UU.) es un pronóstico:** un modelo que se corre cuatro
  veces al día (00, 06, 12 y 18 UTC) y calcula cómo estará la atmósfera en
  las horas siguientes. Cada hora hacia adelante se llama paso de
  pronóstico (`fxx`). Es la fuente para simular algo que **todavía no
  pasó**.
- **FNL (NOAA)** es el estado de la atmósfera que el sistema de GFS estima
  para cada hora, revisado después. Se usa como alternativa a GFS para
  casos recientes, y se descarga sin cuenta (Sección 3b).
- **SENAMHI** no es un modelo: son **mediciones** de estaciones
  meteorológicas del Perú. No entran al WRF; sirven para comprobar si lo
  que simuló se parece a lo que pasó (Sección 3c).

La pregunta que debe poder responder el participante al terminar esta
sección no es "¿cómo se descarga cada uno?" (eso viene después) sino
**"¿cuál corresponde a mi caso de uso?"**.

Una confusión frecuente: "más reciente" no significa "mejor". Para
reproducir un evento que **ya ocurrió**, ERA5 suele ser la mejor opción,
porque incorporó las observaciones de ese período; GFS es la opción correcta
cuando el evento aún no ocurre o cuando se quiere evaluar un pronóstico real.

**2. Herbie: GFS sin buscar direcciones (~25 min)**
Los archivos de GFS están copiados en varios servidores (de NOAA, de
Amazon, de Google) y cada uno guarda distinta cantidad de días. Herbie
busca por ti dónde está el archivo: le dices modelo, fecha, hora de corrida
y paso de pronóstico, y lo encuentra. Son tres pasos:
`Herbie(fecha, model="gfs", fxx=...)` → `.download()` (baja el archivo) →
`.xarray()` (lo abre como un `Dataset`, igual que en el Módulo 2).

`fxx=0` no es "sin pronóstico": es el estado de la atmósfera en la hora
misma de la corrida. `fxx=6` es lo que el modelo calcula para 6 horas
después.

**3. cdsapi: pedir turno para ERA5 (~25 min)**
Descargar ERA5 funciona como sacar turno en un banco: `cdsapi` envía el
pedido (qué variable, qué fechas, qué área), el servidor de Copernicus lo
pone en la fila y lo prepara cuando le toca, y recién ahí entrega el
archivo. Puede tardar segundos o varios minutos según cuánta gente esté
pidiendo datos. Que se "quede esperando" no es un error. Por eso conviene
un script: lanza el pedido y espera solo.

Se ve cómo guardar la clave personal (archivo `.cdsapirc`) y cómo se arma
un pedido: un diccionario con `variable`, `year`, `month`, `day`, `time`,
`area` y `format`. Ojo con `area`: va en el orden
`[norte, oeste, sur, este]`.

**3b. FNL: descarga real por HTTPS directo, sin API (~15 min)**
GDEX (NCAR) publica los archivos FNL (`d083003`) como archivos planos con
una URL predecible por fecha y paso de pronóstico, sin cuenta ni cliente
Python. Se descargan con un script de `wget` que arma esas URLs
(`data/descarga_FNL.csh`). La lección: automatizar no siempre significa usar
un paquete de Python; a veces es escribir el script que arma las URLs.
Detalle del patrón de URL y de cuándo conviene FNL, en
[Para profundizar](#para-profundizar).

**3c. SENAMHI: estaciones, con una persona en el medio (~15 min)**
El portal «Mapa de estaciones» de SENAMHI entrega CSV con datos hora por
hora de cada estación, pero pide pasar una verificación «no soy un robot»
(Cloudflare) en cada descarga. Esa verificación existe para que ningún
programa descargue solo, así que siempre hay una persona en el medio. El
docente lo muestra con [`station-hist`](https://github.com/Japq91/station-hist):
la herramienta abre el navegador, la persona pasa la verificación, y el
script hace el resto (bajar, unir y guardar el CSV). La lección:
automatizar no siempre significa sacar a la persona; se automatiza todo lo
demás y se respeta lo que el sitio pide hacer a mano.

Guion de la demostración (en vivo, ~5 min): buscar la estación por nombre
(`--search`), elegir la versión **automática** (hay dos con el mismo
nombre), descargar un año, mostrar el CSV que sale y recortar el mes. El
paso a paso completo, para quien quiera bajar otras estaciones, está en
[`data/senamhi/README.md`](../../data/senamhi/README.md#cómo-descargar-otras-estaciones-u-otros-meses-paso-a-paso).

Los CSV de 5 estaciones de Lima (marzo de 2025) ya vienen en
[`data/senamhi/`](../../data/senamhi/README.md). Se nota enseguida que no
son como los archivos de modelo: un punto y no una grilla, texto separado
por `;`, **hora local de Perú** (UTC−5) y datos faltantes marcados `S/D`.
El notebook de teoría compara ERA5, GFS y FNL contra lo que midió la
estación Campo de Marte a la misma hora.

**4. Diseño de funciones parametrizadas (~20 min)**
Se cierra la teoría del día conectando con el Módulo 1: en vez de escribir
un script distinto por cada descarga, se diseña una función
`descargar_era5(fecha_inicio, fecha_fin, area, variables)` (y su equivalente
para GFS con Herbie) que recibe estos parámetros y construye internamente la
solicitud. Se discute por qué es buena práctica separar "qué se quiere
descargar" (los parámetros) de "cómo se descarga" (el cuerpo de la función),
ya que esto es lo que en el Módulo 6 permitirá reutilizar estas funciones
sin modificarlas dentro de un pipeline mayor.

**Refuerzo — lo que el WRF realmente necesita.** Para aprender bastó con
1 o 2 variables. Pero el WRF necesita una lista fija de variables de cada
fuente: esa lista está en los archivos **Vtable** (`data/Vtable.GFS`,
`Vtable.GDAS`, `Vtable.ERA5`), que son como la lista de ingredientes que el
preprocesador del WRF (WPS) busca en cada archivo. El notebook compara las
tres listas: GFS y FNL piden casi lo mismo (vienen de la misma institución),
mientras que ERA5 nombra y mide algunas cosas distinto (por ejemplo, la
humedad). Esto prepara la función completa del Día 5.

### Práctica (3 h)

1. **Configuración de credenciales (20 min).** Crear el archivo `.cdsapirc`
   en la carpeta personal (`~/.cdsapirc` en Linux/macOS), con la URL del
   API y la clave personal obtenida del perfil de usuario en el portal
   CDS. `herbie-data` y `cdsapi` ya están instalados como parte de
   `wrf2026` (Módulo 1); este paso es solo de configuración de credenciales,
   no de instalación. Verificar que las librerías se importan correctamente
   desde el entorno activo (`import cdsapi`, `import herbie`) antes de
   continuar.
2. **Primera descarga con Herbie (35 min).** Usando Herbie, localizar y
   descargar un archivo GFS para una fecha y ciclo elegidos por el
   participante, con un subconjunto pequeño de variables (p. ej.
   temperatura a 2 m y viento a 10 m). Abrir el resultado con `.xarray()` y
   verificar sus dimensiones y atributos, aplicando lo aprendido en el
   Módulo 2.
3. **Primera descarga con cdsapi (35 min).** Construir una solicitud a CDS
   para un subconjunto pequeño de ERA5 (un día, un área acotada, 2–3
   variables), enviarla y esperar la respuesta. Mientras la solicitud está
   en cola, se discute en grupo qué está ocurriendo del lado del servidor
   (con base en la teoría del punto 3).
4. **Descarga real de FNL por HTTPS directo (25 min).** Correr (o revisar
   línea a línea, si la red del laboratorio bloquea el puerto usado por el
   nodo de datos de GDEX) el script `data/descarga_FNL.csh` con `tcsh
   descarga_FNL.csh AAAAMMDD` para un ciclo de interés, **desde la carpeta
   `data/`** (`cd data` en la raíz del repositorio), que es donde los
   notebooks buscan el archivo, y abrir el
   resultado con `xarray`/`cfgrib` filtrando por `typeOfLevel` (Módulo 2),
   recortando al mismo dominio pequeño usado con Herbie/cdsapi.
   **4b. SENAMHI (15 min).** El docente muestra una descarga con
   `station-hist` en su navegador. Los participantes leen los CSV de
   `data/senamhi/`, pasan la hora de UTC a hora local y comparan lo que
   midió cada estación con el GFS del Ejercicio 2 en ese mismo punto.
5. **Función parametrizada de descarga (35 min).** Escribir la función
   `descargar_era5(fecha_inicio, fecha_fin, area, variables, destino)`
   descrita en teoría, probarla con dos combinaciones distintas de
   parámetros, y confirmar que genera nombres de archivo distintos y
   coherentes con lo solicitado (p. ej. incluyendo la fecha en el nombre).
   **Refuerzo:** el mismo patrón de parametrizar por fecha se aplica al
   script de FNL — `descarga_FNL.csh` ya recibe la fecha como argumento
   (`$1`) en vez de tenerla escrita a mano, exactamente la misma idea que
   `descargar_era5()`, solo que en `csh` en lugar de una función Python.
6. **Cierre y dudas (15 min).**

**Entregable del día:** función `descargar_era5()` (módulo `.py`, no
notebook, para que sea importable en el Día 5) + notebook con las pruebas de
Herbie, cdsapi, FNL y SENAMHI.

---

## Día 5 — Verificación de integridad y preprocesamiento

### Teoría (2 h)

**1. ¿La descarga salió bien? (~30 min)**
Que el programa termine sin error no garantiza que el archivo esté bien: si
se cortó internet, el archivo queda incompleto; si el pedido estaba mal
hecho, el servidor puede devolver un mensaje de error guardado como si
fuera el archivo. Por eso se revisan tres cosas, de la más rápida a la más
lenta:
1. **¿Existe y tiene un tamaño razonable?** Un archivo de pocos KB casi
   seguro es un mensaje de error, no datos.
2. **¿Se puede abrir?** Un archivo cortado a la mitad falla al abrirlo con
   Xarray.
3. **¿Trae lo que pedí?** Si se pidieron 7 días y el archivo trae 3, algo
   falló sin avisar.

Es como revisar un paquete al recibirlo: primero que llegó, después que
abre, y al final que trae todo lo que se pidió.

**2. Por qué normalizar todo a un mismo formato (~25 min)**
GFS llega en GRIB2, ERA5 puede pedirse en GRIB o NetCDF. Si el resto del
pipeline (Módulos 4 y 5) tuviera que manejar ambos formatos de forma
distinta en cada script, la complejidad crecería innecesariamente. La
práctica del módulo es convertir todo a NetCDF apenas se descarga
(`Dataset.to_netcdf()`), de forma que aguas abajo del pipeline exista un
único formato de trabajo. Ojo: es una conveniencia para el análisis en
Python, no un requisito del WRF; WPS (`ungrib.exe`) lee GRIB directamente.

**3. Organización de archivos descargados (~30 min)**
Se discute una convención simple de nombres y carpetas (p. ej.
`datos/entrada/era5/2026-01-15_2026-01-21.nc`) que codifica en la ruta la
fuente y el rango temporal, evitando que un mismo nombre genérico
(`datos.nc`) se sobrescriba entre descargas distintas. Esta convención se
retoma explícitamente en el Módulo 6 al diseñar la estructura de
directorios del pipeline completo.

**4. Encadenar descarga → verificación → conversión (~35 min)**
Se juntan las descargas y las verificaciones en una sola función,
`obtener_entrada_wrf(...)`, que hace los tres pasos en orden y solo da la
descarga por buena si pasa todas las verificaciones. Para eso se usa
`try/except`: "intenta esto, y si falla, en vez de que el programa se caiga
con un mensaje incomprensible, avisa qué falló". A diferencia del Día 4, esta
función **no recibe una lista de variables a elección** — siempre pide el
conjunto completo que exige `Vtable.ERA5` (refuerzo de la teoría del
Día 4), porque un archivo "casi completo" no sirve para correr WRF sin
problemas; la verificación se extiende con un cuarto control,
`verificar_cobertura_vtable()`, que confirma explícitamente que ninguna
variable requerida quedó afuera.

### Práctica (3 h)

1. **Implementar la verificación en capas (40 min).** Escribir una función
   `verificar_integridad(archivo, cobertura_esperada)` que aplique los tres
   controles de la teoría (tamaño, apertura, cobertura) y devuelva un
   reporte claro (`True`/`False` + mensaje) en vez de solo lanzar una
   excepción sin contexto.
2. **Provocar y detectar un fallo real (35 min).** Truncar deliberadamente
   una copia de un archivo descargado el Día 4 (cortando los últimos bytes)
   y confirmar que la función de verificación lo detecta correctamente en
   el paso de "apertura sin error" (Caso A). Repetir el ejercicio simulando
   una cobertura incompleta (Caso B: abrir el archivo real pero pedirle a
   la función que valide contra un rango de fechas mayor al que realmente
   contiene). **Opcional, si sobra tiempo:** los Casos A y B disparan los controles 2 y 3,
   pero no el control 1 (tamaño mínimo) — se agregan un Caso C (archivo
   casi vacío, como si se hubiera guardado por error una respuesta HTTP de
   error) y un Caso D (ruta inexistente), para que **cada uno** de los 3
   controles de la función tenga su propio caso de fallo demostrado.
   **2b. Integridad de un CSV de estaciones (20 min).** Los mismos 3
   controles, adaptados a los CSV de SENAMHI en
   `verificar_csv_senamhi()`: existe y pesa algo; cada fila tiene tantos
   valores como nombres el encabezado (si no, las columnas quedan corridas);
   y están todas las horas del mes. Incluye un caso real de este curso: el
   archivo de Ceres tal como salió de la descarga, con el encabezado
   equivocado. Pandas lo lee sin error, pero la columna «humedad» trae la
   dirección del viento.
3. **Conversión y organización (35 min).** Tomar el archivo GFS (GRIB2)
   descargado el Día 4 con Herbie, convertirlo a NetCDF, y guardarlo
   siguiendo la convención de nombres/carpetas de la teoría. Repetir para
   el archivo de ERA5. **Refuerzo:** volver a llamar
   `verificar_integridad()` (Ejercicio 1) sobre los archivos ya organizados
   — organizar/copiar un archivo no es lo mismo que confirmar que sigue
   íntegro después de la operación. *Opcional:* repetir la conversión GRIB2 → NetCDF
   una tercera vez sobre el archivo FNL del Ejercicio 4 del Día 4 —
   mismo procedimiento que con GFS, para mostrar que la conversión no
   depende de cómo se obtuvo el archivo (Herbie, cdsapi o `wget` directo),
   solo de su formato de origen.
4. **Función integradora `obtener_entrada_wrf()` (35 min).** Escribir
   `descargar_era5_completo()`, que pide en dos solicitudes a `cdsapi`
   (niveles de presión + superficie) **todo** el conjunto de variables que
   exige `Vtable.ERA5` — no una lista arbitraria — y `verificar_cobertura_vtable()`,
   que confirma que las variables esperadas están presentes. Combinar ambas
   con verificación y manejo de errores en `obtener_entrada_wrf()`, y
   ejecutarla de punta a punta para una fecha nueva no usada en los
   ejercicios anteriores — esto último se completa en
   [`04_entregable_integrador.ipynb`](notebooks/04_entregable_integrador.ipynb),
   que además agrega un caso de contraste (forzar un fallo real: un rango
   de fechas invertido) y el checkpoint de cierre del módulo.
5. **Cierre y dudas (15 min).**

**Entregable del módulo:** módulo `.py` con las funciones
`verificar_integridad()`, `verificar_csv_senamhi()`, `verificar_cobertura_vtable()`,
`descargar_era5_completo()` y `obtener_entrada_wrf()`,
documentadas con docstrings breves, más
[`03_practica_dia5_integridad.ipynb`](notebooks/03_practica_dia5_integridad.ipynb)
(pruebas y casos de fallo provocado) y
[`04_entregable_integrador.ipynb`](notebooks/04_entregable_integrador.ipynb)
(ejecución de punta a punta sobre un caso nuevo, caso de contraste y
checkpoint final).

**Extensión opcional (no evaluada):**
[`05_extension_opcional_peru.ipynb`](notebooks/05_extension_opcional_peru.ipynb)
aplica `obtener_entrada_wrf()` a un caso real nuevo — ERA5-Land para el área
de las 7 estaciones reales de Perú (`data/ogimet/coords_peru.json`), mismo
día que ya tiene observación real disponible. Pensada para un curso con
grupos que termine con margen de tiempo el Día 5; el resultado se retoma en
el Módulo 5, Día 9.

---

## Cierre del módulo

**Checkpoint:** el participante debe poder justificar, para un caso de
estudio dado (p. ej. "simular una helada en la sierra sur la próxima
semana" vs. "simular una lluvia intensa ocurrida en marzo de 2023"), qué
fuente de datos de entrada corresponde (GFS/Herbie vs. ERA5/cdsapi) y por
qué.

<details>
<summary><strong>Respuesta esperada</strong> (ábrela después de intentarlo)</summary>

- **Helada en la sierra sur la próxima semana → GFS (Herbie).** El evento
  todavía no ocurre: no hay reanálisis para fechas futuras, así que la única
  fuente posible es un pronóstico operativo. Se toma el ciclo más reciente y
  los `fxx` que cubren el periodo a simular.
- **Lluvia intensa de marzo de 2023 → ERA5 (cdsapi).** El evento ya ocurrió.
  ERA5 incorporó las observaciones de esos días y es consistente en el
  tiempo, así que da las mejores condiciones iniciales y de frontera para
  reproducirlo. GFS archivado solo tendría sentido si el objetivo fuera
  evaluar qué tan bueno fue el pronóstico de ese momento. FNL es una
  alternativa válida si se prefiere un análisis de NCEP.
</details>

## Preguntas frecuentes

**Pedí una solicitud a `cdsapi` y no pasa nada por varios minutos. ¿Está
mal mi código?**
Probablemente no. Como se explica en la teoría (Sección 3), el CDS procesa
solicitudes por cola: el tiempo de espera depende de cuánta gente está
pidiendo datos al mismo tiempo, no del tamaño de la solicitud en sí. Es
normal que la misma solicitud tarde 10 segundos un día y 5 minutos otro
día. Si pasan más de 15–20 minutos sin respuesta ni error, ahí sí conviene
revisar la solicitud (fechas válidas, nombres de variable correctos).

**¿En qué orden va `area` en una solicitud a `cdsapi`?**
`[norte, oeste, sur, este]` — en ese orden exacto, no alfabético ni por
sentido de lectura de mapa. Invertir el orden (p. ej. poner `sur` antes que
`norte`) es un error común que no siempre lanza una excepción: puede
devolver una solicitud vacía o un área distinta a la esperada. Conviene
verificar el área descargada (Módulo 2, inspección de `latitude`/`longitude`)
antes de asumir que la solicitud fue correcta.

**¿Herbie sirve para descargar ERA5, o solo modelos como GFS/ECMWF
operativo?**
Herbie está pensado para modelos de pronóstico distribuidos por ciclos
(GFS, ECMWF operativo, HRRR, etc.), no para el catálogo de reanálisis de
Copernicus. Para ERA5 se usa `cdsapi`. Ambas herramientas conviven en el
mismo pipeline porque resuelven necesidades distintas: una fuente
operativa por ciclos, otra un catálogo de reanálisis por fecha.

**¿Qué hago si `verificar_integridad()` dice que el archivo falló, pero yo
"sé" que la descarga terminó bien?**
Confiar en la función, no en la impresión visual. Un archivo puede
"terminar de descargarse" (el proceso no arroja error) y aun así estar
incompleto si, por ejemplo, se cortó la conexión a mitad de una respuesta
larga del servidor. Es exactamente el escenario que motivó el diseño de
verificación en capas de la Sección 1: el objetivo es no depender de "se
ve bien" como criterio.

**¿Por qué no verificar con un checksum (hash) del archivo, como se hace
en otros contextos de descarga de software?**
Porque ni el CDS ni los repositorios de GFS exponen de forma simple y
consistente un checksum de referencia para comparar (a diferencia de, por
ejemplo, un instalador de software firmado). Los tres controles de la
Sección 1 (tamaño, apertura, cobertura) son una alternativa práctica que sí
es aplicable con la información realmente disponible.

## Para profundizar

Material opcional: no hace falta para la práctica ni para el proyecto final.

### Combinar varios `fxx`

Para forzar al WRF con el pronóstico más preciso posible en cada instante,
normalmente se combinan varios `fxx` de un mismo ciclo (o de ciclos
sucesivos), no un solo valor fijo. Este detalle aparece al automatizar la
descarga por rango de fechas.

### FNL: patrón de URL y cuándo conviene

Herbie y `cdsapi` son abstracciones en Python sobre un repositorio remoto:
la librería arma la solicitud, sigue el protocolo de la fuente y entrega un
`Dataset`. FNL se descarga distinto, y esa diferencia es en sí misma el
punto a enseñar: GDEX (NCAR) distribuye los archivos `d083003` como
archivos planos por HTTPS directo, sin autenticación ni cliente Python
dedicado — la URL sigue un patrón predecible,
`.../d083003/{año}/{año}{mes}/gdas1.fnl0p25.{fecha}{hora}.f{paso}.grib2`, y
un script de `wget` (`tcsh`/`csh`, el shell en el que GDEX distribuye su
script de ejemplo) itera esa lista de URLs, una por cada paso de pronóstico
(`f00`, `f03`, `f06`, `f09`...) del mismo ciclo. Esto no es menos
"automatizado" que Herbie o `cdsapi`: automatizar una descarga no siempre
significa que exista un paquete de Python para ello, a veces significa
escribir el script (o llamarlo con `subprocess`) que arma las URLs por
fecha. FNL funciona como alternativa a GFS cuando se quiere un análisis ya
reprocesado por NCEP en vez del pronóstico operativo puro, o como
alternativa a ERA5 para fechas muy recientes en las que el reanálisis aún
no está disponible.

## Recursos sugeridos

- Documentación oficial de Herbie — *Getting started*.
- Documentación oficial de `cdsapi` — *How to use the CDS API*.
- Portal del Copernicus Climate Data Store (registro de cuenta, catálogo de
  ERA5).
- [GDEX (NCAR)](https://gdex.ucar.edu/datasets/d083003/dataaccess/) —
  acceso al dataset FNL (`d083003`); no requiere cuenta para la descarga
  directa por HTTPS usada en este módulo.
- `data/Vtable.GFS`, `Vtable.GDAS`, `Vtable.ERA5` — los Vtable reales
  usados en el refuerzo de la teoría del Día 4 y en la función
  integradora del Día 5; documentan exactamente qué campos necesita
  `ungrib.exe` (WPS) de cada fuente.

## Siguiente módulo

[Módulo 4 — Lectura y visualización de salidas WRF](../modulo_04_lectura_visualizacion_wrf/README.md):
los datos que aquí se descargan y normalizan son, conceptualmente, la otra
punta del ciclo de modelado — lo que entra al WRF. El módulo 4 trabaja con
lo que el WRF produce a partir de estos datos.
