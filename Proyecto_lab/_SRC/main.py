import csv
import statistics
from pathlib import Path 
from datetime import datetime

#creamos las rutas de input y output

ROOT=Path(__file__).parents[1] # Ruta del proyecto

IN_FILE=ROOT/'_DATA'/'_RAW'/'datos_sucios_250_v2.csv' # Ruta del archivo de entrada
OUT_FILE=ROOT/'_DATA'/'_PROCESSED'/'Limpieza.csv' # Ruta del archivo de salida (datos limipios)
KPIS_FILE=ROOT/"_DATA"/ "_PROCESSED"/"Indicadores.csv" # Ruta del archivo de salida (indicadores)
#se crea la carpeta processed si no existe
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
KPIS_FILE.parent.mkdir(parents=True, exist_ok=True)

#Contadores o acumuladores para KPIs
total = kept = 0
descartes_valor = 0
descartes_fecha = 0
alertas = 0
temperaturas = []
voltajes = []

#a contuinuacion se abre el archivo de entrada y salida
with open (IN_FILE,"r", encoding="utf-8", newline="") as black, \
    open (OUT_FILE,"w", encoding="utf-8", newline="") as white:  

    reader=csv.DictReader(black, delimiter=";") 
    writer=csv.DictWriter(white, fieldnames=["tiempo", "voltajes", "alerta"], delimiter=";") #creamos las columnas del archivo de salida
    writer.writeheader() #escribimos el encabezado en el archivo de salida

    for row in reader:
        total += 1
       
        temps_raw = (row.get("timestamp") or "").strip()  # elimina espacios en blanco y el row.get obtiene el valor de las columnas de "timestamp"
        voltages_raw = (row.get("value") or "").strip()  # lo mismo para la columna "value"
        
        # limpiamos los voltajes
        voltages_raw =voltages_raw.replace(",","." ) #reemplazamos las comas por puntos en los datos de voltaje
        voltages_raw =voltages_raw.lower() #voltages_raw =voltages_raw.lower() es una funcion para las palabras que le metemos en el if de de voltages_raw, se  convierntan todas a minusculas
        #ejemplo:
        #val = "ERROR"
        #print(val in {"error"})        # False ❌
        # print(val.lower() in {"error"}) # True ✅

        if voltages_raw in {"", "n/a", "na", "nan", "null","none", "error"}: #si el valor de voltaje es vacio o n/a o na, etc se considera un dato malo
            descartes_valor += 1
            continue
        try:
            val =float(voltages_raw) #convertimos el valor de voltaje a float
        except ValueError: 
            descartes_valor += 1
            continue # salta si fila no es un numero 

        good_time = None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"): #se crean dos formatos de fecha
            try:
                dt = datetime.strptime(temps_raw, fmt) #se intenta convertir el valor de tiempo al formato de fecha
                good_time = dt.strftime("%Y-%m-%d %H:%M:%S") #si se logra convertir se guarda en la variable good_time
                break #si se logra convertir se sale del for
            except ValueError: 
                pass #si no se logra convertir se pasa al siguiente formato
        if good_time is None: #si no se logra convertir el valor de tiempo a ningun formato se descarta la fila
            descartes_fecha += 1
            continue

        # conversion a temperatura y alerta
        temp = 18*val-64
        alerta_texto = "temperatura alta" if temp > 40 else "ok" #si la temperatura es mayor a 40 se considera una alerta
        if temp > 40:
            alertas += 1

        # acumular para KPIs
        temperaturas.append(temp)
        voltajes.append(val)

        #finalmente se escriben los datos procesados en el archivo de salida
        writer.writerow({"tiempo": good_time, "voltajes": f"{val:.2f}", "alerta": alerta_texto})
        kept += 1

# --- Cálculo y guardado de KPIs ---
kpis = {
    "Filas_totales": total,
    "Filas Validas": kept,                     
    "Descartes_fecha": descartes_fecha,
    "Descartes_valor": descartes_valor,
    "n": len(temperaturas), # numero de temperaturas validas
    "temp_min": round(min(temperaturas), 2) if temperaturas else None, 
    "temp_max": round(max(temperaturas), 2) if temperaturas else None,
    "temp_prom": round(statistics.fmean(temperaturas), 2) if temperaturas else None,
    "Alertas": alertas,
}

# Indicadores en CSV (KPI;Valor) y también impresión en consola
with open(KPIS_FILE, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["KPI", "Valor"])
    for k, v in kpis.items():
        w.writerow([k, v])

print("\nKPIs calculados:")
for k, v in kpis.items():
    print(f"- {k}: {v}")
print(f"\nArchivos generados:\n- {OUT_FILE}\n- {KPIS_FILE}")
