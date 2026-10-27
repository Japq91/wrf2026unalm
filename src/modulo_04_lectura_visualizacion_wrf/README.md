# Módulo 4 — Lectura y visualización de salidas del WRF

[Índice del curso](../README.md)

**Ubicación en el curso:** Días 6–7 de 10 · **Carga horaria:** 10 h (2 h teoría + 3 h práctica por día)
**Precede a:** [Módulo 5 — Validación de resultados](../modulo_05_validacion_resultados/README.md)
**Requiere:** [Módulo 3 — Descarga de datos de entrada](../modulo_03_descarga_datos_entrada/README.md)

## Objetivo del módulo

Al terminar el módulo, el participante podrá abrir un `wrfout`, explicar en
qué se diferencia de los NetCDF del Módulo 2, extraer variables con
`xwrf` y hacer mapas, series temporales y animaciones con esas salidas.

## Relación con el WRF

Aquí empezamos a trabajar con lo que **produce** el WRF. El `wrfout` tiene
detalles que hay que conocer: dónde ubica el modelo el viento, sobre qué
proyección calcula y cómo guarda la lluvia. Si no se tienen en cuenta, el
código corre sin error pero el mapa o la serie quedan **mal**.

## Prerrequisitos específicos

Haber completado los Módulos 2 y 3 (lectura de NetCDF con Xarray). El
`wrfout` viene en el repositorio, porque en el curso no corremos el WRF.

**Datos de este módulo:** la salida de una corrida del WRF v4.7.1,
recortada a superficie (`data/grid_muestra/wrfout_real_muestra.nc`, unos
44 MB). El dominio cubre Argentina, Uruguay y el sur de Brasil, en
proyección Mercator, con 3 salidas cada 2 h. La estructura de un `wrfout`
es la misma para cualquier dominio. El Ejercicio 4 del Día 6 usa además
`data/grid_muestra/wrfpress_muestra.nc`, la misma corrida interpolada a 6
niveles de presión.

## Antes de empezar: activar el entorno

```bash
conda activate wrf2026
jupyter lab
```
`xwrf` y `cartopy` ya están instalados en `wrf2026`. Si al importar `xwrf`
aparece `ModuleNotFoundError`, revisen primero si la terminal muestra
`(wrf2026)` al inicio de la línea.

---

## Día 6 — Estructura de wrfout, extracción con xwrf y mapas

### Teoría (2 h)

**1. En qué se diferencia el wrfout de otros NetCDF (~35 min)**
El WRF divide la región en celdas, como un tablero. La temperatura, la
presión y la humedad se calculan en el **centro** de cada celda; el viento,
en cambio, en los **bordes** entre celdas (el viento este-oeste, `U`, en
los bordes izquierdo y derecho; el norte-sur, `V`, en los de arriba y
abajo). Así el modelo calcula mejor el flujo de aire entre celdas. A esta
disposición se le llama grilla *staggered* (desplazada) o Arakawa-C.

En un tablero de 10 celdas de ancho hay 11 bordes,
así que `U` tiene **un punto más** que `T2` en esa dirección y sus puntos
están corridos media celda. Antes de combinar viento con temperatura hay
que llevar el viento al centro de las celdas: eso se llama **destagger**.

