import math

#Çevre ve Atmosfer Değerleri
rho = 1.225  # Hava yoğunluğu (kg/m^3)
#İrtifaya göre hava yoğunluğu değişimi için standart atmosfer modeli kullanılabilir. Ancak basitlik açısından sabit bir değer kullanıyoruz
irtifa=float(input("İrtifa (m): "))
r=  1.225 * (1 - 0.00002256 * irtifa) ** 4.256
print("Hava yoğunluğu (kg/m^3):", r)

#2. Aerodinamik Kuvvet Denklemleri (Dört Büyük Kuvvet)
bos= float(input("Boş ağırlık (kg): "))
batarya= float(input("Batarya ağırlığı (kg): "))
yuk= float(input("Yük ağırlığı (kg): "))
toplam = bos + batarya + yuk
w= toplam * 9.81  # Ağırlık kuvveti (N)

print("Total weight :", w)


#Lift (Kaldırma) Kuvveti

wing_span = float(input("Wing span (m): "))  
velocity = float(input("Velocity (m/s): ")) 
cl = float(input("Lift coefficient (Cl): "))

Lift= 0.5 * r * velocity ** 2 * wing_span * cl
print("Lift(N):", Lift, "N")


#Drag (Sürükleme) Kuvveti
cd = float(input("Drag coefficient (Cd): "))
Drag= 0.5 * r * velocity ** 2 * cd
print("Drag(N):", Drag, "N")

