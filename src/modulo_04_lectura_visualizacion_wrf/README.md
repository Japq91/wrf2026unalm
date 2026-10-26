# Módulo 4 — Lectura y visualización de salidas del WRF

[Índice del curso](../README.md)

**Ubicación en el curso:** Días 6–7 de 10 · **Carga horaria:** 10 h (2 h teoría + 3 h práctica por día)
**Precede a:** [Módulo 5 — Validación de resultados](../modulo_05_validacion_resultados/README.md)
**Requiere:** [Módulo 3 — Descarga de datos de entrada](../modulo_03_descarga_datos_entrada/README.md)

## Objetivo del módulo

Al finalizar el módulo, el participante podrá abrir un archivo `wrfout`,
entender por qué su estructura interna no es un `Dataset` "simple" como los
del Módulo 2, extraer variables físicas con nombres y grilla correctos, y
producir mapas georreferenciados, series temporales y animaciones
publicables a partir de esas salidas.

## Por qué este módulo importa para el WRF

Esta es la primera vez en el curso que se trabaja con lo que **produce** el
WRF. El archivo `wrfout` tiene algunas trampas: la forma en que el modelo
ubica el viento, el tipo de mapa sobre el que calcula y la manera en que
guarda la lluvia. Si se ignoran, el código corre sin ningún error pero el
mapa o la serie quedan **mal**. Este módulo enseña a reconocer esas
trampas.

## Prerrequisitos específicos

Haber completado los Módulos 2 y 3 (lectura de NetCDF con Xarray, y tener
disponible al menos un archivo `wrfout` de muestra — provisto como dataset
del curso, ya que generarlo requiere haber corrido el WRF, lo cual está
fuera del alcance de este curso).

**Datos de este módulo:** un `wrfout` **real** del WRF v4.7.1, recortado a
superficie (`data/grid_muestra/wrfout_real_muestra.nc`, ~44 MB): dominio
Argentina/Uruguay/sur de Brasil, proyección Mercator, 3 salidas cada 2 h. El
dominio no importa para lo que se enseña: la estructura de `wrfout` es la
misma en cualquier lugar. El Ejercicio 4 del Día 6 usa además
`data/grid_muestra/wrfpress_muestra.nc`, la misma corrida interpolada a 6
niveles de presión.

## Antes de empezar: activar el entorno

```bash
conda activate wrf2026
jupyter lab
```
`xwrf` y `cartopy` ya están instalados en `wrf2026` desde el Módulo 1. Si
al importar `xwrf` aparece `ModuleNotFoundError`, lo primero a revisar es
si la terminal realmente tiene el entorno activo (¿aparece `(wrf2026)` al
inicio de la línea de comandos?) antes de sospechar de la instalación.

---

## Día 6 — Estructura de wrfout, extracción con xwrf y mapas

### Teoría (2 h)

**1. Por qué wrfout no es un NetCDF "normal" (~35 min)**
El WRF divide la región en celdas, como un tablero. La temperatura, la
presión y la humedad se calculan en el **centro** de cada celda; el viento,
en cambio, en los **bordes** entre celdas (el viento este-oeste, `U`, en
los bordes izquierdo y derecho; el norte-sur, `V`, en los de arriba y
abajo). Al modelo le conviene así para sus cálculos. A esta disposición se
le llama grilla *staggered* (desplazada) o Arakawa-C.

Consecuencia práctica: en un tablero de 10 celdas de ancho hay 11 bordes,
así que `U` tiene **un punto más** que `T2` en esa dirección y sus puntos
están corridos media celda. Antes de combinar viento con temperatura hay
que llevar el viento al centro de las celdas: eso se llama **destagger**.

