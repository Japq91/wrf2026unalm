# Módulo 6 — Flujo de trabajo integrado

[Índice del curso](../README.md)

**Ubicación en el curso:** Día 10 de 10 (final) · **Carga horaria:** 5 h (2 h teoría + 3 h práctica)
**Requiere:** Módulos 1 a 5 completos
**Cierra:** el curso, con el proyecto final

## Objetivo del módulo

Al terminar el módulo, el participante habrá juntado lo construido en los
Módulos 3 a 5 (descargar, graficar, validar) en un **pipeline**: una cadena
de pasos que corre sola, de principio a fin, y que sirve para un caso nuevo
cambiando solo unos pocos datos de entrada, sin reescribir código.

## Relación con el WRF

Hasta ahora practicamos cada etapa por separado. En un trabajo real, el
mismo análisis se repite para muchos casos: otras fechas, otra región,
otras estaciones. Si cada caso nuevo obliga a editar celdas sueltas de
varios notebooks, tarde o temprano algo se olvida o se corre en otro
orden.

## Prerrequisitos específicos

Tener a mano los artefactos generados en los Módulos 3, 4 y 5: el módulo
`descargar_era5()` / `obtener_entrada_wrf()` (Módulo 3), los notebooks de
mapas/series (Módulo 4), y `metricas.py` / `evaluar_variable()` (Módulo 5).

## Antes de empezar: activar el entorno

```bash
conda activate wrf2026
jupyter lab
```
Este módulo no instala nada nuevo: usa el mismo entorno `wrf2026`.

---

## Día 10 — Diseño del pipeline y proyecto integrador

### Teoría (2 h)

**1. Qué hace reproducible a un análisis (~30 min)**
Reproducible quiere decir que otra persona (o tú mismo dentro de un año)
puede correrlo y obtener lo mismo. Se logra con tres hábitos:
- **Mismos datos de entrada, mismo resultado.** Nada escondido dentro del
  código: si una función usa una ruta o una fecha, la recibe como
  parámetro, no la tiene escrita adentro.
- **Lo que cambia, en un solo lugar.** Las fechas, la región y las
  estaciones de cada caso van juntas en un archivo `config.py`. Para un
  caso nuevo se edita ese archivo y nada más. Es la misma idea de las
  funciones con parámetros del Módulo 3, llevada a todo el proyecto.
- **Las mismas versiones de las librerías.** Una actualización puede
  cambiar resultados sin tocar el código. Para eso está el
  `environment.yml` del repositorio, que se copia al proyecto.

**2. Una carpeta ordenada (~25 min)**
Cada cosa en su lugar, siguiendo la idea de nombres de archivo del Módulo 3.
En los notebooks de hoy esta carpeta se llama `proyecto_demo/`:
```
proyecto_demo/
├── config.py            # parámetros del caso (fecha, dominio, estaciones)
├── environment.yml        # copia del environment.yml del curso
├── datos/
│   ├── entrada/           # ERA5 / GFS descargados y verificados (Módulo 3)
│   ├── wrfout/             # salidas del WRF (provistas, no generadas por el curso)
│   └── observaciones/      # datos de estaciones (Módulo 5)
├── pipeline/
│   ├── descarga.py         # funciones del Módulo 3
│   ├── visualizacion.py    # funciones del Módulo 4
│   └── validacion.py       # funciones del Módulo 5 (metricas.py, evaluar_variable)
├── resultados/
│   ├── mapas/
│   ├── series/
│   └── validacion/
└── notebooks/
    └── proyecto_integrador.ipynb   # orquesta el flujo completo (en un proyecto propio)
```
En la práctica de hoy, el trabajo de `proyecto_integrador.ipynb` se reparte
en tres notebooks (armar la carpeta, correr todo, documentar) para ir paso
a paso. En un proyecto propio basta con uno.

Dos carpetas van separadas a propósito:
- **`datos/` aparte de `resultados/`**, para que un gráfico o una tabla no
  reemplace por error un dato que tardó horas en descargarse.
- **`pipeline/` aparte de `notebooks/`**: en `pipeline/` están las
  funciones, que cambian poco; el notebook las llama y muestra los
  resultados, y se lee como un informe del análisis.

**3. Todo lo que cambia, en `config.py` (~30 min)**
Se arma en vivo `config.py`: un archivo con todo lo que define un caso
(fechas, región a descargar, ruta del `wrfout`, estaciones para validar).
Después se revisan las funciones de los módulos anteriores: si alguna tiene
una fecha o una ruta escrita adentro en vez de recibirla como parámetro, se
corrige aquí.

