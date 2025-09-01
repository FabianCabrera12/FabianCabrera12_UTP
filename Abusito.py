import datetime as dt # importar funciones - modulo fecha y hora
import random as rd # importar funciones - modulo aleatorio

nombre = "Cabrera" # constante
fecha = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # variable

voltajes = [] # lista para guardar valores de voltaje
alertas = []  # lista para guardar mensajes de alerta

for i in range(10): # bucle for
    v = rd.randint(0, 1023) # valor aleatorio entre 0 y 1023
    voltajes.append(v)  # agrega el valor v al final de la lista voltajes
    if v > 900: # condicional if
        alertas.append(f"Alerta: Voltaje alto detectado - {v} en la medición {i+1}") # se le coloca i+1 para que inicie en 1 y no de 0
    elif v < 200: # condicional elif
        alertas.append(f"Alerta: Voltaje bajo detectado - {v} en la medición {i+1}") # al darle un valor de 10 al comando range genera 10 valores pero empezando del 0 al 9

# Generar el contenido del correo electrónico
correo = f"""
Estimado Ingeniero {nombre},

Le envío los datos de los voltajes medidos en el día {fecha}.

Voltajes medidos: {voltajes}

Alertas de voltaje:
{chr(10).join(alertas)}

Saludos cordiales,
Su sistema de monitoreo
"""

print("--- Contenido del correo electrónico ---")
print(correo)