import customtkinter as ctk
import math
from tkinter import filedialog

# 1. Genel Tema Ayarları (Modern Karanlık Mod)
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

# ==============================================================================
# 📈 SPEED SWEEP + GRAPH (Range & Endurance vs Airspeed)
# ------------------------------------------------------------------------------
# Fikir: Sabit irtifada düz uçuşta kaldırma = ağırlık olmak zorunda. Hız değişince
#        gereken Cl değişir:  Cl = 2W / (rho * V^2 * S)
#        Sürükleme:           Cd = Cd0 + k * Cl^2   (k = 1 / (pi * AR * e))
#        Düşük hızda indüklenmiş sürükleme, yüksek hızda parazit sürükleme baskın
#        olur -> toplam sürükleme U şeklinde çıkar -> en verimli hız bir tepe noktası.
# ==============================================================================
def build_speed_sweep(sim, points=500):
    import numpy as np

    rho, W, S = sim["rho"], sim["W"], sim["S"]
    k, cd0 = sim["k"], sim["cd0"]
    eta, wh = sim["eta"], sim["wh"]
    v_stall = sim["v_stall"]

    # Stall hızından başlayıp kullanıcının hızının ~1.6 katına kadar tara
    v_max = max(sim["velocity"] * 1.6, v_stall * 2.6)
    v = np.linspace(v_stall, v_max, points)

    cl_req = 2 * W / (rho * v ** 2 * S)          # her hızda gereken Cl
    q_s = 0.5 * rho * v ** 2 * S                 # dinamik basınç * kanat alanı
    d_parasite = q_s * cd0
    d_induced = q_s * k * cl_req ** 2
    drag = d_parasite + d_induced

    power_elec = drag * v / eta                  # W
    hours = wh / power_elec
    return {
        "v": v,
        "cl": cl_req,
        "d_par": d_parasite,
        "d_ind": d_induced,
        "drag": drag,
        "power": power_elec,
        "minutes": hours * 60,
        "range_km": v * hours * 3.6,
    }