**4. Cuatro buenas costumbres (~20 min)**
- **Una función, una tarea:** la que descarga no grafica.
- **Una línea que diga qué hace cada función**, qué recibe y qué devuelve
  (se llama *docstring*).
- **Errores que se entiendan:** si una etapa falla, que avise cuál y por
  qué (el `try/except` del Módulo 3).
- **Mensajes de avance** (`print("Descargando ERA5...")`), para saber en
  qué paso va cuando corre solo.

**5. Cierre del curso (~15 min)**
Se repasa el diagrama del curso (entrada → WRF → salida → mapas →
validación), marcando en qué módulo se construyó cada pieza, y se comentan
posibles pasos siguientes: descargas en paralelo, ejecución programada y
guardar el código en Git.

### Práctica (3 h) — Proyecto integrador final

1. **Montaje del esqueleto del pipeline (30 min).** Crear la estructura de
   carpetas de la teoría y el archivo `config.py` con los parámetros de un
   caso **nuevo**, no usado en módulos anteriores: **Lima, 14 al 17 de
   marzo de 2025**, validado contra la estación Lima-Callao (aeropuerto
   Jorge Chávez) y 5 estaciones automáticas de SENAMHI.
2. **Pasar las funciones a `pipeline/` (45 min, guiado).** Revisar cómo
   las funciones ya construidas (`descargar_era5`, `obtener_entrada_wrf`
   del Módulo 3; la lógica de extracción/mapas del Módulo 4; `metricas.py`
   y `evaluar_variable` del Módulo 5) quedan en los archivos de
   `pipeline/`, recibiendo sus parámetros desde `config.py` en vez de
   valores fijos. El notebook escribe esos archivos; la tarea es leerlos y
   reconocer de qué módulo viene cada función. **Ojo:** en el curso,
   `descargar_era5()` es **sintética** (genera un ERA5 de práctica, sin
   pasar por la cola de Copernicus); en un proyecto propio se reemplaza
   por la descarga real del Módulo 3.
3. **Correr todo de punta a punta (45 min).** Desde
   [`03_practica_ejecucion_completa.ipynb`](notebooks/03_practica_ejecucion_completa.ipynb), ejecutar el flujo completo sobre
   el caso Lima: descargar y verificar datos de entrada → generar el mapa
   desde el `wrfout` → validar contra Lima-Callao y 5 estaciones de
   SENAMHI (de 56 m a 553 m), con al menos RMSE, r y KGE.
   Como no tenemos una corrida del WRF sobre Lima, en la validación se usa
   el pronóstico de GFS (ciclo del 14/03/2025, 00 UTC), descargado con
   Herbie. Si no hay internet, el notebook usa la copia guardada en
   `data/modelos/`. En la estación hay un dato dudoso que, solo, baja la
   correlación de 0,84 a 0,57: hay que mirar los datos antes de calcular
   métricas.
   Con SENAMHI aparece otra cosa: cuatro estaciones caen en la misma
   celda de GFS y reciben el mismo valor, pero el error va de −0,3 °C en
   la costa a −1,8 °C en Ceres. Una celda de 25 km no distingue la costa
   del valle; un WRF con celdas finas, sí. Los archivos de SENAMHI vienen
   con la hora local y `S/D` para los faltantes, y leerlos bien es parte
   del ejercicio (`validacion.leer_senamhi`).
4. **Documentar el resultado (30 min).** Redactar, en
   [`04_entregable_proyecto_final.ipynb`](notebooks/04_entregable_proyecto_final.ipynb), un resumen breve del caso analizado y de los
   resultados de la validación. Este notebook es el entregable del curso.
5. **Guardar el proyecto con Git (15 min).** Git guarda la historia del
   proyecto: qué cambió y cuándo, y permite volver atrás si algo se rompe.
   Desde la carpeta de los notebooks del módulo:
   ```bash
   cp ../../../environment.yml proyecto_demo/
   cp 04_entregable_proyecto_final.ipynb proyecto_demo/notebooks/
   cd proyecto_demo
   git init                          # empezar a llevar historia aquí
   printf "datos/\nresultados/\n__pycache__/\n" > .gitignore   # lo que NO se guarda
   git add .
   git commit -m "Pipeline del proyecto final"
   git log --oneline                 # ver la historia
   ```
   Si `git commit` responde *Author identity unknown*, falta configurar el
   nombre y el correo (ver [`antes_del_curso.md`](../../antes_del_curso.md),
   sección 5).
   En Git va el **código** y la configuración (`pipeline/`,
   `config.py`, el notebook, `environment.yml`), no los datos descargados
   ni los resultados, que pesan mucho y se vuelven a generar corriendo el
   pipeline.
