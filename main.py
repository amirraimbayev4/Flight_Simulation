import customtkinter as ctk
import math
from tkinter import filedialog

# 1. Genel Tema Ayarları (Modern Karanlık Mod)
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class FlightSimulatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Kimliği ve Genişletilmiş Boyutlar
        self.title("Aerospace Technology - Flight Dynamics Simulator v1.2")
        self.geometry("1380x1020")  
        self.resizable(False, False) 

        # ==============================================================================
        # BAŞLIK ŞERİDİ (TOP BANNER)
        # ==============================================================================
        self.title_label = ctk.CTkLabel(
            self, 
            text="AIRCRAFT PERFORMANCE & AERODYNAMICS SIMULATOR", 
            font=ctk.CTkFont(family="Helvetica", size=24, weight="normal"),
            text_color="#3B82F6" 
        )
        self.title_label.pack(padx=20, pady=15)

        # ==============================================================================
        # HAZIR UÇAK PROFİLLERİ (PRESETS) SEÇİM ALANI
        # ==============================================================================
        self.preset_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=8)
        self.preset_frame.pack(fill="x", padx=25, pady=(0, 10))

        self.preset_label = ctk.CTkLabel(
            self.preset_frame, 
            text="⚡ Quick Aircraft Presets:", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FBBF24"
        )
        self.preset_label.pack(side="left", padx=15, pady=10)

        # Hazır uçak seçenekleri
        self.preset_dropdown = ctk.CTkComboBox(
            self.preset_frame, 
            values=["Custom (Manuel Giriş)", "Delivery Drone (İHA)", "Electric Glider (Planör)"],
            command=self.load_preset,
            width=220
        )
        self.preset_dropdown.pack(side="left", padx=10, pady=10)
        self.preset_dropdown.set("Custom (Manuel Giriş)")

        # ==============================================================================
        # ANA PANEL (SOL GİRDİLER VE SAĞ SONUÇLAR)
        # ==============================================================================
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=25, pady=5)

        # ------------------------------------------------------------------------------
        # SOL PANEL: GİRDİLER (INPUT PANEL)
        # ------------------------------------------------------------------------------
        self.input_frame = ctk.CTkScrollableFrame(self.main_container, width=480, label_text="AIRCRAFT & ENVIRONMENT INPUTS")
        self.input_frame.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=10)

        self.entries = {}
        self.labels = {}
        
        # Temel Girdiler
        self.basic_fields = [
            ("Altitude (m)", "e.g., 1500"),
            ("Empty Weight (kg)", "e.g., 5.0"),
            ("Battery Weight (kg)", "e.g., 4.2"),
            ("Payload Weight (kg)", "e.g., 1.8"),
            ("Wing Span (m)", "e.g., 2.5"),
            ("Chord Length (m)", "e.g., 0.32"),
            ("Velocity (m/s)", "e.g., 24"),
            ("Lift Coefficient (Cl)", "e.g., 0.6")
        ]

        # Gelişmiş Girdiler (Başlangıçta gizli)
        self.advanced_fields = [
            ("Drag Coefficient (Cd)", "e.g., 0.042"),
            ("Battery Capacity (Wh)", "e.g., 450")
        ]

        # Temel girdileri ekrana çiziyoruz
        current_row = 0
        for label_text, placeholder_val in self.basic_fields:
            lbl = ctk.CTkLabel(self.input_frame, text=label_text, font=ctk.CTkFont(size=13, weight="normal"))
            lbl.grid(row=current_row, column=0, padx=20, pady=8, sticky="w")
            
            entry = ctk.CTkEntry(self.input_frame, width=160, placeholder_text=placeholder_val)
            entry.grid(row=current_row, column=1, padx=20, pady=8, sticky="e")
            
            self.entries[label_text] = entry
            current_row += 1

        # Gelişmiş girdileri oluşturuyoruz
        for label_text, placeholder_val in self.advanced_fields:
            lbl = ctk.CTkLabel(self.input_frame, text=label_text, text_color="#FBBF24", font=ctk.CTkFont(size=13, weight="bold"))
            entry = ctk.CTkEntry(self.input_frame, width=160, border_color="#FBBF24", placeholder_text=placeholder_val)
            
            self.labels[label_text] = lbl
            self.entries[label_text] = entry

        # ------------------------------------------------------------------------------
        # SAĞ PANEL: DIJITAL EKRAN (OUTPUT PANEL)
        # ------------------------------------------------------------------------------
        self.output_frame = ctk.CTkFrame(self.main_container, width=720)
        self.output_frame.pack(side="right", fill="both", expand=True, padx=(15, 0), pady=10)

        self.output_title = ctk.CTkLabel(self.output_frame, text="FLIGHT REPORT", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FBBF24")
        self.output_title.pack(padx=15, pady=15)

        self.output_text = ctk.CTkTextbox(
            self.output_frame, 
            font=ctk.CTkFont(family="Consolas", size=12), 
            fg_color="#1E1E1E", 
            text_color="#10B981" 
        )
        self.output_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.output_text.insert("0.0", "Select a preset or enter core inputs manually, then press 'RUN SIMULATION'.\nIf takeoff conditions are met, advanced parameters will unlock dynamically!")
        self.output_text.configure(state="disabled") 

        # ==============================================================================
        # ALT PANEL: TETİKLEYİCİ BUTON (RUN BUTTON)
        # ==============================================================================
        self.run_button = ctk.CTkButton(
            self, 
            text="RUN FLIGHT SIMULATION", 
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color="#2563EB", 
            hover_color="#1D4ED8", 
            command=self.calculate_flight_physics
        )
        self.run_button.pack(fill="x", padx=25, pady=(10, 20))

    # ==============================================================================
    # ✈️ HAZIR UÇAK PROFİLLERİNİ YÜKLEME FONKSİYONU
    # ==============================================================================
    def load_preset(self, choice):
        presets_data = {
            "Delivery Drone (İHA)": {
                "Altitude (m)": "100",
                "Empty Weight (kg)": "3.5",
                "Battery Weight (kg)": "2.0",
                "Payload Weight (kg)": "1.5",
                "Wing Span (m)": "2.2",       # 2.0 -> 2.2 m yapıldı
                "Chord Length (m)": "0.28",     # 0.25 -> 0.28 m yapıldı (Kanat alanı büyüdü) Çünkü kod çalıştığında uçağ ağır geliyordu ve lift yetersizdi. Bu yüzden kanat alanını büyüttük.
                "Velocity (m/s)": "20",         # 18 -> 20 m/s yapıldı
                "Lift Coefficient (Cl)": "0.65",# 0.55 -> 0.65 yapıldı
                "Drag Coefficient (Cd)": "0.035",
                "Battery Capacity (Wh)": "300"
            },
            "Electric Glider (Planör)": {
                "Altitude (m)": "500",
                "Empty Weight (kg)": "2.0",
                "Battery Weight (kg)": "1.0",
                "Payload Weight (kg)": "0.2",
                "Wing Span (m)": "3.2",
                "Chord Length (m)": "0.20",
                "Velocity (m/s)": "15",
                "Lift Coefficient (Cl)": "0.80",
                "Drag Coefficient (Cd)": "0.020",
                "Battery Capacity (Wh)": "150"
            }
        }

        if choice in presets_data:
            data = presets_data[choice]
            for key, val in data.items():
                if key in self.entries:
                    self.entries[key].delete(0, "end")
                    self.entries[key].insert(0, val)
            
            # Gelişmiş kutuların gizliliğini açıp değerleri dolduralım
            start_row = len(self.basic_fields)
            for field, _ in self.advanced_fields:
                self.labels[field].grid(row=start_row, column=0, padx=20, pady=8, sticky="w")
                self.entries[field].grid(row=start_row, column=1, padx=20, pady=8, sticky="e")
                start_row += 1
            self.update_idletasks()



    # ==============================================================================
    # 📁 RAPORU BİLGİSAYARA KAYDETME FONKSİYONU
    # ==============================================================================
    def export_report_to_txt(self):
        # Textbox içindeki yazıyı alıyoruz
        report_content = self.output_text.get("0.0", "end")
        
        # Kullanıcıya dosyayı nereye kaydetmek istediğini soran pencere açıyoruz
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Flight Report"
        )
        
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(report_content)

    # ==============================================================================
    # 🧠 THE FLIGHT PHYSICS ENGINE (AKILLI DİNAMİK MOTOR)
    # ==============================================================================
    def calculate_flight_physics(self):
        try:
            # Kutulardaki Değerleri Okuma ve Sayıya Çevirme
            altitude = float(self.entries["Altitude (m)"].get())
            empty_w = float(self.entries["Empty Weight (kg)"].get())
            battery_w = float(self.entries["Battery Weight (kg)"].get())
            payload_w = float(self.entries["Payload Weight (kg)"].get())
            wing_span = float(self.entries["Wing Span (m)"].get())
            chord = float(self.entries["Chord Length (m)"].get())
            velocity = float(self.entries["Velocity (m/s)"].get())
            cl = float(self.entries["Lift Coefficient (Cl)"].get())

            # Temel Aerodinamik Hesaplar
            r = 1.225 * (1 - 0.00002256 * altitude) ** 4.256
            toplam_kitle = empty_w + battery_w + payload_w
            w = toplam_kitle * 9.81
            
            wing_area = wing_span * chord
            Lift = 0.5 * r * (velocity ** 2) * wing_area * cl
            
            cl_max = 1.5 #Bu değer aslında tamamen varsayım beeli bir aralık içinde değişebilir. İleride eğer kanat profilleri ekerlsem bu değerleri de değştiricem.
            v_stall = math.sqrt((2 * w) / (r * wing_area * cl_max))

            is_lift_enough = Lift >= w
            is_cl_valid = cl <= cl_max#Bunu eklememizin sebebi , eğer Cl değeri Cl max değerinden fazlaysa uçak stall olur ve uçak uçamaz.(Yeni bir bilgi daha öğrendim ve bunu eklemenin mantıklı olduğunu düşündüm.)
            is_speed_safe = velocity >= v_stall

            report = ""
            report += "=============================================\n"
            report += "       ENVIRONMENT & ATMOSPHERE LAYER      \n"
            report += "=============================================\n"
            report += f"-> Air Density (ρ) : {r:.4f} kg/m^3\n"
            report += f"-> Total Aircraft Weight (W) : {w:.2f} N\n"
            report += "---------------------------------------------\n"

            # EĞER UÇAK UÇAMIYORSA (FAILED)
            if not (is_lift_enough and is_speed_safe and is_cl_valid):
                for field, _ in self.advanced_fields:
                    self.labels[field].grid_forget()
                    self.entries[field].grid_forget()

                report += "\n=============================================\n"
                report += "FLIGHT STATUS: FAILED! ❌ The aircraft CANNOT fly.\n"
                report += "=============================================\n"
                report += "[DIAGNOSTIC REPORT & FIXES]:\n"
                if not is_lift_enough:
                    report += f"  -> ISSUE: Insufficient Lift Force! Short by {w - Lift:.2f} N.\n"
                    report += "     FIX  : Increase wing span, chord length, or velocity.\n"
                if not is_speed_safe:
                    report += f"  -> ISSUE: STALL RISK! Your speed ({velocity:.2f} m/s) is below safety limit.\n"
                    report += f"     REQUIRED: Fly at least {v_stall:.2f} m/s ({v_stall * 3.6:.1f} km/h).\n"
                if not is_cl_valid:
                    report += f"  -> ISSUE: Cl ({cl}) exceeds Cl_max ({cl_max}). Wing would stall.\n"
                    report += "     FIX  : Lower Cl or use a higher-lift airfoil/flap.\n"

                report += "\n-> Advanced parameters (Cd, Wh) locked due to flight failure.\n"
                report += "=============================================\n"
                
            # EĞER UÇAK GÜVENLİCE UÇUYORSA (SUCCESS)    
            else:
                report += "=============================================\n"
                report += "FLIGHT STATUS: SUCCESS! 🛫 Modelled steady-flight checks passed.\n"
                report += "=============================================\n"
                
                # Gizli kutuları ekrana çiz (grid et)
                start_row = len(self.basic_fields)
                for field, _ in self.advanced_fields:
                    self.labels[field].grid(row=start_row, column=0, padx=20, pady=8, sticky="w")
                    self.entries[field].grid(row=start_row, column=1, padx=20, pady=8, sticky="e")
                    start_row += 1

                self.update_idletasks()

                if self.entries["Drag Coefficient (Cd)"].get() == "" or self.entries["Battery Capacity (Wh)"].get() == "":
                    report += "-> Advanced parameters (Cd, Wh) have been unlocked below!\n"
                    report += "-> ACTION REQUIRED: Please enter values for Cd and Wh in the left panel,\n"
                    report += "   then press 'RUN FLIGHT SIMULATION' again for full analytics.\n"
                    report += "=============================================\n"
                else:
                    cd = float(self.entries["Drag Coefficient (Cd)"].get())
                    battery_capacity_wh = float(self.entries["Battery Capacity (Wh)"].get())
                    
                    report += "-> Advanced inputs loaded successfully! Generating full report...\n"
                    report += "---------------------------------------------\n"
                    
                    Drag = 0.5 * r * (velocity ** 2) * wing_area * cd
                    required_power = Drag * velocity
                    efficiency = 0.70
                    power_electrical = required_power / efficiency
                    
                    flight_time_hours = battery_capacity_wh / power_electrical
                    flight_time_minutes = flight_time_hours * 60
                    range_km = velocity * flight_time_hours * 3.6

                    report += f"-> Generated Lift Force (L)  : {Lift:.2f} N\n"
                    report += f"-> Generated Drag Force (D)  : {Drag:.2f} N\n"
                    report += f"-> Total Electrical Power Draw: {power_electrical:.2f} W\n"
                    report += "---------------------------------------------\n"
                    report += "          TIME & RANGE CALCULATIONS          \n"
                    report += "---------------------------------------------\n"
                    report += f"Estimated Flight Time : {flight_time_hours:.2f} hours ({flight_time_minutes:.1f} minutes)\n"
                    report += f"Estimated Stall Speed : {v_stall:.2f} m/s\n"
                    report += f"Estimated Max Range   : {range_km:.2f} km\n"
                    
                    # ADVANCED FLUID MECHANICS REPORT
                    report += "\n=============================================\n"
                    report += "   ADVANCED AERODYNAMICS & FLUID MECHANICS   \n"
                    report += "=============================================\n"
                    p_static = 101325 * (1 - 0.00002256 * altitude) ** 5.256
                    p_total = p_static + (0.5 * r * velocity ** 2)
                    wing_loading = w / wing_area# Kanadın 1 m²'sine düşen ağırlık miktarı Değer küçükse uçak daha yavaş uçabilir ve daha iyi manevra kabiliyetine sahip olur. Değer büyükse uçak daha hızlı uçabilir ama manevra kabiliyeti düşer.
                    aspect_ratio = wing_span / chord
                    oswald_efficiency = 0.85
                    cd_induced = (cl ** 2) / (math.pi * aspect_ratio * oswald_efficiency)
                    cd_parasite = cd - cd_induced
                    mu = 1.789e-5
                    reynolds = (r * velocity * chord) / mu
                    speed_of_sound = math.sqrt(1.4 * 287.05 * (288.15 - 0.0065 * altitude))
                    mach_number = velocity / speed_of_sound

                    report += "\n=============================================\n"
                    report += "              ASSUMPTIONS USED               \n"
                    report += "=============================================\n"
                    report += f"-> Max Lift Coefficient (Cl_max) : {cl_max:.2f}\n"
                    report += f"-> Oswald Efficiency (e)         : {oswald_efficiency:.2f}\n"
                    report += f"-> Propulsion Efficiency (eta)   : {efficiency:.2f}\n"
                    report += "=============================================\n"

                    report += f"-> Static Ambient Pressure   : {p_static:.2f} Pa\n"
                    report += f"-> Bernoulli Total Pressure  : {p_total:.2f} Pa\n"
                    report += f"-> Wing Loading (W/S)        : {wing_loading:.2f} N/m²\n"
                    report += f"-> Wing Aspect Ratio (AR)    : {aspect_ratio:.2f}\n"
                    report += f"-> Parasite Drag Coeff (Cd0) : {max(0.0, cd_parasite):.4f}\n"
                    report += f"-> Induced Drag Coeff (Cdi)  : {cd_induced:.4f}\n"
                    report += f"-> Reynolds Number (Re)      : {reynolds:.1f}\n"
                    report += f"-> Mach Number (M)           : {mach_number:.4f}\n"
                    report += f"-> Cruise Thrust Required (T): {Drag:.2f} N\n"
                    report += "=============================================\n"

            # Ekrana Raporu Basma
            self.output_text.configure(state="normal")
            self.output_text.delete("0.0", "end")
            self.output_text.insert("0.0", report)
            self.output_text.configure(state="disabled")
        except ValueError:
            self.output_text.configure(state="normal")
            self.output_text.delete("0.0", "end")
            self.output_text.insert("0.0", "ERROR: Please make sure all input fields contain valid numerical values!")
            self.output_text.configure(state="disabled")

if __name__ == "__main__":
    app = FlightSimulatorGUI()
    app.mainloop()