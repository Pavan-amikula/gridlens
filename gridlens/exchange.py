"""Vendor-neutral result ingestion; never impersonates a licensed simulator run."""
import csv
from pathlib import Path
import numpy as np

REQUIRED=('time_s','voltage_pu','frequency_hz','grid_mw')

def read_trace(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not set(REQUIRED).issubset(reader.fieldnames or []):
            raise ValueError('Trace requires time_s, voltage_pu, frequency_hz, grid_mw')
        rows=list(reader)
    if len(rows)<2:raise ValueError('At least two trace rows required')
    values={k:np.array([float(r[k]) for r in rows]) for k in REQUIRED}
    if not all(np.isfinite(v).all() for v in values.values()):raise ValueError('Non-finite trace value')
    if not np.all(np.diff(values['time_s'])>0):raise ValueError('Time must be strictly increasing')
    return values

def compare_traces(reference,candidate):
    """Interpolate over overlap only; callers must align fault time and bases."""
    a,b=read_trace(reference),read_trace(candidate)
    mask=(a['time_s']>=b['time_s'][0])&(a['time_s']<=b['time_s'][-1])
    t=a['time_s'][mask]
    if len(t)<2:raise ValueError('Insufficient overlapping samples')
    return {key:{'rmse':float(np.sqrt(np.mean((a[key][mask]-np.interp(t,b['time_s'],b[key]))**2))),
                 'max_abs_error':float(np.max(np.abs(a[key][mask]-np.interp(t,b['time_s'],b[key]))))}
            for key in REQUIRED[1:]}
