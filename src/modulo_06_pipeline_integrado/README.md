# Módulo 6 — Flujo de trabajo integrado

[Índice del curso](../README.md)

**Ubicación en el curso:** Día 10 de 10 (final) · **Carga horaria:** 5 h (2 h teoría + 3 h práctica)
**Requiere:** Módulos 1 a 5 completos
**Cierra:** el curso — este módulo produce el proyecto integrador final

## Objetivo del módulo

Al finalizar el módulo, el participante habrá juntado lo construido en los
Módulos 3 a 5 (descargar, graficar, validar) en un **pipeline**: una cadena
de pasos que corre sola, de principio a fin, y que sirve para un caso nuevo
cambiando solo unos pocos datos de entrada, sin reescribir código.

## Por qué este módulo importa para el WRF

Hasta ahora cada etapa se practicó por separado. En un trabajo real, el
mismo análisis se repite para muchos casos: otras fechas, otra región,
otras estaciones. Si cada caso nuevo obliga a editar celdas sueltas de
varios notebooks, tarde o temprano algo se olvida o se ejecuta en otro
orden. Este módulo deja todo listo para repetir el análisis sin esos
errores.

## Prerrequisitos específicos

Tener a mano los artefactos generados en los Módulos 3, 4 y 5: el módulo
`descargar_era5()` / `obtener_entrada_wrf()` (Módulo 3), los notebooks de
mapas/series (Módulo 4), y `metricas.py` / `evaluar_variable()` (Módulo 5).

## Antes de empezar: activar el entorno

```bash
conda activate wrf2026
jupyter lab
```
Este módulo no instala nada nuevo: usa el mismo entorno `wrf2026` del
Módulo 1.

---

## Día 10 — Diseño del pipeline y proyecto integrador

### Teoría (2 h)

**1. Qué hace "reproducible" a un análisis (~30 min)**
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
  cambiar resultados sin tocar el código. Ese problema ya está resuelto
  desde el Módulo 1: es el `environment.yml` del repositorio.

