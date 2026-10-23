# Módulo 5 — Validación de resultados del WRF

[Índice del curso](../README.md)

**Ubicación en el curso:** Días 8–9 de 10 · **Carga horaria:** 10 h (2 h teoría + 3 h práctica por día)
**Precede a:** [Módulo 6 — Pipeline integrado](../modulo_06_pipeline_integrado/README.md)
**Requiere:** [Módulo 4 — Lectura y visualización de salidas WRF](../modulo_04_lectura_visualizacion_wrf/README.md)

## Objetivo del módulo

Al finalizar el módulo, el participante podrá comparar cuantitativamente una
simulación del WRF contra observaciones, usando un conjunto de métricas
estadísticas complementarias (no una sola), entendiendo qué aspecto del
error mide cada una, y podrá automatizar ese cálculo para múltiples
variables y estaciones a la vez.

## Por qué este módulo importa para el WRF

Un mapa bonito (Módulo 4) no demuestra que la simulación sea correcta. La
pregunta que responde este módulo —**¿qué tan bien reproduce el WRF la
realidad observada, y mejora algo respecto a los datos que lo forzaron?**—
es la que finalmente le da valor científico al resto del pipeline. Sin esta
etapa, todo lo anterior es solo procesamiento de datos; con ella, se
convierte en evidencia.

## Prerrequisitos específicos

Haber completado el Módulo 4 (productos derivados exportados a NetCDF,
usados aquí como el lado "simulado" de la comparación) y el Módulo 2
(interpolación espacial).

## Antes de empezar: activar el entorno

```bash
conda activate wrf2026
jupyter lab
```
Este módulo no necesita librerías nuevas.

---

## Día 8 — Interpolación a observaciones y métricas de error

### Teoría (2 h)

**1. Tipos de datos observacionales y una advertencia de circularidad (~25 min)**
- **Estaciones meteorológicas superficiales:** medición directa en un punto,
  alta confiabilidad puntual pero cobertura espacial limitada (no dicen nada
  del punto de grilla vecino).
- **Datos satelitales:** cubren grandes áreas, pero no miden la variable
  directamente: la estiman a partir de la radiación que capta el satélite,
  así que tienen su propio error (y huecos por nubes o por la hora en que
  pasa el satélite).
- **Reanálisis como referencia:** útil cuando no hay observaciones directas
  disponibles, pero con una **advertencia conceptual importante**: si el
  WRF fue forzado con ERA5 (Módulo 3), usar el propio ERA5 como "verdad" para
  validar el WRF es parcialmente circular — no es una fuente independiente.
  Esto no invalida su uso, pero cambia la pregunta: ya no es "¿el WRF es
  correcto?" sino "¿el WRF agrega algo frente a su propio forzante?" — la
  pregunta que se retoma formalmente el Día 9 como *added value*.

**2. Interpolar el modelo al punto de observación (~15 min)**
Se reutiliza explícitamente la interpolación bilineal del Módulo 2, ahora en
la dirección opuesta a la del Módulo 4: en vez de extraer una serie en el
punto de grilla *más cercano* a una ciudad, aquí se interpola (no solo se
selecciona el vecino más próximo) la salida del WRF a la coordenada *exacta*
de la estación, porque la estación casi nunca coincide con un nodo de
grilla. Se decide entre `.sel(method="nearest")` e `.interp(method="linear")`
según qué tan suave sea la variable en el espacio (temperatura: interpolar;
precipitación convectiva, muy heterogénea espacialmente: el vecino más
cercano puede ser más honesto que "inventar" un valor intermedio).

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
- **r** solo mira la forma de la curva: un modelo que reproduce el ciclo
  diurno perfecto pero 5 °C más caliente tiene r = 1. Por eso **ninguna
  métrica sola alcanza**.
