import customtkinter as ctk

# 1. Genel Tema Ayarları (Modern Karanlık Mod)
ctk.set_appearance_mode("Dark")  # Havacılık yazılımlarına en çok yakışan koyu tema
ctk.set_default_color_theme("blue")  # Detaylar ve butonlar kurumsal mavi

class FlightSimulatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Kimliği
        self.title("NTHU Aerospace Technology - Flight Dynamics Simulator v1.0")
        self.geometry("900x700")  # Ekranı rahat görmek için genişlik ve yükseklik
        self.resizable(False, False) # Kullanıcı pencere boyutunu bozamasın, tasarım sabit kalsın

        # ==============================================================================
        # BAŞLIK ŞERİDİ (TOP BANNER)
        # ==============================================================================
        self.title_label = ctk.CTkLabel(
            self, 
            text="AIRCRAFT PERFORMANCE & AERODYNAMICS SIMULATOR", 
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color="#3B82F6" # Parlak teknoloji mavisi
        )
        self.title_label.pack(padx=20, pady=20)

        # ==============================================================================
        # ANA PANEL (SOL VE SAĞ OLARAK İKİYE BÖLÜYORUZ)
        # ==============================================================================
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # ------------------------------------------------------------------------------
        # SOL PANEL: GİRDİLER (INPUT PANEL)
        # ------------------------------------------------------------------------------
        self.input_frame = ctk.CTkScrollableFrame(self.main_container, width=400, label_text="AIRCRAFT & ENVIRONMENT INPUTS")
        self.input_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        # Girdi Kutularını ve Etiketlerini Düzenli Eklemek İçin Bir Fonksiyon Kullanacağız
        self.entries = {}
        
        # Ekleyeceğimiz tüm girdilerin listesi ve varsayılan (default) test değerleri
        input_fields = [
            ("Altitude (m)", "1500"),
            ("Empty Weight (kg)", "5.0"),
            ("Battery Weight (kg)", "4.2"),
            ("Payload Weight (kg)", "1.8"),
            ("Wing Span (m)", "2.5"),
            ("Chord Length (m)", "0.32"),
            ("Velocity (m/s)", "24"),
            ("Lift Coefficient (Cl)", "0.6"),
            ("Drag Coefficient (Cd)", "0.042"),
            ("Battery Capacity (Wh)", "450")
        ]

        # Izgara (Grid) mantığıyla kutuları alt alta diziyoruz
        for i, (label_text, default_val) in enumerate(input_fields):
            # Etiket (Yazı)
            lbl = ctk.CTkLabel(self.input_frame, text=label_text, font=ctk.CTkFont(size=13, weight="normal"))
            lbl.grid(row=i, column=0, padx=15, pady=8, sticky="w")
            
            # Girdi Kutusu (Entry)
            entry = ctk.CTkEntry(self.input_frame, width=150, placeholder_text=default_val)
            entry.insert(0, default_val) # Test kolaylığı için içlerini otomatik doldursun
            entry.grid(row=i, column=1, padx=15, pady=8, sticky="e")
            
            # İleride verileri çekebilmek için hafızaya kaydediyoruz
            self.entries[label_text] = entry

        # ------------------------------------------------------------------------------
        # SAĞ PANEL: SONUÇLAR VE RAPORLAMA (OUTPUT PANEL)
        # ------------------------------------------------------------------------------
        self.output_frame = ctk.CTkFrame(self.main_container, width=420)
        self.output_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=10)

        # Sonuç Başlığı
        self.output_title = ctk.CTkLabel(
            self.output_frame, 
            text="FLIGHT REPORT", 
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.output_title.pack(padx=15, pady=15)

        # Sonuçların basılacağı o şık terminal benzeri geniş metin alanı (Textbox)
        self.output_text = ctk.CTkTextbox(
            self.output_frame, 
            font=ctk.CTkFont(family="Consolas", size=12), # Mühendislik yazı tipi
            fg_color="#1E1E1E", # Kod editörü siyahı
            text_color="#10B981" # Mat yeşil dijital yazı rengi
        )
        self.output_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.output_text.insert("0.0", "Enter inputs and press 'RUN SIMULATION' to generate flight analytics...")
        self.output_text.configure(state="disabled") # Kullanıcı elle burayı değiştiremesin

        # ==============================================================================
        # ALT PANEL: TETİKLEYİCİ BUTON (RUN BUTTON)
        # ==============================================================================
        self.run_button = ctk.CTkButton(
            self, 
            text="RUN FLIGHT SIMULATION", 
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color="#2563EB", # Güçlü mavi
            hover_color="#1D4ED8", # Üzerine gelince koyulaşan mavi
            command=self.run_simulation_trigger
        )
        self.run_button.pack(fill="x", padx=20, pady=(10, 20))

    def run_simulation_trigger(self):
        """ Butona basıldığında çalışacak olan geçici tetikleyici fonksiyon """
        self.output_text.configure(state="normal")
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", "Simulation triggered successfully!\nConnecting to Flight Physics Engine...")
        self.output_text.configure(state="disabled")

if __name__ == "__main__":
    app = FlightSimulatorGUI()
    app.mainloop()
