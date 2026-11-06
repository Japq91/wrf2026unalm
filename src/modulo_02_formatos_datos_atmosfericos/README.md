# Módulo 2 — Formatos de datos atmosféricos

[Índice del curso](../README.md)

**Ubicación en el curso:** Día 3 de 10 · **Carga horaria:** 5 h (2 h teoría + 3 h práctica)
**Precede a:** [Módulo 3 — Descarga de datos de entrada](../modulo_03_descarga_datos_entrada/README.md)
**Requiere:** [Módulo 1 — Python básico](../modulo_01_python_basico/README.md) (estructura `Dataset`/`DataArray` de Xarray)

## Objetivo del módulo

Al terminar el módulo, el participante podrá abrir, inspeccionar, recortar e
interpolar archivos NetCDF y GRIB/GRIB2 con Xarray, y leer en sus metadatos
qué es cada variable y en qué unidades está.

## Relación con el WRF

Los datos de entrada del WRF suelen venir en GRIB2 (GFS, ECMWF) o en NetCDF
(ERA5), y sus salidas (`wrfout`) son NetCDF. Desde el Módulo 3 vamos a abrir
estos archivos todos los días. El `Dataset` que en el Módulo 1 armamos a
mano, aquí lo leemos de un archivo.

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
Además de los números, un NetCDF guarda qué es cada variable, en qué
unidades está y en qué ejes se ordena. Tiene tres partes:
- **Dimensiones**: los ejes y cuántos datos hay en cada uno (`time: 744`,
  `latitude: 121`, `longitude: 240`).
- **Variables**: los datos. Algunas son **coordenadas**, que dicen dónde y
  cuándo está cada dato (la variable `latitude` da la latitud real de cada
  fila); otras son los datos en sí (`t2m`, temperatura a 2 m).
- **Atributos**: las etiquetas. Por variable (`units`, `long_name`) o del
  archivo completo (quién lo hizo, cómo se procesó).

La **convención CF** es un acuerdo sobre cómo escribir esas etiquetas: por
ejemplo, la temperatura del aire se identifica como `air_temperature`, en
kelvin, y no con un nombre cualquiera como `"temp"`. Por eso Xarray o
`xwrf` (Módulo 4) reconocen las variables sin que se lo digamos.

**2. Apertura perezosa con Xarray (~20 min)**
`xr.open_dataset(archivo)` no lee todos los números de una vez. Primero lee
qué variables hay, sus ejes y sus atributos. Los números se leen cuando
hacen falta: al graficar, al promediar o al guardar. Así un `wrfout` de
varios GB se abre en un segundo y se lee solo la parte que usamos.

