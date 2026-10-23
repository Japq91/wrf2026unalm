# Módulo 2 — Formatos de datos atmosféricos

[Índice del curso](../README.md)

**Ubicación en el curso:** Día 3 de 10 · **Carga horaria:** 5 h (2 h teoría + 3 h práctica)
**Precede a:** [Módulo 3 — Descarga de datos de entrada](../modulo_03_descarga_datos_entrada/README.md)
**Requiere:** [Módulo 1 — Python básico](../modulo_01_python_basico/README.md) (estructura `Dataset`/`DataArray` de Xarray)

## Objetivo del módulo

Al finalizar el módulo, el participante podrá abrir, inspeccionar, recortar e
interpolar archivos NetCDF y GRIB/GRIB2 reales usando Xarray, entendiendo qué
información contienen los metadatos y por qué esa información es la que hace
posible automatizar el resto del pipeline sin tener que "adivinar" qué
representa cada variable.

## Por qué este módulo importa para el WRF

El WRF consume datos de entrada casi siempre en GRIB2 (salidas de GFS/ECMWF) o
NetCDF (ERA5, tras conversión), y produce sus propias salidas (`wrfout`) en
NetCDF. Todo el resto del curso —descarga (Módulo 3), lectura de `wrfout`
(Módulo 4), validación (Módulo 5)— asume que el participante puede abrir
cualquiera de estos formatos y saber qué está viendo. Este módulo es, en ese
sentido, una bisagra: conecta la estructura genérica `Dataset` del Módulo 1
con los archivos reales del dominio atmosférico.

## Prerrequisitos específicos

Haber completado el Módulo 1, en particular entender la diferencia entre
`.sel()` (por nombre/coordenada) y `.isel()` (por posición) en Xarray.

## Antes de empezar: activar el entorno

En cada terminal nueva, activa el entorno **antes** de abrir Jupyter:
```bash
conda activate wrf2026
jupyter lab
```
Si la terminal no muestra `(wrf2026)` al inicio de la línea, los `import`
de `xarray` o `cfgrib` van a fallar aunque estén instalados.

---

## Día 3 — NetCDF, GRIB y operaciones espaciales básicas

### Teoría (2 h)

**1. NetCDF: un archivo que trae su propia etiqueta (~40 min)**
Un NetCDF no guarda solo números: junto a cada variable guarda qué es, en
qué unidades está y en qué ejes se ordena. Es como una planilla que trae su
propio manual. Tiene tres partes:
- **Dimensiones**: los ejes y cuántos datos hay en cada uno (`time: 744`,
  `latitude: 121`, `longitude: 240`).
- **Variables**: los datos. Algunas son **coordenadas**, que dicen dónde y
  cuándo está cada dato (la variable `latitude` da la latitud real de cada
  fila); otras son los datos en sí (`t2m`, temperatura a 2 m).
- **Atributos**: las etiquetas. Por variable (`units`, `long_name`) o del
  archivo completo (quién lo hizo, cómo se procesó).

La **convención CF** es un acuerdo internacional sobre cómo escribir esas
etiquetas: por ejemplo, que la temperatura del aire se identifique como
`air_temperature` en kelvin, y no con un nombre libre como `"temp"`.
Gracias a ese acuerdo, programas como Xarray o `xwrf` (Módulo 4) entienden
el archivo sin que haya que explicárselo.

**2. Apertura "perezosa" con Xarray (~20 min)**
`xr.open_dataset(archivo)` no lee todos los números de una vez. Primero lee
solo el índice (qué variables hay, sus ejes y etiquetas), como quien hojea
el índice de un libro sin leer todas las páginas. Los números se leen
recién cuando hacen falta: al graficar, al promediar o al guardar. Así se
puede abrir al instante un `wrfout` de varios GB y quedarse solo con la
parte que interesa.

