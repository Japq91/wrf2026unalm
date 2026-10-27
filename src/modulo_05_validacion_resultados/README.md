# Módulo 5 — Validación de resultados del WRF

[Índice del curso](../README.md)

**Ubicación en el curso:** Días 8–9 de 10 · **Carga horaria:** 10 h (2 h teoría + 3 h práctica por día)
**Precede a:** [Módulo 6 — Pipeline integrado](../modulo_06_pipeline_integrado/README.md)
**Requiere:** [Módulo 4 — Lectura y visualización de salidas WRF](../modulo_04_lectura_visualizacion_wrf/README.md)

## Objetivo del módulo

Al terminar el módulo, el participante podrá comparar una simulación del
WRF con observaciones usando varias métricas, explicar qué mide cada una y
repetir el cálculo para muchas estaciones y variables con una función.

## Relación con el WRF

Que un mapa del Módulo 4 se vea bien no dice si la simulación se parece a
lo que pasó. En este módulo respondemos dos preguntas: **¿qué tan cerca
está el WRF de las observaciones?** y **¿mejora algo respecto del modelo
global que lo forzó?**

## Prerrequisitos específicos

Haber completado el Módulo 4 (productos derivados exportados a NetCDF,
que aquí son el lado simulado de la comparación) y el Módulo 2
(interpolación).

## Antes de empezar: activar el entorno

```bash
conda activate wrf2026
jupyter lab
```
Este módulo no necesita librerías nuevas.

---

## Día 8 — Del WRF a la estación y métricas de error

### Teoría (2 h)

**1. Tipos de observaciones, y por qué ERA5 no siempre sirve de referencia (~25 min)**
- **Estaciones de superficie:** miden directamente en un punto. Son
  confiables en ese punto, pero no dicen nada del punto de grilla vecino.
- **Datos satelitales:** cubren grandes áreas, pero no miden la variable
  directamente: la estiman a partir de la radiación que capta el satélite,
  así que tienen su propio error (y huecos por nubes o por la hora en que
  pasa el satélite).
- **Reanálisis:** sirve cuando no hay observaciones, con un cuidado: si
  el WRF se forzó con ERA5 (Módulo 3), validar el WRF contra ese mismo ERA5
  es en parte circular, porque no es una fuente independiente. Se puede
  usar, pero la pregunta cambia: ya no es si el WRF acierta, sino si
  agrega algo respecto de lo que recibió. Esa es la pregunta del *added
  value*, el Día 9.

**2. Llevar el modelo al punto de la estación (~15 min)**
La estación casi nunca coincide con un nodo de la grilla. En el Módulo 2
vimos dos opciones: el punto más cercano (`.sel(method="nearest")`) o
interpolar (`.interp(method="linear")`). Para una variable que cambia de
forma suave, como la temperatura, interpolar suele ser mejor; para la
lluvia convectiva, que cambia mucho en pocos kilómetros, un valor
interpolado puede no parecerse a lo que cayó en ningún lado.

Con el `wrfout` usamos el **punto de grilla más cercano**, igual que en el
Módulo 4: su latitud y su longitud son tablas 2D y `.interp()` solo
funciona con coordenadas 1D como las de ERA5. Con celdas de pocos
kilómetros, para la temperatura la diferencia con una interpolación es
pequeña. Para ERA5-Land, que sí tiene coordenadas 1D, el Día 9 usamos
`.interp()`.

**3. Métricas de error: qué mide cada una (~50 min)**
Cada métrica responde una pregunta distinta sobre el error. Ejemplo para
toda la sección: el WRF simula 24 horas de temperatura en Salto y la
estación midió esas mismas 24 horas. En Python, con `sim` y `obs` como
arreglos NumPy:

| Métrica | Pregunta que responde | En NumPy | Ideal |
|---|---|---|---|
| **Sesgo (bias)** | ¿El modelo está, en promedio, más caliente o más frío? | `np.mean(sim - obs)` | 0 |
| **MAE** | ¿De cuántos grados es el error típico? | `np.mean(np.abs(sim - obs))` | 0 |
| **RMSE** | Como el MAE, pero castigando más los errores grandes | `np.sqrt(np.mean((sim - obs)**2))` | 0 |
| **Correlación (r)** | ¿Sube y baja al mismo tiempo que la observación? | `np.corrcoef(sim, obs)[0, 1]` | 1 |
| **KGE** | Nota global que revisa patrón, promedio y amplitud a la vez | ver abajo | 1 |

