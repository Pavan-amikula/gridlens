"""Balanced positive-sequence screening model; SI units unless named pu.

No switching, PLL, negative sequence or vendor controller model is represented.
See docs/model.md for equations, numerical method and boundaries of validity.
"""
from dataclasses import dataclass, asdict
import math
import numpy as np
from scipy.optimize import brentq

SCENARIOS = {
    "fault": "150 ms upstream voltage dip",
    "frequency": "Regional generation loss",
    "ai_ramp": "30 MW AI workload ramp",
    "cycling": "0.8 Hz workload cycling",
    "recovery": "Fault and post-fault load recovery",
    "combined": "Fault, generation loss and AI ramp",
}
MITIGATIONS = {
    "baseline": "Unmitigated",
    "bess": "BESS droop + ramp buffer",
    "statcom": "STATCOM",
    "condenser": "Synchronous condenser surrogate",
    "ups": "MV UPS + controlled recovery",
    "coordinated": "BESS + STATCOM + UPS + filter",
}

@dataclass
class Config:
    scenario: str = "combined"
    mitigation: str = "coordinated"
    scr: float = 4.0
    load_mw: float = 100.0
    duration: float = 12.0
    dt: float = 0.005
    bess_mw: float = 40.0
    bess_mwh: float = 20.0
    bess_tau: float = 0.06
    support_mva: float = 50.0
    initial_soc: float = 0.6
    fault_voltage: float = 0.55
    fault_duration: float = 0.15
    q_gain: float = 300.0
    seed: int = 42

    def validate(self):
        if self.scenario not in SCENARIOS or self.mitigation not in MITIGATIONS:
            raise ValueError("Unknown scenario or mitigation")
        limits = {"scr": (2, 15), "load_mw": (20, 300), "duration": (5, 30),
                  "dt": (0.001, 0.02), "bess_mw": (0, 150), "bess_mwh": (0.1, 300),
                  "initial_soc": (0.1, 0.9), "fault_voltage": (0.1, 1),
                  "fault_duration": (0.02, 1), "q_gain": (0, 600), "bess_tau": (0.005, 0.2),
                  "support_mva": (10, 300)}
        for key, (low, high) in limits.items():
            value = getattr(self, key)
            if not math.isfinite(value) or not low <= value <= high:
                raise ValueError(f"{key} must be between {low} and {high}")

def power_flow(e, p, q, r, x):
    """High-voltage root of radial constant-PQ two-bus AC equations.

    y=|V|², y²+[2(RP+XQ)-E²]y+|Z|²|S|²=0.
    Negative discriminant is explicitly reported as no equilibrium.
    """
    b = 2*(r*p+x*q)-e*e
    d = b*b-4*(r*r+x*x)*(p*p+q*q)
    if d < 0 or b >= 0:
        return 0.0, False
    return math.sqrt(max(0, (-b+math.sqrt(d))/2)), True

def harmonic_screen(scr, load_mw, filtered=False):
    """Harmonic current source into R+jhX; illustrative spectrum, no resonance."""
    h = np.array([5, 7, 11, 13])
    current = np.array([0.025, 0.018, 0.009, 0.007])
    if filtered:
        current *= np.array([0.18, 0.22, 0.4, 0.4])
    z = np.sqrt(0.1**2+h*h)/math.sqrt(1.01)/scr
    voltage = current*z*100
    return {"orders": h.tolist(), "current_percent": (current*100).tolist(),
            "voltage_percent": voltage.tolist(), "thdv_percent": float(np.linalg.norm(voltage)),
            "model": "Assumed current spectrum; non-resonant impedance screening"}

def controller_modes(scr=4.0, gain=300.0, delay=0.04):
    """Linearized Q control with first-order measurement and actuator lag.

    A=[[ -1/Ta, -K/Ta ],[ X/Tm, -1/Tm ]].
    This assesses one local loop, not converter or full-system stability.
    """
    x = 1/math.sqrt(1.01)/scr
    a = np.array([[-1/delay, -gain/delay], [x/(100*0.06), -1/0.06]])
    eig = np.linalg.eigvals(a)
    return [{"real": float(v.real), "imag": float(v.imag),
             "frequency_hz": float(abs(v.imag)/(2*math.pi)),
             "damping_ratio": float(-v.real/abs(v))} for v in eig]