6. **Revisión entre pares y cierre (15 min).** Revisar el pipeline de otro
   participante (o con el docente), y recomendaciones para seguir después
   del curso.

**Entregable final del curso:** repositorio del proyecto con la estructura
de carpetas completa, los archivos `pipeline/*.py` funcionando y el
notebook `04_entregable_proyecto_final.ipynb` documentado con los
resultados del caso nuevo.

---

## Cierre del módulo

**Pregunta de cierre:** ¿qué habría que cambiar para repetir todo el
análisis con otra fecha y otra estación? ¿Por qué no hace falta tocar las
funciones?

<details>
<summary><strong>Respuesta esperada</strong> (ábrela después de intentarlo)</summary>

Solo `config.py`: la fecha (o rango de fechas), la región si cambia, la
ruta al `wrfout` de ese caso y la estación (nombre y coordenadas). No hay
que tocar `pipeline/descarga.py`, `visualizacion.py` ni `validacion.py`,
porque esas funciones reciben todo como parámetros y no tienen fechas ni
rutas escritas adentro. Después se vuelve a correr el notebook de punta a
punta y los resultados nuevos quedan en `resultados/`, sin pisar los
anteriores ni los datos descargados.
</details>

## Cierre del curso

Al terminar, cada participante tiene un pipeline propio que puede correr
sobre otro caso cambiando `config.py`. Cubre las tres etapas que vimos en
el curso: **entrada** (Módulos 2 y 3), **salida** (Módulo 4) y
**validación** (Módulo 5).

## Preguntas frecuentes

**¿Tengo que reescribir todo el código de los Módulos 3–5 desde cero para
este módulo?**
No. Las funciones que ya probaron en sus notebooks pasan a archivos `.py`
dentro de `pipeline/`, y se ajusta cómo reciben sus parámetros. Si una
función ya recibía todo como argumento, solo cambia de lugar.

**¿Por qué separar `pipeline/` de `notebooks/` si de todas formas voy a
seguir usando notebooks para explorar resultados?**
En `pipeline/` está el código que ya funciona y que no debería cambiar
cada vez que se prueba algo. En `notebooks/` se puede experimentar y
probar variantes sin riesgo de romper ese código. Un notebook que solo
*llama* a funciones de `pipeline/` es más fácil de leer y de revisar que
uno que mezcla definiciones largas con pruebas.

**¿Qué agrega este módulo a lo que tenía al final del Módulo 5?**
Al final del Módulo 5 hay piezas que funcionan por separado (descarga,
gráficos, validación), probadas con los datos de cada módulo. Aquí las
tres corren en orden sobre un caso **nuevo**, cambiando solo `config.py`.

**¿Cómo uso mi propia corrida del WRF sobre Lima en el proyecto final?**
En la Etapa 3 de `03_practica_ejecucion_completa.ipynb`, la serie `sim`
viene de GFS. Se reemplaza por la serie del `wrfout` propio en el punto de
la estación (`visualizacion.serie_temperatura_en_punto`, Módulo 4). Las
observaciones, las métricas y los gráficos no cambian.

**Después del curso, ¿cómo reemplazo los datos sintéticos por datos
reales?**
En el curso, `descargar_era5()` de `pipeline/descarga.py` usa un generador
local (para que el pipeline corra en clase sin esperar la cola de
Copernicus), y la salida del WRF de la Etapa 2 también es simulada. La
descarga real ya la hicieron en el Módulo 3 (`cdsapi`, `Herbie`). Dentro de
esa función se reemplaza la llamada al generador por la descarga real, con
los mismos parámetros. El resto del pipeline no cambia, porque solo usa el
`Dataset` que recibe.

**¿Vale la pena usar Git si trabajo solo en mis proyectos?**
Sí. Además de servir para trabajar en equipo, Git guarda qué cambió y
cuándo, y permite volver atrás si un cambio rompe algo.

## Recursos sugeridos

- *The Turing Way*: guía de investigación reproducible (capítulos sobre
  estructura de proyectos y configuración).
- Documentación de Conda: *Exporting an environment*.

## Módulos del curso

1. [Python básico](../modulo_01_python_basico/README.md)
2. [Formatos de datos atmosféricos](../modulo_02_formatos_datos_atmosfericos/README.md)
3. [Descarga de datos de entrada](../modulo_03_descarga_datos_entrada/README.md)
4. [Lectura y visualización de salidas WRF](../modulo_04_lectura_visualizacion_wrf/README.md)
5. [Validación de resultados](../modulo_05_validacion_resultados/README.md)
6. Pipeline integrado *(este módulo)*
