"""Recreate complete matrix, raw traces, parameter sweeps and publication figures."""
import csv,json,time,hashlib,platform
from pathlib import Path
from dataclasses import asdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from gridlens.engine import Config,simulate,SCENARIOS,MITIGATIONS,controller_modes

ROOT=Path(__file__).resolve().parents[1]
def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    out=ROOT/'results';out.mkdir(exist_ok=True);(out/'traces').mkdir(exist_ok=True)
    started=time.perf_counter();rows=[];references={}
    for scr in (2.,4.,8.):
        for scenario in SCENARIOS:
            for mitigation in MITIGATIONS:
                c=Config(scr=scr,scenario=scenario,mitigation=mitigation)
                r=simulate(c)
                rows.append({'scenario':scenario,'mitigation':mitigation,'scr':scr,**r['metrics'],
                             'national_recovery_screen':r['national_screen']['status']})
                if scr==4 and scenario=='combined':
                    references[mitigation]=r
                    write_csv(out/'traces'/f'{mitigation}.csv',[{'time_s':t,**dict(zip(r['signals'],vals))} for t,*vals in zip(r['time_s'],*r['signals'].values())])
        print(f'Completed SCR={scr}: {len(rows)} cases',flush=True)
    write_csv(out/'study_matrix.csv',rows)
    gains=[]
    for scr in (2,4,8):
        for gain in (0,100,200,300,450,600):
            for mode in controller_modes(scr,gain):gains.append({'scr':scr,'gain':gain,**mode})
    write_csv(out/'controller_sweep.csv',gains)
    convergence=[]
    for dt in (.01,.005,.0025):
        r=simulate(Config(dt=dt))
        convergence.append({'dt_s':dt,**r['metrics']})
    write_csv(out/'convergence.csv',convergence)
    summary={'case_count':len(rows),'method':'Synthetic balanced positive-sequence screening',
             'reference':{k:{'metrics':v['metrics'],'checks':v['checks'],'national_screen':v['national_screen']} for k,v in references.items()},
             'execution_seconds':round(time.perf_counter()-started,3),'python':platform.python_version(),
             'engine_sha256':hashlib.sha256((ROOT/'gridlens'/'engine.py').read_bytes()).hexdigest()}
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#cbd2cd','axes.labelcolor':'#334a50','text.color':'#172b35','xtick.color':'#65757b','ytick.color':'#65757b','axes.grid':True,'grid.color':'#e4e8e3','grid.linewidth':.6})
    fig,axes=plt.subplots(2,2,figsize=(12,6.5),layout='constrained')
    a,b=references['baseline'],references['coordinated']
    for ax,(key,title,unit) in zip(axes.flat,[('voltage_pu','Point-of-connection voltage','pu'),('frequency_hz','Regional frequency','Hz'),('grid_mw','Grid active-power import','MW'),('unserved_mw','IT supply deficit','MW')]):
        ax.plot(a['time_s'],a['signals'][key],color='#8d9a9c',ls='--',lw=1.3,label='Unmitigated')
        ax.plot(b['time_s'],b['signals'][key],color='#b5522f',lw=1.7,label='Coordinated')
        ax.axvspan(2,2.15,color='#b5522f',alpha=.09);ax.set(title=title,xlabel='Time / s',ylabel=unit,xlim=(0,12));ax.legend(fontsize=8)
    fig.suptitle('GridLens | Combined disturbance · 100 MW · SCR 4',fontsize=15)
    fig.savefig(out/'transient_comparison.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(12,3.5),layout='constrained')
    for ax,(metric,title) in zip(axes,[('unserved_mwh','Unserved IT energy / kWh'),('workload_ramp_mw_s','AI ramp / MW per s'),('thdv_percent','Assumed voltage THD / %')]):
        values=[v['metrics'][metric]*(1000 if metric=='unserved_mwh' else 1) for v in references.values()]
        ax.bar(range(6),values,color=['#a8b3b0']*5+['#b5522f']);ax.set_xticks(range(6),['Base','BESS','STAT','SC','UPS','Coord'],fontsize=8);ax.set_title(title,fontsize=11)
    fig.savefig(out/'mitigation_tradeoffs.png',dpi=180);plt.close(fig)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
