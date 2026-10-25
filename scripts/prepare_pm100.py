"""Reproduce an attributed CC-BY subset and operating-point sensitivity.

Download original separately (287 MB); source file is not committed.
Usage: python scripts/prepare_pm100.py path/to/job_table.parquet
"""
import argparse,csv,hashlib,json
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from gridlens.engine import Config,simulate

ROOT=Path(__file__).resolve().parents[1]
def main(source):
    source=Path(source);digest=hashlib.md5(source.read_bytes()).hexdigest()
    if digest!='cf85f171a5ed5ff1d951d93f9bcbc6ef':raise ValueError('Source checksum does not match Zenodo v3')
    columns=['job_id','num_nodes_alloc','node_power_consumption']
    batch=next(pq.ParquetFile(source).iter_batches(batch_size=64,columns=columns)).to_pylist()
    samples=[];jobs=[]
    for idx,row in enumerate(batch):
        values=np.asarray(row['node_power_consumption'],dtype=float)
        nodes=row['num_nodes_alloc']
        if nodes is None or nodes<=0 or len(values)<2 or not np.isfinite(values).all() or np.min(values)<=0:continue
        # Retain first 120 original power values; only add provenance columns.
        values=values[:120]
        for j,v in enumerate(values):samples.append({'source_row':idx,'job_id':row['job_id'],'nodes':nodes,'sample_index':j,'job_power_w':int(v)})
        jobs.append({'source_row':idx,'job_id':row['job_id'],'nodes':nodes,'retained_samples':len(values),'mean_node_w':float(values.mean()/nodes)})
    data=ROOT/'data';data.mkdir(exist_ok=True)
    with (data/'pm100_subset.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(samples[0]));w.writeheader();w.writerows(samples)
    means=np.array([r['mean_node_w'] for r in jobs]);q=np.quantile(means,[.1,.5,.9])
    operating=[]
    for name,value in zip(['p10','p50','p90'],q):
        load=float(np.clip(100*value/q[1],20,300))
        for mitigation in ['baseline','coordinated']:
            result=simulate(Config(load_mw=load,mitigation=mitigation))
            operating.append({'quantile':name,'load_mw':load,'mitigation':mitigation,**result['metrics']})
    provenance={'dataset':'PM100 v3, Marconi100 jobs May–October 2020','authors':'Francesco Antici, Mohsen Seyedkazemi Ardebili, Andrea Bartolini, Zeynep Kiziltan',
        'doi':'https://doi.org/10.5281/zenodo.10127767','license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/',
        'original_url':'https://zenodo.org/api/records/10127767/files/job_table.parquet/content','original_md5':digest,
        'selection':'First 64 source rows; retain valid positive power with >=2 samples and allocated nodes; first 120 values per retained job.',
        'retained_jobs':len(jobs),'retained_samples':len(samples),'jobs':jobs,'node_power_quantiles_w':q.tolist(),
        'use':'HPC loading sensitivity only. Normalize mean-node-power quantiles to a hypothetical 100 MW median facility. No inference of hyperscale grid disturbance behavior or subsecond bandwidth.',
        'not_representative':'Deterministic small head subset, not a representative sample of the full dataset.',
        'operating_points':operating}
    (data/'pm100_provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    plt.rcParams.update({'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans'})
    fig,axes=plt.subplots(1,2,figsize=(11,3.6),layout='constrained')
    axes[0].hist(means,bins=12,color='#416e91',edgecolor='white');axes[0].set(xlabel='Mean power per allocated node / W',ylabel='Jobs in retained subset',title='PM100: measured HPC loading')
    sample_job=max(jobs,key=lambda j:j['retained_samples'])
    trace=[r['job_power_w']/r['nodes'] for r in samples if r['job_id']==sample_job['job_id']]
    axes[1].plot(range(len(trace)),trace,color='#b5522f');axes[1].set(xlabel='Original sample index (no time compression)',ylabel='Power per node / W',title=f"Job {sample_job['job_id']}: retained measurements")
    fig.savefig(ROOT/'results'/'pm100_loading.png',dpi=180);plt.close(fig)
    print(json.dumps({k:v for k,v in provenance.items() if k not in ['jobs','operating_points']},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');main(p.parse_args().source)