def draw_range_figure(sim):
    from matplotlib.figure import Figure
    import numpy as np

    BG, PANEL, GRID = "#242424", "#1E1E1E", "#34373E"
    TEXT, MUTED = "#E5E7EB", "#9CA3AF"
    BLUE, GREEN, AMBER, RED = "#3B82F6", "#10B981", "#FBBF24", "#EF4444"

    s = build_speed_sweep(sim)
    v, rng, mins, drag = s["v"], s["range_km"], s["minutes"], s["drag"]
    i_r = int(np.argmax(rng))       # en uzun menzil
    i_e = int(np.argmax(mins))      # en uzun uçuş süresi
    i_d = int(np.argmin(drag))      # en düşük sürükleme (teoride i_r ile aynı)

    v_stall, v_user = sim["v_stall"], sim["velocity"]
    x_min, x_max = v_stall * 0.82, v[-1]

    fig = Figure(figsize=(10, 7.6), dpi=100, facecolor=BG)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.3, 1], hspace=0.30,
                          left=0.085, right=0.915, top=0.80, bottom=0.12)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    def style(ax, grid=True):
        ax.set_facecolor(PANEL)
        for sp in ax.spines.values():
            sp.set_color(GRID)
        ax.tick_params(colors=MUTED, labelsize=9)
        if grid:
            ax.grid(True, color=GRID, alpha=0.7, linewidth=0.7)
            ax.set_axisbelow(True)

    # ------------------------------------------------------------------
    # ÜST GRAFİK: Menzil (mavi) ve Uçuş Süresi (yeşil) - hıza karşı
    # ------------------------------------------------------------------
    style(ax1)
    ax1b = ax1.twinx()
    style(ax1b, grid=False)

    ax1.plot(v, rng, color=BLUE, lw=2.8, label="Range (km)", zorder=3)
    ax1.fill_between(v, rng, color=BLUE, alpha=0.12, zorder=2)
    ax1b.plot(v, mins, color=GREEN, lw=2.4, label="Endurance (min)", zorder=3)

    r_top, e_top = rng.max() * 1.50, mins.max() * 1.50
    ax1.set_ylim(0, r_top)
    ax1b.set_ylim(0, e_top)
    ax1.set_xlim(x_min, x_max)
    ax1.set_ylabel("Range (km)", color=BLUE, fontsize=10.5, weight="bold")
    ax1b.set_ylabel("Endurance (min)", color=GREEN, fontsize=10.5, weight="bold")
    ax1.tick_params(axis="y", colors=BLUE)
    ax1b.tick_params(axis="y", colors=GREEN)

    # Stall bölgesi (uçulamaz)
    ax1.axvspan(x_min, v_stall, color=RED, alpha=0.18, lw=0, zorder=1)
    ax1.text((x_min + v_stall) / 2, r_top * 0.5, "STALL ZONE", rotation=90,
             ha="center", va="center", color=RED, fontsize=9, weight="bold")

    # Kullanıcının girdiği hız
    ax1.axvline(v_user, color=AMBER, ls="--", lw=1.5, zorder=2)
    r_user = float(np.interp(v_user, v, rng))
    ax1.scatter([v_user], [r_user], s=60, color=AMBER, edgecolor=BG, zorder=6)
    ax1.text(v_user, r_top * 0.97, f" Your speed\n {v_user:.1f} m/s", color=AMBER,
             fontsize=9, va="top", ha="left")

    # En uzun menzil noktası
    ax1.scatter([v[i_r]], [rng[i_r]], s=260, marker="*", color=AMBER,
                edgecolor=BG, linewidth=1.2, zorder=7)
    ax1.annotate(
        f"MAX RANGE\n{rng[i_r]:.0f} km @ {v[i_r]:.1f} m/s ({v[i_r] * 3.6:.0f} km/h)",
        xy=(v[i_r], rng[i_r]), xytext=(55, -75), textcoords="offset points",
        color=TEXT, fontsize=9.5, weight="bold",
        bbox=dict(boxstyle="round,pad=0.45", fc=BG, ec=BLUE, lw=1.4),
        arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.4), zorder=8)

    # En uzun uçuş süresi noktası
    ax1b.scatter([v[i_e]], [mins[i_e]], s=260, marker="*", color=GREEN,
                 edgecolor=BG, linewidth=1.2, zorder=7)
    ax1b.annotate(
        f"MAX ENDURANCE\n{mins[i_e]:.0f} min @ {v[i_e]:.1f} m/s",
        xy=(v[i_e], mins[i_e]), xytext=(-20, 30), textcoords="offset points",
        ha="right", color=TEXT, fontsize=9.5, weight="bold",
        bbox=dict(boxstyle="round,pad=0.45", fc=BG, ec=GREEN, lw=1.4),
        arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.4), zorder=8)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax1b.get_legend_handles_labels()
    leg = ax1.legend(h1 + h2, l1 + l2, loc="lower right", facecolor=BG,
                     edgecolor=GRID, fontsize=9, labelcolor=TEXT)
    leg.set_zorder(10)

    # Üstte ikinci eksen: km/h
    top = ax1.secondary_xaxis("top", functions=(lambda x: x * 3.6, lambda x: x / 3.6))
    top.set_xlabel("Airspeed (km/h)", color=MUTED, fontsize=9.5)
    top.tick_params(colors=MUTED, labelsize=9)
    for sp in top.spines.values():
        sp.set_color(GRID)
    ax1.tick_params(labelbottom=False)

    # ------------------------------------------------------------------
    # ALT GRAFİK: Sürükleme bileşenleri (U şekli) - hıza karşı
    # ------------------------------------------------------------------
    style(ax2)
    ax2.plot(v, s["d_par"], color=BLUE, ls="--", lw=1.9, label="Parasite drag (grows with V²)")
    ax2.plot(v, s["d_ind"], color=RED, ls="--", lw=1.9, label="Induced drag (falls with V²)")
    ax2.plot(v, drag, color=AMBER, lw=2.9, label="Total drag", zorder=4)
    ax2.fill_between(v, drag, color=AMBER, alpha=0.08)
    ax2.axvspan(x_min, v_stall, color=RED, alpha=0.18, lw=0)

    d_top = drag.max() * 1.70
    ax2.set_ylim(0, d_top)
    ax2.set_xlabel("Airspeed (m/s)", color=MUTED, fontsize=10.5)
    ax2.set_ylabel("Drag (N)", color=AMBER, fontsize=10.5, weight="bold")
    ax2.tick_params(axis="y", colors=AMBER)

    ax2.scatter([v[i_d]], [drag[i_d]], s=240, marker="*", color=AMBER,
                edgecolor=BG, linewidth=1.2, zorder=7)
    ax2.annotate(
        f"MIN DRAG {drag[i_d]:.2f} N @ {v[i_d]:.1f} m/s\n= best-range speed",
        xy=(v[i_d], drag[i_d]), xytext=(-70, 70), textcoords="offset points",
        color=TEXT, fontsize=9.5, weight="bold",
        bbox=dict(boxstyle="round,pad=0.45", fc=BG, ec=AMBER, lw=1.4),
        arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.4), zorder=8)

    # Aynı hızları üst grafikle bağlayan ince çizgiler
    for ax in (ax1, ax2):
        ax.axvline(v[i_r], color=BLUE, ls=":", lw=1.2, alpha=0.8, zorder=1)
        ax.axvline(v[i_e], color=GREEN, ls=":", lw=1.2, alpha=0.8, zorder=1,
                   label="Best-endurance speed (min power)" if ax is ax2 else None)

    leg2 = ax2.legend(loc="upper right", facecolor=BG, edgecolor=GRID, fontsize=9, labelcolor=TEXT)
    leg2.set_zorder(10)

    # ------------------------------------------------------------------
    # Başlık ve dipnotlar
    # ------------------------------------------------------------------
    fig.text(0.5, 0.955, "RANGE & ENDURANCE vs. AIRSPEED", ha="center",
             color=BLUE, fontsize=17, weight="bold")
    fig.text(0.5, 0.915,
             f"Steady level flight  •  Mass {sim['mass']:.1f} kg  •  Wing area {sim['S']:.2f} m²  •  "
             f"Aspect ratio {sim['AR']:.1f}  •  Battery {sim['wh']:.0f} Wh  •  η = {sim['eta']:.2f}",
             ha="center", color=MUTED, fontsize=9.5)
    fig.text(0.5, 0.038,
             "Model: Cd = Cd0 + k·Cl²,  Cl = 2W/(ρV²S) at every speed.   "
             f"Cd0 = {sim['cd0']:.4f} (from your Cd),  Oswald e = {sim['e']:.2f} (assumed).",
             ha="center", color=MUTED, fontsize=8.5)
    fig.text(0.5, 0.014,
             "Battery treated as 100% usable and avionics power ignored, so absolute values are optimistic; "
             "the SHAPE of the curves is the point.",
             ha="center", color=MUTED, fontsize=8.5, style="italic")
    return fig



class FlightSimulatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Kimliği ve Genişletilmiş Boyutlar
        self.title("Aerospace Technology - Flight Dynamics Simulator v1.2")
        self.geometry("1200x800")  
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
        self.input_frame.pack(side="left", fill="y", expand=False, padx=(0, 15), pady=10)

        self.entries = {}
        self.report_ready = False
        self.last_sim = None   # grafik için son başarılı simülasyonun verileri
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
            ("Battery Capacity (Wh)", "e.g., 450"),
            ("Propulsion Efficiency (0-1)", "e.g., 0.70"),
        ]

        # Temel girdileri ekrana çiziyoruz
        current_row = 0
        for label_text, placeholder_val in self.basic_fields:
            lbl = ctk.CTkLabel(self.input_frame, text=label_text, font=ctk.CTkFont(size=13, weight="normal"))
            lbl.grid(row=current_row, column=0, padx=20, pady=8, sticky="w")
            self.labels[label_text] = lbl
            
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
        self.output_frame = ctk.CTkFrame(self.main_container, width=1000)
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
        self.run_button.pack(side="left", padx=20, pady=10)
        self.save_button = ctk.CTkButton(
            self,
            text="SAVE REPORT 💾",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color="#059669",
            hover_color="#047857",
            command=self.export_report_to_txt
        )
        self.save_button.pack(side="left", padx=20, pady=10)
        self.graph_button = ctk.CTkButton(
            self,
            text="RANGE GRAPH 📈",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            command=self.open_range_graph
        )
        self.graph_button.pack(side="left", padx=20, pady=10)

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
                "Battery Capacity (Wh)": "300",
                "Propulsion Efficiency (0-1)": "0.70"
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
                "Battery Capacity (Wh)": "150",
                "Propulsion Efficiency (0-1)": "0.70"
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
        if not self.report_ready:
            return
        else:
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
    # 📈 GRAFİK PENCERESİ
    # ==============================================================================
    def show_message(self, text):
        self.output_text.configure(state="normal")
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", text)
        self.output_text.configure(state="disabled")

    def open_range_graph(self):
        # Grafik, tam raporun (Cd, Wh, verimlilik girilmiş) başarıyla çıkmış olmasını ister
        if self.last_sim is None:
            self.show_message(
                "GRAPH NOT AVAILABLE YET.\n\n"
                "1) Enter your inputs (or pick a preset) and press 'RUN FLIGHT SIMULATION'.\n"
                "2) If the aircraft can fly, fill Cd, Battery Capacity and Propulsion Efficiency.\n"
                "3) Run again to get the full report, then press 'RANGE GRAPH'."
            )
            return

        if self.last_sim["cd0"] <= 0.001:
            self.show_message(
                "GRAPH NOT AVAILABLE: your Cd is too low.\n\n"
                f"At Cl = {self.last_sim['cl_input']:.2f} the induced drag alone is "
                f"{self.last_sim['k'] * self.last_sim['cl_input'] ** 2:.4f}, "
                f"but you entered Cd = {self.last_sim['cd_input']:.4f}.\n"
                "Total Cd must be larger than induced drag. Increase Cd and run again."
            )
            return

        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            fig = draw_range_figure(self.last_sim)
        except ImportError:
            self.show_message("matplotlib is missing. Install it with:\n\n    pip install matplotlib")
            return

        win = ctk.CTkToplevel(self)
        win.title("Range & Endurance Analysis")
        win.geometry("1050x840")

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(10, 5))

        save_png = ctk.CTkButton(
            win,
            text="SAVE GRAPH AS PNG 🖼️",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            fg_color="#059669",
            hover_color="#047857",
            command=lambda: self.save_graph_png(fig)
        )
        save_png.pack(pady=(0, 12))

        win.after(200, win.lift)   # pencere ana pencerenin arkasında kalmasın
        win.focus()

    def save_graph_png(self, fig):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
            title="Save Graph"
        )
        if file_path:
            fig.savefig(file_path, dpi=200, facecolor=fig.get_facecolor())

    # ==============================================================================
    # 🧠 THE FLIGHT PHYSICS ENGINE (AKILLI DİNAMİK MOTOR)
    # ==============================================================================
    def calculate_flight_physics(self):
        self.last_sim = None
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

                if self.entries["Drag Coefficient (Cd)"].get() == "" or self.entries["Battery Capacity (Wh)"].get() == "" or self.entries["Propulsion Efficiency (0-1)"].get() == "":
                    report += "-> Advanced parameters (Cd, Wh) have been unlocked below!\n"
                    report += "-> ACTION REQUIRED: Please enter values for Cd and Wh in the left panel,\n"
                    report += "   then press 'RUN FLIGHT SIMULATION' again for full analytics.\n"
                    report += "=============================================\n"
                else:
                    cd = float(self.entries["Drag Coefficient (Cd)"].get())
                    battery_capacity_wh = float(self.entries["Battery Capacity (Wh)"].get())
                    propulsion_efficiency = float(self.entries["Propulsion Efficiency (0-1)"].get())
                    
                    if not (0 < propulsion_efficiency <= 1):
                                            report += "-> ERROR: Propulsion efficiency must be between 0 and 1 (e.g., 0.70, not 70).\n"
                                            report += "=============================================\n"
                    else:
                                        # buradaki her şey (Drag hesabı, rapor satırları...) bir tab içeri girecek
                        report += "-> Advanced inputs loaded successfully! Generating full report...\n"
                        report += "---------------------------------------------\n"
                        
                        Drag = 0.5 * r * (velocity ** 2) * wing_area * cd
                        required_power = Drag * velocity
                        power_electrical = required_power / propulsion_efficiency
                        

                    
                        
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
                        report += f"Estimated Range (at your speed): {range_km:.2f} km\n"
                        report += "-> Tip: press 'RANGE GRAPH' to find the speed with the longest range.\n"


                        
                        
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

                        # Grafik penceresi için son simülasyonun verileri
                        self.last_sim = {
                            "rho": r, "W": w, "S": wing_area, "AR": aspect_ratio,
                            "e": oswald_efficiency,
                            "k": 1 / (math.pi * aspect_ratio * oswald_efficiency),
                            "cd0": cd_parasite,            # Cd - indüklenmiş sürükleme
                            "cd_input": cd, "cl_input": cl,
                            "eta": propulsion_efficiency, "wh": battery_capacity_wh,
                            "mass": toplam_kitle, "velocity": velocity, "v_stall": v_stall,
                        }
        
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
                        report += "\n=============================================\n"
                        report += "              ASSUMPTIONS USED               \n"
                        report += "=============================================\n"
                        report += f"-> Max Lift Coefficient (Cl_max) : {cl_max:.2f}\n"
                        report += f"-> Oswald Efficiency (e)         : {oswald_efficiency:.2f}\n"
                        report += f"-> Propulsion Efficiency (eta)   : {propulsion_efficiency:.2f}\n"
                        report += "=============================================\n"                       

            # Ekrana Raporu Basma
            self.output_text.configure(state="normal")
            self.output_text.delete("0.0", "end")
            self.output_text.insert("0.0", report)
            self.report_ready = True
            self.output_text.configure(state="disabled")
        except ValueError:
            self.report_ready = False
            self.output_text.configure(state="normal")
            self.output_text.delete("0.0", "end")
            self.output_text.insert("0.0", "ERROR: Please make sure all input fields contain valid numerical values!")
            self.output_text.configure(state="disabled")

if __name__ == "__main__":
    app = FlightSimulatorGUI()
    app.mainloop()