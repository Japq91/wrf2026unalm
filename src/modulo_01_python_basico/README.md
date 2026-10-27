# Módulo 1 — Python básico para ciencias atmosféricas

[Índice del curso](../README.md)

**Ubicación en el curso:** Días 1–2 de 10 · **Carga horaria:** 10 h (2 h teoría + 3 h práctica por día)
**Precede a:** [Módulo 2 — Formatos de datos atmosféricos](../modulo_02_formatos_datos_atmosfericos/README.md)

## Objetivo del módulo

Al terminar el módulo, el participante podrá escribir programas cortos en
Python (variables, condicionales, bucles, funciones, scripts) y usar NumPy,
Pandas, Xarray y Matplotlib para calcular y graficar series de datos. Los
NetCDF llegan en el Módulo 2; aquí trabajamos con las mediciones de 5
estaciones automáticas de SENAMHI en Lima (marzo de 2025, carpeta
[`data/senamhi/`](../../data/senamhi/README.md)) y armamos a mano los
mismos arreglos con nombre que después vamos a leer de los archivos.

## Relación con el WRF

Descargar ERA5, leer un `wrfout` o calcular un RMSE son operaciones sobre
arreglos de números con metadatos (tiempo, latitud, longitud, nivel). Si
estas bases no quedan claras, en los módulos siguientes se termina copiando
código sin saber qué hace.

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

