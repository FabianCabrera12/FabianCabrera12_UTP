import datetime as dt # importar funciones - modulo fecha y hora
import random as rd # importar funciones - modulo aleatorio
Vingreso=[]
for i in range(20): 
    Vingreso.append(rd.randint(0, 100))
Vmayor= []
Vmenor= []
for i in Vingreso:
    if i >= 50:
        Vmayor.append(i)
    elif i < 50:
        Vmenor.append(i)
print(f"Los valores mayores son:{Vmayor}")
print(f"Los valores menores son:{Vmenor}")

Vvalores=[]
for i in range(40):
    Vvalores.append(rd.randint(0, 1300))
print(Vvalores)