import random as rd  
Vingreso=[]
for i in range(20): 
    Vingreso.append(rd.randint(0, 100))
print(Vingreso)
Vmayor= []
Vmenor= []
for i in Vingreso:
    if i >= 50:
        Vmayor.append(i)
    elif i < 50:
        Vmenor.append(i)
print(f"Los valores mayores son:{Vmayor}")
print(f"Los valores menores son:{Vmenor}")