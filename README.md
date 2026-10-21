# Aircraft Performance & Aerodynamics Simulator

## 1. What is it?
This is an aircraft calculator. It performs calculations based on the values entered by the user and checks if the aircraft can fly.

## 2. What is it for?
This calculator is for students who want to learn the basics of aircraft performance. It is meant for learning and early estimates, not for real flight design or certification.

## 3. How it works
The user enters numbers into the input fields. The program then runs the equations and prints the results on the screen. If the aircraft can fly, extra inputs (drag coefficient, battery capacity, propulsion efficiency) are unlocked for flight time and range calculations.

**Main equations:**
- Air density: `rho = 1.225 * (1 - 0.00002256 * altitude) ** 4.256`
- Wing area: `S = wing_span * chord`
- Lift: `L = 0.5 * rho * V^2 * S * Cl`
- Stall speed: `V_stall = sqrt(2 * W / (rho * S * Cl_max))`
- Drag: `D = 0.5 * rho * V^2 * S * Cd`
- Required power: `P = D * V`
- Electrical power: `P_electrical = P / eta`
- Induced drag coefficient: `Cd_induced = Cl^2 / (pi * AR * e)`

**Variables:**
- `V`: velocity, `W`: total weight of the aircraft (N)
- `Cl`, `Cd`: lift and drag coefficients (entered by the user)
- `AR`: aspect ratio (wing span / chord)
- `eta`: propulsion efficiency (entered by the user)

## 4. How to run
**Option 1: Windows executable (no installation needed)**
1. Go to the Releases page and download the .exe file.
2. Double-click it.

**Option 2: Run from source code**
1. Install Python 3.
2. Run: `pip install customtkinter`
3. Run: `python main.py`

## 5. Assumptions, limitations and development notes
**Assumptions:**
- Cl_max = 1.5. I took it as 1.5 because it is a typical value for small UAV wings with cambered airfoils at low Reynolds numbers. The real value depends on the airfoil.
- Oswald efficiency e = 0.85, also a typical value for small UAVs.

**Limitations:** This is a simplified model of steady, level flight. The weight is constant, and wind, climb and turns are not included. The results are estimates.

**Development notes:** I used AI assistance while coding, debugging and designing. The idea, the physics model and the testing are my own work. I reviewed and understood all assumptions used.

## Planned features
- Fuel-powered (engine-based) aircraft support
- Wind, climb and turn calculations
- Graphs and a more modern interface
