import math
# ==============================================================================
# AIRCRAFT TYPE SELECTION (Uçak Türü Seçimi)
# ==============================================================================
print("=============================================")
print("          AIRCRAFT PROPULSION TYPE           ")
print("=============================================")
print("1. Electric (UAV / Battery Powered)")#There are different equations for electric and fuel aircrafts, so we need to select the type first
print("2. Fuel / Jet Engine (Kerosene Powered)")#First I will finish the electric one then I will implement the fuel one
aircraft_type = input("Choose aircraft type (1 or 2): ").strip()
print("=" * 45)

if aircraft_type == "1":
    print("You have selected Electric Aircraft (UAV / Battery Powered).")
    print("=" * 45) #This one is really useful for separating sections in the terminal output, makes it more readable
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

    #Stall speed hesaplaması
    cl_max=1.5  # Maximum lift coefficient (Cl_max) for typical UAVs
    v_stall= math.sqrt((2 * w) / (r * wing_area * cl_max))  # Stall speed (m/s)

     # 3. İLK BÜYÜK KONTROL: Uçak fiziksel olarak kalkabiliyor mu?
    is_lift_enough = Lift >= w    #There is no need to calculate range and power if the lift is not enough to lift the aircraft, so we check this first
    is_speed_safe = velocity >= v_stall

    if not (is_lift_enough and is_speed_safe):
        # EĞER UÇAK UÇAMIYORSA: Menzil ve Güç hesaplarını pas geçip direkt rapor veriyoruz!
        print("\n" + "=" * 45)
        print("FLIGHT STATUS: FAILED! ❌ The aircraft CANNOT fly.")
        print("=" * 45)
        print("[DIAGNOSTIC REPORT & FIXES]:")
        
        if not is_lift_enough:
            print(f"  -> ISSUE: Insufficient Lift Force! Short by {w - Lift:.2f} N.")
            print("     FIX  : Increase wing span, chord length, or velocity.")
        if not is_speed_safe:
            print(f"  -> ISSUE: STALL RISK! Your speed ({velocity:.2f} m/s) is below the minimum safety limit.")
            # İşte buraya hem m/s hem de km/h cinsinden stall limitini yazdırıyoruz:
            print(f"     REQUIRED: You must fly at least {v_stall:.2f} m/s ({v_stall * 3.6:.1f} km/h) to stay in the air.")
            print("     FIX     : Increase your 'Velocity' input above this limit.")
        print("\n-> Time & Range calculations bypassed due to critical flight failure.")
        print("=" * 45)

    else:
        # EĞER UÇAK GÜVENLİCE UÇUYORSA: Artık menzil ve güç hesaplayabiliriz!
        print("\n" + "=" * 45)
        print("FLIGHT STATUS: SUCCESS! 🛫 Safe takeoff conditions met.")
        print("=" * 45)

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
        #Stall speed hesaplaması
        cl_max=1.5  # Maximum lift coefficient (Cl_max) for typical UAVs
        

        print(f"Estimated Flight Time : {flight_time_hours:.2f} hours ({flight_time_minutes:.1f} minutes)")
        print(f"Estimated Stall Speed : {v_stall:.2f} m/s")

        #Menzil Hesaplaması
        range_km = velocity * flight_time_hours *3.6 # Menzil (km)

        print(f"Estimated Max Range   : {range_km:.2f} km")
        print("=" * 40)

         # ==============================================================================
        # FLUID MECHANICS & PRESSURE LAYER (EN SONDA RAPORLAMA)
        # ==============================================================================
        print("\n" + "-" * 40)
        print("       FLUID MECHANICS & PRESSURE REPORT       ")
        print("-" * 40)
        
        # 1. Dynamic Pressure (q = 0.5 * r * V^2)
        dynamic_pressure = 0.5 * r * velocity ** 2
        print(f"-> Dynamic Pressure (q)       : {dynamic_pressure:.2f} Pa")
        
        # 2. Mach Number (M = V / a)
        speed_of_sound = 340.29  
        mach_number = velocity / speed_of_sound
        print(f"-> Mach Number (M)            : {mach_number:.4f}")
        
        # Sıkıştırılabilirlik kontrolü (Akademik Yorum)
        if mach_number < 0.3:
            print("   * Compressibility          : Subsonic (Incompressible)")
        else:
            print("   * Compressibility          : Subsonic (Compressible effects starting)")
        print("=" * 40)




    # Terminali açık tutma kodu elektrikli if bloğunun sonunda kalabilir
    input("\nPress Enter to exit the simulator...")

elif aircraft_type == "2":
    print("You have selected Fuel / Jet Engine Aircraft (Kerosene Powered).")
    print("=" * 45)
    # Yakıtlı mod kodları ileride buraya gelecek
    input("\nPress Enter to exit the simulator...")