**2. Una carpeta ordenada (~25 min)**
Cada cosa en su lugar, siguiendo la idea de nombres de archivo del Módulo 3.
En los notebooks de hoy esta carpeta se llama `proyecto_demo/`:
```
proyecto_demo/
├── config.py            # parámetros del caso (fecha, dominio, estaciones)
├── environment.yml        # el mismo entorno reproducible del Módulo 1
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

Dos separaciones importan:
- **`datos/` aparte de `resultados/`**, para que un gráfico o una tabla
  nunca sobrescriba por error un dato descargado (que pudo tardar horas en
  bajar).
- **`pipeline/` aparte de `notebooks/`**: en `pipeline/` viven las
  funciones que ya funcionan y no se tocan; el notebook solo las llama y
  muestra resultados, así se lee como el resumen del análisis.

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
siguientes pasos: descargas en paralelo, ejecución automática programada y
llevar el código en Git.

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
   un pronóstico **real**: GFS (ciclo del 14/03/2025, 00 UTC), descargado
   con Herbie. Si no hay internet, el notebook usa la copia guardada en
   `data/modelos/`. El caso trae una sorpresa real: un dato dudoso de la
   estación que, solo, baja la correlación de 0,84 a 0,57. Se discute por
   qué hay que mirar los datos antes de calcular métricas.
   Con SENAMHI aparece la otra lección: cuatro estaciones caen en la misma
   celda de GFS y reciben el mismo valor, pero el error va de −0,3 °C en
   la costa a −1,8 °C en Ceres. Una celda de 25 km no distingue la costa
   del valle; un WRF con celdas finas, sí. Los archivos de SENAMHI vienen
   con la hora local y `S/D` para los faltantes: leerlos bien es parte del
   ejercicio (`validacion.leer_senamhi`).
4. **Documentar el resultado (30 min).** Redactar, en
   [`04_entregable_proyecto_final.ipynb`](notebooks/04_entregable_proyecto_final.ipynb), un resumen breve del caso analizado y de los
   resultados de validación obtenidos — este notebook documentado es el
   entregable de evaluación del curso completo.
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
   La regla: en Git va el **código** y la configuración (`pipeline/`,
   `config.py`, el notebook, `environment.yml`), no los datos descargados
   ni los resultados, que pesan mucho y se vuelven a generar corriendo el
   pipeline.
6. **Revisión cruzada y cierre (15 min).** Intercambio breve entre
   participantes (o revisión guiada por el instructor) del pipeline
   resultante, y recomendaciones finales para continuar trabajando con el
   flujo después del curso.

**Entregable final del curso:** repositorio del proyecto con la estructura
de carpetas completa, los archivos `pipeline/*.py` funcionando y el
notebook `04_entregable_proyecto_final.ipynb` documentado con los
resultados del caso nuevo.

---

## Cierre del módulo

**Checkpoint:** el participante debe poder explicar qué tendría que
cambiar para repetir todo el análisis con otra fecha y otra estación, y
por qué con este pipeline eso no obliga a tocar las funciones.

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

Al completar este módulo, cada participante cuenta con un pipeline propio,
ejecutable de nuevo sobre cualquier caso futuro cambiando solo
`config.py`, que cubre las tres etapas centrales del ciclo de modelado con
WRF trabajadas a lo largo del curso: **entrada** (Módulos 2–3), **salida**
(Módulo 4) y **validación** (Módulo 5).

## Preguntas frecuentes

**¿Tengo que reescribir todo el código de los Módulos 3–5 desde cero para
este módulo?**
No. Se trata de reordenar, no de reescribir: mover
funciones que ya funcionan (probadas en sus respectivos notebooks) a
archivos `.py` dentro de `pipeline/`, ajustando cómo reciben sus
parámetros. Si una función ya estaba bien escrita (parametrizada, sin
valores fijos internos), el cambio es casi solo de "dónde vive el código",
no de qué hace.

**¿Por qué separar `pipeline/` de `notebooks/` si de todas formas voy a
seguir usando notebooks para explorar resultados?**
Porque cumplen roles distintos: `pipeline/` contiene la lógica que ya
está validada y no debería cambiar cada vez que se prueba algo nuevo;
`notebooks/` es el lugar seguro para experimentar, graficar variantes,
romper cosas y probar ideas sin miedo a desordenar la lógica central. Un
notebook que además define funciones complejas mezcladas con exploración
es más difícil de mantener y de revisar que uno que solo *llama* a
funciones ya escritas en `pipeline/`.

**¿Qué gano exactamente con este módulo que no tuviera ya al final del
Módulo 5?**
Al final del Módulo 5 existen piezas que funcionan por separado (descarga,
visualización, validación), cada una probada con datos de muestra fijos.
Lo que agrega este módulo es la capacidad de correr las tres, en orden,
sobre un caso **que nunca se usó antes**, cambiando solo unos pocos
parámetros en un único archivo (`config.py`) — sin tocar el resto del
código. Esa es la diferencia entre "tengo código que funciona" y "tengo
una herramienta reutilizable".

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
descarga real ya la hiciste en el Módulo 3 (`cdsapi`, `Herbie`). El cambio es puntual: dentro de esa función, reemplazar la
llamada al generador sintético por la llamada real a la librería
correspondiente, manteniendo la misma firma de parámetros — el resto del
pipeline (visualización, validación) no necesita cambiar, porque solo le
importa qué `Dataset` recibe, no de dónde vino.

**¿Vale la pena usar Git/GitHub si voy a trabajar sola/o en mis propios
proyectos, sin equipo?**
Sí, incluso trabajando en solitario: Git no es solo para coordinar con
otras personas, también sirve como historial de qué cambió y cuándo en el
propio código, y permite volver atrás si un cambio rompe algo. Como se
menciona en las recomendaciones de cierre, es el primer hábito sugerido
para continuar después del curso.

## Recursos sugeridos

- *The Turing Way* — guía comunitaria de investigación reproducible
  (capítulos sobre estructura de proyectos y gestión de configuración).
- Documentación de Conda — *Exporting an environment*.

## Módulos del curso

1. [Python básico](../modulo_01_python_basico/README.md)
2. [Formatos de datos atmosféricos](../modulo_02_formatos_datos_atmosfericos/README.md)
3. [Descarga de datos de entrada](../modulo_03_descarga_datos_entrada/README.md)
4. [Lectura y visualización de salidas WRF](../modulo_04_lectura_visualizacion_wrf/README.md)
5. [Validación de resultados](../modulo_05_validacion_resultados/README.md)
6. Pipeline integrado *(este módulo)*