- En la vertical, `wrfout` tampoco usa alturas ni niveles de presión sino
  una escala propia del modelo (eta). En este curso se trabaja en
  superficie o con el producto ya convertido a niveles de presión, así que
  no hace falta manejarla (qué es, en [Para profundizar](#para-profundizar)).
- La latitud y longitud (`XLAT`/`XLONG`) no son una lista por eje como en
  ERA5, sino una **tabla**: cada celda tiene su propia latitud y longitud.
  Es porque el WRF calcula sobre un mapa plano (una proyección), y en un
  mapa plano las líneas de latitud y longitud no son rectas paralelas.

**2. El rol de xwrf (~25 min)**
`xwrf` hace por ti tres arreglos que a mano son tediosos: (a) lleva el
viento al centro de las celdas (destagger), (b) convierte la escala
vertical del modelo en alturas y presiones entendibles y (c) lee en el
archivo qué proyección usó el WRF y la deja lista para dibujar mapas con
`cartopy`. No inventa nada: la información ya está en el `wrfout`, solo
que escrita en el idioma del modelo.

**3. Proyecciones: el error de mapa más común (~30 min)**
La Tierra es redonda y un mapa es plano, así que todo mapa la deforma un
poco; cada forma de aplanarla es una **proyección**. Al dibujar con
`cartopy` hay que decir dos cosas distintas, y confundirlas es el error
más común:
- **`transform`: en qué están los datos que le paso.** Si le paso
  `XLAT`/`XLONG`, están en grados de latitud y longitud, y eso se indica con
  `transform=ccrs.PlateCarree()`. Siempre, aunque el WRF haya calculado en
  otra proyección.
- **`projection`: cómo quiero que se vea el mapa.** Puede ser la misma u
  otra; es una elección de presentación.

Si se confunden, el continente sale deformado o corrido de lugar, y Python
no da ningún error. En clase se muestra primero un mapa mal hecho y se
busca el problema antes de explicarlo.

**3.b. El viento del modelo y el norte real (~15 min)**
`U` y `V` dicen hacia dónde sopla el viento **según las líneas del tablero
del modelo**, no según el norte geográfico. Si el tablero está un poco
girado respecto al norte (pasa en varias proyecciones), "U positivo" ya no
es exactamente "viento hacia el este". `xwrf` corrige ese giro y entrega
`wind_east` y `wind_north`, que sí están referidos al norte real.
**Regla práctica:** para dibujar viento en un mapa o compararlo con una
estación, usar siempre `wind_east`/`wind_north`, no `U`/`V`.

**Con los datos del curso** la corrección da exactamente cero, porque la
proyección Mercator mantiene el norte de la grilla alineado con el norte
geográfico. No es un error, y la regla práctica sigue valiendo: con Lambert
Conformal la diferencia sí aparece.

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
4. **Refuerzo — otro producto real de WRF, a niveles de presión (35 min).**
   Los Ejercicios 1-3 trabajan el `wrfout` crudo. En la
   práctica real casi nunca se hacen mapas sinópticos sobre el `wrfout`
   crudo directamente — se post-procesa antes a **niveles de presión
   estándar** (1000, 850, 700, 500, 300, 200 hPa), un producto distinto y
   más comparable con ERA5/GFS (Módulo 3). Usando `wrfpress_muestra.nc`
   (misma corrida real, post-procesada), construir un mapa sinóptico
   clásico en 500 hPa (altura geopotencial en contornos + viento) y, como
   **tipo de gráfico distinto** a todo lo anterior (un perfil, no un mapa),
   un perfil vertical de temperatura en un punto fijo a través de los 6
   niveles disponibles.
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

La herramienta es la misma; el resultado depende de qué dimensión se
aplasta. Una advertencia: el promedio simple trata a todas las celdas como
si cubrieran la misma superficie. En una región del tamaño de las del WRF
eso es casi cierto; en un mapa global en latitud y longitud no, porque las
celdas cerca de los polos son mucho más chicas (cómo se corrige, en
[Para profundizar](#para-profundizar)).

**2. La lluvia viene acumulada (~20 min)**
`RAINC` y `RAINNC` (las dos partes de la lluvia que calcula el WRF) no dicen
cuánto llovió en cada hora, sino **cuánto lleva lloviendo desde que empezó
la simulación**, como el odómetro de un auto. Para saber cuánto llovió
entre dos salidas se resta: lluvia de ahora menos lluvia de la salida
anterior (de `RAINC + RAINNC`). Graficar el acumulado como si fuera la
lluvia de una hora es un error muy común.

Ojo con el intervalo: en el `wrfout` de este módulo hay una salida cada
**2 horas**, así que la resta da lluvia en 2 horas, no por hora. Siempre
revisar cada cuánto hay salidas (`ds["Time"].values`).

**3. Animaciones: un mapa por cada hora (~35 min)**
Una animación es una secuencia de mapas como los del Día 6, uno por cada
salida del modelo, pasados uno tras otro como un folioscopio. Se arma con
`FuncAnimation` de Matplotlib, que actualiza la misma figura en cada
cuadro y guarda el resultado como `.gif`. (Otra forma válida: guardar una
imagen por hora y juntarlas después con `imageio`.)

**4. Guardar lo calculado (~20 min)**
La lluvia por intervalo, las series y los promedios se guardan con
`.to_netcdf()` en un archivo propio, mucho más liviano que el `wrfout`. Así
no hay que recalcularlos cada vez, y es lo que lee directamente la
validación del Módulo 5.

**5. Cierre: lista de control antes de confiar en un mapa (~20 min)**
Se repasan las cinco trampas del módulo: el viento en los bordes de las
celdas, la proyección al dibujar, el viento girado respecto al norte, la
lluvia acumulada y el promedio sin ponderar. Es la lista para revisar antes
de creerle a un mapa o a un número sacado de un `wrfout`.

### Práctica (3 h)

1. **Serie temporal en un punto (35 min).** Extraer la serie temporal
   completa de `T2` en el punto de grilla más cercano a un punto de interés
   (en la práctica del curso, el aeropuerto de Iguazú, una de las 6
   estaciones reales dentro del dominio que se validan en el Módulo 5 — ver
   `data/ogimet/coords_area_wrf.json`), buscando el índice `(y, x)` de distancia
   mínima en `XLAT`/`XLONG` (2D, no `.sel(method="nearest")` directo como
   en el Módulo 2, donde las coordenadas eran 1D), y graficarla con
   Matplotlib con eje temporal legible.
2. **Promedio espacial del dominio (25 min).** Calcular y graficar la
   evolución temporal del promedio espacial de `T2` sobre todo el dominio,
   superpuesto en el mismo eje que la serie puntual del ejercicio anterior,
   para comparar visualmente la variabilidad local frente a la del dominio
   completo.
3. **La lluvia viene acumulada (30 min).** Calcular la lluvia entre dos
   salidas como la diferencia de `RAINC + RAINNC` entre pasos de tiempo
   consecutivos y graficarla junto al error común (el acumulado total
   graficado como si fuera la lluvia de un intervalo), para ver la
   diferencia.
4. **Animación de temperatura (40 min).** Construir una animación con
   `FuncAnimation` que recorra los pasos de tiempo disponibles del `wrfout`
   real (3 pasos, cada 2 horas — corta pero suficiente para practicar la
   técnica; con una corrida completa de varios días se vería igual, solo
   con más cuadros), mostrando el mapa de `T2` con la misma escala de
   colores fija en todos los cuadros (para que la animación sea comparable
   entre pasos), y exportarla como archivo `.gif`.
5. **Exportación de productos derivados (30 min).** Consolidar en un único
   `Dataset` la lluvia por intervalo (Ejercicio 3), la serie puntual y el
   promedio espacial (este día), y exportarlo con `.to_netcdf()` a la
   carpeta de resultados del curso, siguiendo la convención de nombres
   introducida en el Módulo 3.
6. **Cierre y dudas (20 min).**

**Entregable del módulo:** tus copias de
`03_practica_dia7_series.ipynb` y `04_entregable_animacion.ipynb`, el
archivo `.gif` de la animación y el NetCDF de productos derivados
exportado.

---

## Cierre del módulo

**Checkpoint:** el participante debe poder listar, sin consultar el
notebook, las cinco fuentes de error silencioso trabajadas en este módulo
y explicar en una frase cómo se evita cada una.

<details>
<summary><strong>Respuesta esperada</strong> (ábrela después de intentarlo)</summary>

| Error silencioso | Cómo se evita |
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
los puntos de masa. `xwrf.postprocess().xwrf.destagger()` es seguro de
aplicar de todas formas sobre el `Dataset` completo: simplemente no
modifica las variables que no lo necesitan.

**¿Por qué XLAT/XLONG cambian un poco de un paso de tiempo a otro en el
archivo crudo, si el dominio no se mueve?**
En dominios estáticos (los más comunes, incluidos los de este curso) no
deberían cambiar de verdad; que la variable tenga una dimensión `Time`
además de `south_north`/`west_east` es una particularidad del formato de
salida del WRF, no una señal de que la grilla se mueve. `xwrf` colapsa esa
dimensión redundante automáticamente al postprocesar (usa el primer paso de
tiempo como referencia). Si se trabaja con un dominio *móvil* (seguimiento
de huracanes, por ejemplo), ahí sí XLAT/XLONG cambian genuinamente con el
tiempo — un caso que este curso no cubre.

**¿Cómo sé si mi mapa está mal proyectado si "a simple vista" se ve
razonable?**
La señal más confiable no es la forma del continente (a veces la
distorsión es sutil), sino verificar código: ¿el `transform` que se le pasó
a la función de graficado corresponde al sistema de coordenadas real de
`XLAT`/`XLONG` (`PlateCarree`, porque son grados)? Si en algún momento se
grafica usando directamente las coordenadas `x`/`y` en metros de la
proyección (las que agrega `xwrf`) pero con `transform=PlateCarree()`, el
mapa "correrá" sin error visible evidente en dominios pequeños, y el
desfase crece con dominios más grandes.

**La animación tarda mucho en generarse o el archivo `.gif` pesa
demasiado. ¿Cómo lo controlo?**
El tamaño y tiempo dependen del número de cuadros (pasos de tiempo) y de la
resolución/tamaño de la figura. Para pruebas rápidas conviene generar la
animación primero con pocos cuadros (`ds.isel(Time=slice(0, 3))`) para
validar que el código funciona, y recién después correrla con todos los
pasos de tiempo disponibles.

## Para profundizar

Material opcional: no hace falta para la práctica ni para el proyecto final.

### La coordenada vertical eta

El WRF no define sus niveles verticales a alturas fijas ni a presiones
fijas. Usa una coordenada eta ($\eta$) que vale 1 en la superficie del
terreno y 0 en el tope del modelo, y que sigue el relieve cerca del suelo
(los niveles bajos se curvan sobre los Andes) para luego volverse planos
en altura (coordenada híbrida). Por eso el mismo nivel del modelo cae a
distinta altura y presión en cada punto. Para hacer mapas a 500 hPa o
comparar con ERA5 se interpola primero a niveles de presión: eso es
justamente el archivo `wrfpress_muestra.nc` del Ejercicio 4 del Día 6.

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

- Documentación de `xwrf` — *Overview* y ejemplo de destagger.
- Documentación de `cartopy` — *Understanding the transform and projection
  keywords*.
- NCAR/UCAR — descripción de la grilla Arakawa-C y la coordenada vertical
  eta del WRF (documentación técnica del modelo, como lectura de referencia
  opcional).

## Siguiente módulo

[Módulo 5 — Validación de resultados](../modulo_05_validacion_resultados/README.md):
los productos derivados exportados aquí (series puntuales, precipitación
horaria) son exactamente lo que se compara contra observaciones en el
módulo siguiente.
