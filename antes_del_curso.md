# Antes de la primera clase

Hazlo con unos días de anticipación: la primera clase empieza con Python, no
con la instalación. Si algo falla, escribe al docente **antes** del Día 1
con el mensaje de error completo (copiado como texto, no como foto).

## 1. Un equipo listo

- **Linux o macOS:** sirve tal como está.
- **Windows:** instala WSL2 con Ubuntu
  ([guía oficial](https://learn.microsoft.com/es-es/windows/wsl/install)) y
  haz todos los pasos siguientes **dentro de la terminal de Ubuntu**.
- 8 GB de RAM y 20 GB libres en disco (el entorno ocupa unos 3 GB y las
  descargas del curso, varios más).

## 2. Instalar Miniconda

Sigue la [guía de instalación de Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install)
para tu sistema. Al terminar, cierra y vuelve a abrir la terminal, y
comprueba:

```bash
conda --version
```

Debe responder algo como `conda 24.x.x`.

## 3. Descargar el curso y crear el entorno

```bash
git clone https://github.com/Japq91/wrf2026unalm.git
cd wrf2026unalm
conda env create -f environment.yml
```

La creación del entorno tarda (de 5 a 20 minutos) y descarga bastante.
Hazla con buena conexión.

## 4. Comprobar que todo funciona

```bash
conda activate wrf2026
python -c "import xarray, cartopy, cfgrib, herbie, xwrf, cdsapi; print('entorno OK')"
python -m ipykernel install --user --name wrf2026 --display-name "Python (wrf2026)"
jupyter lab
```

Debe imprimir `entorno OK` y abrirse Jupyter en el navegador. La tercera
línea registra el entorno como **kernel** de Jupyter: el «motor» que ejecuta
las celdas. Los notebooks del curso ya vienen configurados para usar el
kernel `Python (wrf2026)`; si Jupyter te pide elegir uno, elige ese (se ve
arriba a la derecha de cada notebook). Abre
`src/modulo_01_python_basico/notebooks/01_teoria_demos.ipynb` y ejecuta la
primera celda (Shift+Enter): si muestra `0.1 + 0.2 = 0.30000000000000004`,
Jupyter funciona (ese número raro es justamente el tema de esa celda).

## 5. Configurar Git y tu forma de guardar el trabajo

Git es el programa que usaste para descargar el curso (`git clone`). Antes
de cada clase traerás el material nuevo con `git pull`, y el Día 10 harás
tu propio repositorio. Para eso Git necesita saber quién eres (una sola vez
por computadora):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu_correo@ejemplo.com"
```

Sin esto, `git commit` falla con el mensaje *Author identity unknown*.

**Regla para no perder trabajo ni bloquear `git pull`:** no guardes tus
cambios encima de los notebooks del curso. Cuando abras uno, haz primero
*File → Save Notebook As…* y agrega `_mio` al nombre, en la **misma
carpeta** (por ejemplo `02_practica_dia1_mio.ipynb`). Así las rutas a
`data/` siguen funcionando, tu copia no la toca `git pull` y Git no la
muestra como cambio pendiente.

Si aun así `git pull` responde *Please commit your changes or stash them
before you merge*, es porque modificaste un archivo del curso. Para traer
la versión nueva sin perder lo tuyo:

```bash
git stash          # aparta tus cambios
git pull           # trae el material nuevo
git stash pop      # vuelve a poner tus cambios (si chocan, avisa al docente)
```

## 6. Crear tu cuenta de Copernicus (para el Día 4)

El Día 4 se descarga ERA5 del Copernicus Climate Data Store. Hace falta una
cuenta personal, y **la activación puede tardar**:

1. Regístrate en <https://cds.climate.copernicus.eu> y confirma el correo.
2. Inicia sesión y acepta las licencias de los tres conjuntos de datos que
   se usan en el curso. En cada página, baja hasta **Download**, y en
   *Terms of use* pulsa **Accept**:
   - [ERA5 hourly data on single levels](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels)
   - [ERA5 hourly data on pressure levels](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels)
   - [ERA5-Land hourly data](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land)

La clave personal (archivo `.cdsapirc`) se configura juntos en el Día 4; por
ahora basta con tener la cuenta activa y las licencias aceptadas.

Los datos de GFS y FNL se descargan sin cuenta.

## 7. Repasar la terminal (si hace falta)

El curso asume que sabes moverte por carpetas en la terminal. Si dudas,
comprueba que puedes hacer esto sin buscar ayuda:

```bash
pwd                      # ¿en qué carpeta estoy?
ls data                  # ¿qué hay en la carpeta data?
cd src/modulo_01_python_basico
cd ../..                 # subir dos niveles
```

Si alguno no te sale, dedica media hora a un tutorial de terminal básica
antes de empezar; en clase se usa todo el tiempo.

## Lista final

- [ ] `conda --version` responde.
- [ ] `conda activate wrf2026` funciona y la prueba imprime `entorno OK`.
- [ ] Jupyter abre con el kernel `Python (wrf2026)` y la primera celda del Módulo 1 corre sin error.
- [ ] `git config --global user.name` responde con tu nombre.
- [ ] Cuenta de Copernicus activa y las 3 licencias de ERA5 aceptadas.
- [ ] Te mueves por carpetas en la terminal sin problema.
- [ ] Respondiste la encuesta diagnóstica que envió el docente.
