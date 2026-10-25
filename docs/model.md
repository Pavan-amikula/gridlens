# Model and validity

GridLens is a reproducible **balanced positive-sequence engineering screening model**, using an original Python implementation. It is not an EMT solver, a grid-forming converter implementation, certified equipment sizing, or a connection approval. The included results are synthetic. No PSCAD, PowerFactory or PSS/E calculation is represented as having been executed.

## Network

A regional source feeds an aggregate demand bus through a Thevenin impedance. Facility MW is the MVA calculation base; SCR sets `|Z| = 1/SCR` pu, with X/R = 10. The upstream source magnitude is initialized so that the point of connection is 1 pu with rated load and PF=0.98. This is a representative radial interface, not a Nordic network equivalent derived from a TSO case.

For a receiving voltage magnitude V, load P and Q, the scalar AC balance is:

`E² = V² + 2(RP + XQ) + (R² + X²)(P² + Q²)/V²`.

The nonlinear demand changes from constant power to constant impedance below 0.85 pu, with `k=min(1,(V/0.85)²)`. The algebraic root is computed with Brent's method and a 1e-10 pu voltage tolerance. Failure to bracket an equilibrium is counted explicitly. The plotted voltage passes through a 20 ms first-order lag; this represents measurement/aggregate response, not electromagnetic network dynamics. Protection uses that lagged voltage. Internal algebraic voltage is used for delivered power. Cooling and IT are aggregated; induction motor stalling and detailed rectifier DC-link dynamics are not represented.

`power_flow()` provides a separate analytical constant-PQ high-voltage solution used in Kirchhoff and collapse tests. The time-domain model uses the voltage-dependent nonlinear solution, not the analytical constant-PQ approximation.

## Frequency

The regional equivalent has Sbase=10,000 MVA, H=4 s, 50 Hz nominal frequency, 300 MW/Hz damping, and a first-order governor with 0.8 s lag and 1,000 MW/Hz gain:

`df/dt = 50/(2 H Sbase) [Pgov - Ploss - (Pgrid - Pinitial) - 300(f-50)]`.

The frequency event is a 200 MW generation loss at 3 s. This is an illustrative coherent-area model. It excludes inter-area modes and geographically varying inertia. Euler integrates frequency; exact first-order exponential updates integrate simple controller lags. Timestep convergence is reported for 10, 5 and 2.5 ms. A 12 s run cannot prove a 30-minute frequency withstand obligation.

## Mitigations

| Architecture | Implemented behavior | Important limitation |
|---|---|---|
| Baseline | Aggregate PQ/impedance demand, undervoltage transfer logic | Protective behavior is an assumed risk case, not measured UPS firmware |
| BESS | 40 MW / 20 MWh, 60 ms P response, 80 MW/Hz droop, 8 MW per Hz/s synthetic inertia term; 5 MW/s ramp target | No voltage-angle oscillator, PLL or switching model; **not GFM validation** |
| STATCOM | Saturated proportional voltage control, 40 ms actuator and 60 ms voltage measurement lag | No semiconductor switching, DC link or detailed current-loop dynamics |
| Synchronous condenser surrogate | Reactive support, 100 ms actuator, 0.15 s added effective regional H | No dq machine, AVR, exciter, losses or fault-current calculation |
| MV UPS | Online deficit support up to 100 MW / 2 MWh; controlled grid reconnection over 2 s | Grid isolation, static switch and DC bus are abstracted |
| Coordinated | All BESS, STATCOM, UPS and assumed harmonic filter effects | Conservative shared 50 MVA P/Q support envelope; verify actual equipment topology |

Battery SOC starts at 60% and remains between 10–90%, with 95% charge/discharge efficiency. A positive BESS MW value means injection and discharge. Converter active injection is limited by `Pmax*V`. Reactive support is bounded by the 50 MVA P/Q circle and voltage current limit. The condenser instead uses a 60 Mvar surrogate limit. Reported Pgrid is receiving-end active import; upstream I²R losses are not added to the regional swing balance, a limitation of the reduced regional equivalent.

Protection transfers load after V<0.8 pu for 40 ms; it stays off-grid for 0.8 s. Baseline reconnects immediately, while the UPS architecture uses a 2 s recovery. Online UPS covers the IT power deficit before and during transfer until its power/energy limits bind. Energy depletion is tracked. Battery control is intentionally finite-bandwidth: a 200 ms workload ramp can outrun it. Coordinated support is **not tuned to make every target pass**.

## Events and measurements

Six scenarios: 150 ms source sag to 0.55 of initial magnitude at 2 s; regional generation loss; a 30% load increase over 0.2 s at 5 s; ±12% 0.8 Hz cycling; fault/recovery; combined fault, loss and load ramp. In this version, `fault` and `recovery` deliberately share the same stimulus so protection/recovery can be isolated under identical conditions; these are two study views, not independent waveforms. Network strengths SCR 2, 4 and 8 produce 108 matrix entries, **90 unique event/architecture/SCR configurations** because of that duplicate view.

Ramp metrics use a 100 ms finite difference; the AI metric considers the 4.9–6.0 s event window. Fault-driven import interruption is shown separately as the whole-horizon maximum. IT unserved energy integrates demanded minus delivered IT power; battery throughput integrates absolute BESS power. Offline replay is wall-clock animated visualization of already-computed samples, not real-time deterministic hardware execution or a live grid stream.

## Harmonics and interaction

The assumed 5th/7th/11th/13th current spectrum is 2.5/1.8/0.9/0.7% on rated-load current. With `Zh=R+jhX`, harmonic voltage magnitudes are calculated independently and THDv uses their root-sum-square. The coordinated case attenuates the four currents by 0.18/0.22/0.4/0.4. This **does not** simulate resonance, filter design, IEEE 519 compliance, IEC emission allocation, or the spectrum changing with instantaneous load.

The interaction screen linearizes a local actuator/measurement Q-control loop with voltage sensitivity X/Sbase, 40 ms actuator and 60 ms measurement lag. It reports complex poles and damping ratios across SCR/gain sweeps. This local two-state model cannot establish multi-converter, PLL, subsynchronous or GFM stability. Its poles are not the eigenvalues of the entire nonlinear simulation model.

## Regulatory screen

Dashboard study targets are illustrative, separate from the cited legal register. A Finnish section 9.1.11 recovery screen evaluates Pgrid against 90% of pre-fault import at one second after post-fault voltage first reaches 0.90 pu. It is only an endpoint screen, not proof of all time-domain obligations. The flag for complete grid transfer exposes the difference between supplying IT with UPS and satisfying demand-facility ride-through. Exact figure 9.2 voltage-envelope testing and vendor protection qualification remain external studies. A passing recovery endpoint cannot override the detected transfer risk.

All scenarios, constants, model code hash, raw traces, convergence results and failures are retained. Future work should replace assumed protection/UPS/cooling blocks with validated vendor models before making equipment procurement or compliance claims.
