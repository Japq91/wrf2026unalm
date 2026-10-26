# Módulo 1 — Python básico para ciencias atmosféricas

[Índice del curso](../README.md)

**Ubicación en el curso:** Días 1–2 de 10 · **Carga horaria:** 10 h (2 h teoría + 3 h práctica por día)
**Precede a:** [Módulo 2 — Formatos de datos atmosféricos](../modulo_02_formatos_datos_atmosfericos/README.md)

## Objetivo del módulo

Al finalizar el módulo, el participante podrá escribir programas Python correctos y
organizados (variables, control de flujo, funciones, scripts) y usar las librerías
científicas base (NumPy, Pandas, Xarray, Matplotlib) para representar y graficar
series de datos numéricos. Este módulo no toca todavía archivos NetCDF —eso es el
Módulo 2—, pero sí introduce la *forma* en que esos datos se van a representar
(arreglos N-dimensionales etiquetados), usando mediciones **reales** de 5
estaciones automáticas de SENAMHI en Lima (marzo de 2025, carpeta
[`data/senamhi/`](../../data/senamhi/README.md)).

## Por qué este módulo importa para el WRF

Todo lo que el curso hace después —descargar ERA5, leer `wrfout`, calcular un
RMSE— es, en el fondo, manipular arreglos numéricos con metadatos (tiempo,
latitud, longitud, nivel vertical). Si el fundamento de Python y de NumPy/Xarray
no está firme, cada módulo posterior se vuelve una colección de recetas
copiadas sin entender por qué funcionan. Este módulo construye ese fundamento.

## Prerrequisitos específicos

