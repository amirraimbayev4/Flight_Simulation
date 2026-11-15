import customtkinter as ctk
import math
import os
from datetime import datetime
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

    BG, PANEL, GRID = "#0B0F19", "#11151F", "#2A3040"
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



# ==============================================================================
# ✈️ HAZIR UÇAK PROFİLLERİ (simülatör ve karşılaştırma sayfası ortak kullanır)
# ==============================================================================
PRESETS = {
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


# Yeni örnek konfigürasyonlar: modelde uçabildikleri ve birbirinden farklı bir ödünleşim
# gösterdikleri kontrol edildi. Bunlar GERÇEK uçak değil, eğitim amaçlı örnek değerlerdir.
PRESETS.update({
    "Survey UAV (Haritalama)": {
        "Altitude (m)": "300", "Empty Weight (kg)": "4.0", "Battery Weight (kg)": "2.5",
        "Payload Weight (kg)": "1.0", "Wing Span (m)": "2.6", "Chord Length (m)": "0.30",
        "Velocity (m/s)": "18", "Lift Coefficient (Cl)": "0.60", "Drag Coefficient (Cd)": "0.040",
        "Battery Capacity (Wh)": "450", "Propulsion Efficiency (0-1)": "0.70"
    },
    "Endurance UAV (Uzun Süre)": {
        "Altitude (m)": "1000", "Empty Weight (kg)": "3.0", "Battery Weight (kg)": "3.0",
        "Payload Weight (kg)": "0.6", "Wing Span (m)": "4.0", "Chord Length (m)": "0.25",
        "Velocity (m/s)": "14", "Lift Coefficient (Cl)": "0.85", "Drag Coefficient (Cd)": "0.022",
        "Battery Capacity (Wh)": "540", "Propulsion Efficiency (0-1)": "0.72"
    },
    "Heavy Cargo UAV (Ağır Yük)": {
        "Altitude (m)": "200", "Empty Weight (kg)": "9.0", "Battery Weight (kg)": "6.0",
        "Payload Weight (kg)": "8.0", "Wing Span (m)": "3.4", "Chord Length (m)": "0.45",
        "Velocity (m/s)": "22", "Lift Coefficient (Cl)": "0.70", "Drag Coefficient (Cd)": "0.050",
        "Battery Capacity (Wh)": "1080", "Propulsion Efficiency (0-1)": "0.68"
    },
})


# ==============================================================================
# ⚖️ UÇAK KARŞILAŞTIRMA MOTORU (iki uçağı aynı modelle hesaplar)
# ==============================================================================
ADV_KEYS = ("Drag Coefficient (Cd)", "Battery Capacity (Wh)", "Propulsion Efficiency (0-1)")


def compute_aircraft(p):
    """p: simülatördeki kutularla aynı anahtarlara sahip sözlük. Sonuçları sözlük olarak döndürür."""
    g = lambda key: float(str(p[key]).strip())
    altitude = g("Altitude (m)")
    empty_w, battery_w, payload_w = g("Empty Weight (kg)"), g("Battery Weight (kg)"), g("Payload Weight (kg)")
    span, chord = g("Wing Span (m)"), g("Chord Length (m)")
    velocity, cl = g("Velocity (m/s)"), g("Lift Coefficient (Cl)")

    rho = 1.225 * (1 - 0.00002256 * altitude) ** 4.256
    mass = empty_w + battery_w + payload_w
    W = mass * 9.81
    S = span * chord
    AR = span / chord
    lift = 0.5 * rho * velocity ** 2 * S * cl
    cl_max = 1.5
    v_stall = math.sqrt(2 * W / (rho * S * cl_max))

    problems = []
    if lift < W:
        problems.append(f"Not enough lift (short by {W - lift:.1f} N)")
    if velocity < v_stall:
        problems.append(f"Below stall speed ({v_stall:.1f} m/s needed)")
    if cl > cl_max:
        problems.append(f"Cl above Cl_max ({cl_max})")

    res = {"mass": mass, "payload": payload_w, "S": S, "AR": AR, "wing_loading": W / S,
           "v_stall": v_stall, "problems": problems, "can_fly": not problems, "notes": []}
    if problems:
        return res

    if not all(str(p.get(k, "")).strip() != "" for k in ADV_KEYS):
        res["notes"].append("Cd, battery capacity and efficiency are needed for performance numbers.")
        return res
    cd, wh, eta = g("Drag Coefficient (Cd)"), g("Battery Capacity (Wh)"), g("Propulsion Efficiency (0-1)")
    if not (0 < eta <= 1):
        res["notes"].append("Propulsion efficiency must be between 0 and 1 (e.g., 0.70).")
        return res

    # --- Senin girdilerinle (simülatör raporundaki ile aynı hesap) ---
    drag = 0.5 * rho * velocity ** 2 * S * cd
    power = drag * velocity / eta
    hours = wh / power
    res.update(flight_min=hours * 60, range_km=velocity * hours * 3.6, power=power, ld=cl / cd)

    # --- Optimum hız taraması (grafikteki düz uçuş modeli) ---
    e = 0.85
    k = 1 / (math.pi * AR * e)
    cd0 = cd - k * cl ** 2
    if cd0 <= 0.001:
        res["notes"].append(f"Cd ({cd:g}) is not above the induced drag ({k * cl ** 2:.4f}), "
                            "so optimized values are unavailable. Raise Cd or lower Cl.")
        return res
    v_max = max(velocity * 1.6, v_stall * 2.6)
    n = 400
    best_r, best_e = (0.0, v_stall), (0.0, v_stall)
    for i in range(n):
        v = v_stall + (v_max - v_stall) * i / (n - 1)
        cl_req = 2 * W / (rho * v * v * S)
        d = 0.5 * rho * v * v * S * (cd0 + k * cl_req ** 2)
        hrs = wh / (d * v / eta)
        if v * hrs * 3.6 > best_r[0]:
            best_r = (v * hrs * 3.6, v)
        if hrs * 60 > best_e[0]:
            best_e = (hrs * 60, v)
    res.update(best_range_km=best_r[0], v_best_range=best_r[1],
               best_end_min=best_e[0], v_best_end=best_e[1],
               wh_per_km=wh / best_r[0],
               wh_per_payload_km=(wh / best_r[0] / payload_w) if payload_w > 0 else None)
    res["sim"] = {"rho": rho, "W": W, "S": S, "AR": AR, "e": e, "k": k, "cd0": cd0, "eta": eta,
                  "wh": wh, "mass": mass, "velocity": velocity, "v_stall": v_stall}
    return res


def draw_compare_figure(a, b, name_a, name_b):
    from matplotlib.figure import Figure
    import numpy as np

    BG, PANEL, GRID = "#0B0F19", "#11151F", "#2A3040"
    TEXT, MUTED = "#E5E7EB", "#9CA3AF"
    CA, CB = "#3B82F6", "#A78BFA"

    sweeps = [(build_speed_sweep(a["sim"]), CA, f"A · {name_a}"),
              (build_speed_sweep(b["sim"]), CB, f"B · {name_b}")]

    fig = Figure(figsize=(10, 7.4), dpi=100, facecolor=BG)
    gs = fig.add_gridspec(2, 1, hspace=0.30, left=0.085, right=0.95, top=0.82, bottom=0.145)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    for ax, key, ylabel in ((ax1, "range_km", "Range (km)"), (ax2, "minutes", "Endurance (min)")):
        ax.set_facecolor(PANEL)
        for sp in ax.spines.values():
            sp.set_color(GRID)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.grid(True, color=GRID, alpha=0.7, linewidth=0.7)
        ax.set_axisbelow(True)
        ax.set_ylabel(ylabel, color=TEXT, fontsize=10.5, weight="bold")
        top = 0
        for s, col, label in sweeps:
            ax.plot(s["v"], s[key], color=col, lw=2.8, label=label, zorder=3)
            ax.fill_between(s["v"], s[key], color=col, alpha=0.08, zorder=2)
            i = int(np.argmax(s[key]))
            ax.scatter([s["v"][i]], [s[key][i]], s=240, marker="*", color=col,
                       edgecolor=BG, linewidth=1.2, zorder=7)
            ax.annotate(f"{s[key][i]:.0f} @ {s['v'][i]:.1f} m/s", xy=(s["v"][i], s[key][i]),
                        xytext=(0, 13), textcoords="offset points", ha="center",
                        color=col, fontsize=9.5, weight="bold", zorder=8)
            top = max(top, float(s[key].max()))
        ax.set_ylim(0, top * 1.28)

    leg = ax1.legend(loc="upper right", facecolor=BG, edgecolor=GRID, fontsize=9.5, labelcolor=TEXT)
    leg.set_zorder(10)
    ax1.tick_params(labelbottom=False)
    ax2.set_xlabel("Airspeed (m/s)", color=MUTED, fontsize=10.5)

    fig.text(0.5, 0.945, "AIRCRAFT COMPARISON", ha="center", color=TEXT, fontsize=17, weight="bold")
    fig.text(0.5, 0.905, "Range & endurance vs. airspeed  •  stars mark each aircraft's best speed",
             ha="center", color=MUTED, fontsize=9.5)
    fig.text(0.5, 0.04, "Each curve starts at that aircraft's own stall speed. Model: steady level flight, "
             "Cd = Cd0 + k·Cl², Oswald e = 0.85 (assumed).", ha="center", color=MUTED, fontsize=8.5)
    fig.text(0.5, 0.015, "Battery treated as 100% usable and avionics power ignored, so absolute values "
             "are optimistic; compare the SHAPES and the RATIOS.", ha="center", color=MUTED,
             fontsize=8.5, style="italic")
    return fig


# ==============================================================================
# 🧾 KARŞILAŞTIRMA SATIRLARI (ekran ve dosya kaydı aynı veriyi kullanır)
# ==============================================================================
COMPARE_SPEC = [
    ("DESIGN", None, None, None),
    ("Total mass (kg)", "mass", "{:.2f}", None),
    ("Payload (kg)", "payload", "{:.2f}", None),
    ("Wing area (m²)", "S", "{:.2f}", None),
    ("Aspect ratio", "AR", "{:.1f}", None),
    ("Wing loading (N/m²)", "wing_loading", "{:.1f}", None),
    ("Stall speed (m/s)", "v_stall", "{:.1f}", "low"),
    ("AS CONFIGURED  (your speed and Cd)", None, None, None),
    ("Flight time (min)", "flight_min", "{:.0f}", "high"),
    ("Range (km)", "range_km", "{:.1f}", "high"),
    ("Electrical power (W)", "power", "{:.0f}", "low"),
    ("Lift-to-drag (Cl / Cd)", "ld", "{:.1f}", "high"),
    ("OPTIMIZED SPEED  (level-flight model)", None, None, None),
    ("Best-range speed (m/s)", "v_best_range", "{:.1f}", None),
    ("Max range (km)", "best_range_km", "{:.0f}", "high"),
    ("Best-endurance speed (m/s)", "v_best_end", "{:.1f}", None),
    ("Max endurance (min)", "best_end_min", "{:.0f}", "high"),
    ("Energy per km (Wh/km)", "wh_per_km", "{:.2f}", "low"),
    ("Energy per payload kg·km (Wh)", "wh_per_payload_km", "{:.2f}", "low"),
]

# İki şeyi karşılaştırdığımız için "longer / lower" (en uzun / en düşük değil)
VERDICT_SPEC = [
    # (başlık, anahtar, yön, yedek anahtar, yedek başlık)  yedek: optimum hesaplanamazsa kendi hızındaki değer
    ("Longer range", "best_range_km", "high", "range_km", "Longer range (at your speed)"),
    ("Longer endurance", "best_end_min", "high", "flight_min", "Longer endurance (at your speed)"),
    ("Lower energy per km", "wh_per_km", "low", None, None),
    ("Lower energy per payload kg·km", "wh_per_payload_km", "low", None, None),
    ("Lower stall speed", "v_stall", "low", None, None),
]


def _winner(a, b, key, better):
    """İki uçağın aynı değerini kıyaslar: (kazanan harf, yüzde farkı) ya da None."""
    va, vb = a.get(key), b.get(key)
    if better is None or va is None or vb is None or va == vb:
        return None
    a_higher = va > vb
    win = "A" if (a_higher if better == "high" else not a_higher) else "B"
    w, l = (va, vb) if win == "A" else (vb, va)
    if l == 0:
        return win, "n/a"
    pct = f"+{(w / l - 1) * 100:.0f}%" if better == "high" else f"−{(1 - w / l) * 100:.0f}%"
    return win, pct


def build_comparison_view(a, b):
    verdict = []
    for title, key, better, fb_key, fb_title in VERDICT_SPEC:
        res = _winner(a, b, key, better)
        if res is None and fb_key and (a.get(key) is None or b.get(key) is None):
            res, title = _winner(a, b, fb_key, better), fb_title
        if res:
            verdict.append((title, res[0], res[1]))
    w1, w2 = _winner(a, b, "wh_per_km", "low"), _winner(a, b, "wh_per_payload_km", "low")
    insight = bool(w1 and w2 and w1[0] != w2[0])
    rows = []
    for label, key, fmt, better in COMPARE_SPEC:
        if key is None:
            rows.append(("section", label))
            continue
        va, vb = a.get(key), b.get(key)
        ta = fmt.format(va) if va is not None else "—"
        tb = fmt.format(vb) if vb is not None else "—"
        win = _winner(a, b, key, better)
        rows.append(("row", label, ta, tb, win[0] if win else None))
    return {"verdict": verdict, "insight": insight, "rows": rows}


INSIGHT_TEXT = ("'More efficient' depends on what you measure: one aircraft wins per km, "
                "the other wins per kg of payload carried.")


def build_comparison_text(a, b, name_a, name_b, params_a, params_b, field_keys):
    view = build_comparison_view(a, b)
    w1, w2 = 34, 30
    short = lambda s: s if len(s) <= 26 else s[:25] + "…"
    line = lambda x, y, z: f"{x:<{w1}}{y:<{w2}}{z:<{w2}}\n"
    rule = "=" * (w1 + 2 * w2) + "\n"

    out = "AIRCRAFT COMPARISON REPORT\n" + rule
    out += f"Generated: {datetime.now():%Y-%m-%d %H:%M}\n\n"
    out += line("", "A: " + short(name_a), "B: " + short(name_b))
    out += "-" * (w1 + 2 * w2) + "\n"

    out += "\nINPUTS\n"
    for key in field_keys:
        out += line("  " + key, params_a.get(key) or "—", params_b.get(key) or "—")

    out += "\nSTATUS\n"
    out += line("  Can it fly?", "yes" if a["can_fly"] else "NO", "yes" if b["can_fly"] else "NO")
    for tag, res in (("A", a), ("B", b)):
        for problem in res["problems"]:
            out += f"  {tag}: {problem}\n"
        for note in res["notes"]:
            out += f"  {tag}: {note}\n"

    out += "\nVERDICT\n"
    if view["verdict"]:
        for title, who, pct in view["verdict"]:
            nm = name_a if who == "A" else name_b
            out += f"  {title}: {who} · {nm} ({pct})\n"
        if view["insight"]:
            out += f"  Note: {INSIGHT_TEXT}\n"
    else:
        out += "  Not enough data for a verdict (both aircraft must fly and have Cd, battery and efficiency).\n"

    out += "\nRESULTS   (▲ = better of the two)\n"
    for row in view["rows"]:
        if row[0] == "section":
            out += f"\n  [{row[1].strip()}]\n"
        else:
            _, label, ta, tb, win = row
            out += line("  " + label, ("▲ " if win == "A" else "") + ta, ("▲ " if win == "B" else "") + tb)

    out += "\n" + "-" * (w1 + 2 * w2) + "\n"
    out += ("Model: steady level flight, Cd = Cd0 + k·Cl², Oswald e = 0.85 (assumed), Cl_max = 1.5 (assumed).\n"
            "Battery treated as 100% usable and avionics power ignored, so absolute values are optimistic;\n"
            "compare the ratios, not the exact numbers.\n")
    return out


# ==============================================================================
# 🎨 DASHBOARD RENK PALETİ (sağ panel)
# ==============================================================================
UI = {
    "bg": "#0B0F19", "field": "#0F1420", "panel": "#11151F", "card": "#171C28", "card_border": "#262D3D", "row_alt": "#1B2130",
    "text": "#E5E7EB", "muted": "#8B93A7", "track": "#2A3144",
    "green": "#34D399", "cyan": "#22D3EE", "amber": "#FBBF24", "red": "#F87171",
    "violet": "#A78BFA", "blue": "#60A5FA", "orange": "#FB923C",
    "green_bg": "#0F2A24", "red_bg": "#2A1517", "amber_bg": "#2A2210",
    "blue_bg": "#10233A", "cyan_bg": "#0E2530",
}


def _font(size=12, weight="normal", family=None):
    if family:
        return ctk.CTkFont(family=family, size=size, weight=weight)
    return ctk.CTkFont(size=size, weight=weight)


class FlightSimulatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Kimliği ve Genişletilmiş Boyutlar
        self.title("AeroSim — Flight Dynamics Simulator")
        self.configure(fg_color=UI["bg"])
        self.geometry("1200x820")  
        self.resizable(False, False) 

        # ==============================================================================
        # ✈️ MARKA ŞERİDİ (ince, modern başlık)
        # ==============================================================================
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=24, pady=(14, 4))
        ctk.CTkLabel(self.header, text="✈", width=40, height=40, corner_radius=12, fg_color="#2563EB",
                     text_color="white", font=_font(20)).pack(side="left")
        brand = ctk.CTkFrame(self.header, fg_color="transparent")
        brand.pack(side="left", padx=12)
        ctk.CTkLabel(brand, text="AeroSim", font=_font(20, "bold"), text_color=UI["text"],
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(brand, text="Aircraft performance & aerodynamics simulator", font=_font(11),
                     text_color=UI["muted"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(self.header, text="v1.3", width=52, height=24, corner_radius=12, fg_color=UI["card"],
                     text_color=UI["muted"], font=_font(11, "bold")).pack(side="right")

        # ==============================================================================
        # 📑 İKİ SAYFA: 1) Simulator   2) Compare
        # ==============================================================================
        self.tabs = ctk.CTkTabview(self, fg_color="transparent", corner_radius=14,
                                   segmented_button_fg_color=UI["card"],
                                   segmented_button_selected_color="#2563EB",
                                   segmented_button_selected_hover_color="#1D4ED8",
                                   segmented_button_unselected_color=UI["card"],
                                   segmented_button_unselected_hover_color=UI["row_alt"],
                                   text_color=UI["text"])
        self.tabs.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        self.sim_tab = self.tabs.add("✈  Simulator")
        self.cmp_tab = self.tabs.add("⚖  Compare")
        try:
            self.tabs._segmented_button.configure(font=_font(13, "bold"), height=34)
        except Exception:
            pass

        # ==============================================================================
        # HAZIR UÇAK PROFİLLERİ (PRESETS) SEÇİM ALANI
        # ==============================================================================
        self.preset_frame = ctk.CTkFrame(self.sim_tab, fg_color=UI["card"], corner_radius=12,
                                         border_width=1, border_color=UI["card_border"])
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
            values=["Custom (Manuel Giriş)"] + list(PRESETS),
            command=self.load_preset,
            width=240, height=34,
            fg_color=UI["field"], border_color=UI["card_border"],
            button_color="#2563EB", button_hover_color="#1D4ED8",
            dropdown_fg_color=UI["card"]
        )
        self.preset_dropdown.pack(side="left", padx=10, pady=10)
        self.preset_dropdown.set("Custom (Manuel Giriş)")

        # ==============================================================================
        # ANA PANEL (SOL GİRDİLER VE SAĞ SONUÇLAR)
        # ==============================================================================
        self.main_container = ctk.CTkFrame(self.sim_tab, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=25, pady=5)

        # ------------------------------------------------------------------------------
        # SOL PANEL: GİRDİLER (INPUT PANEL)
        # ------------------------------------------------------------------------------
        self.input_frame = ctk.CTkScrollableFrame(
            self.main_container, width=480, label_text="AIRCRAFT & ENVIRONMENT INPUTS",
            fg_color=UI["panel"], corner_radius=14, label_fg_color=UI["card"],
            label_text_color=UI["muted"], label_font=_font(11, "bold"))
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
            lbl = ctk.CTkLabel(self.input_frame, text=label_text, font=_font(13), text_color=UI["text"])
            lbl.grid(row=current_row, column=0, padx=20, pady=8, sticky="w")
            self.labels[label_text] = lbl
            
            entry = ctk.CTkEntry(self.input_frame, width=160, height=34, corner_radius=8, fg_color=UI["field"],
                                 border_color=UI["card_border"], placeholder_text=placeholder_val)
            entry.grid(row=current_row, column=1, padx=20, pady=8, sticky="e")
            
            self.entries[label_text] = entry
            current_row += 1

        # Gelişmiş girdileri oluşturuyoruz
        for label_text, placeholder_val in self.advanced_fields:
            lbl = ctk.CTkLabel(self.input_frame, text=label_text, text_color="#FBBF24", font=ctk.CTkFont(size=13, weight="bold"))
            entry = ctk.CTkEntry(self.input_frame, width=160, height=34, corner_radius=8, fg_color=UI["field"],
                                 border_color="#FBBF24", placeholder_text=placeholder_val)
            
            self.labels[label_text] = lbl
            self.entries[label_text] = entry
        

    

        # ------------------------------------------------------------------------------
        # SAĞ PANEL: DIJITAL EKRAN (OUTPUT PANEL)
        # ------------------------------------------------------------------------------
        self.output_frame = ctk.CTkFrame(self.main_container, width=1000, fg_color=UI["panel"], corner_radius=14)
        self.output_frame.pack(side="right", fill="both", expand=True, padx=(15, 0), pady=10)

        # Üst şerit: başlık + durum rozeti
        self.output_header = ctk.CTkFrame(self.output_frame, fg_color="transparent")
        self.output_header.pack(fill="x", padx=18, pady=(14, 6))

        self.output_title = ctk.CTkLabel(self.output_header, text="FLIGHT REPORT", font=_font(18, "bold"), text_color=UI["text"])
        self.output_title.pack(side="left")

        self.status_pill = ctk.CTkLabel(
            self.output_header, text="READY", width=120, height=26, corner_radius=13,
            font=_font(11, "bold"), text_color=UI["cyan"], fg_color=UI["cyan_bg"]
        )
        self.status_pill.pack(side="right")

        # Kartların çizildiği kaydırılabilir alan
        self.dash = ctk.CTkScrollableFrame(self.output_frame, fg_color="transparent")
        self.dash.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        self.report_text = ""   # "Save Report" için düz metin hali burada tutulur
        self.render_dashboard({
            "status": "idle",
            "banner": ("🧭", "READY FOR TAKEOFF CHECK",
                       "Select a preset or enter the core inputs, then press RUN FLIGHT SIMULATION."),
            "notes": [("HOW IT WORKS", [
                "1.  Core inputs decide if the aircraft can fly (lift, stall speed, Cl limit).",
                "2.  If it can, advanced fields unlock: Cd, battery capacity and efficiency.",
                "3.  Run again for the full report, then open RANGE GRAPH 📈.",
            ], UI["cyan"])],
        })

        # ==============================================================================
        # ALT PANEL: AKSİYON ÇUBUĞU (RUN / SAVE / GRAPH, eşit hizalı)
        # ==============================================================================
        self.action_bar = ctk.CTkFrame(self.sim_tab, fg_color="transparent")
        self.action_bar.pack(side="bottom", fill="x", padx=25, pady=(4, 8))
        for col, weight in enumerate((3, 2, 2)):
            self.action_bar.grid_columnconfigure(col, weight=weight, uniform="act")

        self.run_button = ctk.CTkButton(
            self.action_bar, text="▶  RUN FLIGHT SIMULATION", font=_font(15, "bold"), height=46,
            corner_radius=12, fg_color="#2563EB", hover_color="#1D4ED8",
            command=self.calculate_flight_physics
        )
        self.run_button.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.save_button = ctk.CTkButton(
            self.action_bar, text="SAVE REPORT 💾", font=_font(15, "bold"), height=46, corner_radius=12,
            fg_color="transparent", border_width=2, border_color=UI["green"], text_color=UI["green"],
            hover_color=UI["green_bg"], command=self.export_report_to_txt
        )
        self.save_button.grid(row=0, column=1, padx=8, sticky="ew")
        self.graph_button = ctk.CTkButton(
            self.action_bar, text="RANGE GRAPH 📈", font=_font(15, "bold"), height=46, corner_radius=12,
            fg_color="#7C3AED", hover_color="#6D28D9", command=self.open_range_graph
        )
        self.graph_button.grid(row=0, column=2, padx=(8, 0), sticky="ew")

        # Çubuk altta sabit kalsın: ana paneli çubuktan sonra yeniden yerleştir
        self.main_container.pack_forget()
        self.main_container.pack(fill="both", expand=True, padx=25, pady=5)

        self.build_compare_tab()

    # ==============================================================================
    # ✈️ HAZIR UÇAK PROFİLLERİNİ YÜKLEME FONKSİYONU
    # ==============================================================================
    def load_preset(self, choice):
        presets_data = PRESETS

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
        # Ekrandaki kartlar yerine arka planda tuttuğumuz düz metin raporu kaydediyoruz
        report_content = self.report_text
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
    # ⚖️ KARŞILAŞTIRMA SAYFASI (2. sayfa): iki uçak da hazır seçilebilir ya da elle girilebilir
    # ==============================================================================
    CMP_BLANK = "Blank (enter your own)"
    CMP_FIELDS = [
        ("Altitude (m)", "Altitude (m)", "100"),
        ("Empty Weight (kg)", "Empty weight (kg)", "3.5"),
        ("Battery Weight (kg)", "Battery weight (kg)", "2.0"),
        ("Payload Weight (kg)", "Payload (kg)", "1.5"),
        ("Wing Span (m)", "Wing span (m)", "2.2"),
        ("Chord Length (m)", "Chord (m)", "0.28"),
        ("Velocity (m/s)", "Speed (m/s)", "20"),
        ("Lift Coefficient (Cl)", "Lift coeff. Cl", "0.65"),
        ("Drag Coefficient (Cd)", "Drag coeff. Cd", "0.035"),
        ("Battery Capacity (Wh)", "Battery (Wh)", "300"),
        ("Propulsion Efficiency (0-1)", "Efficiency (0-1)", "0.70"),
    ]

    def build_compare_tab(self):
        tab = self.cmp_tab
        self.cmp_entries = {"A": {}, "B": {}}
        self.cmp_names = {}
        self.cmp_data = None

        # ---- Üst şerit: butonlar + durum yazısı ----
        bar = ctk.CTkFrame(tab, fg_color=UI["card"], corner_radius=12, border_width=1, border_color=UI["card_border"])
        bar.pack(fill="x", padx=6, pady=(8, 6))
        self.cmp_button = ctk.CTkButton(bar, text="COMPARE ⚖", font=_font(14, "bold"), height=38, width=140,
                                        corner_radius=10, fg_color="#2563EB", hover_color="#1D4ED8",
                                        command=self.run_comparison)
        self.cmp_button.pack(side="left", padx=(12, 8), pady=10)
        self.cmp_graph_button = ctk.CTkButton(bar, text="OVERLAY GRAPH 📈", font=_font(14, "bold"), height=38, width=170,
                                              corner_radius=10, fg_color="#7C3AED", hover_color="#6D28D9",
                                              command=self.open_compare_graph)
        self.cmp_graph_button.pack(side="left", padx=8, pady=10)
        self.cmp_save_button = ctk.CTkButton(bar, text="SAVE COMPARISON 💾", font=_font(14, "bold"), height=38, width=190,
                                             corner_radius=10, fg_color="transparent", border_width=2,
                                             border_color=UI["green"], text_color=UI["green"],
                                             hover_color=UI["green_bg"], command=self.save_comparison)
        self.cmp_save_button.pack(side="left", padx=8, pady=10)
        self.cmp_status = ctk.CTkLabel(bar, text="", font=_font(12), text_color=UI["muted"], anchor="e",
                                       justify="right", wraplength=330)
        self.cmp_status.pack(side="right", padx=14)

        # ---- Kaydırılabilir alan: girdi kartları + sonuçlar ----
        self.cmp_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.cmp_scroll.pack(fill="both", expand=True, pady=(0, 4))

        inputs = ctk.CTkFrame(self.cmp_scroll, fg_color="transparent")
        inputs.pack(fill="x")
        inputs.grid_columnconfigure(0, weight=1, uniform="cmpcard")
        inputs.grid_columnconfigure(1, weight=1, uniform="cmpcard")
        presets = list(PRESETS)
        self._build_cmp_card(inputs, "A", UI["blue"], 0, presets[0])
        self._build_cmp_card(inputs, "B", UI["violet"], 1, presets[min(1, len(presets) - 1)])

        self.cmp_results = ctk.CTkFrame(self.cmp_scroll, fg_color="transparent")
        self.cmp_results.pack(fill="x", pady=(4, 0))
        self.cmp_message("Compare two aircraft side by side",
                         ["Each aircraft starts from a preset, but every field is editable: change any value, "
                          "or pick 'Blank' to type your own design.",
                          "'⇩ Simulator' copies whatever is in the Simulator tab into that aircraft.",
                          "Press COMPARE, then use OVERLAY GRAPH or SAVE COMPARISON (graph + values)."],
                         UI["cyan"], "🧭")

    def _build_cmp_card(self, parent, which, accent, column, default_preset):
        card = ctk.CTkFrame(parent, fg_color=UI["card"], corner_radius=14, border_width=1, border_color=UI["card_border"])
        card.grid(row=0, column=column, padx=6, pady=4, sticky="nsew")

        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=14, pady=(12, 6))
        ctk.CTkLabel(head, text=which, width=30, height=30, corner_radius=8, fg_color=accent,
                     text_color=UI["bg"], font=_font(14, "bold")).pack(side="left")
        name = ctk.CTkEntry(head, width=150, height=30, corner_radius=8, fg_color=UI["field"],
                            border_color=UI["card_border"], placeholder_text="Aircraft name")
        name.pack(side="left", padx=(10, 8))
        self.cmp_names[which] = name
        combo = ctk.CTkComboBox(head, values=list(PRESETS) + [self.CMP_BLANK], width=150, height=30,
                                fg_color=UI["field"], border_color=UI["card_border"],
                                button_color="#2563EB", button_hover_color="#1D4ED8",
                                dropdown_fg_color=UI["card"],
                                command=lambda choice, w=which: self.fill_cmp_preset(w, choice))
        combo.pack(side="left")
        combo.set("Load preset…")
        ctk.CTkButton(head, text="⇩ Simulator", width=92, height=30, corner_radius=8, fg_color=UI["field"],
                      border_width=1, border_color=UI["card_border"], hover_color=UI["row_alt"],
                      font=_font(12), command=lambda w=which: self.copy_cmp_from_sim(w)).pack(side="right")

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=14, pady=(2, 12))
        for c in (1, 3):
            grid.grid_columnconfigure(c, weight=1)
        for i, (key, short, hint) in enumerate(self.CMP_FIELDS):
            r, c = divmod(i, 2)
            advanced = key in ADV_KEYS
            ctk.CTkLabel(grid, text=short, font=_font(11, "bold" if advanced else "normal"),
                         text_color=UI["amber"] if advanced else UI["muted"],
                         anchor="w").grid(row=r, column=c * 2, padx=(4, 6), pady=4, sticky="w")
            entry = ctk.CTkEntry(grid, width=88, height=30, corner_radius=8, fg_color=UI["field"],
                                 border_color=UI["amber"] if advanced else UI["card_border"],
                                 placeholder_text=hint)
            entry.grid(row=r, column=c * 2 + 1, padx=(0, 10), pady=4, sticky="e")
            self.cmp_entries[which][key] = entry
        self.fill_cmp_preset(which, default_preset)

    def fill_cmp_preset(self, which, choice):
        if choice in PRESETS:
            values, name = PRESETS[choice], choice
        elif choice == self.CMP_BLANK:
            values, name = {}, f"Custom {which}"
        else:
            return
        for key, entry in self.cmp_entries[which].items():
            entry.delete(0, "end")
            if key in values:
                entry.insert(0, values[key])
        self.cmp_names[which].delete(0, "end")
        self.cmp_names[which].insert(0, name)

    def copy_cmp_from_sim(self, which):
        for key, entry in self.cmp_entries[which].items():
            entry.delete(0, "end")
            value = self.entries[key].get().strip() if key in self.entries else ""
            if value:
                entry.insert(0, value)
        self.cmp_names[which].delete(0, "end")
        self.cmp_names[which].insert(0, "My design")
        self.set_cmp_status(f"Copied the Simulator inputs into Aircraft {which}.", UI["muted"])

    def set_cmp_status(self, text, color=None):
        self.cmp_status.configure(text=text, text_color=color or UI["muted"])

    def _read_cmp(self, which):
        params = {k: e.get().strip() for k, e in self.cmp_entries[which].items()}
        name = self.cmp_names[which].get().strip() or f"Aircraft {which}"
        return params, name

    def cmp_message(self, title, lines, accent, icon="⚠️"):
        for child in self.cmp_results.winfo_children():
            child.destroy()
        card = ctk.CTkFrame(self.cmp_results, fg_color=UI["card"], corner_radius=12,
                            border_width=1, border_color=accent)
        card.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(card, text=f"{icon}  {title}", font=_font(16, "bold"), text_color=accent,
                     anchor="w").pack(fill="x", padx=18, pady=(14, 6))
        for line in lines:
            ctk.CTkLabel(card, text=line, font=_font(12), text_color=UI["text"], anchor="w",
                         justify="left", wraplength=1000).pack(fill="x", padx=18, pady=1)
        ctk.CTkFrame(card, height=10, fg_color="transparent").pack()

    def run_comparison(self):
        results, params_list, names = [], [], []
        for which in ("A", "B"):
            params, name = self._read_cmp(which)
            try:
                results.append(compute_aircraft(params))
            except (ValueError, ZeroDivisionError):
                self.cmp_data = None
                self.cmp_message(f"Aircraft {which} has missing or invalid inputs",
                                 ["Fill the first eight fields (altitude to Cl) with numbers; "
                                  "wing span and chord must be above zero.",
                                  "Cd, battery and efficiency are optional, but without them there are no "
                                  "performance numbers."], UI["amber"])
                return
            params_list.append(params)
            names.append(name)
        self.cmp_data = (results[0], results[1], names[0], names[1], params_list[0], params_list[1])
        self.set_cmp_status("")
        self.render_comparison(*self.cmp_data[:4])

    def render_comparison(self, a, b, name_a, name_b):
        for child in self.cmp_results.winfo_children():
            child.destroy()
        CA, CB = UI["blue"], UI["violet"]
        view = build_comparison_view(a, b)

        # ---- Hüküm kartı ----
        card = ctk.CTkFrame(self.cmp_results, fg_color=UI["card"], corner_radius=12,
                            border_width=1, border_color=UI["card_border"])
        card.pack(fill="x", padx=6, pady=5)
        ctk.CTkLabel(card, text="VERDICT", font=_font(11, "bold"),
                     text_color=UI["muted"]).pack(anchor="w", padx=16, pady=(12, 4))
        if view["verdict"]:
            for title, who, pct in view["verdict"]:
                nm = name_a if who == "A" else name_b
                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=2)
                ctk.CTkLabel(row, text=f"🏆  {title}", font=_font(13), text_color=UI["text"],
                             anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=f"{who} · {nm}   ({pct})", font=_font(13, "bold"),
                             text_color=CA if who == "A" else CB, anchor="e").pack(side="right")
            if view["insight"]:
                ctk.CTkLabel(card, text="💡  " + INSIGHT_TEXT, font=_font(12), text_color=UI["amber"],
                             anchor="w", justify="left", wraplength=1000).pack(fill="x", padx=16, pady=(8, 2))
        else:
            ctk.CTkLabel(card, text="No verdict yet: both aircraft must fly and have Cd, battery capacity "
                                    "and efficiency filled in.", font=_font(12), text_color=UI["muted"],
                         anchor="w", justify="left", wraplength=1000).pack(fill="x", padx=16)
        ctk.CTkFrame(card, height=10, fg_color="transparent").pack()

        # ---- Karşılaştırma tablosu ----
        table = ctk.CTkFrame(self.cmp_results, fg_color=UI["card"], corner_radius=12,
                             border_width=1, border_color=UI["card_border"])
        table.pack(fill="x", padx=6, pady=5)

        def cell_row(left, va, vb, left_color=None, bold=False, bg=None, ca=None, cb=None):
            row = ctk.CTkFrame(table, fg_color=bg or "transparent", corner_radius=6)
            row.pack(fill="x", padx=10, pady=1)
            ctk.CTkLabel(row, text=left, font=_font(12, "bold" if bold else "normal"),
                         text_color=left_color or UI["muted"], anchor="w", width=330).pack(side="left", padx=8, pady=4)
            ctk.CTkLabel(row, text=vb, font=_font(12, "bold", "Consolas"), text_color=cb or UI["text"],
                         anchor="center", width=260).pack(side="right", padx=8, pady=4)
            ctk.CTkLabel(row, text=va, font=_font(12, "bold", "Consolas"), text_color=ca or UI["text"],
                         anchor="center", width=260).pack(side="right", padx=8, pady=4)

        cell_row("", f"A · {name_a}", f"B · {name_b}", bold=True, ca=CA, cb=CB)
        cell_row("Can it fly?", "✔ yes" if a["can_fly"] else "✖ no", "✔ yes" if b["can_fly"] else "✖ no",
                 ca=UI["green"] if a["can_fly"] else UI["red"], cb=UI["green"] if b["can_fly"] else UI["red"])
        for tag, res in (("A", a), ("B", b)):
            for problem in res["problems"]:
                cell_row(f"   ⚠ {tag}: {problem}", "", "", left_color=UI["red"])
            for note in res["notes"]:
                cell_row(f"   ℹ {tag}: {note}", "", "", left_color=UI["amber"])

        i = 0
        for row in view["rows"]:
            if row[0] == "section":
                ctk.CTkLabel(table, text=row[1], font=_font(11, "bold"), text_color=UI["cyan"],
                             anchor="w").pack(fill="x", padx=18, pady=(12, 2))
                i = 0
                continue
            _, label, ta, tb, win = row
            ca = cb = UI["text"]
            if win == "A":
                ta, ca = "▲ " + ta, UI["green"]
            elif win == "B":
                tb, cb = "▲ " + tb, UI["green"]
            cell_row(label, ta, tb, bg=UI["row_alt"] if i % 2 == 0 else None, ca=ca, cb=cb)
            i += 1
        ctk.CTkFrame(table, height=10, fg_color="transparent").pack()

        try:
            self.cmp_scroll._parent_canvas.yview_moveto(0.0)
        except Exception:
            pass

    def open_compare_graph(self):
        if self.cmp_data is None:
            self.set_cmp_status("Press COMPARE first: the graph is drawn from the last comparison.", UI["amber"])
            return
        a, b, name_a, name_b = self.cmp_data[:4]
        if "sim" not in a or "sim" not in b:
            self.set_cmp_status("Graph needs both aircraft to fly with Cd, battery and efficiency filled in "
                                "(and Cd above induced drag).", UI["amber"])
            return
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            fig = draw_compare_figure(a, b, name_a, name_b)
        except ImportError:
            self.set_cmp_status("matplotlib is missing:  pip install matplotlib", UI["amber"])
            return

        win = ctk.CTkToplevel(self)
        win.configure(fg_color=UI["bg"])
        win.title("Aircraft Comparison Graph")
        win.geometry("1050x820")
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(10, 5))
        ctk.CTkButton(win, text="SAVE GRAPH AS PNG 🖼️", font=_font(14, "bold"), height=38, corner_radius=10,
                      fg_color="#059669", hover_color="#047857",
                      command=lambda: self.save_graph_png(fig)).pack(pady=(0, 12))
        win.after(200, win.lift)
        win.focus()

    def save_comparison(self):
        if self.cmp_data is None:
            self.set_cmp_status("Press COMPARE first: there is nothing to save yet.", UI["amber"])
            return
        a, b, name_a, name_b, params_a, params_b = self.cmp_data
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="aircraft_comparison",
            filetypes=[("Comparison report", "*.txt"), ("All Files", "*.*")],
            title="Save comparison (creates a .txt with the values and a _graph.png)"
        )
        if not path:
            return
        base = os.path.splitext(path)[0]
        text = build_comparison_text(a, b, name_a, name_b, params_a, params_b,
                                     [key for key, _, _ in self.CMP_FIELDS])
        with open(base + ".txt", "w", encoding="utf-8") as f:
            f.write(text)
        saved = [os.path.basename(base + ".txt")]

        if "sim" in a and "sim" in b:
            try:
                fig = draw_compare_figure(a, b, name_a, name_b)
                fig.savefig(base + "_graph.png", dpi=200, facecolor=fig.get_facecolor())
                saved.append(os.path.basename(base + "_graph.png"))
            except ImportError:
                self.set_cmp_status(f"✔ Saved {saved[0]}. The graph needs matplotlib (pip install matplotlib).", UI["amber"])
                return
            self.set_cmp_status("✔ Saved: " + "  +  ".join(saved), UI["green"])
        else:
            self.set_cmp_status(f"✔ Saved {saved[0]}. No graph: both aircraft must fly and have Cd, battery "
                                "and efficiency filled in.", UI["amber"])

    # ==============================================================================
    # 📈 GRAFİK PENCERESİ
    # ==============================================================================
    def show_message(self, text):
        # İlk paragraf başlık, kalanı açıklama olur
        parts = text.strip().split("\n\n", 1)
        lines = parts[1].split("\n") if len(parts) > 1 else []
        self.render_dashboard({
            "status": "warning",
            "banner": ("⚠️", parts[0].strip().rstrip("."), "Press RUN FLIGHT SIMULATION to bring your report back."),
            "notes": [("WHAT TO DO", [l for l in lines if l.strip()], UI["amber"])] if lines else [],
        })

    # ==============================================================================
    # 🖥️ MODERN DASHBOARD (SAĞ PANEL) - kart çizen yardımcı metotlar
    # ==============================================================================
    def clear_dashboard(self):
        for child in self.dash.winfo_children():
            child.destroy()

    def _card(self, border=None, fg=None):
        card = ctk.CTkFrame(self.dash, fg_color=fg or UI["card"], corner_radius=12,
                            border_width=1, border_color=border or UI["card_border"])
        card.pack(fill="x", padx=6, pady=5)
        return card

    def add_banner(self, icon, title, subtitle, accent, bg):
        card = self._card(border=accent, fg=bg)
        ctk.CTkLabel(card, text=icon, font=_font(34)).pack(side="left", padx=(18, 10), pady=14)
        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(side="left", fill="x", expand=True, pady=10, padx=(0, 12))
        ctk.CTkLabel(box, text=title, font=_font(17, "bold"), text_color=accent,
                     anchor="w", justify="left", wraplength=420).pack(fill="x")
        ctk.CTkLabel(box, text=subtitle, font=_font(12), text_color=UI["muted"],
                     anchor="w", justify="left", wraplength=420).pack(fill="x", pady=(2, 0))

    def add_issue(self, title, detail, fix):
        card = self._card(border=UI["red"], fg=UI["red_bg"])
        ctk.CTkLabel(card, text="⚠  " + title, font=_font(13, "bold"), text_color=UI["red"],
                     anchor="w", justify="left", wraplength=520).pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(card, text=detail, font=_font(12), text_color=UI["text"],
                     anchor="w", justify="left", wraplength=520).pack(fill="x", padx=16)
        ctk.CTkLabel(card, text="💡  " + fix, font=_font(12), text_color=UI["amber"],
                     anchor="w", justify="left", wraplength=520).pack(fill="x", padx=16, pady=(2, 12))

    def add_metrics(self, metrics, columns=3):
        grid = ctk.CTkFrame(self.dash, fg_color="transparent")
        grid.pack(fill="x")
        for c in range(columns):
            grid.grid_columnconfigure(c, weight=1, uniform="metric")
        for i, (label, value, unit, accent) in enumerate(metrics):
            card = ctk.CTkFrame(grid, fg_color=UI["card"], corner_radius=12,
                                border_width=1, border_color=UI["card_border"])
            card.grid(row=i // columns, column=i % columns, padx=6, pady=5, sticky="nsew")
            ctk.CTkLabel(card, text=label.upper(), font=_font(10, "bold"),
                         text_color=UI["muted"]).pack(anchor="w", padx=14, pady=(12, 0))
            ctk.CTkLabel(card, text=value, font=_font(26, "bold"),
                         text_color=accent).pack(anchor="w", padx=14)
            ctk.CTkLabel(card, text=unit, font=_font(11),
                         text_color=UI["muted"]).pack(anchor="w", padx=14, pady=(0, 12))

    def add_checks(self, checks):
        card = self._card()
        ctk.CTkLabel(card, text="FLIGHT SAFETY CHECKS", font=_font(11, "bold"),
                     text_color=UI["muted"]).pack(anchor="w", padx=16, pady=(12, 2))
        for label, value_text, hint, fraction, ok in checks:
            color = UI["green"] if ok else UI["red"]
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=6)
            top = ctk.CTkFrame(row, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=("✔  " if ok else "✖  ") + label, font=_font(13, "bold"),
                         text_color=color).pack(side="left")
            ctk.CTkLabel(top, text=value_text, font=_font(13, "bold"),
                         text_color=UI["text"]).pack(side="right")
            bar = ctk.CTkProgressBar(row, height=8, corner_radius=4,
                                     fg_color=UI["track"], progress_color=color)
            bar.pack(fill="x", pady=(5, 3))
            bar.set(max(0.0, min(1.0, fraction)))
            ctk.CTkLabel(row, text=hint, font=_font(11), text_color=UI["muted"],
                         anchor="w", justify="left", wraplength=520).pack(fill="x")
        ctk.CTkFrame(card, height=6, fg_color="transparent").pack()

    def add_section(self, title, rows, accent):
        card = self._card()
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkFrame(header, width=4, height=16, corner_radius=2, fg_color=accent).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(header, text=title, font=_font(12, "bold"), text_color=accent).pack(side="left")
        for i, (label, value) in enumerate(rows):
            row = ctk.CTkFrame(card, fg_color=UI["row_alt"] if i % 2 == 0 else "transparent", corner_radius=6)
            row.pack(fill="x", padx=10, pady=1)
            ctk.CTkLabel(row, text=label, font=_font(12), text_color=UI["muted"],
                         anchor="w").pack(side="left", padx=8, pady=4)
            ctk.CTkLabel(row, text=value, font=_font(12, "bold", "Consolas"), text_color=UI["text"],
                         anchor="e").pack(side="right", padx=8, pady=4)
        ctk.CTkFrame(card, height=6, fg_color="transparent").pack()

    def add_note(self, title, lines, accent):
        card = self._card()
        ctk.CTkLabel(card, text=title, font=_font(11, "bold"), text_color=accent).pack(anchor="w", padx=16, pady=(12, 4))
        for line in lines:
            ctk.CTkLabel(card, text=line, font=_font(12), text_color=UI["text"],
                         anchor="w", justify="left", wraplength=540).pack(fill="x", padx=16, pady=1)
        ctk.CTkFrame(card, height=8, fg_color="transparent").pack()

    def render_dashboard(self, view):
        styles = {
            "idle":    ("READY",        UI["cyan"],   UI["cyan_bg"]),
            "success": ("FLIGHT OK",    UI["green"],  UI["green_bg"]),
            "failed":  ("CANNOT FLY",   UI["red"],    UI["red_bg"]),
            "pending": ("INPUT NEEDED", UI["blue"],   UI["blue_bg"]),
            "warning": ("CHECK INPUT",  UI["amber"],  UI["amber_bg"]),
            "error":   ("ERROR",        UI["red"],    UI["red_bg"]),
            "info":    ("INFO",         UI["cyan"],   UI["cyan_bg"]),
        }
        pill_text, accent, bg = styles[view["status"]]
        self.clear_dashboard()
        self.status_pill.configure(text=pill_text, text_color=accent, fg_color=bg)

        icon, title, subtitle = view["banner"]
        self.add_banner(icon, title, subtitle, accent, bg)
        for issue_title, detail, fix in view.get("issues", []):
            self.add_issue(issue_title, detail, fix)
        if view.get("metrics"):
            self.add_metrics(view["metrics"])
        if view.get("checks"):
            self.add_checks(view["checks"])
        for sec_title, rows, sec_color in view.get("sections", []):
            self.add_section(sec_title, rows, sec_color)
        for note_title, lines, note_color in view.get("notes", []):
            self.add_note(note_title, lines, note_color)

        try:
            self.dash._parent_canvas.yview_moveto(0)   # her yeni raporda en üste dön
        except Exception:
            pass

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
        win.configure(fg_color=UI["bg"])
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

            # --- Dashboard (sağ panel) için ortak veriler ---
            lift_ratio = Lift / w
            speed_ratio = velocity / v_stall
            cl_usage = cl / cl_max
            checks = [
                ("Lift vs. Weight", f"{lift_ratio:.2f}×",
                 f"Lift {Lift:.1f} N  •  Weight {w:.1f} N  •  needs at least 1.00×", lift_ratio / 2, is_lift_enough),
                ("Speed vs. Stall Speed", f"{velocity:.1f} m/s",
                 f"Stall speed {v_stall:.1f} m/s ({v_stall * 3.6:.0f} km/h)  •  margin {speed_ratio:.2f}×", speed_ratio / 2, is_speed_safe),
                ("Lift Coefficient Limit", f"{cl:.2f} / {cl_max:.2f}",
                 f"Using {cl_usage * 100:.0f}% of the wing's maximum Cl", cl_usage, is_cl_valid),
            ]
            env_rows = [("Air Density (ρ)", f"{r:.4f} kg/m³"), ("Total Aircraft Weight (W)", f"{w:.2f} N")]
            view = {"status": "info", "banner": ("", "", ""), "checks": checks,
                    "sections": [("ENVIRONMENT & ATMOSPHERE", env_rows, UI["cyan"])]}

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

                issues = []
                if not is_lift_enough:
                    issues.append(("Insufficient lift force", f"Short by {w - Lift:.2f} N.",
                                   "Increase wing span, chord length, or velocity."))
                if not is_speed_safe:
                    issues.append(("Stall risk", f"Your speed ({velocity:.2f} m/s) is below the safety limit. "
                                   f"Fly at least {v_stall:.2f} m/s ({v_stall * 3.6:.1f} km/h).",
                                   "Increase velocity or wing area."))
                if not is_cl_valid:
                    issues.append(("Cl exceeds Cl_max", f"Cl ({cl}) is above Cl_max ({cl_max}). The wing would stall.",
                                   "Lower Cl or use a higher-lift airfoil/flap."))
                view.update({
                    "status": "failed",
                    "banner": ("❌", "THE AIRCRAFT CANNOT FLY", "Fix the issues below and run again."),
                    "issues": issues,
                    "notes": [("ADVANCED PARAMETERS LOCKED",
                               ["Cd, battery capacity and efficiency unlock once all safety checks pass."], UI["amber"])],
                })
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
                    view.update({
                        "status": "pending",
                        "banner": ("🔓", "ADVANCED INPUTS UNLOCKED",
                                   "Enter Cd, Battery Capacity and Propulsion Efficiency in the left panel, "
                                   "then press RUN FLIGHT SIMULATION again for the full analysis."),
                    })
                    report += "-> Advanced parameters (Cd, Wh) have been unlocked below!\n"
                    report += "-> ACTION REQUIRED: Please enter values for Cd and Wh in the left panel,\n"
                    report += "   then press 'RUN FLIGHT SIMULATION' again for full analytics.\n"
                    report += "=============================================\n"
                else:
                    cd = float(self.entries["Drag Coefficient (Cd)"].get())
                    battery_capacity_wh = float(self.entries["Battery Capacity (Wh)"].get())
                    propulsion_efficiency = float(self.entries["Propulsion Efficiency (0-1)"].get())
                    
                    if not (0 < propulsion_efficiency <= 1):
                                            view.update({
                                                "status": "warning",
                                                "banner": ("⚠️", "CHECK YOUR INPUT", "Propulsion efficiency must be between 0 and 1 (e.g., 0.70, not 70)."),
                                            })
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
        
                        view.update({
                            "status": "success",
                            "banner": ("🛫", "FLIGHT OK — ALL CHECKS PASSED",
                                       "Modelled steady-flight checks passed: lift ≥ weight, speed ≥ stall speed, Cl ≤ Cl_max."),
                            "metrics": [
                                ("Flight Time", f"{flight_time_minutes:.0f}", f"minutes  ({flight_time_hours:.2f} h)", UI["cyan"]),
                                ("Range (at your speed)", f"{range_km:.1f}", "km", UI["violet"]),
                                ("Electrical Power", f"{power_electrical:.0f}", "watts", UI["amber"]),
                                ("Lift Force", f"{Lift:.1f}", "newtons", UI["blue"]),
                                ("Drag Force", f"{Drag:.2f}", "newtons", UI["orange"]),
                                ("Stall Speed", f"{v_stall:.1f}", f"m/s  ({v_stall * 3.6:.0f} km/h)", UI["green"]),
                            ],
                            "sections": [
                                ("ENVIRONMENT & ATMOSPHERE", env_rows + [
                                    ("Static Ambient Pressure", f"{p_static:.2f} Pa"),
                                    ("Bernoulli Total Pressure", f"{p_total:.2f} Pa")], UI["cyan"]),
                                ("AERODYNAMICS & FLUID MECHANICS", [
                                    ("Wing Loading (W/S)", f"{wing_loading:.2f} N/m²"),
                                    ("Wing Aspect Ratio (AR)", f"{aspect_ratio:.2f}"),
                                    ("Parasite Drag Coeff (Cd0)", f"{max(0.0, cd_parasite):.4f}"),
                                    ("Induced Drag Coeff (Cdi)", f"{cd_induced:.4f}"),
                                    ("Reynolds Number (Re)", f"{reynolds:,.0f}"),
                                    ("Mach Number (M)", f"{mach_number:.4f}"),
                                    ("Cruise Thrust Required (T)", f"{Drag:.2f} N")], UI["violet"]),
                                ("ASSUMPTIONS USED", [
                                    ("Max Lift Coefficient (Cl_max)", f"{cl_max:.2f}"),
                                    ("Oswald Efficiency (e)", f"{oswald_efficiency:.2f}"),
                                    ("Propulsion Efficiency (η)", f"{propulsion_efficiency:.2f}")], UI["amber"]),
                            ],
                            "notes": [("NEXT STEP", ["Press RANGE GRAPH 📈 to find the speed with the longest range and endurance."],
                                       UI["violet"])],
                        })
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

            # Ekrana Raporu Basma (modern dashboard)
            self.report_text = report
            self.report_ready = True
            self.render_dashboard(view)
        except ValueError:
            self.report_ready = False
            self.render_dashboard({
                "status": "error",
                "banner": ("🚫", "INVALID INPUT",
                           "Please make sure all input fields contain valid numerical values!"),
            })

if __name__ == "__main__":
    app = FlightSimulatorGUI()
    app.mainloop()