def simulate(config=None):
    c = config or Config()
    c.validate()
    t = np.arange(0, c.duration+c.dt/2, c.dt)
    n = len(t)
    names = ["voltage_pu", "frequency_hz", "grid_mw", "demand_mw", "bess_mw",
             "reactive_mvar", "soc", "ups_mw", "unserved_mw", "connected", "equilibrium"]
    out = {name: np.zeros(n) for name in names}
    base = c.load_mw
    # Network base = facility rated power; X/R=10.
    x = 1/math.sqrt(1.01)/c.scr
    r = x/10
    q0 = base*math.tan(math.acos(0.98))
    # Set source voltage for Vpoc=1 pu at initial operating point.
    e0 = math.sqrt(1+2*(r+x*q0/base)+(r*r+x*x)*(1+(q0/base)**2))
    bess = c.mitigation in ("bess", "coordinated")
    reactive = c.mitigation in ("statcom", "coordinated", "condenser")
    ups = c.mitigation in ("ups", "coordinated")
    pb = qs = 0.0
    soc = c.initial_soc
    f = 50.0
    gov = 0.0
    v = vm = 1.0
    grid_target = base
    disconnect_at = -1.0
    uv_timer = 0.0
    prev_f = 50.0
    ups_energy = 2.0 # MWh, 100 MW UPS, initially fully charged
    for i, ti in enumerate(t):
        fault_case = c.scenario in ("fault", "recovery", "combined")
        fault = fault_case and 2 <= ti < 2+c.fault_duration
        e = e0*(c.fault_voltage if fault else 1)
        demand = base
        if c.scenario in ("ai_ramp", "combined"):
            demand += 0.3*base*min(max((ti-5)/0.2, 0), 1)
        if c.scenario == "cycling" and ti >= 2:
            demand += 0.12*base*math.sin(2*math.pi*0.8*(ti-2))
        generation_loss = 200.0 if c.scenario in ("frequency", "combined") and ti >= 3 else 0.0
        # UPS transfer protection is driven by previous accepted bus voltage.
        uv_timer = uv_timer+c.dt if v < 0.8 else 0
        if uv_timer >= 0.04 and disconnect_at < 0:
            disconnect_at = ti
        connected = 1.0
        if disconnect_at >= 0:
            reconnect = disconnect_at+0.8
            if ti < reconnect:
                connected = 0.0
            elif ups:
                connected = min(1, (ti-reconnect)/2)
        load = demand*connected
        grid_target += np.clip(load-grid_target, -5*c.dt, 5*c.dt)
        if bess:
            rocof = (f-prev_f)/c.dt if i else 0
            request = load-grid_target+80*(50-f)-8*rocof
            active_cap = min(c.bess_mw, c.support_mva) if c.mitigation == "coordinated" else c.bess_mw
            request = np.clip(request, -active_cap, active_cap)
            pb += (request-pb)*(1-math.exp(-c.dt/c.bess_tau))
            # Energy bounds apply before network injection; positive P discharges.
            pb = float(np.clip(pb, -(0.9-soc)*c.bess_mwh*3600/c.dt/0.95,
                              (soc-0.1)*c.bess_mwh*3600/c.dt*0.95))
        else:
            pb = 0.0
        if reactive:
            qlim = 60.0 if c.mitigation == "condenser" else c.support_mva
            requestq = float(np.clip(c.q_gain*(1-vm), -qlim, qlim))
            tau = 0.1 if c.mitigation == "condenser" else 0.04
            qs += (requestq-qs)*(1-math.exp(-c.dt/tau))
            # Converter current circle in MW/Mvar on 50 MVA rating.
            qcircle = math.sqrt(max(0, c.support_mva**2-min(abs(pb), c.support_mva)**2))
            if c.mitigation != "condenser":
                current_factor = min(1.0, max(v, 0.1))
                qs = float(np.clip(qs, -qcircle*current_factor, qcircle*current_factor))
        # Constant impedance transition below 0.85 pu prevents unphysical CPL blowup.
        def powers(vc):
            factor = min(1, (vc/0.85)**2)
            # BESS active current limited on its converter rating during a dip.
            active = max(-c.bess_mw*vc, min(pb, c.bess_mw*vc))
            return load*factor-active, q0*(load/base)*factor-qs*min(1, vc), factor, active
        def residual(vc):
            pp, qq, _, _ = powers(vc)
            pp, qq = pp/base, qq/base
            return vc*vc+2*(r*pp+x*qq)+(r*r+x*x)*(pp*pp+qq*qq)/(vc*vc)-e*e
        try:
            vn = brentq(residual, 1e-5, e+2, xtol=1e-10)
            feasible = True
        except ValueError:
            vn, feasible = 0.0, False
        netp, netq, scale, pb = powers(vn)
        ups_power = min(max(0, demand-load*scale), 100.0, ups_energy*3600/c.dt) if ups else 0.0
        ups_energy = max(0, ups_energy-ups_power*c.dt/3600)
        v += (vn-v)*(1-math.exp(-c.dt/0.02))
        vm += (v-vm)*(1-math.exp(-c.dt/0.06))
        prev_f = f
        # Regional 10 GVA equivalent, H=4 s; condenser adds 0.15 s effective H.
        h = 4.15 if c.mitigation == "condenser" else 4.0
        gov += ((50-f)*1000-gov)*(1-math.exp(-c.dt/0.8))
        df = 50/(2*h*10000)*(gov-generation_loss-(netp-base)-300*(f-50))
        f += c.dt*df
        soc -= (pb/0.95 if pb >= 0 else pb*0.95)*c.dt/(3600*c.bess_mwh)
        values = [v, f, netp, demand, pb, qs*min(1, vn), soc, ups_power,
                  max(0, demand-load*scale-ups_power), connected, float(feasible)]
        for name, value in zip(names, values):
            out[name][i] = value
    # 100 ms average ramp instead of an undefined instantaneous derivative.
    w = max(1, round(0.1/c.dt))
    ramp = np.abs((out["grid_mw"][w:]-out["grid_mw"][:-w])/(w*c.dt))
    recovery_mask = t >= 2+c.fault_duration+0.5
    settled_mask = t >= c.duration-1
    harmonics = harmonic_screen(c.scr, base, c.mitigation == "coordinated")
    metrics = {
        "min_voltage_pu": float(out["voltage_pu"].min()),
        "postfault_min_voltage_pu": float(out["voltage_pu"][recovery_mask].min()),
        "frequency_nadir_hz": float(out["frequency_hz"].min()),
        "max_rocof_hz_s": float(np.abs(np.diff(out["frequency_hz"])/c.dt).max()),
        "max_ramp_mw_s": float(ramp.max()),
        "workload_ramp_mw_s": float(np.max(ramp[max(0, round(4.9/c.dt)-w):round(6/c.dt)])),
        "unserved_mwh": float(np.trapezoid(out["unserved_mw"], t)/3600),
        "bess_throughput_mwh": float(np.trapezoid(np.abs(out["bess_mw"]), t)/3600),
        "final_soc": float(out["soc"][-1]),
        "thdv_percent": harmonics["thdv_percent"],
        "no_equilibrium_samples": int(np.sum(out["equilibrium"] == 0)),
        "steady_voltage_pu": float(out["voltage_pu"][settled_mask].mean()),
    }
    # Explicitly study assumptions, not legal grid-code acceptance thresholds.
    checks = [
        ("Post-fault recovery", metrics["postfault_min_voltage_pu"] >= 0.9, ">= 0.90 pu after clearance + 0.5 s"),
        ("Frequency nadir", metrics["frequency_nadir_hz"] >= 49.5, ">= 49.50 Hz"),
        ("AI workload ramp", metrics["workload_ramp_mw_s"] <= 20, "<= 20 MW/s, 100 ms window"),
        ("Harmonic voltage", metrics["thdv_percent"] <= 3, "THDv <= 3% for assumed spectrum"),
        ("IT supply continuity", metrics["unserved_mwh"] <= 0.0001, "unserved energy <= 0.1 kWh"),
    ]
    national = {"profile": "FI directly transmission-connected large demand, June 2026",
                "applicability": "Potentially applicable to new >=30 MW directly connected demand; confirm project terms",
                "source": "https://www.fingrid.fi/globalassets/dokumentit/fi/palvelut/kulutuksen-ja-tuotannon-liittaminen-kantaverkkoon/fingrid---suurten-kulutuslaitosten-tekniset-vaatimukset.pdf",
                "basis": "Section 9.1.11; reduced-model recovery screening only"}
    fault_case = c.scenario in ("fault", "recovery", "combined")
    if fault_case:
        clear = 2+c.fault_duration
        recoveries = np.where((t >= clear) & (out["voltage_pu"] >= 0.9))[0]
        if len(recoveries):
            origin = t[recoveries[0]]
            idx = min(n-1, int(np.searchsorted(t, origin+1)))
            recovered = out["grid_mw"][idx]/base
            national.update({"status": "MEETS RECOVERY SCREEN" if recovered >= 0.9 else "RECOVERY RISK",
                             "grid_demand_at_deadline_pu": float(recovered),
                             "deadline_s": float(t[idx]), "criterion": ">=90% pre-fault grid demand by 1 s after V>=0.90 pu"})
        else:
            national.update({"status": "RECOVERY RISK", "criterion": "Voltage did not recover to 0.90 pu"})
        national["whole_facility_disconnection_detected"] = bool(np.any(out["connected"] == 0))
        national["frt_conclusion"] = "Protection logic requires redesign and EMT verification" if national["whole_facility_disconnection_detected"] else "Not certified; full voltage envelope not exercised"
    else:
        national["status"] = "NOT EXERCISED"
    return {"config": asdict(c), "time_s": t.round(6).tolist(),
            "signals": {k: v.round(7).tolist() for k, v in out.items()}, "metrics": metrics,
            "checks": [{"name": a, "passed": bool(b), "criterion": d, "basis": "Illustrative engineering study target"} for a,b,d in checks],
            "harmonics": harmonics, "modes": controller_modes(c.scr, c.q_gain), "national_screen": national,
            "scope": "Synthetic positive-sequence screening. Not grid-code certification or an EMT/GFM validation."}