En la demo se ve el momento exacto en que ocurre la lectura (detalle en
[Para profundizar](#para-profundizar)).

**3. GRIB/GRIB2: un formato orientado a mensajes (~30 min)**
Un NetCDF es un solo bloque ordenado. Un GRIB, en cambio, es como una
**pila de fichas**: cada ficha (un "mensaje") es un solo mapa, de una sola
variable, en un solo nivel y una sola hora, guardado de forma muy
comprimida. Por eso los centros de pronóstico lo usan para distribuir sus
datos: los archivos son pequeños y viajan rápido. Las fichas no traen el
nombre de la variable sino un código numérico; `cfgrib` lo traduce y arma
un `Dataset` de Xarray, igual al de un NetCDF (cómo, en
[Para profundizar](#para-profundizar)). Si en la pila hay fichas de tipos
muy distintos (superficie y niveles de presión, por ejemplo), `cfgrib` pide
separarlas con `filter_by_keys`.

**4. Selección, recorte e interpolación espacial (~30 min)**
- **El punto más cercano** (`.sel(..., method="nearest")`): para cuando el
  lugar buscado (una estación, por ejemplo) no cae justo en un punto de la
  grilla.
- **Recortar una región** (`.sel(latitude=slice(a, b))`): ERA5 guarda las
  latitudes de norte a sur (de 90° a -90°). Si se pide `slice(sur, norte)`,
  el resultado sale **vacío y sin ningún error**. Por eso se mira primero
  el orden de la latitud y después se recorta.
- **Interpolar** (`.interp(..., method="linear")`): en vez de copiar el
  valor del punto más cercano, calcula uno nuevo mezclando los cuatro
  puntos de grilla que rodean al lugar. Cada uno pesa más cuanto más cerca
  está: si una estación está casi encima de un punto de grilla, el
  resultado se parece mucho a ese punto. Se llama interpolación
  **bilineal** (la fórmula, en [Para profundizar](#para-profundizar)). En
  el Módulo 5 se usa para llevar el WRF a la ubicación exacta de cada
  estación.

### Práctica (3 h)

1. **Inspección de un NetCDF real (40 min).** Abrir con
   `xr.open_dataset()` un archivo de muestra de ERA5 (recortado, incluido en
   los datasets del curso). Listar dimensiones, coordenadas, variables y
   atributos globales. Responder por escrito, en el notebook: ¿en qué
   unidades está la temperatura?, ¿la latitud es ascendente o descendente?,
   ¿qué convención declara el atributo global `Conventions`? **Refuerzo:**
   repetir las mismas preguntas sobre otra variable del mismo archivo
   (`msl`, presión a nivel del mar) — para confirmar que la lógica de
   inspección se generalizó, no que se memorizaron las respuestas de la
   primera variable — y de paso notar que ERA5 da la presión en pascales
   (Pa), no en hectopascales (hPa), la unidad habitual en un mapa
   sinóptico: hay que dividir entre 100 antes de comparar con lo que se
   está acostumbrado a leer.
2. **Apertura de un GRIB2 con cfgrib (35 min).** Abrir un archivo GRIB2 de
   muestra (p. ej. un extracto de GFS) con
   `xr.open_dataset(archivo, engine="cfgrib")` y comparar su estructura
   resultante contra el `Dataset` de ERA5 abierto en NetCDF. En este
   ejercicio, `cfgrib` decodifica el mensaje GRIB2 (`shortName="2t"`) al
   mismo nombre `t2m` que ya tenía el NetCDF — el participante verifica
   esto con código, no de memoria, y a partir de ahí se discute el caso
   general: **no siempre coinciden**, otras fuentes/centros meteorológicos
   sí pueden usar un nombre corto distinto para la misma variable física, y
   por eso conviene verificar `long_name`/`standard_name` en vez de asumir
   el nombre — problema que se retoma formalmente en el Módulo 3, al
   automatizar la descarga de varias fuentes.
3. **Recorte de dominio y periodo (40 min).** A partir del `Dataset` de
   ERA5, recortar el dominio a una región de interés (p. ej. la costa
   central del Perú) y a un rango de fechas de una semana, verificando
   primero el orden de la coordenada de latitud antes de escribir el
   `slice`. Guardar el subconjunto recortado como un nuevo NetCDF con
   `.to_netcdf()`.
4. **Interpolación a un punto (45 min).** Elegir una coordenada
   (lat, lon) que no coincida exactamente con ningún nodo de la grilla del
   dataset recortado. Extraer la serie temporal de temperatura en ese punto
   con `.sel(method="nearest")` y con `.interp(method="linear")`, graficar
   ambas series superpuestas con Matplotlib, y comprobar que el valor
   interpolado queda entre los valores de los cuatro puntos vecinos.
   *Opcional:* calcularlo a mano con la
   [fórmula bilineal](#interpolación-bilineal-la-fórmula) y ver que coincide
   con `.interp`.
5. **Cierre y dudas (20 min).**

**Entregable del día:** los tres notebooks de práctica —
[`02_practica_inspeccion_netcdf_grib.ipynb`](notebooks/02_practica_inspeccion_netcdf_grib.ipynb)
(Ejercicios 1–2),
[`03_practica_recorte_dominio.ipynb`](notebooks/03_practica_recorte_dominio.ipynb)
(Ejercicio 3) y
[`04_entregable_interpolacion.ipynb`](notebooks/04_entregable_interpolacion.ipynb)
(Ejercicio 4) — con las cuatro secciones resueltas, más el archivo NetCDF
recortado generado en el Ejercicio 3.

---

## Cierre del módulo

**Checkpoint:** el participante debe poder explicar por qué `.sel(method="nearest")`
y `.interp(method="linear")` dan resultados distintos, y en qué situación
usaría cada uno (p. ej. nearest para elegir el nivel vertical más cercano
frente a interpolar entre dos niveles con significado físico continuo).

<details>
<summary><strong>Respuesta esperada</strong> (ábrela después de intentarlo)</summary>

`nearest` no calcula nada: devuelve el valor de un nodo existente de la
grilla, el más cercano. `interp` calcula un valor nuevo, ponderando los
nodos vecinos según su distancia al punto, así que cambia de forma suave a
medida que el punto se mueve entre nodos.

- **`nearest`**: cuando se necesita un dato que realmente existe en el
  archivo (elegir un nivel de presión, una fecha, una celda), o cuando la
  variable no es continua (una máscara tierra/mar o una categoría de uso del
  suelo, donde promediar no tiene sentido).
- **`interp`**: cuando la variable cambia de forma continua en el espacio
  (temperatura, presión) y se quiere el valor en un punto que cae entre
  nodos, como la ubicación de una estación (Módulo 5).
</details>

## Preguntas frecuentes

**¿Voy a recibir mis datos en NetCDF o en GRIB? ¿Yo elijo?**
Depende de la fuente. ERA5 vía `cdsapi` (Módulo 3) permite pedir el
formato de salida (NetCDF o GRIB). GFS vía Herbie llega nativamente en
GRIB2, porque así es como NOAA lo publica; si se prefiere trabajar todo en
NetCDF, hay que convertirlo después de descargarlo (se automatiza en el
Módulo 3). Ninguno de los dos formatos es "mejor" de forma absoluta: GRIB
es más compacto para difusión operativa, NetCDF es más simple de inspeccionar
y es el formato nativo de las salidas del WRF (Módulo 4).

**Si genero mis propios archivos NetCDF (por ejemplo, guardando un
resultado con `.to_netcdf()`), ¿tengo que seguir la convención CF?**
No es obligatorio para que el archivo funcione —Xarray puede leer
cualquier NetCDF válido—, pero sí es una buena práctica hacerlo, porque es
lo que permite que **otra persona** (o el propio participante, meses
después) entienda las variables sin tener que preguntar. Basta con
completar `units`, `long_name` y, cuando exista, `standard_name` en los
atributos de cada variable al crearla.

**¿Qué pasa si intento recortar con `.sel(latitude=slice(...))` y el
resultado sale vacío, pero no hay ningún error?**
Esto es precisamente el problema de la Sección 4 (orden descendente de la
latitud). Xarray no lanza un error porque, técnicamente, `slice(a, b)` con
`a > b` sobre una coordenada descendente es una operación válida que
simplemente no encuentra ningún punto dentro del rango — no es un error de
sintaxis, es un resultado lógicamente vacío. Por eso el hábito de imprimir
`ds.latitude.values[:3]` antes de recortar (para ver el orden) evita este
error silencioso.

**¿La interpolación bilineal funciona igual en la vertical (entre niveles
de presión o altura)?**
La misma idea (ponderar por distancia a los puntos vecinos) se aplica,
pero con un solo eje en vez de dos (interpolación lineal simple, no
bilineal). Xarray lo maneja con el mismo método `.interp()`, solo que
sobre la dimensión vertical en vez de latitud/longitud. No se trabaja en
este módulo porque los archivos de muestra son de un solo nivel, pero la
lógica es la misma.

**¿Qué pasa si pido `.interp()` en un punto que está *fuera* del dominio de
la grilla (por ejemplo, una estación justo en el borde o afuera)?**
Xarray devuelve `NaN` en vez de un error, porque no hay dos nodos que
"rodeen" al punto en esa dirección — no se puede extrapolar con
interpolación bilineal simple. Es buena práctica verificar, antes de
interpolar, que el punto de interés esté dentro del rango de latitud y
longitud del dominio descargado.

## Para profundizar

Material opcional: no hace falta para la práctica ni para el proyecto final.

### Cuándo lee Xarray los datos

Este es el momento exacto en que ocurre la lectura: justo después de
`xr.open_dataset(...)`, el objeto `Dataset` ya existe y su `repr()` (lo que
se imprime al mostrarlo) ya lista variables, dimensiones y atributos —pero
si se inspecciona el arreglo interno de una variable en ese momento, no es
todavía un arreglo NumPy en memoria, sino un "puntero" a dónde leerlo en el
disco. Recién al llamar a `.values`, `.load()`, o al graficar con
Matplotlib, Xarray dispara la lectura real y el arreglo se convierte en
NumPy. Una duda común aquí es *"¿entonces `open_dataset` no verifica que el
archivo existe o esté bien formado?"* — sí lo hace: si el archivo no existe
o está corrupto, `open_dataset` falla de inmediato, porque para leer los
metadatos igual necesita poder abrir el archivo; lo que se pospone es solo
la lectura de los **valores numéricos** de cada variable.

### Cómo traduce `cfgrib` los códigos de GRIB

Cada mensaje GRIB identifica su variable con números de tablas
estandarizadas por la OMM, no con un nombre de texto. Por ejemplo, en las
tablas del ECMWF la temperatura a 2 m es `parameter 167` de la `table 128`.
La biblioteca `eccodes` contiene esas tablas y `cfgrib` la usa para
convertir cada código en una variable con nombre (`t2m`) y atributos
(`units`, `long_name`). Por eso no hace falta conocer los códigos: basta
con verificar `long_name` y `units` después de abrir el archivo.

### Interpolación bilineal: la fórmula

Para un punto $(x, y)$ rodeado por cuatro nodos de grilla $Q_{11}, Q_{12},
Q_{21}, Q_{22}$, con coordenadas $x_1, x_2$ e $y_1, y_2$:

$$f(x,y) \approx \frac{1}{(x_2-x_1)(y_2-y_1)} \Big[ f(Q_{11})(x_2-x)(y_2-y) + f(Q_{21})(x-x_1)(y_2-y) + f(Q_{12})(x_2-x)(y-y_1) + f(Q_{22})(x-x_1)(y-y_1) \Big]$$

Cada nodo pesa según el área del rectángulo opuesto a él: cuanto más cerca
está el punto de un nodo, mayor es ese peso. Es la fórmula que se verifica
a mano en el Ejercicio 4.

## Recursos sugeridos

- Documentación oficial de Xarray — *Reading and writing files*,
  *Interpolating data*.
- Documentación de `cfgrib` — *Read GRIB files*.
- Convenciones CF — [cfconventions.org](https://cfconventions.org) (sección
  *Standard Name Table* como referencia de consulta, no lectura completa).

## Siguiente módulo

[Módulo 3 — Descarga automatizada de datos de entrada](../modulo_03_descarga_datos_entrada/README.md):
se usan estas mismas herramientas de lectura para verificar y preprocesar
datos descargados automáticamente desde repositorios globales (ERA5, GFS).
