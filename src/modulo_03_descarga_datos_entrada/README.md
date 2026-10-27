# Módulo 3 — Descarga automatizada de datos de entrada para el WRF

[Índice del curso](../README.md)

**Ubicación en el curso:** Días 4–5 de 10 · **Carga horaria:** 10 h (2 h teoría + 3 h práctica por día)
**Precede a:** [Módulo 4 — Lectura y visualización de salidas WRF](../modulo_04_lectura_visualizacion_wrf/README.md)
**Requiere:** [Módulo 2 — Formatos de datos atmosféricos](../modulo_02_formatos_datos_atmosfericos/README.md)

## Objetivo del módulo

Al terminar el módulo, el participante podrá descargar con funciones de
Python los datos globales (ERA5, GFS y FNL) que el WRF usa como condición
inicial y de frontera, revisar que lo descargado esté completo y dejarlo
todo en NetCDF para los módulos siguientes.

## Relación con el WRF

El WRF simula el tiempo en una región (por ejemplo, el Perú). Para
arrancar necesita dos cosas que vienen de un modelo global:

- **Condición inicial:** cómo está la atmósfera en toda la región en el
  momento en que empieza la simulación.
- **Condiciones de frontera:** qué entra por los bordes de la región
  mientras la simulación avanza (el aire que llega del Pacífico, de la
  Amazonía, etc.).

Bajar esos datos a mano desde un portal sirve una vez, pero no para 30
fechas ni para repetir el trabajo cuando cambia el caso. Por eso aquí
escribimos la descarga como funciones.

## Prerrequisitos específicos

