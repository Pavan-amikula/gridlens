# Measured workload data

`pm100_subset.csv` is an attributed derived subset of **PM100 v3**, by Francesco Antici, Mohsen Seyedkazemi Ardebili, Andrea Bartolini and Zeynep Kiziltan (2023), [doi:10.5281/zenodo.10127767](https://doi.org/10.5281/zenodo.10127767), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This dataset is separate from the repository's MIT software license.

Changes: select the first 64 source rows, reject missing/nonpositive power or invalid allocated-node counts, retain up to the first 120 node-level job-power values per job, and flatten to CSV with provenance columns. `job_power_w` is the original aggregate job power, not a per-node value; divide by allocated nodes for a per-node loading statistic. Sample index preserves order, not a synthesized timestamp. This is a small deterministic head subset and is not representative of all PM100 jobs.

`pm100_provenance.json` records the original MD5, exact selection, job IDs, statistics and six loading sensitivity studies. The original Parquet is not committed. Reproduce with:

```bash
pip install pyarrow
python scripts/prepare_pm100.py /path/to/job_table.parquet
```

The selected job-power mean quantiles are normalized to a hypothetical 100 MW median facility operating point. Those operating points feed the same synthetic disturbance engine. This is **measured-data-informed loading sensitivity**, not measured AI data-center grid telemetry and not model calibration. The data is not compressed into a 12-second waveform. The original extraction repository uses 20-second alignment for occupancy; no subsecond bandwidth is inferred from these records.

Google PowerData2019, Fingrid historical frequency data and MIT Supercloud were reviewed as alternatives in the [source register](../docs/research.md); they are not silently included as measurements in these simulations.
