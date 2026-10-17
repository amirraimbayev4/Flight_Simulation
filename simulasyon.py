import math
# ==============================================================================
# AIRCRAFT TYPE SELECTION (Uçak Türü Seçimi)
# ==============================================================================
print("=============================================")
print("          AIRCRAFT PROPULSION TYPE           ")
print("=============================================")
print("1. Electric (UAV / Battery Powered)")
print("2. Fuel / Jet Engine (Kerosene Powered)")
aircraft_type = input("Choose aircraft type (1 or 2): ").strip()
print("=" * 45)

if aircraft_type == "1":
    print("You have selected Electric Aircraft (UAV / Battery Powered).")
    print("=" * 45) 
    #Çevre ve Atmosfer Değerleri
    rho = 1.225  # Hava yoğunluğu (kg/m^3)
    #İrtifaya göre hava yoğunluğu değişimi için standart atmosfer modeli kullanılabilir. Ancak basitlik açısından sabit bir değer kullanıyoruz
    print("\n" + "=" * 45)
    print("       ENVIRONMENT & ATMOSPHERE LAYER       ")
    print("=" * 45)
    altitude=float(input("Altitude (m): "))
    r=  1.225 * (1 - 0.00002256 * altitude) ** 4.256
    print(f"-> Air Density (\u03c1) : {r:.4f} kg/m^3")
    print("-" * 45)

    #2. Aerodinamik Kuvvet Denklemleri (Dört Büyük Kuvvet)
    print("          AIRCRAFT MASS & WEIGHT            ")
    print("-" * 45)
    bos= float(input("Empty weight (kg): "))
    batarya= float(input("Battery weight (kg): "))
    yuk= float(input("Payload weight (kg): "))
    toplam = bos + batarya + yuk
    w= toplam * 9.81  # Ağırlık kuvveti (N)

    print(f"-> Total Aircraft Weight (W) : {w:.2f} N")
    print("-" * 45)


    #Lift (Kaldırma) Kuvveti
    print("         AERODYNAMIC CONFIGURATION          ")
    print("-" * 45)

    wing_span = float(input("Wing span (m): "))
    chord = float(input("Chord length (m): ")) 
    velocity = float(input("Velocity (m/s): ")) 
    cl = float(input("Lift coefficient (Cl): "))
    wing_area = wing_span * chord  # Kanat alanı (m^2)

    Lift= 0.5 * r * velocity ** 2 * wing_area * cl



    #Drag (Sürükleme) Kuvveti
    cd = float(input("Drag coefficient (Cd): "))
    Drag= 0.5 * r * velocity ** 2 * wing_area * cd


    print("-" * 45)
    print(f"-> Generated Lift Force (L)  : {Lift:.2f} N")
    print(f"-> Generated Drag Force (D)  : {Drag:.2f} N")
    print("-" * 45)

    #Required Power (Gerekli Güç)
    required_power = Drag * velocity  # Gerekli güç (W)
    print("        PROPULSION & POWER CONSUMPTION       ")
    print("-" * 45)


    efficiency = 0.70  # %70 System efficiency constant

    # Total Electrical Power drawn from battery (Watts)
    power_electrical = required_power / efficiency

    print(f"-> Required Aerodynamic Power : {required_power:.2f} W")
    print(f"-> Total Electrical Power Draw: {power_electrical:.2f} W")


    # 5. Flight Time (Endurance) and Range Calculations
    print("-" * 40)
    print("          TIME & RANGE CALCULATIONS          ")
    print("-" * 40)

    #kullanıcıdan batarya kapasitesi alıyoruz
    battery_capacity_wh = float(input("Battery capacity (Wh): "))

    flight_time_hours = battery_capacity_wh / power_electrical  # Uçuş süresi (saat)
    flight_time_minutes = flight_time_hours * 60  # Uçuş süresi (dakika)


    print(f"Estimated Flight Time : {flight_time_hours:.2f} hours ({flight_time_minutes:.1f} minutes)")

    #Menzil Hesaplaması
    range_km = velocity * flight_time_hours *3.6 # Menzil (km)

    print(f"Estimated Max Range   : {range_km:.2f} km")
    print("=" * 40)

    # Keep the terminal window open until user presses Enter
    input("\nPress Enter to exit the simulator...")


elif aircraft_type == "2":
    print("You have selected Fuel / Jet Engine Aircraft (Kerosene Powered).")
    print("=" * 45)
