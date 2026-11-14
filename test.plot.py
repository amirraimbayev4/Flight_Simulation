import math
import matplotlib.pyplot as plt


def calculate_power_curve(d, W, S, AR, Cd0, eta, e, cl_max):
    v_stall = cl_max  # stall hızı formülü, 1.5 yerine cl_max kullan
    speeds = []
    powers = []
    v = v_stall

    while v <=3 * v_stall:        # üst sınır: 3 * v_stall
        cl = cl_max          # L = W için gereken Cl
        cd = Cd0 + cl ** 2 / (math.pi * AR * e)  # Cd0 + Cl^2 / (pi * AR * e)
        drag = 0.5 * d * v ** 2 * S * cd  # 0.5 * d * v^2 * S * cd
        power = drag * v / eta   # drag * v / eta
        speeds.append(v)
        powers.append(power)
        v = v + 0.5

    return speeds, powers


# Delivery Drone değerleri
d = 1.225 * (1 - 0.00002256 * 100) ** 4.256
W = 7 * 9.81
S = 2.2 * 0.28
AR = 2.2 / 0.28
e = 0.85
eta = 0.7
Cd0 = 0.035 - 0.65 ** 2 / (math.pi * AR * e)

speeds, powers = calculate_power_curve(d, W, S, AR, Cd0, eta, e, 1.5)

plt.plot(speeds, powers)
plt.xlabel("Speed (m/s)")
plt.ylabel("Electrical power (W)")
plt.show()