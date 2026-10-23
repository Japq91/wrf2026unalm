#!/bin/bash
year=2025
mon=3
for day in {1..31..1}; do
	echo $day
#    	python h1_ogimet.py --anio $year --mes $mon --dia $day
#    	python h2_procesa_horario.py --anio $year --mes $mon --dia $day
done
python h3_junta_mensual.py --anio $year --mes $mon --borrar_diarios
