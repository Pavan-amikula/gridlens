# Findings, risks and mitigation priorities

## Purpose and reproducibility

Assess technical risks for a representative large data-center transmission connection and compare mitigation behavior before committing to expensive vendor EMT studies. The project combines a primary-source review, transparent reduced-order physics, deterministic experiments, measured HPC loading sensitivity and an interactive evidence interface. It supports a thesis investigation; it is not a substitute for it.

All results below are synthetic screening results unless explicitly identified as PM100 measured loading. The full matrix, traces, source hash, convergence and tuning data are in `results/`.

## Reference comparison

100 MW rated demand, PF 0.98, SCR 4, X/R 10; source dip at 2 s for 150 ms; 200 MW regional generation loss at 3 s; 30 MW AI load ramp over 200 ms at 5 s. A 12 s horizon uses a 5 ms integration step.

The default coordinated package changes minimum voltage from 0.564 to 0.586 pu and frequency nadir from 49.813 to 49.840 Hz. It reduces the AI-window ramp from 150.0 to 70.6 MW/s. Online UPS covers the 23.08 kWh IT deficit of the unmitigated case, producing zero modeled unserved energy within the supplied power and energy limits. Assumed filtering reduces THDv from 5.54% to 1.61%. The harmonic improvement is conditional on the assumed current spectrum and attenuation, not a measured filter performance result.

The default coordinated package meets four of five illustrative study targets. Its ramp remains above the 20 MW/s target; the whole-horizon ramp also includes the much larger fault-driven load interruption. These two measurements must not be conflated.

## Capacity, bandwidth and saturation

The 12-case tuning sweep changes BESS active rating and first-order response time. The 60 MW case uses an 80 MVA support envelope; smaller cases use 50 MVA. Capacity and bandwidth are both required: making a saturated 40 MW controller faster does not automatically improve the worst ramp, because frequency support and ramp buffering compete for headroom.

A 60 MW / 20 MWh BESS with a 10 ms assumed response, 80 MVA support envelope, UPS, STATCOM behavior and assumed filtering reduces the AI-window ramp to 14.68 MW/s: a 90.2% reduction from baseline. It meets five illustrative targets. This is a candidate for further EMT evaluation, not an optimized procurement specification. A 10 ms response is a modeling assumption requiring vendor verification; no cost, thermal, lifetime or protection optimum is claimed.

Candidate timestep refinement gives 14.68 / 16.30 / 17.35 MW/s at 5 / 2.5 / 1 ms. The target still passes at 1 ms, where the baseline reduction is 88.4%. The metric shows measurable numerical sensitivity; quote the timestep alongside the reduction. Do not report 90.2% as a converged equipment-performance guarantee.

## IT continuity can conflict with grid recovery

Fingrid's June 2026 technical reading indicates recovery to at least 90% of pre-fault grid demand within one second after voltage reaches 0.90 pu, subject to applicability and the controlling Finnish original. The endpoint screen uses the simulation's receiving-end grid import, not IT consumption behind UPS.

The default coordinated package reaches roughly 55.5% of pre-fault import at that deadline. The tuned candidate reaches roughly 75.5%. Both flag recovery risk. The unmitigated case recovers the endpoint but still has a complete-transfer flag and an IT energy deficit. Therefore no architecture is presented as fully compliant. IT continuity, import recovery and facility ride-through must each be assessed.

Recommended next control change: coordinate UPS transfer, BESS ramp control and grid-import recovery with a TSO-agreed priority hierarchy. Avoid a slow ramp limiter that suppresses demand restoration after a fault. Use permitted internal current blocking and validated protection coordination instead of assuming an entire demand facility may disconnect. Retest the complete voltage envelope, including retained connection and recovery timing.

## Other mitigation trade-offs

| Measure | Main benefit represented | Constraint / risk requiring follow-up |
|---|---|---|
| BESS | Active-power buffering, frequency support | Power/current saturation, SOC, bandwidth, import recovery; no GFM claim |
| STATCOM | Reactive voltage support | Finite current, low-voltage capability, control delay; does not supply sustained active energy |
| Synchronous condenser | Reactive support and additional effective inertia | Aggregate surrogate omits actual fault-current and machine/AVR behavior; losses and maintenance not quantified |
| MV UPS | IT continuity and controlled reconnection | Backup autonomy, transfer coordination, simultaneous load restoration, grid-demand recovery |
| Harmonic filter | Reduced assumed harmonic voltage | Resonance, detuning, background distortion, site emission allocation and switching transients |
| Coordinated package | Complementary service across several objectives | More devices and control interactions; rating/headroom allocation and protection need validation |

## Data-informed loading

The original PM100 v3 file checksum matches the published Zenodo MD5. From the first 64 rows, the pipeline retains 30 valid jobs and 2,022 original power values. The P10/median/P90 of retained mean power per allocated node are about 510/602/889 W. Normalization to a hypothetical 100 MW median facility produces loading points near 84.7/100.0/147.6 MW. Each is simulated with baseline and coordinated support.

This explicitly separates real measured loading from synthetic aggregation. It does not validate the electrical model, reproduce hyperscale POI telemetry or justify a subsecond workload waveform. The subset is deterministic and small; a representative statistical study needs a justified sampling plan over the full dataset.

## Validation and limits

Numerical tests independently verify the analytical AC balance with Kirchhoff's relation, detect infeasible constant-PQ cases, check SOC/energy accounting and power/MVA limits, compare timestep convergence, verify harmonic impedance scaling, inspect mode trends, reject invalid inputs and validate API/CSV behavior. Fifteen tests pass in the supplied environment. Browser checks exercise the actual interface and exports. The video records those real interactions.

The balanced radial network does not establish network-wide voltage stability. The coherent-area frequency equation does not establish inter-area stability. The two-state local control poles are not a full-system eigenanalysis. The harmonic screen does not establish resonance immunity. The BESS is not a validated grid-forming converter. The condenser is not a full machine model. Licensed simulators and hardware were not used. A credible thesis should extend these areas using validated facility/vendor models, TSO source cases, full FRT envelopes and measured control/protection responses.

## Recommended thesis sequence

1. Agree applicability and acceptance criteria with the relevant system operator; retain legal status and version for each source.
2. Acquire validated IT rectifier, cooling, UPS, BESS and STATCOM models; initialize the actual transmission equivalent.
3. Reproduce baseline and coordinated studies in RMS and EMT tools; compare aligned exported traces using the supplied exchange utility.
4. Replace the local-loop screen with converter impedance/interaction analysis and network modes.
5. Resolve the identified ride-through/import-recovery conflict, then assess cost, energy autonomy, equipment ratings and robustness across uncertainty.
6. Document model provenance, sensitivity, deviations and independent review before making compliance conclusions.