En la demo se ve cuándo ocurre la lectura (detalle en
[Para profundizar](#para-profundizar)).

**3. GRIB/GRIB2: un formato orientado a mensajes (~30 min)**
Un GRIB es una secuencia de **mensajes**. Cada mensaje es un solo campo:
una variable, un nivel y una hora, muy comprimido. Los centros de
pronóstico distribuyen en GRIB porque los archivos son chicos. Los mensajes
no traen el nombre de la variable sino un código numérico; `cfgrib` lo
traduce y arma un `Dataset` de Xarray como el de un NetCDF (cómo, en
[Para profundizar](#para-profundizar)). Si el archivo mezcla mensajes de
tipos distintos (superficie y niveles de presión, por ejemplo), `cfgrib`
pide separarlos con `filter_by_keys`.

**4. Selección, recorte e interpolación espacial (~30 min)**
- **El punto más cercano** (`.sel(..., method="nearest")`): cuando el
  lugar buscado (una estación, por ejemplo) no cae justo en un punto de la
  grilla.
- **Recortar una región** (`.sel(latitude=slice(a, b))`): ERA5 guarda las
  latitudes de norte a sur (de 90° a -90°). Si se pide `slice(sur, norte)`,
  el resultado sale **vacío y sin ningún error**. Antes de recortar, miren
  el orden de la latitud.
- **Interpolar** (`.interp(..., method="linear")`): en vez de copiar el
  valor del punto más cercano, calcula uno nuevo mezclando los cuatro
  puntos de grilla que rodean al lugar. Cada uno pesa más cuanto más cerca
  está: si una estación está casi encima de un punto de grilla, el
  resultado se parece mucho a ese punto. Se llama interpolación
  **bilineal** (la fórmula, en [Para profundizar](#para-profundizar)).
  Funciona sobre coordenadas 1D, como las de ERA5. En el Módulo 5, con el
  `wrfout` (coordenadas 2D), usamos el punto más cercano.

### Práctica (3 h)

Cada ejercicio tiene un **📘 ejemplo resuelto** con un archivo de práctica
(sintético, con la misma estructura que ERA5 y GFS) y un **✍️ tu turno** con
el ERA5 de `data/era_muestra/era5_peru_20241213.nc`, seguido de una celda
**✔️ comprobar**.

1. **Inspección de un NetCDF (40 min).** Abrir el archivo con
   `xr.open_dataset()` y listar dimensiones, coordenadas, variables y
   atributos. Responder en el notebook: ¿en qué unidades está la
   temperatura?, ¿la latitud es ascendente o descendente?, ¿qué convención
   declara el atributo `Conventions`? Después, lo mismo con `msl` (presión
   a nivel del mar): ERA5 la da en pascales, así que hay que dividir entre
   100 para tener hPa. En el «tu turno», el ERA5 del repositorio tiene
   otras sorpresas: el tiempo se llama `valid_time` y la precipitación
   viene en metros.
2. **Apertura de un GRIB2 con cfgrib (35 min).** Abrir un GRIB2 (un
   extracto tipo GFS) con `xr.open_dataset(archivo, engine="cfgrib")` y
   compararlo con el NetCDF. En este archivo, `cfgrib` traduce el mensaje
   `shortName="2t"` al mismo nombre `t2m` del NetCDF; compruébenlo con
   código. Otras fuentes pueden usar otro nombre corto para la misma
   variable, así que conviene revisar `long_name` y `standard_name`. En el
   «tu turno», pasar la longitud de 0–360 a −180–180 y sacar el valor en
   Lima.
3. **Recorte de dominio y periodo (40 min).** Recortar a una región (la
   costa central del Perú) y a un rango de horas, revisando antes el orden
   de la latitud. Guardar el recorte con `.to_netcdf()`.
4. **Interpolación a un punto (45 min).** Elegir un punto que no coincida
   con ningún nodo de la grilla (en el «tu turno», Campo de Marte). Sacar
   la serie de temperatura con `.sel(method="nearest")` y con
   `.interp(method="linear")`, graficar las dos y comprobar que el valor
   interpolado queda entre los cuatro vecinos. *Opcional:* calcularlo a
   mano con la [fórmula bilineal](#interpolación-bilineal-la-fórmula).
5. **Cierre y dudas (20 min).

**Entregable del día:** tus copias `_mio` de los tres notebooks de práctica,
[`02_practica_inspeccion_netcdf_grib.ipynb`](notebooks/02_practica_inspeccion_netcdf_grib.ipynb)
(Ejercicios 1–2),
[`03_practica_recorte_dominio.ipynb`](notebooks/03_practica_recorte_dominio.ipynb)
(Ejercicio 3) y
[`04_entregable_interpolacion.ipynb`](notebooks/04_entregable_interpolacion.ipynb)
(Ejercicio 4), con las comprobaciones en ✅, y el NetCDF recortado del
Ejercicio 3.

---

## Cierre del módulo

**Pregunta de cierre:** ¿por qué `.sel(method="nearest")` y
`.interp(method="linear")` dan resultados distintos, y cuándo usarían cada
uno? Por ejemplo, ¿elegir el nivel de presión más cercano o interpolar
entre dos niveles?

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
  nodos, como la ubicación de una estación.
</details>

## Preguntas frecuentes

**¿Voy a recibir mis datos en NetCDF o en GRIB? ¿Yo elijo?**
Depende de la fuente. ERA5 vía `cdsapi` (Módulo 3) permite pedir el
formato de salida (NetCDF o GRIB). GFS vía Herbie llega nativamente en
GRIB2, porque así es como NOAA lo publica; si se prefiere trabajar todo en
NetCDF, se convierte después de descargarlo (Módulo 3). GRIB ocupa menos;
NetCDF es más fácil de inspeccionar y es el formato de las salidas del WRF
(Módulo 4).

**Si genero mis propios archivos NetCDF (por ejemplo, guardando un
resultado con `.to_netcdf()`), ¿tengo que seguir la convención CF?**
No es obligatorio: Xarray lee cualquier NetCDF válido. Pero conviene,
porque así otra persona (o uno mismo, meses después) sabe qué es cada
variable sin preguntar. Basta con completar `units`, `long_name` y, si
existe, `standard_name` al crear cada variable.

**¿Qué pasa si intento recortar con `.sel(latitude=slice(...))` y el
resultado sale vacío, pero no hay ningún error?**
Es el problema de la sección 4: la latitud está ordenada de norte a sur.
Para Xarray, pedir un rango en el orden contrario es válido; simplemente no
encuentra puntos y devuelve un resultado vacío. Imprimir
`ds.latitude.values[:3]` antes de recortar muestra el orden y evita el
problema.

**¿La interpolación bilineal funciona igual en la vertical (entre niveles
de presión o altura)?**
La idea es la misma, pero sobre un solo eje (interpolación lineal). Se
hace con el mismo `.interp()`, sobre la dimensión vertical. No lo
practicamos porque los archivos del módulo tienen un solo nivel.

**¿Qué pasa si pido `.interp()` en un punto que está *fuera* del dominio de
la grilla (por ejemplo, una estación justo en el borde o afuera)?**
Xarray devuelve `NaN`, sin error, porque no hay nodos a ambos lados del
punto y la interpolación bilineal no extrapola. Antes de interpolar,
conviene revisar que el punto esté dentro del rango de latitud y longitud
del archivo.

## Para profundizar

Material opcional: no hace falta para la práctica ni para el proyecto final.

### Cuándo lee Xarray los datos

Justo después de `xr.open_dataset(...)`, el `Dataset` ya lista variables,
dimensiones y atributos, pero los valores de cada variable todavía están en
el disco: al imprimirla se ve `[N values with dtype=...]` en vez de los
números. Al usar `.values` o `.load()`, o al graficar, Xarray lee los datos
y los pasa a un arreglo NumPy.

¿Entonces `open_dataset` no revisa si el archivo existe o está dañado? Sí lo
revisa: para leer los metadatos tiene que abrirlo, así que falla en ese
momento. Lo que se pospone es solo la lectura de los valores.

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

- Documentación de Xarray: *Reading and writing files*, *Interpolating
  data*.
- Documentación de `cfgrib`: *Read GRIB files*.
- Convenciones CF: [cfconventions.org](https://cfconventions.org). La
  *Standard Name Table* sirve para consultar nombres.

## Siguiente módulo

[Módulo 3 — Descarga automatizada de datos de entrada](../modulo_03_descarga_datos_entrada/README.md):
con estas mismas herramientas revisamos y preparamos lo que descargamos de
ERA5, GFS y FNL.
