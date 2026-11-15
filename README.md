# Aircraft Performance & Aerodynamics Simulator

## 1. Overview

The **Aircraft Performance & Aerodynamics Simulator** is an educational aircraft performance calculator developed in Python. It allows users to enter aircraft parameters, perform basic aerodynamic calculations, and evaluate whether an aircraft can maintain flight under the specified conditions.

The project is designed for students and beginners interested in aerospace engineering, aerodynamics, and aircraft performance analysis.

## 2. Features

- Aircraft lift and drag calculations
- Stall speed estimation
- Air density calculation based on altitude
- Wing area and aspect ratio calculations
- Required aerodynamic and electrical power estimation
- Flight endurance and range estimation
- Range vs. Airspeed graph
- Endurance vs. Airspeed graph
- Visually updated graphical user interface
- Additional flight calculations unlocked when the aircraft meets the basic flight condition

## 3. How It Works

Users enter aircraft parameters through the graphical interface. The program processes these inputs using basic aerodynamic equations and displays the calculated results.

If the aircraft meets the basic lift condition, additional parameters become available, including drag coefficient, battery capacity, and propulsion efficiency. These parameters are used to estimate flight endurance and range.

The simulator also generates performance graphs to illustrate how airspeed affects aircraft range and endurance.

## 4. Main Equations

**Air Density:**

`rho = 1.225 * (1 - 0.00002256 * altitude) ** 4.256`

**Wing Area:**

`S = wing_span * chord`

**Lift:**

`L = 0.5 * rho * V^2 * S * Cl`

**Stall Speed:**

`V_stall = sqrt(2 * W / (rho * S * Cl_max))`

**Drag:**

`D = 0.5 * rho * V^2 * S * Cd`

**Required Power:**

`P = D * V`

**Electrical Power:**

`P_electrical = P / eta`

**Induced Drag Coefficient:**

`Cd_induced = Cl^2 / (pi * AR * e)`

## 5. Variables

| Variable | Description |
|---|---|
| V | Airspeed |
| W | Total aircraft weight (N) |
| Cl | Lift coefficient |
| Cd | Drag coefficient |
| AR | Wing aspect ratio |
| eta | Propulsion efficiency |
| rho | Air density |
| S | Wing area |

## 6. Assumptions and Limitations

**Assumptions:**

- Maximum lift coefficient (Cl_max) is assumed to be 1.5. This is an approximate value for small UAV wings; the actual value depends on the airfoil and operating conditions.
- Oswald efficiency factor (e) is assumed to be 0.85.

**Limitations:**

- The simulator uses a simplified steady, level-flight model.
- Aircraft weight is assumed to remain constant.
- Wind, climbing, and turning flight conditions are not included.
- Aerodynamic coefficients and propulsion efficiency are simplified inputs or assumptions.
- Results are educational estimates and should not be used for real aircraft design, flight operations, or certification.

## 7. How to Run

### Option 1: Windows Executable (No Python Installation Required)

1. Visit the GitHub Releases page.
2. Download the latest Windows `.exe` file.
3. Double-click the executable to launch the simulator.

### Option 2: Run from Source Code

1. Install Python 3.
2. Install the required dependencies:

   `pip install customtkinter numpy matplotlib pillow`

3. Run the application:

   `python main.py`

## 8. Development Notes

This project was developed as a personal learning project to explore the fundamentals of aircraft performance and aerodynamics.

AI tools were used as assistance during coding, debugging, and interface development. The project concept, physics model, assumptions, and testing process were developed and reviewed by me.

## 9. Planned Features

- Support for fuel-powered, engine-based aircraft
- Wind effects and calculations
- Climbing flight performance
- Turning flight calculations
- Further improvements to the graphical interface
- More advanced aircraft performance models

---

**Project Status:** Educational simulator – ongoing development.<img width="1197" height="827" alt="Flight Simulator İnterface" src="https://github.com/user-attachments/assets/cd073b9d-0af4-410a-8fae-c502f32439f0" />
<img width="1051" height="868" alt="Flight Simulator Graphs" src="https://github.com/user-attachments/assets/bddc98ab-bc12-42e7-9689-73734e88def1" />
