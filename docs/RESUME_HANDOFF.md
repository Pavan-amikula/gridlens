# GridLens — complete resume and interview handoff

## Instructions for a resume-writing chat

Use the following verified project evidence to tailor a resume to **Hitachi Energy R0144080: Master thesis — Grid Code Compliance Assessment of Large Data Centers: Identification of Interconnection Risks and Mitigation Measures**. Choose two or three strong bullets; retain truthful boundaries. Do not invent a thesis award, employment relationship, qualification, professional simulator experience, hardware experiment, field deployment or certification. Use completed-project wording only after the applicant has run and understood the code and can explain it in an interview. Do not claim PSCAD, PowerFactory, PSS/E or GFM validation merely because these appear in the validation roadmap.

## Project identity

**Title:** GridLens — Large Data Center Grid Connection Risk and Mitigation Assessment

**Repository:** https://github.com/Pavan-amikula/gridlens

**Type:** Independent electrical power systems portfolio project, October 2026.

**Working deliverable:** Python simulation package and FastAPI dashboard with local calculations, waveform replay, baseline overlays, six-architecture comparison, control-mode display, CSV export, measured-data provenance, automated tests, reproducible evidence and an actual interface demonstration video.

## Complete project description

GridLens investigates the grid integration risks of a representative 100 MW data center connected to a transmission equivalent. It translates a review of European demand-connection rules, Swedish implementation, Finnish June 2026 large-demand requirements and storage-code applicability into a transparent screening workflow. The project separates binding provisions, national implementation, draft requirements, literature guidance and illustrative engineering targets.

The numerical engine solves a nonlinear balanced radial AC interface with voltage-dependent demand and a regional swing/governor frequency model. Synthetic voltage dips, generation loss, AI load ramps, cyclic workloads and recovery events expose risks involving voltage support, frequency response, fault-related transfer, IT continuity and rapid changes in grid import. The model compares unmitigated demand against BESS droop/ramp support, STATCOM behavior, a synchronous-condenser surrogate, MV UPS support and coordinated support with assumed harmonic filtering. Battery energy, SOC, efficiency, active-power limits and a P/Q rating envelope constrain support.

The study matrix contains 108 entries across six scenario views, six architectures and SCR 2/4/8; because fault and recovery share an identical stimulus, there are 90 unique configurations. Additional evidence includes a local reactive-loop pole/gain sweep, three timestep-convergence studies, 12 BESS capacity/bandwidth tuning cases and six measured-data-informed loading studies.

The PM100 pipeline verifies the source dataset checksum, extracts an attributed CC BY 4.0 subset of 2,022 original power samples from 30 HPC jobs and uses mean-node-power quantiles to define hypothetical facility loading points. Those measurements inform loading sensitivity; they are not hyperscale POI data and are not compressed into a synthetic subsecond AI trace.

In the combined 100 MW, SCR 4 reference event, coordinated 40 MW support reduces the AI-window ramp from 150 to approximately 70.6 MW/s, raises post-fault minimum voltage from approximately 0.947 to 0.984 pu, improves frequency nadir from 49.813 to 49.840 Hz, eliminates the modeled 23.08 kWh IT supply deficit using online UPS, and reduces assumed-spectrum THDv from 5.54% to 1.61%. The reference package meets four of five illustrative targets.

A 60 MW / 20 MWh BESS candidate with an 80 MVA support envelope and assumed 10 ms response reduces the AI-window ramp to about 14.7 MW/s, a 90.2% reduction from baseline. This candidate meets all five illustrative targets, but still flags Finnish grid-demand recovery risk. The project identifies a practical conflict: UPS and BESS support can preserve IT continuity while delaying demand restoration at the grid connection. The candidate reaches about 75.5% of pre-fault grid import at the recovery-screen deadline, below the 90% threshold. This motivates protection/recovery priority changes and a full validated EMT study.

The dashboard presents a single-line overview, unit-labeled traces, baseline overlays, illustrative target results and a separate national recovery screen. Automated verification covers AC balance, collapse detection, battery energy/SOC/rating constraints, timestep sensitivity, harmonic impedance scaling, mode trends, invalid-input rejection and API/CSV behavior. Fifteen numerical/API/exchange tests pass, alongside browser QA for desktop/mobile interaction, comparison, playback and downloads.