Haber completado el Módulo 2 (apertura de NetCDF/GRIB con Xarray/`cfgrib`,
que se usa para revisar las descargas el Día 5). Además, hace falta una
cuenta activa en el Copernicus Climate Data Store (CDS), con las licencias
de ERA5 aceptadas, creada **antes de esta clase**, porque la activación
puede tardar (sección 6 de
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
Usamos tres fuentes de modelo y una de observaciones:
- **ERA5 (Copernicus) es un reanálisis:** una reconstrucción del tiempo que
  **ya pasó**, que combina un modelo con millones de observaciones
  (estaciones, satélites, radiosondeos). Usa el mismo método para todo el
  registro desde 1940, así que sirve para estudiar el clima o para
  reproducir un evento pasado.
- **GFS (NOAA, EE. UU.) es un pronóstico:** un modelo que se corre cuatro
  veces al día (00, 06, 12 y 18 UTC) y calcula cómo estará la atmósfera en
  las horas siguientes. Cada hora hacia adelante se llama paso de
  pronóstico (`fxx`). Es la fuente para simular algo que **todavía no
  pasó**.
- **FNL** es el análisis final de NCEP: el estado inicial que estima el
  sistema de GFS, procesado otra vez unas horas después con más
  observaciones. Lo distribuye NCAR. Sirve para casos recientes que ERA5
  todavía no cubre, y se descarga sin cuenta (sección 3b).
- **SENAMHI** son **mediciones** de estaciones del Perú. No entran al WRF;
  las usamos para comparar con lo simulado (sección 3c).

Antes de ver cómo se descarga cada una, la pregunta es cuál sirve para cada
caso. Para reproducir un evento que **ya ocurrió**, ERA5 suele ser la mejor
opción, porque usa las observaciones de esos días. GFS sirve cuando el
evento todavía no ocurre, o cuando se quiere evaluar un pronóstico.

**2. Herbie: GFS sin buscar direcciones (~25 min)**
Los archivos de GFS están copiados en varios servidores (de NOAA, de
Amazon, de Google) y cada uno guarda distinta cantidad de días. Con Herbie
se indica modelo, fecha, hora de corrida y paso de pronóstico, y la
librería busca dónde está el archivo. Son tres pasos:
`Herbie(fecha, model="gfs", fxx=...)` → `.download()` (baja el archivo) →
`.xarray()` (lo abre como un `Dataset`, igual que en el Módulo 2).

`fxx=0` es el estado de la atmósfera en la hora de inicio de la corrida
(el análisis). `fxx=6` es lo que el modelo calcula para 6 horas
después.

**3. cdsapi: la cola del CDS (~25 min)**
`cdsapi` envía el pedido (variable, fechas, área), el servidor de
Copernicus lo pone en cola y, cuando le toca, prepara el archivo y lo
entrega. Puede tardar segundos o varios minutos, según cuánta gente esté
pidiendo datos. Esperar es normal, y un script puede esperar sin que
estemos mirando.

Se ve cómo guardar la clave personal (archivo `.cdsapirc`) y cómo se arma
un pedido: un diccionario con `variable`, `year`, `month`, `day`, `time`,
`area` y `format`. Ojo con `area`: va en el orden
`[norte, oeste, sur, este]`.

**3b. FNL: descarga por HTTPS, sin librería (~15 min)**
GDEX (NCAR) publica los archivos FNL (`d083003`) con una dirección que se
arma a partir de la fecha y el paso de pronóstico, sin cuenta ni librería
de Python. Los descargamos con un script de `wget` que arma esas
direcciones (`data/descarga_FNL.csh`). No toda descarga tiene una librería
de Python; a veces basta con un script.
Detalle del patrón de URL y de cuándo conviene FNL, en
[Para profundizar](#para-profundizar).

**3c. SENAMHI: estaciones, con una persona en el medio (~15 min)**
El portal «Mapa de estaciones» de SENAMHI entrega CSV con datos hora por
hora de cada estación, pero pide pasar una verificación «no soy un robot»
(Cloudflare) en cada descarga, así que una persona tiene que estar ahí. El
docente lo muestra con [`station-hist`](https://github.com/Japq91/station-hist):
la herramienta abre el navegador, la persona pasa la verificación y el
script hace el resto (bajar, unir y guardar el CSV). Lo que el sitio pide
hacer a mano, lo hacemos a mano.

Guion de la demostración (en vivo, ~5 min): buscar la estación por nombre
(`--search`), elegir la versión **automática** (hay dos con el mismo
nombre), descargar un año, mostrar el CSV que sale y recortar el mes. El
paso a paso completo, para quien quiera bajar otras estaciones, está en
[`data/senamhi/README.md`](../../data/senamhi/README.md#cómo-descargar-otras-estaciones-u-otros-meses-paso-a-paso).

Los CSV de 5 estaciones de Lima (marzo de 2025) ya vienen en
[`data/senamhi/`](../../data/senamhi/README.md). Son muy distintos de los
archivos de modelo: un punto y no una grilla, texto separado
por `;`, **hora local de Perú** (UTC−5) y datos faltantes marcados `S/D`.
El notebook de teoría compara ERA5, GFS y FNL contra lo que midió la
estación Campo de Marte a la misma hora.

**4. Diseño de funciones parametrizadas (~20 min)**
En vez de un script distinto para cada descarga, escribimos una función
`descargar_era5(fecha_inicio, fecha_fin, area, variables)` (y otra para GFS
con Herbie) que recibe esos parámetros y arma la solicitud. Lo que cambia
de un caso a otro entra como argumento; cómo se descarga queda dentro de la
función. Así, en el Módulo 6 usamos estas mismas funciones en el pipeline
sin tocarlas.

**Lo que necesita el WRF.** Para aprender alcanzó con 1 o 2 variables,
pero el WRF necesita una lista fija de variables de cada fuente. Esa lista
está en los archivos **Vtable** (`data/Vtable.GFS`, `Vtable.GDAS`,
`Vtable.ERA5`): es lo que el WPS busca en cada archivo. El notebook compara las
tres listas: GFS y FNL piden casi lo mismo (vienen de la misma institución),
mientras que ERA5 nombra y mide algunas cosas distinto (por ejemplo, la
humedad). Esto prepara la función completa del Día 5.

### Práctica (3 h)

1. **Configuración de credenciales (20 min).** Crear el archivo `.cdsapirc`
   en la carpeta personal (`~/.cdsapirc` en Linux/macOS), con la URL del
   API y la clave personal obtenida del perfil de usuario en el portal
   CDS. `herbie-data` y `cdsapi` ya están instalados en `wrf2026`; solo
   falta la clave. Comprobar que `import cdsapi` e `import herbie`
   funcionan antes de seguir.
2. **Primera descarga con Herbie (35 min).** Usando Herbie, localizar y
   descargar un archivo GFS para una fecha y ciclo elegidos por el
   participante, con un subconjunto pequeño de variables (p. ej.
   temperatura a 2 m y viento a 10 m). Abrir el resultado con `.xarray()` y
   verificar sus dimensiones y atributos, aplicando lo aprendido en el
   Módulo 2.
3. **Primera descarga con cdsapi (35 min).** Construir una solicitud a CDS
   para un subconjunto pequeño de ERA5 (un día, un área acotada, 2–3
   variables), enviarla y esperar la respuesta. Mientras la solicitud está
   en cola, conversamos qué está pasando del lado del servidor (punto 3 de
   la teoría).
4. **Descarga de FNL por HTTPS (25 min).** Correr (o revisar
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
   El script de FNL hace lo mismo: `descarga_FNL.csh` recibe la fecha como
   argumento (`$1`) en vez de tenerla escrita dentro, como
   `descargar_era5()`, pero en `csh`.
6. **Cierre y dudas (15 min).**

**Entregable del día:** función `descargar_era5()` (módulo `.py`, no
notebook, para que sea importable en el Día 5) + notebook con las pruebas de
Herbie, cdsapi, FNL y SENAMHI.

---

## Día 5 — Verificación de integridad y preprocesamiento

### Teoría (2 h)

**1. ¿La descarga salió bien? (~30 min)**
Que el programa termine sin error no quiere decir que el archivo esté
bien. Si se cortó internet, el archivo queda incompleto; si el pedido
estaba mal hecho, el servidor puede devolver un mensaje de error guardado
como si fuera el archivo. Revisamos tres cosas, de la más rápida a la más
lenta:
1. **¿Existe y tiene un tamaño razonable?** Un archivo de pocos KB
   probablemente es un mensaje de error.
2. **¿Se puede abrir?** Un archivo cortado a la mitad falla al abrirlo con
   Xarray.
3. **¿Trae lo que pedí?** Si se pidieron 7 días y el archivo trae 3, algo
   falló sin avisar.

**2. Por qué normalizar todo a un mismo formato (~25 min)**
GFS llega en GRIB2; ERA5 puede pedirse en GRIB o NetCDF. Para no escribir
cada script dos veces, convertimos todo a NetCDF apenas se descarga
(`Dataset.to_netcdf()`). Es una decisión para trabajar más cómodos en
Python: el WRF no lo pide, porque el WPS (`ungrib.exe`) lee GRIB.

**3. Organización de archivos descargados (~30 min)**
Una forma simple de nombrar carpetas y archivos, por ejemplo
`datos/entrada/era5/2026-01-15_2026-01-21.nc`, con la fuente y las fechas
en la ruta. Así una descarga no reemplaza a otra que tenía el mismo nombre
(`datos.nc`). En el Módulo 6 usamos la misma estructura.

**4. Encadenar descarga → verificación → conversión (~35 min)**
Se juntan las descargas y las verificaciones en una sola función,
`obtener_entrada_wrf(...)`, que hace los tres pasos en orden y solo da la
descarga por buena si pasa todas las verificaciones. Para eso se usa
`try/except`: «intenta esto y, si falla, avisa qué pasó» en vez de
detenerse con un mensaje difícil de entender. A diferencia del Día 4, esta
función **no recibe una lista de variables**: siempre pide todas las que
exige `Vtable.ERA5`, porque al WRF no le sirve un archivo al que le falta
una. Por eso se agrega un cuarto control, `verificar_cobertura_vtable()`,
que revisa que estén todas.

### Práctica (3 h)

1. **Implementar la verificación en capas (40 min).** Escribir una función
   `verificar_integridad(archivo, cobertura_esperada)` que aplique los tres
   controles (tamaño, apertura, cobertura) y devuelva `True`/`False` con un
   mensaje que diga qué falló.
2. **Provocar una falla y detectarla (35 min).** Truncar a propósito
   una copia de un archivo descargado el Día 4 (cortando los últimos bytes)
   y comprobar que la función lo detecta en el control de apertura
   (Caso A). Repetir el ejercicio simulando
   una cobertura incompleta (Caso B: abrir el archivo real pero pedirle a
   la función que valide contra un rango de fechas mayor al que realmente
   contiene). **Opcional:** los Casos A y B prueban los controles 2 y 3. El
   Caso C (un archivo casi vacío, como una respuesta de error del servidor)
   y el Caso D (una ruta que no existe) prueban el control 1.
   **2b. Integridad de un CSV de estaciones (20 min).** Los mismos 3
   controles, adaptados a los CSV de SENAMHI en
   `verificar_csv_senamhi()`: existe y pesa algo; cada fila tiene tantos
   valores como nombres el encabezado (si no, las columnas quedan corridas);
   y están todas las horas del mes. Incluye algo que nos pasó preparando el
   curso: el archivo de Ceres tal como salió de la descarga, con el
   encabezado equivocado. Pandas lo lee sin error, pero la columna
   «humedad» trae la dirección del viento.
3. **Conversión y organización (35 min).** Tomar el archivo GFS (GRIB2)
   descargado el Día 4 con Herbie, convertirlo a NetCDF, y guardarlo
   siguiendo la convención de nombres/carpetas de la teoría. Repetir para
   el archivo de ERA5, y volver a pasar `verificar_integridad()` por los
   archivos ya organizados: copiar un archivo no asegura que siga bien.
   *Opcional:* lo mismo con el FNL del Ejercicio 4 del Día 4. La conversión
   es igual sin importar cómo se descargó el archivo.
4. **Función integradora `obtener_entrada_wrf()` (35 min).** Escribir
   `descargar_era5_completo()`, que pide en dos solicitudes a `cdsapi`
   (niveles de presión + superficie) **todo** el conjunto de variables que
   exige `Vtable.ERA5`, y `verificar_cobertura_vtable()`, que revisa que
   estén todas. Juntar ambas, con la verificación y el manejo de errores,
   en `obtener_entrada_wrf()`, y correrla para una fecha nueva en
   [`04_entregable_integrador.ipynb`](notebooks/04_entregable_integrador.ipynb).
   Ese notebook incluye además un caso de contraste (fechas invertidas) y
   la pregunta de cierre del módulo.
5. **Cierre y dudas (15 min).**

**Entregable del módulo:** módulo `.py` con las funciones
`verificar_integridad()`, `verificar_csv_senamhi()`, `verificar_cobertura_vtable()`,
`descargar_era5_completo()` y `obtener_entrada_wrf()`,
documentadas con docstrings breves, más
[`03_practica_dia5_integridad.ipynb`](notebooks/03_practica_dia5_integridad.ipynb)
(pruebas y casos de fallo provocado) y
[`04_entregable_integrador.ipynb`](notebooks/04_entregable_integrador.ipynb)
(ejecución completa sobre un caso nuevo, caso de contraste y pregunta de
cierre).

**Extensión opcional (no evaluada):**
[`05_extension_opcional_peru.ipynb`](notebooks/05_extension_opcional_peru.ipynb)
usa `obtener_entrada_wrf()` para bajar ERA5-Land sobre el área de las 7
estaciones de Perú (`data/ogimet/coords_peru.json`), el mismo día del que
tenemos observaciones. Es para quien termine antes el Día 5; el resultado
se usa en el Módulo 5, Día 9.

---

## Cierre del módulo

**Pregunta de cierre:** para cada caso, ¿qué fuente de entrada usarían
(GFS con Herbie o ERA5 con cdsapi) y por qué? (a) Simular una helada en la
sierra sur la próxima semana. (b) Simular una lluvia intensa de marzo de
2023.

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
  evaluar qué tan bueno fue el pronóstico de ese momento. FNL también
  sirve, sobre todo si el evento es tan reciente que ERA5 todavía no lo
  cubre.
</details>

## Preguntas frecuentes

**Pedí una solicitud a `cdsapi` y no pasa nada por varios minutos. ¿Está
mal mi código?**
Probablemente no. El CDS atiende las solicitudes por cola (sección 3 de la
teoría): la espera depende sobre todo de cuánta gente esté pidiendo datos,
y algo del tamaño del pedido. La misma solicitud puede tardar 10 segundos
un día y 5 minutos otro. Si pasan más de 15–20 minutos sin respuesta ni error, ahí sí conviene
revisar la solicitud (fechas válidas, nombres de variable correctos).

**¿En qué orden va `area` en una solicitud a `cdsapi`?**
`[norte, oeste, sur, este]`. Si se cambia el orden (por ejemplo, `sur`
antes que `norte`), no siempre hay error: puede llegar un archivo vacío o
de otra área. Revisen `latitude` y `longitude` del archivo descargado
(Módulo 2).

**¿Herbie sirve para descargar ERA5, o solo modelos como GFS/ECMWF
operativo?**
Herbie está pensado para modelos de pronóstico distribuidos por ciclos
(GFS, ECMWF operativo, HRRR, etc.), no para el catálogo de reanálisis de
Copernicus. Para ERA5 se usa `cdsapi`. Por eso el pipeline usa las dos.

**¿Qué hago si `verificar_integridad()` dice que el archivo falló, pero la
descarga terminó sin error?**
Hagan caso a la función. Una descarga puede terminar sin error y dejar un
archivo incompleto, por ejemplo si se cortó la conexión a mitad de la
respuesta. Para eso están los controles de la sección 1. Si creen que la
función se equivoca, revisen el mensaje: dice qué control falló.

**¿Por qué no verificar con un checksum (hash) del archivo, como se hace
en otros contextos de descarga de software?**
Porque ni el CDS ni los servidores de GFS publican un checksum fácil de
usar con el cual comparar, como sí lo hace un instalador de software. Los
tres controles de la sección 1 (tamaño, apertura, cobertura) funcionan con
lo que sí tenemos.

## Para profundizar

Material opcional: no hace falta para la práctica ni para el proyecto final.

### Combinar varios `fxx`

Para forzar al WRF con el pronóstico más preciso posible en cada instante,
normalmente se combinan varios `fxx` de un mismo ciclo (o de ciclos
sucesivos), no un solo valor fijo. Este detalle aparece al automatizar la
descarga por rango de fechas.

### FNL: patrón de URL y cuándo conviene

Con Herbie y `cdsapi`, la librería arma la solicitud y entrega un
`Dataset`. FNL es distinto: GDEX (NCAR) publica los archivos `d083003` por
HTTPS, sin cuenta ni librería, en direcciones que siguen el patrón
`.../d083003/{año}/{año}{mes}/gdas1.fnl0p25.{fecha}{hora}.f{paso}.grib2`.
El script de `wget` (en `tcsh`, el shell del ejemplo que distribuye GDEX)
recorre esa lista, una dirección por cada paso (`f00`, `f03`, `f06`,
`f09`...) del mismo ciclo. Desde Python se puede llamar con `subprocess`.

FNL sirve en lugar de GFS cuando se quiere un análisis procesado otra vez
por NCEP y no el pronóstico, y en lugar de ERA5 para fechas tan recientes
que el reanálisis todavía no está publicado.

## Recursos sugeridos

- Documentación de Herbie: *Getting started*.
- Documentación de `cdsapi`: *How to use the CDS API*.
- Portal del Copernicus Climate Data Store (registro de cuenta, catálogo de
  ERA5).
- [GDEX (NCAR)](https://gdex.ucar.edu/datasets/d083003/dataaccess/):
  acceso al dataset FNL (`d083003`), sin cuenta.
- `data/Vtable.GFS`, `Vtable.GDAS`, `Vtable.ERA5`: las tablas que usa
  `ungrib.exe` (WPS) para saber qué campos tomar de cada fuente.

## Siguiente módulo

[Módulo 4 — Lectura y visualización de salidas WRF](../modulo_04_lectura_visualizacion_wrf/README.md):
aquí trabajamos con lo que entra al WRF; en el Módulo 4, con lo que sale.
