# Limpieza de datos en un archivo CSV
import csv # Para manejar archivos CSV
from datetime import datetime # Para manejar fechas y horas
from pathlib import Path #importo el comando path (busca el lugar donde esta el codigo)

#Path - ruta de acceso 
ROOT = Path(__file__).resolve().parents[0] # sube desde src/ a la raiz del proyecto 
TXT = ROOT / "Practicas"
IN_FILE = TXT / "voltajes_250_sucio.csv" # Archivo de entrada 
OUT_FILE = TXT /"voltajes_250_limpio.csv" # Archivo de salida

#apertura de archivos
with open(IN_FILE, "r", encoding="utf-8", newline="") as fin,\
    open(OUT_FILE, "w", encoding="utf-8", newline="") as fout:
    reader = csv.DictReader(fin, delimiter=';') # Lee el archivo CSV con ; como delimitador
    writer = csv.DictWriter(fout, fieldnames=["timestamp", "value"]) # Crea el archivo y su cabecera
    writer.writeheader() # Escribe la cabecera en el archivo de salida
#leer linea por linea y seleccionar en crudo raw
    total = kept = 0
    for row in reader:
        total += 1
        ts_raw  = (row.get("timestamp") or "").strip() # Lee y limpia el campo timestamp
        val_raw = (row.get("value") or "").strip() # Lee y limpia el campo value
#limpiar datos
        val_raw = val_raw.replace(",", ".") # Reemplaza , por . en el valor
        val_low = val_raw.lower() # Convierte el valor a minúsculas
        if val_low in {"na", "", "n/a", "nan", "null", "none", "error"}: 
            continue # Si el valor es inválido, salta a la siguiente fila
        try:
            val = float(val_raw) # Intenta convertir el valor a float
        except ValueError:
            continue # Si falla, salta a la siguiente fila
#limpieza de datoss de tiempo 
        ts_clean = None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S"):
            try:
                dt = datetime.strptime(ts_raw, fmt) # Intenta parsear la fecha con el formato dado
                ts_clean = dt.strftime("%Y-%m-%dT%H:%M:%S") # Formatea la fecha al formato estándar
                break # Si tiene éxito, sale del bucle
            except ValueError:
                pass      # Si falla, intenta con el siguiente formato
#grabar datos en writer 
        writer.writerow({"timestamp": ts_clean, "value": f"{val:.2f}"}) # Escribe la fila limpia en el archivo de salida # Incrementa el contador de filas mantenidas
        kept += 1 

