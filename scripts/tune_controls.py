"""Bandwidth/capacity trade-off sweep; retains infeasible targets."""
import csv,json
from pathlib import Path
from gridlens.engine import Config,simulate
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for mw in (20.,40.,60.):
    for tau in (.01,.03,.06,.1):
        rating=80. if mw==60 else 50.
        r=simulate(Config(bess_mw=mw,bess_tau=tau,support_mva=rating))
        rows.append({'bess_mw':mw,'support_mva':rating,'response_tau_s':tau,**r['metrics'],
                     'targets_met':sum(x['passed'] for x in r['checks']),
                     'national_recovery':r['national_screen']['status']})
with (ROOT/'results'/'control_tuning.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
best=simulate(Config(bess_mw=60,bess_tau=.01,support_mva=80))
(ROOT/'results'/'optimized_candidate.json').write_text(json.dumps({k:v for k,v in best.items() if k not in ['time_s','signals']},indent=2),encoding='utf-8')
print(json.dumps({'metrics':best['metrics'],'checks':best['checks'],'national_screen':best['national_screen']},indent=2))
convergence=[]
for dt in (.005,.0025,.001):
    r=simulate(Config(bess_mw=60,bess_tau=.01,support_mva=80,dt=dt))
    convergence.append({'dt_s':dt,**r['metrics']})
with (ROOT/'results'/'candidate_convergence.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(convergence[0]));w.writeheader();w.writerows(convergence)