- **Sesgo:** positivo = el modelo sobreestima. Un sesgo de +2 °C dice que
  el modelo está 2 °C más caliente en promedio, pero no si se equivoca
  siempre igual o a veces mucho y a veces nada.
- **MAE y RMSE** están en las mismas unidades que la variable (°C). El RMSE
  siempre es mayor o igual que el MAE; si es bastante mayor, el error viene
  de unas pocas horas muy malas más que de un error parejo.
- **r** solo mira la forma de la curva: un modelo que reproduce bien el
  ciclo diurno pero está 5 °C más caliente tiene r = 1. Por eso se
  reportan varias métricas.
- **KGE** junta tres revisiones en un solo número: ¿sigue el patrón? (r),
  ¿acierta el promedio? (β, promedio del modelo entre el observado) y
  ¿acierta la amplitud de las subidas y bajadas? (α, variabilidad del
  modelo entre la observada). Si el KGE sale bajo, mirar r, β y α por
  separado dice cuál de los tres falla.

Las fórmulas escritas, en [Para profundizar](#para-profundizar).

Casi siempre aparece la pregunta: *«si solo puedo mostrar una, ¿cuál
reporto?»* Mejor no reportar una sola. Como mínimo, una de error (RMSE o
MAE) y una de patrón (r o KGE). Solo r puede esconder un sesgo grande;
solo RMSE no dice si el error es sistemático o aleatorio.

### Práctica (3 h)

1. **Carga de observaciones (30 min).** Leer con Pandas la observación
   horaria de Lima (decodificada de mensajes SYNOP,
   `data/obs/Lima_2024_12_13_horario.csv`), armar su `DatetimeIndex`
   (Módulo 1) y graficar la serie. Aquí solo practicamos la lectura: Lima
   está fuera del dominio del WRF.
2. **Del WRF al punto de estación (40 min).** Desde aquí usamos Salto
   (Uruguay), que sí está dentro del dominio. Con el `wrfout` de **día
   completo** (`data/grid_muestra/wrfout_muestra.nc`, 24 salidas
   horarias), se toma el punto de grilla más cercano a la estación y se
   comparan las 24 horas del WRF con las observadas.
3. **Métricas escritas a mano (50 min).** Escribir `calcular_mae`,
   `calcular_rmse`, `calcular_bias`, `calcular_r` y `calcular_kge` sin usar
   una librería que ya las calcule, aplicarlas a las dos series (n = 24) y
   responder en el notebook: ¿el modelo está sesgado?, ¿qué tan bien sigue
   el ciclo diurno?
4. **Caso de contraste (30 min).** WRF y ERA5-Land contra la misma
   observación en Salto. Los dos tienen un sesgo parecido, pero fallan en
   sentido contrario en la variabilidad (`alpha`): uno exagera el ciclo
   diurno y el otro lo aplana. Con RMSE o bias no se ve. Calcular el KGE de
   los dos y explicar la diferencia en una frase.
5. **Cierre y dudas (10 min).**

**Entregable del día:** módulo `metricas.py` con las cinco funciones +
notebook con la validación de la estación de muestra y el caso de
contraste.

---

## Día 9 — Added value, diagramas de Taylor y automatización

### Teoría (2 h)

**1. Valor añadido (added value) de la simulación (~25 min)**
Correr el WRF cuesta tiempo y cómputo. La pregunta del valor añadido es:
**¿el WRF se acerca más a la observación que el modelo global con el que se
forzó?** Se comparan, contra la misma estación, dos fuentes:

1. el modelo global (ERA5 o GFS) en la ubicación de la estación, y
2. el WRF en la misma ubicación.

Si el WRF tiene mejores métricas, su resolución capta algo local que el
modelo global no ve (relieve, brisas, lluvia orográfica). Si no, para esa
variable y ese lugar el WRF no aporta, y ese resultado también vale. Aquí
el modelo global no es la referencia (eso sería la circularidad del
Día 8): es el competidor del WRF.

**2. Diagramas de Taylor: tres métricas en un solo gráfico (~45 min)**
Con varios modelos, tres tablas de números se vuelven difíciles de leer.
El diagrama de Taylor pone a cada modelo como un punto en un
cuarto de círculo, y la observación como un punto de referencia sobre el
eje horizontal. Se lee así:

- **Distancia al centro:** cuánto varía el modelo (su desviación estándar).
  Lo ideal es que esté a la misma distancia que la observación.
- **Ángulo:** la correlación. Cuanto más cerca del eje horizontal, más alta.
- **Distancia al punto de la observación:** el error (RMSE centrado). El
  mejor modelo es el punto más cercano a la observación.

Las tres caben en un mismo dibujo por la ley de cosenos (detalle en
[Para profundizar](#para-profundizar)).

**3. Automatizar el cálculo para múltiples variables y periodos (~30 min)**
Escribimos una función `evaluar_variable(variable, estaciones, periodo)`
que recorre estaciones y variables, hace para cada una lo del Día 8
(alinear y calcular métricas) y junta los resultados en un `DataFrame`
(una fila por estación y variable, una columna por métrica).

**4. Comunicar resultados: tablas resumen (~20 min)**
Algunas reglas para una tabla de validación: ordenarla por la métrica que
más importe para el caso, usar los decimales que tengan sentido para la
variable y reportar RMSE o MAE junto con r o KGE (por lo visto el Día 8).

### Práctica (3 h)

1. **Opcional: un punto del diagrama a mano.**
   Con las métricas ya calculadas el Día 8 para la estación de muestra
   ($\sigma_s$, $\sigma_o$, $r$), verificar a mano (con una celda de
   código, aplicando la fórmula de la teoría) que la distancia calculada
   por ley de cosenos coincide con el RMSE centrado calculado
   directamente sobre las series (fórmula en
   [Para profundizar](#diagrama-de-taylor-la-ley-de-cosenos)).
2. **Diagrama de Taylor con SkillMetrics (60 min).** Usando el paquete
   [`SkillMetrics`](https://github.com/PeterRochford/SkillMetrics)
   (`sm.taylor_statistics()` + `sm.taylor_diagram()`), construir un
   diagrama con **una estación como referencia** (Salto) y **dos
   modelos** (WRF y ERA5-Land): 3 puntos en total.
   `sm.taylor_statistics()` calcula σ, RMSD centrado y r. Después, cada
   grupo repite el diagrama con otra de las 5 estaciones del dominio
   (Ezeiza, Rosario, Resistencia, Iguazú, Carrasco).
3. **Cálculo de added value (50 min).** Para la misma estación de
   referencia (Salto), repetir la comparación del Día 8 con ERA5-Land
   interpolado en lugar del WRF, calcular las mismas métricas y armar una
   tabla WRF contra observación y ERA5-Land contra observación. ¿Hay valor
   añadido para esa variable?
4. **Automatización multi-estación (50 min).** Implementar
   `evaluar_variable()` según el diseño de la teoría, ejecutarla sobre las
   6 estaciones del dominio del WRF y guardar la tabla en un `.csv`.
5. **Cierre y dudas (20 min).**

**Entregable del módulo:** tus copias de
`03_practica_dia9_taylor_addedvalue.ipynb` (diagrama de Taylor con
SkillMetrics, referencia + 2 modelos) y `04_entregable_automatizacion.ipynb`
(tabla de *added value* y archivo `.csv` con la validación automatizada de
todas las estaciones).

---

## Dos casos más en el entregable

El notebook `04_entregable_automatizacion.ipynb` agrega dos casos:

- **Un caso mal hecho a propósito:** las mismas 6 estaciones, pero
  con latitud y longitud intercambiadas al buscar el punto del WRF. Todas
  caen en la misma esquina del dominio, sobre el mar. El código no da error
  y `r` incluso sigue alto en algunas estaciones (el ciclo de día y noche
  se parece en toda la región), pero el sesgo y el KGE muestran el
  problema. Si el punto del modelo no corresponde al lugar de la estación,
  la validación no sirve. Al final hay una función que avisa cuando el
  punto encontrado queda lejos.
- **El caso bien hecho:** 6 aeropuertos de Argentina y Uruguay dentro del
  dominio, con observación hora por hora, comparando WRF y ERA5-Land contra
  la misma observación (143 pares). En temperatura, ERA5-Land gana en
  sesgo, MAE, RMSE y r, pero el WRF gana en KGE (0,75 frente a 0,69). Ese
  KGE junta las 6 estaciones en una sola serie, y la diferencia de
  temperatura entre estaciones lo infla; estación por estación, el WRF
  pierde en casi todas. En viento, ninguno de los dos sigue bien el patrón
  horario, y la lluvia horaria es lo más difícil de validar.

Cómo se obtuvieron las observaciones y los números completos, en
[Para profundizar](#para-profundizar).

**Extensión opcional (no evaluada):**
[`05_extension_opcional_peru_addedvalue.ipynb`](notebooks/05_extension_opcional_peru_addedvalue.ipynb)
repite la pregunta de *added value* fuera del dominio del WRF, con 7
estaciones de Perú: ERA5-Land (9 km) frente a ERA5 (31 km), contra la
misma observación. Requiere la extensión del Módulo 3, Día 5.

---

## Cierre del módulo

**Pregunta de cierre:** sin mirar el notebook, ¿por qué un modelo puede
tener r alto y KGE bajo? ¿Qué comparación, además de WRF contra
observación, hace falta para hablar de valor añadido?

<details>
<summary><strong>Respuesta esperada</strong> (ábrela después de intentarlo)</summary>

- **r alto y KGE bajo:** r solo mira si las curvas suben y bajan juntas. Si
  el modelo reproduce bien el ciclo diurno pero está 3 °C más caliente (β
  lejos de 1), o exagera o aplana las subidas y bajadas (α lejos de 1), r
  sigue alto pero el KGE baja, porque el KGE también revisa el promedio y
  la amplitud.
- **Valor añadido:** hace falta comparar también el **modelo global** (el
  ERA5 o GFS que forzó al WRF) contra la **misma observación**, en el mismo
  lugar y las mismas horas. Solo si el WRF sale mejor que el modelo global
  se puede decir que correrlo aportó algo.
</details>

## Preguntas frecuentes

**¿Por qué el RMSE y el MAE no coinciden con lo que veo en el gráfico?**
Porque son promedios de todo el período, y el ojo se fija en los picos. Un
modelo puede verse casi perfecto casi todo el tiempo y tener un RMSE alto
por unas pocas horas con mucho error, porque el RMSE pesa más los errores
grandes (sección 3 de la teoría).

**Mi KGE me dio un valor negativo. ¿Hice algo mal?**
No necesariamente. A diferencia de r (entre −1 y 1), el KGE no tiene
mínimo: puede ser muy negativo si $\beta$ o $\alpha$ se alejan mucho de 1,
o si r es negativo. Un KGE negativo indica un ajuste malo, no un error de
cálculo. Revisen $r$, $\beta$ y $\alpha$ por separado para ver cuál lo
baja.

**¿Por qué con el WRF usamos el punto más cercano y con ERA5-Land
interpolamos?**
Porque `.interp()` necesita coordenadas 1D, como las de ERA5-Land, y el
`wrfout` tiene `XLAT`/`XLONG` en 2D. Interpolar el WRF se puede hacer (por
ejemplo con `scipy` o con `xesmf`), pero con celdas de pocos km la
diferencia en temperatura es pequeña, y en el curso preferimos el método
que ya conocen del Módulo 4. ERA5-Land tiene celdas de 9 km, así que ahí
interpolar sí cambia más el resultado.

**Si mi caso de estudio no tiene estaciones cercanas, ¿puedo saltarme este
módulo?**
No. Si no hay estaciones en la zona, hay dos opciones: (a) usar datos
satelitales como referencia, con su propia incertidumbre (sección 1), o
(b) comparar con el reanálisis, diciendo claramente que eso muestra
consistencia con ERA5 y no una validación contra observaciones
independientes.

**¿El diagrama de Taylor reemplaza a las tablas de métricas, o se usan
juntos?**
Se usan juntos. El diagrama sirve para comparar muchas estaciones o
variables y ver cuál se aparta; la tabla, para citar valores exactos en un
informe. En la práctica del Día 9 se hacen los dos.

## Para profundizar

Material opcional: no hace falta para la práctica ni para el proyecto final.

### Las métricas, en fórmulas

Con $s_i$ el valor simulado, $o_i$ el observado y $n$ pares:

- Sesgo: $\text{bias} = \frac{1}{n}\sum (s_i - o_i)$
- MAE: $\text{MAE} = \frac{1}{n}\sum |s_i - o_i|$
- RMSE: $\text{RMSE} = \sqrt{\frac{1}{n}\sum (s_i - o_i)^2}$. Siempre
  $\text{RMSE} \geq \text{MAE}$ (desigualdad de Jensen): elevar al
  cuadrado pesa más los errores grandes.
- Correlación de Pearson:
  $r = \dfrac{\sum (s_i - \bar{s})(o_i - \bar{o})}{\sqrt{\sum (s_i-\bar{s})^2}\sqrt{\sum(o_i-\bar{o})^2}}$
- KGE: $\text{KGE} = 1 - \sqrt{(r-1)^2 + (\beta-1)^2 + (\alpha-1)^2}$, con
  $\beta = \bar{s}/\bar{o}$ y $\alpha = \sigma_s/\sigma_o$. No tiene
  mínimo: puede ser muy negativo.

### Diagrama de Taylor: la ley de cosenos

El RMSE centrado (el RMSE después de quitar el sesgo) cumple

$$\text{RMSE}_{centrado}^2 = \sigma_s^2 + \sigma_o^2 - 2\,\sigma_s\,\sigma_o\, r$$

que tiene la misma forma que la ley de cosenos, $c^2 = a^2 + b^2 -
2ab\cos\theta$, si $\theta = \arccos(r)$. Por eso, si se dibuja el modelo
a distancia $\sigma_s$ del origen y con ángulo $\arccos(r)$, y la
observación a distancia $\sigma_o$ sobre el eje horizontal, la distancia
entre ambos puntos es exactamente el RMSE centrado.

### De dónde salen las observaciones y los resultados completos

**Estaciones.** El notebook `04_entregable_automatizacion.ipynb` usa 6
aeropuertos de Argentina y Uruguay dentro del dominio del WRF. Sus
coordenadas salen del encabezado de cada reporte de OGIMET
(`data/ogimet/coords_area_wrf.json`).

**Modelo.** Usa el `wrfout` de día completo
(`data/grid_muestra/wrfout_muestra.nc`, 24 salidas horarias del
13/12/2024). El del Módulo 4 (`wrfout_real_muestra.nc`) cubre solo 3
horas, pero trae las variables 3D y escalonadas que hacían falta para
explicar la grilla y la rotación del viento.

**Observaciones.** Salen de los mensajes SYNOP de OGIMET, decodificados
con `pymetdecoder` para tener temperatura, viento y precipitación hora por
hora (`data/obs/*_horario.csv`). Los scripts que los generan son
`data/h1_ogimet.py`, `h2_procesa_horario.py` y `h3_junta_mensual.py`, y
`data/h0_datos_ogimet.sh` los corre en orden para un rango de fechas. No
son contenido del curso; están por si quieren conseguir otras
observaciones.

**Resultados.** Con 143 pares estación-hora (6 estaciones × 24 horas,
menos algún reporte faltante), WRF y ERA5-Land se comparan con la misma
observación:
- **Temperatura:** ERA5-Land tiene menor sesgo (0,37 frente a 1,28 °C),
  menor RMSE (1,78 frente a 2,39 °C) y mayor r (0,81 frente a 0,76). El
  WRF tiene mayor KGE agregado (0,75 frente a 0,69), pero ese valor está
  inflado por juntar estaciones; estación por estación pierde en casi
  todas.
- **Viento:** ninguno de los dos sigue bien el patrón horario (r entre
  0,18 y 0,37). Se valida la velocidad y no la dirección, porque la
  dirección es circular (359° y 1° están cerca) y `calcular_r` o
  `calcular_kge` darían cualquier cosa.
- **Precipitación horaria:** `RAINC`/`RAINNC` del WRF y `tp` de ERA5-Land
  vienen acumulados (con reinicio diario) y se pasan a lluvia horaria con
  `.diff()`. Solo Salto reporta lluvia de 1 h (23 pares), y con esa
  muestra r sale bajo o negativo para los dos. La lluvia puntual y horaria
  es lo más difícil de validar, también para los modelos operativos.

El diagrama de Taylor de temperatura (Salto, n = 24) está en
`03_practica_dia9_taylor_addedvalue.ipynb`; esta tabla con las 6
estaciones lo complementa.

## Recursos sugeridos

- Taylor, K. E. (2001), *Summarizing multiple aspects of model performance
  in a single diagram*, J. Geophys. Res. El artículo original del
  diagrama.
- Gupta, H. V. et al. (2009), *Decomposition of the mean squared error and
  NSE performance criteria*. El origen del KGE.
- Documentación de Pandas: *GroupBy* y *DataFrame*, para la tabla
  resumen.

## Siguiente módulo

[Módulo 6 — Pipeline integrado](../modulo_06_pipeline_integrado/README.md):
juntamos las funciones de descarga (Módulo 3), de gráficos (Módulo 4) y de
validación (este módulo) en un solo pipeline.
