import math

#Çevre ve Atmosfer Değerleri
rho = 1.225  # Hava yoğunluğu (kg/m^3)
#İrtifaya göre hava yoğunluğu değişimi için standart atmosfer modeli kullanılabilir. Ancak basitlik açısından sabit bir değer kullanıyoruz
irtifa=float(input("İrtifa (m): "))
r=  1.225 * (1 - 0.00002256 * irtifa) ** 4.256
print("Hava yoğunluğu (kg/m^3):", r)
