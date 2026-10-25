# PSCAD / PowerFactory / PSS®E validation handoff

## Execution status

**Not executed:** licensed simulator models, hardware-in-the-loop tests, site acceptance tests or vendor model calibration. No license or installed simulator has been supplied to this project. CSV result exchange is implemented and tested. The following is a concrete study recipe, not a claim of native project files or verified vendor automation APIs.

1. Create a source and 400/110 kV interface on the agreed base; derive R/X from the selected SCR. Replace this placeholder voltage level with the actual connection offer.
2. Initialize rated demand at 100 MW, PF 0.98, and match 1 pu point-of-connection voltage. Export load-flow P/Q, bus voltages and losses.
3. Separate IT rectifiers, UPS DC bus/storage, cooling motors, transformers, cables, protection and on-site generation. Obtain manufacturer models and validate their permitted operating range.
4. In PSCAD, model the switching/average converter control, voltage-angle behavior for GFM BESS, current priority/limits, UPS transfer, unbalanced faults and protection timers. Use vendor-recommended EMT timesteps and convergence checks; Python's 5 ms screening step is not an EMT setting.
5. In PowerFactory or PSS/E, use validated RMS dynamic load, motor and converter models. Confirm initialization, machine/AVR data and accepted model version before parameter fitting.
6. Exercise the **complete** applicable voltage envelope and frequency-duration obligations, not just the single included voltage sag. Sweep fault clearing, phase jumps, SCR/XR, reactive priority, source impedance and control delays. Coordinate reconnection against post-fault demand recovery requirements.
7. Run a frequency-dependent impedance scan with background harmonic voltage and measured load spectra. Check resonances after filter/STATCOM/BESS changes. Assess equipment thermal loading, protection selectivity and fault-current contribution separately.
8. Export a CSV with `time_s,voltage_pu,frequency_hz,grid_mw`. Use seconds, receiving-end per-unit voltage on the same base, Hz, and MW positive into the facility. Align the fault inception time and sampling definitions. Preserve simulator version, model revisions, initialization report and run logs with the export.
9. Compare traces using `python scripts/compare_external.py results/traces/baseline.csv path/to/vendor.csv`. The importer rejects nonfinite values, missing columns and non-monotonic time. It interpolates within overlap only and reports RMSE and peak absolute errors. Agreement is not independent validation when both models use the same simplifying assumptions.

## Acceptance dossier

For each applicable requirement, record source/revision/clause, facility applicability, approved test waveform, measured quantities, acceptance rule, model provenance, result, deviations, mitigation and independent review. Obtain TSO agreement on models and criteria. Use the source register to avoid applying BESS requirements to the demand facility or treating draft KJV2026 as binding.

## Remaining thesis opportunities

Implement a vendor-validated GFM voltage-source control and compare against grid-following support; add cooling motor stalling/reacceleration; calibrate protection using measured traces; evaluate filter resonance; optimize the Pareto frontier of ramp compliance, IT continuity and post-fault grid import recovery. The Python project provides a reproducible starting point and a transparent shortlist of risks for these studies.