- En la vertical, `wrfout` tampoco usa alturas ni niveles de presión sino
  una escala propia del modelo (eta). En este curso se trabaja en
  superficie o con el producto ya convertido a niveles de presión, así que
  no hace falta manejarla (qué es, en [Para profundizar](#para-profundizar)).
- La latitud y la longitud (`XLAT`/`XLONG`) no son una lista por eje como
  en ERA5, sino una **tabla**: cada celda tiene su latitud y su longitud.
  El WRF calcula sobre una grilla regular en metros sobre un plano
  proyectado. En Mercator, como el dominio del curso, la latitud es
  constante en cada fila pero el paso en grados cambia de una fila a otra;
  en Lambert varía incluso dentro de una fila.

**2. El rol de xwrf (~25 min)**
`xwrf` hace tres cosas que a mano llevan tiempo: (a) lleva el viento al
centro de las celdas (destagger), (b) calcula alturas y presiones a partir
de la coordenada vertical del modelo y (c) lee qué proyección usó el WRF y
la deja lista para `cartopy`. Todo eso ya está en el `wrfout`, en los
atributos y variables propios del modelo.

**3. Proyecciones (~30 min)**
Cada forma de pasar la Tierra a un plano es una **proyección**, y todas
deforman algo. Al dibujar con `cartopy` hay que indicar dos cosas
distintas, y es muy fácil confundirlas:
- **`transform`: en qué están los datos que le paso.** Si le paso
  `XLAT`/`XLONG`, están en grados de latitud y longitud, y eso se indica con
  `transform=ccrs.PlateCarree()`. Siempre, aunque el WRF haya calculado en
  otra proyección.
- **`projection`: cómo quiero que se vea el mapa.** Puede ser la misma u
  otra; se elige por cómo se quiere mostrar.

Si se confunden, el continente sale deformado o corrido de lugar, y Python
no da ningún error. En clase se muestra primero un mapa mal hecho y se
busca el problema antes de explicarlo.

**3.b. El viento del modelo y el norte real (~15 min)**
`U` y `V` dan la dirección del viento **según los ejes de la grilla del
modelo**, no según el norte geográfico. Si la grilla está girada respecto
al norte (pasa en varias proyecciones), U positivo ya no es exactamente
viento hacia el este. `xwrf` corrige ese giro y entrega `wind_east` y
`wind_north`, referidos al norte. Para dibujar viento o compararlo con una
estación, usamos `wind_east`/`wind_north`.

**Con los datos del curso** la corrección da cero, porque en Mercator la
grilla está alineada con el norte. Con Lambert Conformal la diferencia sí
aparece, y por eso usamos igual `wind_east`/`wind_north`.

### Práctica (3 h)

1. **Primera apertura con xwrf (40 min).** Abrir el `wrfout` de muestra con
   `xr.open_dataset(archivo, engine="xwrf")` (o el flujo equivalente de
   `xwrf`), comparar las dimensiones de `U`/`V` frente a `T2` antes y
   después del destagger, e imprimir los atributos de proyección detectados.
2. **Mapa de temperatura en superficie (45 min).** Extraer `T2` en un
   instante de tiempo, convertir de Kelvin a Celsius, y construir un mapa
   con `cartopy` (`PlateCarree` como transform de los datos) que incluya
   línea de costa, fronteras, un mapa de colores apropiado para
   temperatura, barra de color con unidades, y título con la fecha/hora
   exacta del dato graficado.
3. **Campo de viento (40 min).** Extraer `U10`/`V10` (viento a 10 m, ya
   destaggered), y superponer al mapa anterior un campo de vectores o
   *barbs* de viento (`ax.quiver` o `ax.barbs`), submuestreando la grilla
   (p. ej. cada 5 puntos) para que el mapa sea legible.
4. **Extra: la misma corrida en niveles de presión (35 min).** Los
   Ejercicios 1 a 3 usan el `wrfout` tal como sale del modelo. Para mapas
   sinópticos se suele interpolar antes a **niveles de presión** (1000,
   850, 700, 500, 300, 200 hPa), que además se comparan directamente con
   ERA5 y GFS. Con `wrfpress_muestra.nc` (la misma corrida, ya
   interpolada), hacer un mapa en 500 hPa (altura geopotencial en
   contornos y viento) y un perfil vertical de temperatura en un punto,
   con los 6 niveles.
5. **Cierre y dudas (20 min).**

**Entregable del día:**
[`02_practica_dia6_mapas.ipynb`](notebooks/02_practica_dia6_mapas.ipynb) con
los mapas de temperatura y viento, el mapa sinóptico en 500 hPa y el perfil
vertical.

---

## Día 7 — Series temporales, promedios espaciales, animaciones y exportación

### Teoría (2 h)

**1. Una serie en un punto o un promedio de la región (~25 min)**
Es el `axis` del Módulo 1, ahora con nombres. Con la misma grilla
`(Time, south_north, west_east)` se pueden sacar dos cosas opuestas:
- **Serie de tiempo en un punto:** se fija un lugar
  (`.isel(south_north=..., west_east=...)`) y queda cómo cambia en el
  tiempo.
- **Promedio de la región:** se aplasta el espacio
  (`.mean(dim=["south_north", "west_east"])`) y queda cómo cambia la región
  entera en el tiempo.

La operación es la misma; cambia la dimensión que se promedia. Ojo: el
promedio simple trata a todas las celdas como
si cubrieran la misma superficie. En una región del tamaño de las del WRF
eso es casi cierto; en un mapa global en latitud y longitud no, porque las
celdas cerca de los polos son mucho más chicas (cómo se corrige, en
[Para profundizar](#para-profundizar)).

**2. La lluvia viene acumulada (~20 min)**
`RAINC` y `RAINNC` (las dos partes de la lluvia que calcula el WRF) no dicen
cuánto llovió en cada hora, sino **cuánto lleva lloviendo desde que empezó
la simulación**, como el odómetro de un auto. Para saber cuánto llovió
entre dos salidas se resta el valor de la salida anterior al de la actual
(de `RAINC + RAINNC`). Graficar el acumulado como si fuera la lluvia de una
hora es un error muy frecuente.

Ojo con el intervalo: en el `wrfout` de este módulo hay una salida cada
**2 horas**, así que la resta da lluvia en 2 horas, no por hora. Revisen
siempre cada cuánto hay salidas (`ds["Time"].values`).

**3. Animaciones: un mapa por cada hora (~35 min)**
Una animación es una secuencia de mapas como los del Día 6, uno por cada
salida del modelo. Se arma con `FuncAnimation` de Matplotlib, que
actualiza la misma figura en cada cuadro y guarda el resultado como
`.gif`. También se puede guardar una imagen por hora y juntarlas después
con `imageio`.

**4. Guardar lo calculado (~20 min)**
La lluvia por intervalo, las series y los promedios se guardan con
`.to_netcdf()` en un archivo propio, mucho más liviano que el `wrfout`. Así
no hay que recalcularlos, y es lo que lee la validación del Módulo 5.

**5. Cierre: qué revisar antes de usar un resultado (~20 min)**
Repasamos los cinco errores del módulo: el viento en los bordes de las
celdas, la proyección al dibujar, el viento girado respecto al norte, la
lluvia acumulada y el promedio sin ponderar. Conviene revisarlos cada vez
que se saca un mapa o un número de un `wrfout`.

### Práctica (3 h)

1. **Serie temporal en un punto (35 min).** Extraer la serie temporal
   completa de `T2` en el punto de grilla más cercano a un punto de interés
   (en el curso, el aeropuerto de Iguazú, una de las 6 estaciones del
   dominio que usamos en el Módulo 5; ver
   `data/ogimet/coords_area_wrf.json`). Se busca el índice `(y, x)` de
   menor distancia en `XLAT`/`XLONG`, porque con coordenadas 2D no sirve
   `.sel(method="nearest")` como en el Módulo 2. Graficarla con un eje de
   tiempo legible.
2. **Promedio espacial del dominio (25 min).** Calcular y graficar la
   evolución temporal del promedio espacial de `T2` sobre todo el dominio,
   en el mismo gráfico que la serie del ejercicio anterior, para comparar
   cuánto varía un punto y cuánto el dominio completo.
3. **La lluvia viene acumulada (30 min).** Calcular la lluvia entre dos
   salidas como la diferencia de `RAINC + RAINNC` entre pasos de tiempo
   consecutivos y graficarla junto al error común (el acumulado total
   graficado como si fuera la lluvia de un intervalo), para ver la
   diferencia.
4. **Animación de temperatura (40 min).** Construir una animación con
   `FuncAnimation` que recorra los pasos de tiempo disponibles del `wrfout`
   (3 salidas, cada 2 horas; con una corrida completa habría más cuadros),
   con el mapa de `T2` y la misma escala de colores en todos los cuadros
   para poder compararlos. Guardarla como `.gif`.
5. **Exportación de productos derivados (30 min).** Consolidar en un único
   `Dataset` la lluvia por intervalo (Ejercicio 3), la serie puntual y el
   promedio espacial (este día), y exportarlo con `.to_netcdf()` a la
   carpeta de resultados, con la forma de nombrar archivos del Módulo 3.
6. **Cierre y dudas (20 min).**

**Entregable del módulo:** tus copias de
`03_practica_dia7_series.ipynb` y `04_entregable_animacion.ipynb`, el
archivo `.gif` de la animación y el NetCDF de productos derivados
exportado.

---

## Cierre del módulo

**Pregunta de cierre:** sin mirar el notebook, nombren los cinco errores
del módulo y expliquen en una frase cómo se evita cada uno.

<details>
<summary><strong>Respuesta esperada</strong> (ábrela después de intentarlo)</summary>

| Error | Cómo se evita |
|---|---|
| **Grilla staggered**: `U`/`V` tienen un punto más que `T2` y quedan desplazados medio punto | Hacer destagger (`xwrf`) antes de combinar viento con variables de masa |
| **Proyección al graficar**: confundir `transform` con `projection` | `transform=PlateCarree()` para datos en `XLAT`/`XLONG` (grados); la `projection` del mapa es aparte |
| **Viento grid-relative**: `U`/`V` siguen los ejes de la grilla, no el norte real | Usar `wind_east`/`wind_north` (earth-relative) para mapas y para comparar con estaciones |
| **Variable acumulada**: `RAINC`/`RAINNC` suman desde el inicio | Restar pasos consecutivos y revisar cada cuánto hay salidas (aquí, 2 h) |
| **Promedio espacial sin ponderar**: supone celdas de igual área | En dominios grandes o grillas lat/lon, ponderar por `cos(lat)` o por el área de la celda |
</details>

## Preguntas frecuentes

**¿Tengo que hacer destagger *siempre*, incluso si solo voy a graficar
`T2` (que no está staggered)?**
No. Solo las variables que tienen una dimensión terminada en `_stag`
(`U`, `V`, y cualquier otra definida en las caras de la celda) necesitan
destagger. `T2`, `U10`, `V10`, `RAINC`, `RAINNC`, entre otras, ya están en
los puntos de masa. Se puede aplicar `xwrf.postprocess().xwrf.destagger()`
al `Dataset` completo: las variables que no lo necesitan quedan igual.

**¿Por qué XLAT/XLONG cambian un poco de un paso de tiempo a otro en el
archivo crudo, si el dominio no se mueve?**
En un dominio fijo, como el del curso, no cambian: el WRF guarda `XLAT` y
`XLONG` con una dimensión `Time` aunque la grilla no se mueva. `xwrf`
elimina esa dimensión al postprocesar y usa el primer tiempo. Solo en un
dominio *móvil* (por ejemplo, siguiendo un huracán) cambian de verdad; no
lo vemos en el curso.

**¿Cómo sé si mi mapa está mal proyectado, si a simple vista se ve bien?**
La forma del continente no siempre lo muestra. Revisen el código: si
grafican con `XLAT`/`XLONG`, el `transform` tiene que ser `PlateCarree()`,
porque están en grados. El error típico es graficar con `x`/`y` (en
metros, las que agrega `xwrf`) y poner `transform=PlateCarree()`: no da
error, y el desfase crece con el tamaño del dominio.

**La animación tarda mucho en generarse o el archivo `.gif` pesa
demasiado. ¿Cómo lo controlo?**
Dependen del número de cuadros y del tamaño de la figura. Prueben primero
con pocos cuadros (`ds.isel(Time=slice(0, 3))`) y, cuando funcione,
córranla con todos.

## Para profundizar

Material opcional: no hace falta para la práctica ni para el proyecto final.

### La coordenada vertical eta

El WRF no define sus niveles verticales a alturas fijas ni a presiones
fijas. Usa una coordenada eta ($\eta$) que vale 1 en la superficie del
terreno y 0 en el tope del modelo, y que sigue el relieve cerca del suelo
(los niveles bajos se curvan sobre los Andes) para luego volverse planos
en altura (coordenada híbrida). Por eso el mismo nivel del modelo cae a
distinta altura y presión en cada punto. Para hacer mapas a 500 hPa o
comparar con ERA5 se interpola primero a niveles de presión: eso es el
archivo `wrfpress_muestra.nc` del Ejercicio 4 del Día 6.

### Por qué ponderar un promedio espacial

En una grilla regular en latitud/longitud, una celda de 0.25° × 0.25° cubre
unos 770 km² en el ecuador y apenas la mitad a 60° de latitud, porque los
meridianos se juntan hacia los polos (el área es proporcional a
$\cos(\text{lat})$). Un promedio simple les da a todas el mismo peso y
sobrerrepresenta las latitudes altas. La corrección es
`ds.weighted(np.cos(np.deg2rad(ds.latitude))).mean(...)`. En el dominio del
WRF de este curso las celdas tienen casi el mismo tamaño y la diferencia es
pequeña.

## Recursos sugeridos

- Documentación de `xwrf`: *Overview* y el ejemplo de destagger.
- Documentación de `cartopy`: *Understanding the transform and projection
  keywords*.
- Documentación técnica del WRF (NCAR/UCAR): grilla Arakawa-C y
  coordenada vertical eta (opcional).

## Siguiente módulo

[Módulo 5 — Validación de resultados](../modulo_05_validacion_resultados/README.md):
los productos derivados exportados aquí (series puntuales, precipitación
horaria) son exactamente lo que se compara contra observaciones en el
módulo siguiente.