The project documents a PSCAD / PowerFactory / PSS/E validation handoff and provides a tested vendor-neutral CSV importer with time alignment over overlap, RMSE and peak-error reporting. Native licensed simulator models and calculations are not completed. The BESS control is a reduced-order support surrogate and is not represented as a validated grid-forming converter.

## Suggested resume bullets

- Developed a Python/FastAPI interconnection-risk study bench for a 100 MW data center, comparing six mitigation architectures across 108 matrix entries and SCR 2/4/8 using nonlinear AC-interface and regional frequency models.
- Evaluated BESS, STATCOM, MV UPS, synchronous-condenser surrogate and harmonic-filter support; identified a 60 MW BESS screening candidate that reduced the AI-ramp metric by 90.2% while exposing a separate post-fault grid-demand recovery risk.
- Reviewed EU and Nordic connection requirements, distinguishing demand and storage applicability, and integrated 2,022 attributed PM100 power measurements with reproducible loading sensitivity, 15 automated tests and an interactive waveform/CSV evidence dashboard.

Short two-bullet alternative:

- Built a reproducible 100 MW data-center grid-integration study in Python, comparing voltage/frequency response, load ramping, UPS continuity and assumed harmonic distortion across six mitigation architectures and SCR 2/4/8.
- Reduced the simulated AI-ramp metric from 150 to 14.7 MW/s through BESS capacity/bandwidth tuning; separated IT continuity from national grid-demand recovery risk using a source-traceable requirements register and documented EMT validation plan.

## Supported keywords

Numerical precision note: the candidate's AI ramp is 14.68 MW/s at 5 ms, 16.30 MW/s at 2.5 ms, and 17.35 MW/s at 1 ms. The target passes at every tested step. A more conservative resume bullet can say **“reduced the simulated AI-ramp metric by over 88% across timestep refinement”** instead of quoting 90.2% without the timestep. This sensitivity is documented and should be discussed candidly.

Power system analysis; transmission interconnection; large demand facilities; data-center grid integration; hyperscale/AI load risk; European Demand Connection Code; Nordic grid requirements; voltage ride-through screening; post-fault active-power recovery; voltage/frequency response; short-circuit ratio; BESS; active-power buffering; droop control; STATCOM; reactive-power support; synchronous-condenser surrogate; MV UPS; power quality; harmonic voltage screening; load ramping; control interaction screening; eigenvalues; damping; nonlinear AC equations; dynamic simulation; Python; NumPy; SciPy; FastAPI; Matplotlib; data provenance; PM100; parameter sensitivity; timestep convergence; automated verification; CSV trace comparison; technical documentation.

## Terms requiring qualification

**Grid-forming BESS:** literature and future validation topic; not implemented/validated GFM firmware or EMT control. **PSCAD / PowerFactory / PSS/E:** documented study handoff and CSV result exchange, not executed native models. **Real time:** interactive local simulation and replay, not live-grid or hardware-in-the-loop operation. **Compliance:** applicability review and screening; no formal grid-code certificate. **Harmonics:** assumed spectrum/impedance calculation, not measured emissions or resonance qualification. **Synchronous condenser:** simplified reactive/inertia surrogate. **Best results:** best illustrative ramp candidate from the tested sweep, not an economic/global optimum.

## Interview preparation

Be able to explain the two-bus AC equation, why low-voltage constant-power behavior needs a bounded load model, how SCR changes network impedance, the sign of battery discharge and grid import, the difference between MW and MWh, why SOC and current limits matter, and what the regional frequency equivalent omits.

Be able to explain why a faster saturated BESS can fail to improve the worst ramp; why a STATCOM does not supply sustained active power; why UPS continuity can coexist with a ride-through/recovery concern; why real HPC samples cannot establish subsecond hyperscale load behavior; why local-loop poles do not prove complete converter stability; and what evidence PSCAD/PowerFactory models would add.

Point the interviewer to `results/control_tuning.csv`, `results/study_matrix.csv`, `results/convergence.csv`, `data/pm100_provenance.json`, the demonstration video, and `docs/model.md`. These are stronger evidence than an unsupported claim that every requirement passed.
