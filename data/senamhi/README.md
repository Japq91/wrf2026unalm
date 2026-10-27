# Estaciones automáticas de SENAMHI — Lima, marzo de 2025

Datos de temperatura, precipitación, humedad y viento, cada hora,
de 5 estaciones meteorológicas automáticas (EMA) del SENAMHI en Lima.
Se usan en el Módulo 1 (primeros ejercicios con datos), en el Módulo 3
(cuarta fuente y verificación de integridad) y en el caso Lima del Módulo 6.

| Código | Estación | Altura | Archivo |
|---|---|---|---|
| 112265 | San Martín de Porres | 56 m | `112265_2025_03.csv` |
| 112181 | Campo de Marte | 117 m | `112181_2025_03.csv` |
| 472AC278 | Von Humboldt (UNALM) | 247 m | `472AC278_2025_03.csv` |
| 112278 | Ceres | 339 m | `112278_2025_03.csv` |
| 111290 | Ñaña | 553 m | `111290_2025_03.csv` |

Coordenadas y altura de cada una: `estaciones_lima.json`.

## Cómo leer estos archivos

Se dejaron **tal como los entrega SENAMHI** (solo se recortó marzo de
2025), porque leerlos es parte del aprendizaje:

- Separador `;`.
- La fecha viene en 4 columnas: `Año`, `Mes`, `Día`, `Hora`.
- La hora es **local de Perú (UTC−5)**. Para comparar con modelos (GFS,
  ERA5, WRF), que usan UTC, hay que sumar 5 horas.
- `S/D` significa «sin dato».
- **Ceres no tiene sensor de humedad:** su archivo tiene una columna menos
  (sin `Humedad (%)`). En la descarga original el encabezado traía esa
  columna igual y los valores quedaban corridos. Aquí ya se corrigió el
  encabezado.

En el curso: el Módulo 1 los lee primero «a mano» (`open()` + `split(";")`) y
luego con Pandas; en el Módulo 6, `validacion.leer_senamhi()` hace todo esto.

## De dónde salen

Portal «Mapa de estaciones» de SENAMHI
(<https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/>), descargados con
[`station-hist`](https://github.com/Japq91/station-hist):

```bash
python run_operativo.py --station 112265 --station 112181 --station 472AC278 \
  --station 112278 --station 111290 --yeari 2025 --yearf 2025
```

El portal pide pasar una verificación de Cloudflare en un navegador, por eso
la descarga la hace una persona y no los notebooks.

## Cómo descargar otras estaciones u otros meses (paso a paso)

Se hace **en una computadora con navegador** (Chrome, Brave o Edge), no en
un servidor remoto sin pantalla: la herramienta abre una ventana real del
navegador y a veces hay que marcar la casilla de «no soy un robot».

**1. Instalar `station-hist` (una sola vez).** Trae su propio ambiente de
conda, `getdata`, separado del ambiente del curso:

```bash
git clone https://github.com/Japq91/station-hist.git
cd station-hist
conda env create -f environment.yml
conda activate getdata
python run_operativo.py --doctor     # debe decir ok: True y mostrar el navegador
```

**2. Buscar el código de la estación.** El buscador no abre el navegador:
consulta la lista de 1010 estaciones que viene con la herramienta.

```bash
python run_operativo.py --search "CAMPO DE MARTE"
python run_operativo.py --dep LIMA          # todas las de un departamento
```

Ojo: muchas estaciones aparecen **dos veces con el mismo nombre**, una
convencional y otra automática. Por ejemplo, «Campo De Marte» es `112171`
(convencional, lecturas a horas fijas) y `112181` (automática, **cada
hora**). Este curso usa siempre la automática (categoría `EMA` en
`data_operativo/estaciones.json`), porque su CSV trae las columnas
descritas arriba; las convencionales traen otras columnas.

**3. Descargar.** Se elige el año inicial y final; baja años completos:

```bash
python run_operativo.py --station 112181 --yeari 2025 --yearf 2025
# varias a la vez: --station 112181 --station 111290
```

Lo que pasa en pantalla:

- Se abre el navegador en la página de la estación y la terminal va
  mostrando cada mes descargado (`2025-03: 744 filas`).
- **Desde la segunda estación**, la terminal se detiene con
  `Presiona ENTER aquí para continuar...`. Si en el navegador apareció la
  casilla de Cloudflare, se marca y recién ahí se presiona ENTER. Si no
  apareció, se presiona ENTER y listo.
- Al final dice `OK -> downloads_operativo/112181-2025-2025.csv`.

**4. Recortar el periodo que se necesita.** El archivo trae el año entero.
Los de esta carpeta son solo marzo, sin ningún otro cambio:

```python
with open("112181-2025-2025.csv", encoding="utf-8") as f:
    lineas = f.read().splitlines()
marzo = [l for l in lineas[1:] if l.startswith("2025;03;")]
with open("112181_2025_03.csv", "w", encoding="utf-8") as f:
    f.write("\n".join([lineas[0]] + marzo) + "\n")
```

**5. Revisar antes de usarlo.** Es lo que se practica en el Día 5 con
`verificar_csv_senamhi()`:

- ¿Están todas las horas del mes? (31 días × 24 = 744 filas en marzo).
- ¿Cada fila tiene tantos valores como columnas el encabezado? Las
  estaciones sin sensor de humedad (como Ceres) traen una columna menos.
  La versión actual de `station-hist` ya arma el encabezado sin
  `Humedad (%)` y lo avisa en la terminal; con una versión anterior el
  encabezado salía con 9 columnas y las filas con 8, y los valores quedaban
  corridos sin que Pandas avisara (es el caso que se practica en el Día 5).
- Agregar la estación a `estaciones_lima.json` (o a un JSON propio) con
  `lat`, `lon` y `alt`, copiados de la salida de `--search` o de
  `data_operativo/estaciones.json`.

Fuente de los datos: Servicio Nacional de Meteorología e Hidrología del
Perú (SENAMHI). Son datos de estaciones automáticas, sin control de calidad
completo: pueden traer valores dudosos.