- **KGE** junta tres revisiones en un solo número: ¿sigue el patrón? (r),
  ¿acierta el promedio? (β, promedio del modelo entre el observado) y
  ¿acierta la amplitud de las subidas y bajadas? (α, variabilidad del
  modelo entre la observada). Si el KGE sale bajo, mirar r, β y α por
  separado dice cuál de los tres falla.

Las fórmulas escritas, en [Para profundizar](#para-profundizar).

Una pregunta que surge casi siempre en este punto: *"¿cuál de todas reporto
si solo puedo mostrar una métrica?"* La respuesta corta es que no conviene
reportar una sola: como mínimo, una medida de error absoluto (RMSE o MAE) y
una medida de patrón (r o, mejor, KGE) juntas. Reportar solo r puede
esconder un sesgo grande; reportar solo RMSE no dice si el error es
sistemático o aleatorio. Esta idea —nunca una métrica sola— es el hilo
conductor del resto del módulo.

### Práctica (3 h)

1. **Carga de observaciones (30 min).** Leer con Pandas la observación real
   horaria de una estación de Perú (decodificada de mensajes SYNOP,
   `data/obs/Lima_2024_12_13_horario.csv`), construir su `DatetimeIndex`
   (retomando el Módulo 1) y graficar la serie cruda para inspección
   visual. Este ejercicio es de carga pura — no requiere correspondencia
   con el dominio del WRF.
2. **Interpolación del WRF al punto de estación (40 min).** El dominio real
   del WRF no cubre Perú, así que de acá en adelante se cambia a una
   estación real dentro del dominio (Salto, Uruguay). Usando el `wrfout`
   real de **día completo** (`data/grid_muestra/wrfout_muestra.nc`, 24
   pasos horarios), se toma el punto de grilla más cercano a las
   coordenadas reales de la estación y se comparan las 24 horas del WRF
   contra la observación real de esas mismas horas.
3. **Cálculo manual de métricas (50 min).** Implementar como funciones
   propias (no usar directamente una librería que ya las calcule, para
   fijar la fórmula) `calcular_mae`, `calcular_rmse`, `calcular_bias`,
   `calcular_r` y `calcular_kge`, aplicarlas al par de series alineadas
   (n=24), e interpretar el resultado por escrito en el notebook: ¿el
   modelo está sesgado?, ¿qué tan bien sigue el ciclo diurno?
4. **Caso de contraste (30 min).** Se comparan dos fuentes reales contra la
   misma observación (WRF y ERA5-Land en Salto, día completo) — con datos
   reales el RMSE no sale igual entre ambas, pero eso no es lo importante:
   los dos modelos tienen sesgos parecidos en signo y magnitud, pero fallan
   en direcciones OPUESTAS en variabilidad (`alpha`) — uno sobre-dispersa
   el ciclo diurno, el otro lo aplana — algo invisible si solo se mira RMSE
   o bias. El participante calcula KGE para ambas fuentes y explica en una
   frase la diferencia física entre los dos casos.
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

Si el WRF tiene mejores métricas, su mayor resolución está captando algo
local que el modelo global no ve (relieve, brisas, lluvia por montaña). Si
no las tiene, no es un error: para esa variable y ese lugar, el WRF no está
aportando. Aquí el modelo global no hace de "verdad" (eso sería la
circularidad del Día 8); hace del competidor contra el que se compara el WRF.

**2. Diagramas de Taylor: tres métricas en un solo gráfico (~45 min)**
Comparar varios modelos con tres tablas de números es difícil de un
vistazo. El diagrama de Taylor pone a cada modelo como un punto en un
cuarto de círculo, y la observación como un punto de referencia sobre el
eje horizontal. Se lee así:

- **Distancia al centro:** cuánto varía el modelo (su desviación estándar).
  Lo ideal es que esté a la misma distancia que la observación.
- **Ángulo:** la correlación. Cuanto más cerca del eje horizontal, más alta.
- **Distancia al punto de la observación:** el error (RMSE centrado). El
  mejor modelo es el punto más cercano a la observación.

Que esas tres cosas encajen en un mismo dibujo no es casualidad: sale de la
ley de cosenos (detalle en [Para profundizar](#para-profundizar)).

**3. Automatizar el cálculo para múltiples variables y periodos (~30 min)**
Se diseña una función `evaluar_variable(variable, estaciones, periodo)` que
recorre una lista de estaciones y/o variables, aplica para cada una el flujo
completo del Día 8 (alinear, calcular métricas), y acumula los resultados en
un `DataFrame` de Pandas (una fila por combinación estación–variable, una
columna por métrica) en vez de repetir el análisis manualmente por cada
caso — cerrando el ciclo de automatización que empezó en el Módulo 3 con la
descarga.

**4. Comunicar resultados: tablas resumen (~20 min)**
Buenas prácticas mínimas para una tabla de validación presentable:
ordenar por la métrica más relevante para el caso de uso, redondear a un
número razonable de decimales según la magnitud física de la variable, y
acompañar siempre RMSE/MAE de r o KGE — nunca reportar una sola métrica de
error sin una medida de patrón, por la razón discutida el Día 8.

### Práctica (3 h)

1. **Opcional, si sobra tiempo — un punto del diagrama a mano.**
   Con las métricas ya calculadas el Día 8 para la estación de muestra
   ($\sigma_s$, $\sigma_o$, $r$), verificar a mano (con una celda de
   código, aplicando la fórmula de la teoría) que la distancia calculada
   por ley de cosenos coincide con el RMSE centrado calculado
   directamente sobre las series (fórmula en
   [Para profundizar](#diagrama-de-taylor-la-ley-de-cosenos)).
2. **Diagrama de Taylor con SkillMetrics (60 min).** Usando el paquete
   [`SkillMetrics`](https://github.com/PeterRochford/SkillMetrics)
   (`sm.taylor_statistics()` + `sm.taylor_diagram()`), construir un
   diagrama con **una estación real como referencia** (Salto) y **los dos
   modelos reales a comparar** (WRF y ERA5-Land) — 3 puntos en total: 1 de
   referencia + 2 de modelo. `sm.taylor_statistics()` calcula σ, RMSD
   centrado y r por ti. Las 5 estaciones
   restantes del dominio (Ezeiza, Rosario, Resistencia, Iguazú, Carrasco)
   quedan para la práctica dirigida: cada participante/grupo repite el
   mismo diagrama con la estación que le toque.
3. **Cálculo de added value (50 min).** Para la misma estación de
   referencia (Salto), repetir la comparación del Día 8 pero usando
   ERA5-Land real interpolado en lugar del WRF, calcular las mismas
   métricas, y construir una tabla comparativa WRF-vs-obs frente a
   ERA5-Land-vs-obs que responda explícitamente si hay evidencia de valor
   añadido para esa variable.
4. **Automatización multi-estación (50 min).** Implementar
   `evaluar_variable()` según el diseño de la teoría, ejecutarla sobre las
   6 estaciones reales del dominio del WRF, y exportar la tabla resultante
   a `.csv`.
5. **Cierre y dudas (20 min).**

**Entregable del módulo:** notebook `dia_09_validacion_completa.ipynb` con
el diagrama de Taylor (SkillMetrics, referencia + 2 modelos), la tabla de
*added value*, y el archivo `.csv` con la validación automatizada de todas
las estaciones.

---

## Extensión con datos reales

Todo el módulo usa datos reales. El notebook
`04_entregable_automatizacion.ipynb` agrega dos casos:

- **Un caso mal hecho a propósito:** las mismas 6 estaciones reales, pero
  con latitud y longitud intercambiadas al buscar el punto del WRF. Todas
  caen en la misma esquina del dominio, sobre el mar. El código no da error
  y `r` incluso sigue alto en algunas estaciones (el ciclo de día y noche
  se parece en toda la región), pero el sesgo y el KGE delatan el problema:
  sin correspondencia real de lugar, la validación no significa nada. Se
  cierra con una función que avisa cuando el punto encontrado queda lejos.
- **El caso bien hecho:** 6 aeropuertos de Argentina y Uruguay dentro del
  dominio, con observación hora por hora, comparando WRF y ERA5-Land contra
  la misma observación (143 pares). En temperatura, ERA5-Land gana en
  sesgo, MAE, RMSE y r, pero el WRF gana en KGE (0.75 frente a 0.69): las
  métricas no siempre coinciden, y por eso se reportan varias. En viento
  ninguno de los dos acierta bien el patrón horario, y la lluvia por hora
  es lo más difícil de validar.

Cómo se obtuvieron las observaciones y los números completos, en
[Para profundizar](#para-profundizar).

**Extensión opcional (no evaluada):**
[`05_extension_opcional_peru_addedvalue.ipynb`](notebooks/05_extension_opcional_peru_addedvalue.ipynb)
repite la pregunta de *added value* fuera del dominio del WRF, con las 7
estaciones reales de Perú: ERA5-Land (9 km) vs. ERA5 estándar (31 km),
ambos reales, contra la misma observación real. Requiere haber completado
la extensión del Módulo 3, Día 5.

---

## Cierre del módulo

**Checkpoint:** el participante debe poder explicar, sin ver el notebook,
por qué un modelo puede tener r alto y KGE bajo al mismo tiempo, y qué
comparación adicional (más allá de WRF vs. observación) hace falta para
hablar de "valor añadido" de forma rigurosa.

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

**¿Por qué RMSE y MAE casi nunca coinciden con lo que veo "a ojo" en el
gráfico de la serie temporal?**
Porque son promedios sobre todo el período, mientras que el ojo tiende a
fijarse en los picos (donde el desacople suele ser más visible). Un modelo
puede verse "casi perfecto" en el gráfico durante la mayor parte del
período y tener un RMSE relativamente alto por un puñado de horas con
error grande — precisamente porque RMSE penaliza los errores grandes más
que proporcionalmente (Sección 3 de la teoría).

**Mi KGE me dio un valor negativo. ¿Hice algo mal?**
No necesariamente. A diferencia de r (acotado entre -1 y 1), KGE no tiene
un límite inferior definido — puede ser arbitrariamente negativo si $\beta$
o $\alpha$ se alejan mucho de 1, o si r es negativo. Un KGE negativo sí
indica un ajuste pobre, pero no es un error de cálculo por sí solo; conviene
revisar los tres componentes ($r$, $\beta$, $\alpha$) por separado para
entender cuál está arrastrando el valor hacia abajo.

**¿Por qué interpolar el WRF a la estación y no, al revés, "mover" la
estación al punto de grilla más cercano?**
Ambas son técnicas válidas y ya se discutieron en el Módulo 2/4
(`.sel(nearest)` vs. `.interp()`), pero interpolar el modelo a la
coordenada *exacta* de la estación evita introducir un error adicional de
posicionamiento: la estación tiene una ubicación fija y conocida, así que
lo que se ajusta es el dato del modelo (que sí varía suavemente en el
espacio), no la observación.

**Si mi caso de estudio no tiene estaciones cercanas, ¿puedo saltarme este
módulo?**
No — pero si de verdad no hay estaciones disponibles en la zona de interés,
las alternativas son (a) usar datos satelitales como referencia (con la
salvedad de que también tienen su propia incertidumbre, discutida en la
Sección 1), o (b) validar contra el propio reanálisis, dejando explícito
que en ese caso solo se puede hablar de "consistencia con ERA5", no de
validación contra una observación independiente.

**¿El diagrama de Taylor reemplaza a las tablas de métricas, o se usan
juntos?**
Se complementan. El diagrama es excelente para comparar muchas
estaciones/variables de un vistazo (patrones generales, outliers visuales),
pero no reemplaza el detalle numérico exacto de una tabla cuando hace falta
citar un valor preciso (por ejemplo, en un informe o publicación). La
práctica del Día 9 produce ambos.

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

El notebook `04_entregable_automatizacion.ipynb` usa 6 aeropuertos de Argentina y
Uruguay que sí están dentro del dominio real del WRF, con coordenadas
reales extraídas de la cabecera de cada reporte de OGIMET
(`data/ogimet/coords_area_wrf.json`), **y** el `wrfout` real de **día
completo** (`data/grid_muestra/wrfout_muestra.nc`, 24 pasos horarios del
2024-12-13 — a diferencia de `wrfout_real_muestra.nc`, usado en el Módulo
4, que solo cubre 3 horas pero sí trae las variables 3D/staggered
necesarias para las lecciones de grilla y rotación de viento). La
observación ya no viene del resumen climático diario de OGIMET, sino de
sus **mensajes SYNOP crudos** (binario `getsynop`), decodificados con
`pymetdecoder` para obtener temperatura, viento y precipitación **hora por
hora** (`data/obs/*_horario.csv`, generados por las herramientas de
preparación `data/h1_ogimet.py` → `h2_procesa_horario.py` →
`h3_junta_mensual.py`, orquestadas por `data/h0_datos_ogimet.sh` para un
rango de fechas — no son parte del contenido del curso, pero se muestran
como ejemplo de herramienta ya lista para conseguir datos observados
reales).

Con correspondencia espacial y temporal reales, **el mismo conjunto de
n=143 pares estación-hora** (6 estaciones × 24 horas, descontando algún
reporte faltante) se usa para validar WRF y ERA5-Land contra la misma
observación, dando una comparación de valor añadido completa, honesta y
con tamaño de muestra sustancial. El resultado real es instructivo
precisamente porque no está arreglado: en temperatura, ERA5-Land gana en
sesgo (0.37 vs. 1.28 °C), RMSE (1.78 vs. 2.39 °C) y r (0.81 vs. 0.76), pero
el WRF gana en KGE (0.75 vs. 0.69); en
viento, ambos mejoran algo pero ninguno reproduce bien el patrón horario
(r≈0.18–0.37) — validado por velocidad escalar, no por dirección, que es
una variable circular y rompería `calcular_r`/`calcular_kge` si se le
aplicara directo. La precipitación horaria real (`RAINC`/`RAINNC` del WRF
y `tp` de ERA5-Land, ambos acumulados con reinicio diario confirmado,
diferenciados con `.diff()` entre pasos consecutivos) solo tiene
observación de 1 h disponible en Salto (23 pares) — con esa muestra, `r`
sale bajo o negativo para ambas fuentes, un resultado real y honesto: la
precipitación puntual y horaria es el campo más difícil de validar, incluso
para modelos operativos serios. El diagrama de Taylor con `SkillMetrics`
(referencia + WRF + ERA5-Land) que resume visualmente el resultado de
temperatura se construye en `03_practica_dia9_taylor_addedvalue.ipynb`
(con Salto como referencia, n=24) — esta sección se queda con la tabla
numérica agregada (n=143) como su complemento, más robusta que un solo
punto de referencia.

## Recursos sugeridos

- Taylor, K. E. (2001), *Summarizing multiple aspects of model performance
  in a single diagram*, J. Geophys. Res. — artículo original del diagrama,
  lectura de referencia opcional.
- Gupta, H. V. et al. (2009), *Decomposition of the mean squared error and
  NSE performance criteria* — origen del KGE.
- Documentación de Pandas — *GroupBy* y *DataFrame* (para la tabla resumen
  automatizada).

## Siguiente módulo

[Módulo 6 — Pipeline integrado](../modulo_06_pipeline_integrado/README.md):
las funciones de descarga (Módulo 3), extracción/visualización (Módulo 4) y
validación (este módulo) se ensamblan en un único flujo reproducible de
principio a fin.