**¿Por qué instalar desde `environment.yml`?** Es la lista de librerías y
versiones del curso. Con un comando, cada participante tiene el mismo
entorno con el que probamos los notebooks. Más detalle en
[Para profundizar](#para-profundizar).

**2. Tipos de datos y el modelo de variables en Python (~25 min)**
- Tipos primitivos: `int`, `float`, `str`, `bool`. Un `float` no es exacto
  (`0.1 + 0.2 != 0.3`), por eso los resultados numéricos se comparan con una
  tolerancia (`np.isclose`) y no con `==`.
- Una variable es una **etiqueta pegada a un dato**, no una caja que lo
  guarda. Si se hace `b = a` con una lista, `a` y `b` son dos etiquetas
  sobre la **misma** lista: cambiar `b` también cambia `a`. Es un error
  común al empezar; para tener una copia independiente se usa
  `b = a.copy()`.

**3. Estructuras de datos: listas y diccionarios (~30 min)**
- Listas: colecciones ordenadas que se pueden modificar. Se cubre cómo
  tomar un elemento (`datos[2]`) o un tramo (`datos[2:5]`). Por posición
  es fácil equivocarse: `temperaturas["2026-01-03"]` dice más que
  `temperaturas[2]`.
- Diccionarios: pares clave–valor, por ejemplo el nombre de cada estación
  con sus coordenadas (`coords["Ñaña"]`).
- Anidamiento: una lista de diccionarios para varios registros, por
  ejemplo una lista de estaciones, cada una con sus datos.

**4. Flujos de control e iteración (~20 min)**
- Condicionales (`if`/`elif`/`else`) para escribir reglas simples, como
  clasificar la lluvia según umbrales en mm.
- Bucles `for` y `while`. Cuando no hace falta la posición, se recorre la
  colección directamente (`for temp in temperaturas`) en vez de usar un
  índice (`for i in range(len(temperaturas))`).

**5. Funciones y organización de scripts (~20 min)**
- Una función es una receta con nombre: recibe ingredientes (entradas),
  hace algo y devuelve un resultado. Se escribe una vez y se usa muchas,
  sin copiar código. En los módulos 3 a 5 cada tarea (descargar, graficar,
  validar) será una función.
- Lo que se crea dentro de una función se queda dentro: una variable
  definida ahí no existe afuera. Así una función no altera por accidente el
  resto del programa.
- Script `.py` o notebook `.ipynb`: el notebook para explorar, el script
  para lo que se va a repetir.

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
   **Al empezar cada clase**, trae el material nuevo desde la carpeta del
   repositorio:
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
2. **Tipos y estructuras (45 min).** Se leen las temperaturas horarias de
   Von Humboldt (La Molina, 14 de marzo de 2025) del archivo de SENAMHI con
   `open()` y `split(";")`. Con listas, bucles y condicionales (todavía sin
   NumPy) se calcula el promedio, el máximo, el mínimo y cuántas horas
   superaron un umbral. Mañana hacemos lo mismo con NumPy y comparamos.
3. **Diccionarios anidados (45 min).** Se construye un
   diccionario con las 5 estaciones de SENAMHI, cada una con nombre,
   coordenadas (lat/lon), altura y sus 24 temperaturas del mismo día.
   El participante escribe funciones para: (a) encontrar la estación con
   la temperatura promedio más alta, (b) filtrar estaciones dentro de un
   rango de altura, (c) imprimir un resumen formateado por estación.
   Después recorre el mes completo buscando los huecos: horas con `S/D`
   («sin dato») y horas que faltan en el archivo.
4. **Un script de clasificación (45 min).** Un script `.py` que suma la
   lluvia horaria de una estación (Ñaña, si no se indica otra) y clasifica
   cada día como "sin lluvia", "llovizna", "moderada" o "fuerte" con la
   función `clasificar_precipitacion(valor)`, que devuelve "sin dato"
   cuando no hay medición. Se ejecuta desde la terminal. Ya lo verán: en
   marzo casi no llueve en Lima.
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
> nuevo el entorno antes de abrir Jupyter. La activación **no** queda
> guardada de una terminal a otra:
> ```bash
> conda activate wrf2026
> jupyter lab
> ```
> Lo vamos a repetir al inicio de cada módulo: es el olvido más frecuente
> con Conda.

### Teoría (2 h)

**1. Por qué vectorizar: NumPy frente al Python puro (~30 min)**
Retomamos el ejercicio del Día 1 (estadísticas con bucles) y lo hacemos
con un arreglo NumPy. El código es más corto y, con cientos de miles de
puntos como en una grilla del WRF, mucho más rápido (el porqué, en
[Para profundizar](#para-profundizar)).
- Un arreglo tiene una **forma** (`shape`): cuántos datos hay en cada
  dirección. Una grilla de 24 horas × 30 latitudes × 40 longitudes tiene
  forma `(24, 30, 40)`.
- Tomar partes de un arreglo: `arr[:, 0]` (todas las filas, primera
  columna), `arr[1:3, :]` (filas 1 y 2, todas las columnas).
- **Broadcasting**: NumPy repite el arreglo más chico para que calce con
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
Un arreglo NumPy de forma `(24, 30, 40)` no dice si sus ejes son
(tiempo, lat, lon), (nivel, lat, lon) u otra cosa. Hay que recordarlo o
anotarlo en comentarios, y si nos equivocamos de eje el código corre igual
con un resultado equivocado. Xarray le pone nombre a cada eje.
- `DataArray`: un arreglo NumPy + nombres de dimensión + coordenadas +
  atributos (metadatos como unidades). Se construye uno desde cero con
  los datos de SENAMHI (`temperatura` indexada por `tiempo` y `estacion`),
  antes de abrir un NetCDF en el Módulo 2.
- `Dataset`: varios `DataArray` que comparten dimensiones, como una tabla
  con varias columnas pero en N dimensiones.
- Indexado por **nombre** (`.sel(tiempo="2026-01-15")`) frente a indexado
  por **posición** (`.isel(tiempo=0)`). Lo usaremos en todos los módulos.
- Un `wrfout` tiene esta misma estructura, con dimensiones `Time`,
  `bottom_top`, `south_north` y `west_east` (lo vemos en el Módulo 4).

**3. Pandas para series temporales (~25 min)**
- `Series` y `DataFrame`: tablas indexadas por tiempo, como el registro
  horario de una estación.
- `DatetimeIndex`: con las fechas como índice se puede pedir «todo enero» o
  «cada medianoche» sin comparar fechas a mano.
- `resample`: pasar de horario a diario o de diario a mensual. Es un
  `groupby` por intervalos de tiempo; lo volvemos a usar con las
  estaciones del Módulo 5.

**4. Matplotlib: el modelo Figure/Axes (~20 min)**
- `Figure` es el lienzo y `Axes` es cada sistema de ejes donde se dibuja.
  Con esa distinción clara, armar figuras de varios paneles (Módulo 4) es
  directo.
- Gráfico de línea y de dispersión, con etiquetas en los ejes y título.
- **Múltiples paneles con `plt.subplots(nrows, ncols)`:** `fig, axes =
  plt.subplots(1, 2, figsize=(...))` devuelve una `Figure` y un arreglo de
  `Axes`; cada panel se dibuja sobre `axes[i]`. Lo necesitamos hoy para
  la figura de 2 paneles del entregable, y otra vez en el Módulo 4 para
  poner un mapa y una serie lado a lado.

**5. Cierre y repaso antes de la práctica (~10 min)**
Repaso de las cuatro librerías: NumPy calcula, Xarray le pone nombre a los
ejes, Pandas maneja el tiempo y Matplotlib dibuja. Preguntas antes de la
práctica. Mañana, en el Módulo 2, el `Dataset` ya no lo armamos a mano: lo
leemos de un NetCDF o un GRIB.

### Práctica (3 h)

1. **De bucles a NumPy (30 min).** Reescribir el ejercicio de estadísticas
   del día 1 (promedio, máximo, mínimo, conteo sobre umbral) usando
   arreglos NumPy en lugar de bucles, y comparar los dos códigos.
2. **Broadcasting (30 min).** Dado un arreglo de práctica
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
   columnas (`Año`, `Mes`, `Día`, `Hora`) y los faltantes como `S/D`. Hay
   que juntarlas y convertirlas con `pd.to_datetime()`, pasar
   `S/D` a `NaN` con `pd.to_numeric(..., errors="coerce")` y fijarla como índice con `.set_index()` antes de
   poder usar `resample()`, esta vez con una frecuencia distinta
   (`resample("7D")`, mínimo y máximo semanal). En (a) ese trabajo lo hizo
   `leer_senamhi()` sin que lo viéramos.
5. **Entregable (30 min):** un notebook que usa las cuatro librerías
   juntas, con el mismo orden de pasos que repetiremos en los módulos
   siguientes.

**Entregable del día:** tu copia `03_practica_dia2_mio.ipynb` con las
comprobaciones en ✅, y tu copia de
[`04_entregable_integrador.ipynb`](notebooks/04_entregable_integrador.ipynb)
con la sección 7 (el mismo flujo, escrito por ti, para la humedad
relativa) y el archivo `entregable_modulo1_mio.nc`.

---

## Cierre del módulo

**Pregunta de cierre (sin nota, la revisamos en clase):** expliquen con sus
palabras la diferencia entre seleccionar por posición y por nombre en
Xarray, y por qué importa cuando se trabaja con archivos NetCDF. El Módulo 2
empieza con esta pregunta.

<details>
<summary><strong>Respuesta esperada</strong> (ábrela después de intentarlo)</summary>

`.isel(tiempo=0)` elige por **posición** (el primer elemento, sea cual sea su
fecha); `.sel(tiempo="2026-01-15")` elige por **valor de la coordenada**. Con
archivos distintos la posición no es confiable: pueden empezar en
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
ya probada pasa a scripts `.py` desde el Módulo 3, y en el Módulo 6 todo
termina en un pipeline.

**¿Necesito memorizar la fórmula de broadcasting o las reglas exactas de
NumPy?**
No. Basta con la idea: una operación entre
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
El Día 1 no supone experiencia previa; el Día 2 va más rápido. Es normal
sentir que dos días es poco. No hace falta memorizar la sintaxis: los mismos
patrones vuelven en todos los módulos siguientes, y se van fijando con el
uso.

## Para profundizar

Material opcional: no hace falta para la práctica ni para el proyecto final.

### Por qué un `environment.yml` versionado

`environment.yml` lista lo que necesita el proyecto: el nombre del
entorno, el canal de paquetes y cada librería con su versión. Está en el
repositorio junto al código. Eso sirve para tres cosas:
- **Tener lo mismo que el docente:** el entorno de cada participante tiene
  las mismas versiones con las que probamos los notebooks. Instalando
  paquete por paquete, cada computadora termina con versiones algo
  distintas, y aparecen errores que solo le pasan a una persona.
- **Actualizar en un solo lugar:** si el curso necesita una librería
  nueva, se agrega a `environment.yml` y cada uno actualiza con
  `conda env update -f environment.yml --prune`.
- **Instalar con un comando:** clonar el repositorio y ejecutar
  `conda env create`, como en `antes_del_curso.md`.

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
operación en código C compilado. Con grillas como las del WRF, suele ser
entre 10 y 100 veces más rápido.

## Recursos sugeridos

- Documentación de NumPy: *Quickstart* y *Broadcasting*.
- Documentación de Xarray: *Data Structures*.
- Wes McKinney, *Python for Data Analysis*, capítulos de Pandas y series
  temporales (opcional).

## Siguiente módulo

[Módulo 2 — Formatos de datos atmosféricos](../modulo_02_formatos_datos_atmosfericos/README.md):
el mismo `Dataset`, ahora leído de archivos NetCDF y GRIB, con sus
convenciones (CF) y metadatos.
