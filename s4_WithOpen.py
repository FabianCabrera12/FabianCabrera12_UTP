#Busca la ruta donde esta el codigo y luego se añade la ruta del archivo de ingreso 
from pathlib import Path #importo el comando path (busca el lugar donde esta el codigo)
ROOT = Path(__file__).resolve().parents[0] # sube desde src/ a la raiz del proyecto 
TXT = ROOT / "Practicas"/ "mediciones_200_mixto.txt"

valores=[]
with open(TXT, "r", encoding="utf-8") as f: 
    for linea in f: #lee linea por linea del archivo ingresado
        s=linea.strip() #elimina espacios en blanco al inicio y final de la linea
        if not s or s.startswith("#"): #si la linea esta vacia o empieza con #
            continue
        if not s or s.startswith("!"): #si la linea esta vacia o empieza con !
            continue
        s = s.replace(",", ".") #reemplaza las comas por puntos
        try: 
            valores.append(s) #intenta convertir la linea en un numero flotante y agregarlo a la lista valores 
        except ValueError:
            #si no es ni linea ni numero, debe saltarlo 
            pass
Vmayor= []
Vmenor= []
for i in valores:
    if i >= str(5):
        Vmayor.append(i)
    else:
        Vmenor.append(i)
print(Vmayor)
print(Vmenor)

print(len(Vmayor))
print(len(Vmenor))