Los generales del curso ([¿Para quién es este curso?](../../README.md#para-quién-es-este-curso))
y la guía [`antes_del_curso.md`](../../antes_del_curso.md) completada: entorno
`wrf2026` creado y Jupyter funcionando. No se asume experiencia previa en
programación, pero sí moverse por carpetas en la terminal; si el
participante ya sabe Python, el día 1 sirve como nivelación rápida y el día
2 sí introduce contenido nuevo (Xarray).

---

## Día 1 — Entorno de trabajo y sintaxis esencial

### Teoría (2 h)

**1. Cómo corre Python y por qué usamos entornos (~25 min)**
Python ejecuta el código línea por línea, en el momento. Por eso en Jupyter
se puede probar de a poco y ver el resultado al instante. (El WRF, en
cambio, está escrito en Fortran: se traduce completo a lenguaje de máquina
antes de correr, lo que lo hace muy rápido pero menos cómodo para
explorar.)

Las librerías de Python cambian con el tiempo, y un proyecto puede
necesitar una versión que rompe otro. Un **entorno** es como una caja de
herramientas separada para cada proyecto: lo que se instala en una caja no
toca a las demás. En el curso usamos una caja llamada `wrf2026`, distinta
de `base` (la que trae Miniconda por defecto).

**¿Por qué instalar desde `environment.yml`?** Porque es la lista exacta de
librerías y versiones del curso: con un solo comando cada participante obtiene
el mismo entorno con el que se probaron los notebooks, y se evitan los errores
de "a mí sí me funciona". Más detalle en [Para profundizar](#para-profundizar).

**2. Tipos de datos y el modelo de variables en Python (~25 min)**
- Tipos primitivos: `int`, `float`, `str`, `bool`. Un `float` no es exacto
  (`0.1 + 0.2 != 0.3`), por eso los resultados numéricos se comparan con una
  tolerancia (`np.isclose`), nunca con `==`.
- Una variable es una **etiqueta pegada a un dato**, no una caja que lo
  guarda. Si se hace `b = a` con una lista, `a` y `b` son dos etiquetas
  sobre la **misma** lista: cambiar `b` también cambia `a`. Es un error
  común al empezar; para tener una copia independiente se usa
  `b = a.copy()`.

**3. Estructuras de datos: listas y diccionarios (~30 min)**
- Listas: colecciones ordenadas que se pueden modificar. Se cubre cómo
  tomar un elemento (`datos[2]`) o un tramo (`datos[2:5]`), y por qué el indexado por posición es frágil para datos
  con significado físico (p. ej. "la temperatura del día 3" es más claro
  como `temperaturas["2026-01-03"]` que como `temperaturas[2]`).
- Diccionarios: estructura clave–valor, la forma natural de, por ejemplo,
  mapear nombres de estaciones meteorológicas a sus coordenadas
  (`coords["Lima"]`).
- Anidamiento: listas de diccionarios como forma simple de representar
  varios registros (ej. una lista de estaciones, cada una con su propio
  diccionario de metadatos).

**4. Flujos de control e iteración (~20 min)**
- Condicionales (`if`/`elif`/`else`) como forma de codificar reglas físicas
  simples (p. ej. clasificar precipitación en categorías según umbrales
  en mm).
- Bucles `for` y `while`, y la noción de iterar sobre una colección en vez
  de controlar un índice manualmente (`for temp in temperaturas` en vez de
  `for i in range(len(temperaturas))` cuando no se necesita el índice).

**5. Funciones y organización de scripts (~20 min)**
- Una función es una receta con nombre: recibe ingredientes (entradas),
  hace algo y devuelve un resultado. Se escribe una vez y se usa muchas,
  sin copiar código. En los módulos 3 a 5 cada tarea (descargar, graficar,
  validar) será una función.
- Lo que se crea dentro de una función se queda dentro: una variable
  definida ahí no existe afuera. Así una función no altera por accidente el
  resto del programa.
- Organización de un script `.py` vs. un notebook `.ipynb`: cuándo conviene
  cada uno (exploración interactiva vs. código reproducible/automatizable).

### Práctica (3 h)

1. **Revisión del entorno (30 min).** El repositorio ya está clonado y el
   entorno ya está creado desde el
   [`environment.yml`](../../environment.yml) (guía
   [`antes_del_curso.md`](../../antes_del_curso.md)). **No se repite
   `conda env create`**: si alguien no lo hizo, lo hace ahora siguiendo
   esa guía. Se activa el entorno y se verifica que quedó bien:
   ```bash
   cd wrf2026unalm
   conda activate wrf2026
   ```
   Verificación de que el entorno quedó bien creado y activo:
   ```bash
   conda env list        # wrf2026 debe aparecer marcado como el entorno activo
   python -c "import numpy, pandas, xarray, matplotlib; print('OK')"
   jupyter lab            # debe abrir usando el intérprete de wrf2026, no el de base
   ```
   **Al empezar cada clase**, trae el material nuevo del curso desde la
   carpeta del repositorio:
   ```bash
   git pull
   ```
   `git clone` descarga el repositorio una sola vez; `git pull` trae solo
   lo que cambió desde la última vez. Para que `git pull` no choque con
   tus cambios, trabaja siempre en una copia de cada notebook con el sufijo
   `_mio` (*File → Save Notebook As…*, en la misma carpeta; ver
   `antes_del_curso.md`, sección 5). Si el `environment.yml` cambió, el
   entorno se actualiza con `conda env update -f environment.yml --prune`,
   sin recrearlo.
2. **Ejercicio guiado — tipos y estructuras (45 min).** A partir de una
   lista de temperaturas horarias reales (Von Humboldt, La Molina, 14 de
   marzo de 2025), que primero se lee del archivo de SENAMHI con `open()` y
   `split(";")`, el participante calcula manualmente (sin NumPy todavía) el promedio, el
   máximo, el mínimo y cuántas horas superaron un umbral, usando solo
   listas, bucles y condicionales. El objetivo es sentir el costo de hacer
   esto sin librerías vectorizadas, para apreciar por qué NumPy existe
   (se retoma el día siguiente).
3. **Ejercicio guiado — diccionarios anidados (45 min).** Se construye un
   diccionario con las 5 estaciones de SENAMHI, cada una con nombre,
   coordenadas (lat/lon), altura y sus 24 temperaturas del mismo día.
   El participante escribe funciones para: (a) encontrar la estación con
   la temperatura promedio más alta, (b) filtrar estaciones dentro de un
   rango de altura, (c) imprimir un resumen formateado por estación.
   Después recorre el mes completo buscando los huecos: horas con `S/D`
   («sin dato») y horas que faltan en el archivo.
4. **Ejercicio autónomo — mini-script de clasificación (45 min).**
   Escribir un script `.py` (no notebook) que sume la lluvia de cada hora
   de una estación (por defecto Ñaña) y clasifique cada día como "sin lluvia",
   "llovizna", "moderada" o "fuerte" según umbrales dados, usando una
   función `clasificar_precipitacion(valor)` reutilizable, que además
   devuelve "sin dato" cuando no hay medición. Se ejecuta desde la
   terminal, reforzando la diferencia script/notebook vista en teoría. Spoiler
   real: en marzo casi no llueve en Lima.
5. **Cierre y dudas (15 min).**

En el notebook, cada ejercicio trae un **📘 ejemplo resuelto** (otra
estación u otro día) y un **✍️ tu turno** que el participante escribe, con
una celda **✔️ comprobar** que le dice si su resultado es correcto.

**Entregable del día**, en la carpeta `notebooks/` del módulo (así las
rutas a `data/` siguen funcionando): tu copia `02_practica_dia1_mio.ipynb`
con las comprobaciones en ✅, el script `clasificar_precipitacion.py` y tu
script `temperatura_maxima_mio.py`.

---

## Día 2 — NumPy, Xarray (introducción), Pandas y Matplotlib

> **Recordatorio antes de empezar:** si se abrió una terminal nueva desde
> el Día 1 (por ejemplo, al reiniciar la computadora), hay que activar de
> nuevo el entorno antes de abrir Jupyter — la activación **no** queda
> guardada entre sesiones de terminal distintas:
> ```bash
> conda activate wrf2026
> jupyter lab
> ```
> Este recordatorio se repite al inicio de cada módulo del curso, porque es
> el error de configuración más común entre quienes recién empiezan a usar
> entornos Conda.

### Teoría (2 h)

**1. Por qué vectorizar: NumPy frente al Python puro (~30 min)**
Se retoma el ejercicio del día 1 (calcular estadísticas sobre una lista con
bucles) y se muestra la misma operación con un arreglo NumPy: más corta de
escribir y órdenes de magnitud más rápida sobre grillas de cientos de miles
de puntos, como una grilla del WRF (el porqué, en
[Para profundizar](#para-profundizar)).
- Un arreglo tiene una **forma** (`shape`): cuántos datos hay en cada
  dirección. Una grilla de 24 horas × 30 latitudes × 40 longitudes tiene
  forma `(24, 30, 40)`.
- Tomar partes de un arreglo: `arr[:, 0]` (todas las filas, primera
  columna), `arr[1:3, :]` (filas 1 y 2, todas las columnas).
- **Broadcasting**: NumPy "estira" el arreglo más chico para que calce con
  el más grande, sin bucles. Ejemplo: restar a cada nivel de una grilla
  `(niveles, lat, lon)` una corrección distinta por nivel. El perfil de
  corrección tiene 5 valores; para que NumPy sepa que van por nivel, se le
  da la forma `(5, 1, 1)` con `correccion[:, np.newaxis, np.newaxis]`, y
  NumPy repite cada valor en toda su capa.
- Resumir datos: `mean`, `std`, `max`, `min`. El parámetro `axis` dice
  **qué dirección se aplasta** al resumir: en una grilla
  `(tiempo, lat, lon)`, `mean(axis=0)` promedia el tiempo y deja un mapa;
  `mean(axis=(1, 2))` promedia el espacio y deja una serie de tiempo.

**2. Introducción a Xarray: arreglos con nombre (~35 min)**
Se motiva el problema que Xarray resuelve: un arreglo NumPy de forma
`(24, 30, 40)` no dice, por sí mismo, si esos ejes son (tiempo, lat, lon)
o (nivel, lat, lon) o cualquier otra combinación — hay que recordarlo
mentalmente o llevar la cuenta en comentarios, lo cual es frágil y es una
fuente común de errores silenciosos al analizar datos de modelos.
- `DataArray`: un arreglo NumPy + nombres de dimensión + coordenadas +
  atributos (metadatos como unidades). Se construye uno desde cero con
  los datos de SENAMHI (`temperatura` indexada por `tiempo` y `estacion`) para
  fijar el concepto antes de ver un NetCDF real en el Módulo 2.
- `Dataset`: una colección de `DataArray` que comparten dimensiones,
  análogo a una tabla con varias columnas pero en N dimensiones.
- Indexado por **nombre** (`.sel(tiempo="2026-01-15")`) frente a indexado
  por **posición** (`.isel(tiempo=0)`) — esta distinción es la que se va a
  usar constantemente desde el Módulo 2 en adelante.
- Por qué esto importa para WRF: adelantar (sin profundizar todavía, eso es
  Módulo 2) que un archivo `wrfout` es exactamente esta clase de estructura
  con dimensiones `Time`, `bottom_top`, `south_north`, `west_east`.

**3. Pandas para series temporales (~25 min)**
- `Series` y `DataFrame` como estructuras para datos tabulares e indexados
  en el tiempo — el formato natural de, por ejemplo, un registro horario de
  una estación meteorológica.
- `DatetimeIndex`: por qué usar fechas reales como índice (en vez de un
  entero) habilita operaciones como seleccionar "todo enero" o "cada
  medianoche" de forma declarativa.
- `resample`: agregación temporal (de horario a diario, de diario a
  mensual) — se explica como una generalización de `groupby` sobre
  intervalos de tiempo, y se anticipa que se volverá a usar al procesar
  datos de estaciones en el Módulo 5.

**4. Matplotlib: el modelo Figure/Axes (~20 min)**
- Diferencia entre una `Figure` (el lienzo) y un `Axes` (el sistema de
  ejes donde se dibuja) — entender este modelo evita la confusión típica
  de principiantes con `plt.plot` "mágico" y permite construir figuras con
  varios paneles más adelante (Módulo 4).
- Gráfico de línea simple y gráfico de dispersión, con etiquetas de ejes y
  título — el mínimo indispensable para que una figura sea interpretable
  científicamente.
- **Múltiples paneles con `plt.subplots(nrows, ncols)`:** `fig, axes =
  plt.subplots(1, 2, figsize=(...))` devuelve una `Figure` y un arreglo de
  `Axes` — cada panel se dibuja llamando al método correspondiente sobre
  `axes[i]` en vez de sobre un único `ax`. Se presenta acá, brevemente,
  porque el ejercicio de cierre de este mismo día (integración de las 4
  librerías) ya arma una figura de 2 paneles, y porque es exactamente el
  patrón que se reutiliza en el Módulo 4 para mapa + serie temporal lado a
  lado.

**5. Cierre y repaso antes de la práctica (~10 min)**
Repaso rápido de cómo encajan las cuatro librerías del día — NumPy para el
cálculo vectorizado de base, Xarray para darle nombre a los ejes de ese
cálculo, Pandas para el eje temporal, Matplotlib para comunicarlo — y
preguntas abiertas antes de pasar a la práctica. Se adelanta que el Módulo
2 retoma `Dataset` de Xarray, pero ahora leído desde un archivo NetCDF/GRIB
real, no construido a mano.

### Práctica (3 h)

1. **De bucles a NumPy (30 min).** Reescribir el ejercicio de estadísticas
   del día 1 (promedio, máximo, mínimo, conteo sobre umbral) usando
   arreglos NumPy en lugar de bucles, y comparar la longitud y claridad del
   código resultante.
2. **Broadcasting con sentido físico (30 min).** Dado un arreglo inventado
   de temperatura (todavía no leemos un WRF) con forma `(niveles=5, lat=10, lon=10)` y un perfil de
   corrección vertical de forma `(5,)`, aplicar la corrección a toda la
   grilla usando broadcasting, y verificar el resultado comparando un punto
   específico contra el cálculo manual.
3. **Primer `DataArray` y `Dataset` desde cero (45 min).** Construir un
   `Dataset` de Xarray con los datos de SENAMHI: 5 estaciones × 72 horas
   (temperatura y humedad relativa), con coordenadas `estacion` y `tiempo`, y
   practicar selección por nombre (`.sel`) y por posición (`.isel`),
   además de un promedio por estación y un promedio temporal.
4. **Serie temporal con Pandas (45 min).**
   **(a)** Tomar la serie horaria de marzo completo de una estación y usar `resample("1D").mean()` y `resample("1ME").max()`
   para obtener promedios diarios y máximos mensuales; graficar la serie
   horaria original y la diaria resampleada en el mismo `Axes`, con
   leyenda.
   **(b) Refuerzo:** repetir el ejercicio partiendo esta vez del CSV de
   SENAMHI leído «crudo»: la fecha llega como **texto** repartido en 4
   columnas (`Año`, `Mes`, `Día`, `Hora`) y los faltantes como `S/D` —
   juntarlas y convertirlas explícitamente con `pd.to_datetime()`, pasar
   `S/D` a `NaN` con `pd.to_numeric(..., errors="coerce")` y fijarla como índice con `.set_index()` antes de
   poder usar `resample()`, esta vez con una frecuencia distinta
   (`resample("7D")`, min/max semanal). Este paso existe porque en (a)
   la función `leer_senamhi()` hizo ese trabajo sin que lo viéramos.
5. **Cierre e integración (30 min):** cada participante construye un
   notebook único que combina las cuatro librerías (NumPy para el cálculo
   base, Xarray para estructurar los datos con nombre, Pandas para el
   manejo temporal, Matplotlib para la figura final), como ensayo general
   del tipo de flujo que se repetirá en cada módulo siguiente.

**Entregable del día:** tu copia `03_practica_dia2_mio.ipynb` con las
comprobaciones en ✅, y tu copia de
[`04_entregable_integrador.ipynb`](notebooks/04_entregable_integrador.ipynb)
con la sección 7 (el mismo flujo, escrito por ti, para la humedad
relativa) y el archivo `entregable_modulo1_mio.nc`.

---

## Cierre del módulo

**Checkpoint (no evaluado formalmente, sí revisado en clase):** cada
participante debe poder explicar, en sus propias palabras, la diferencia
entre indexar por posición y por nombre en Xarray, y por qué esa distinción
va a ser importante al trabajar con archivos NetCDF reales. Esta pregunta se
retoma como gancho de apertura del Módulo 2.

<details>
<summary><strong>Respuesta esperada</strong> (ábrela después de intentarlo)</summary>

`.isel(tiempo=0)` elige por **posición** (el primer elemento, sea cual sea su
fecha); `.sel(tiempo="2026-01-15")` elige por **valor de la coordenada**. Con
archivos reales la posición no es confiable: dos archivos pueden empezar en
fechas distintas, tener otro orden de latitudes (norte→sur o sur→norte) o
un recorte diferente, y `isel` devolvería otro dato sin dar ningún error.
`sel` busca lo que se pidió por su nombre, así que el código sigue siendo
correcto aunque cambie el archivo.
</details>

## Preguntas frecuentes

**Instalé el entorno pero `jupyter lab` abre y no encuentra `numpy`. ¿Qué
pasó?**
Casi siempre es que Jupyter se abrió con el entorno equivocado activo (por
ejemplo, `base` en vez de `wrf2026`). Cerrar Jupyter, confirmar en la
terminal que aparece `(wrf2026)` al inicio de la línea de comandos
(ejecutando `conda activate wrf2026` si no aparece), y recién ahí volver a
ejecutar `jupyter lab`. Si el problema persiste, `conda env list` muestra
todos los entornos existentes y cuál está activo (marcado con un asterisco).

**¿Por qué a veces se usa un notebook (`.ipynb`) y otras veces un script
(`.py`)?**
Un notebook es mejor para explorar datos paso a paso, ver resultados
intermedios (tablas, gráficos) y documentar el razonamiento junto al
código. Un script es mejor para lógica que se va a reutilizar o ejecutar
repetidamente sin supervisión (por ejemplo, desde otro programa, o
programado para correr cada noche). En este curso, los notebooks se usan
para practicar y explorar, mientras que la lógica que se vuelve
"definitiva" migra a scripts `.py` a partir del Módulo 3 — anticipando el
patrón que se formaliza en el Módulo 6.

**¿Necesito memorizar la fórmula de broadcasting o las reglas exactas de
NumPy?**
No. Lo que sí conviene interiorizar es la intuición: una operación entre
arreglos de formas distintas solo funciona si, comparando de derecha a
izquierda, cada par de dimensiones es igual o una de ellas vale 1. Frente a
un error de broadcasting, imprimir `.shape` de cada arreglo involucrado
suele ser más rápido que intentar recordar la regla de memoria.

**¿Xarray reemplaza a NumPy y Pandas, o los tres se usan juntos?**
Se usan juntos. Xarray está construido *sobre* NumPy (cada `DataArray`
contiene, por dentro, un arreglo NumPy) y toma prestadas varias ideas de
Pandas (como el manejo de índices con nombre). En la práctica: NumPy para
cálculo numérico puro, Pandas para datos tabulares/series temporales de una
o dos dimensiones, Xarray cuando hay tres o más dimensiones con nombre
(como en casi todos los datos atmosféricos del resto del curso).

**Si no tengo experiencia previa programando, ¿este ritmo (2 días) alcanza?**
El Día 1 está diseñado para no asumir experiencia previa, y el Día 2
avanza más rápido apoyándose en lo aprendido el Día 1. Aun así, es normal
sentir que dos días es poco tiempo para todo lo cubierto — no se espera
memorizar sintaxis, sino reconocer los patrones al verlos de nuevo en los
módulos siguientes, donde se reutilizan constantemente sobre datos reales.

## Para profundizar

Material opcional: no hace falta para la práctica ni para el proyecto final.

### Por qué un `environment.yml` versionado

`environment.yml` es una lista exacta y versionada de qué necesita el
proyecto (nombre del entorno, canal de paquetes, cada librería y —cuando
hace falta— su versión). Todo el material del curso (este repositorio
`wrf2026unalm`) vive en GitHub, y ese archivo vive junto al código, no en la
cabeza del instructor ni en una guía aparte. Esto tiene tres consecuencias
prácticas, no solo de comodidad:
- **Reproducibilidad:** el entorno que arma un participante el día 1 es
  *exactamente* el mismo (mismas versiones) que el que usó el instructor
  para preparar y probar cada notebook del curso. Instalar "a mano" paquete
  por paquete casi garantiza pequeñas diferencias de versión entre
  computadoras, que después se manifiestan como errores difíciles de
  reproducir ("a mí sí me funciona").
- **Una sola fuente de verdad:** si el curso agrega una librería nueva
  (como pasó aquí con varias herramientas específicas de meteorología), el
  cambio se hace una vez en `environment.yml` dentro del repositorio, y
  cada participante simplemente vuelve a sincronizar su entorno — no hay
  que re-explicar manualmente qué instalar.
- **Onboarding de un solo comando:** en vez de una lista de instrucciones
  para copiar y pegar librería por librería (con riesgo de saltarse una o
  instalar la versión equivocada), la instalación completa se reduce a
  clonar el repositorio y ejecutar `conda env create`, como se hace en la
  práctica de este mismo día.

### Por qué `0.1 + 0.2 != 0.3`

Python guarda los `float` en el estándar IEEE 754 de doble precisión, en
base 2. Números como 0.1 no tienen representación binaria exacta (igual que
1/3 en base 10), así que se guardan redondeados y el error aparece al
operar. Por eso, al comparar la salida del WRF con un valor esperado, se usa
una tolerancia (`np.isclose(a, b)` o `abs(a - b) < 1e-6`) y no `==`.

### Diccionarios frente a listas: costo de búsqueda

Buscar un elemento en una lista obliga a recorrerla (tiempo O(n): el doble
de elementos, el doble de tiempo). Un diccionario usa una tabla hash y
encuentra la clave en tiempo promedio constante, O(1), tenga 10 o 10 000
estaciones.

### Por qué NumPy es más rápido que un bucle

Un bucle `for` en Python puro revisa el tipo de cada elemento en cada
iteración, porque Python es de tipado dinámico. Un arreglo NumPy guarda
datos de un solo tipo en un bloque contiguo de memoria y aplica la
operación en código C compilado. La diferencia es de uno a dos órdenes de
magnitud sobre grillas como las del WRF.

## Recursos sugeridos

- Documentación oficial de NumPy — *Quickstart* y *Broadcasting*.
- Documentación oficial de Xarray — *Data Structures*.
- Wes McKinney, *Python for Data Analysis* (capítulos de Pandas/series
  temporales) — lectura opcional de referencia, no obligatoria.

## Siguiente módulo

[Módulo 2 — Formatos de datos atmosféricos](../modulo_02_formatos_datos_atmosfericos/README.md):
se retoma la estructura `Dataset` vista aquí, pero ahora sobre archivos
NetCDF y GRIB reales, con sus convenciones (CF) y metadatos propios de
ciencias atmosféricas.
