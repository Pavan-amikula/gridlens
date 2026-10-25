import math
import numpy as np
import pytest
from fastapi.testclient import TestClient
from gridlens.engine import Config, simulate, power_flow, harmonic_screen, controller_modes
from gridlens.server import app

def test_powerflow_matches_independent_complex_kirchhoff():
    e,p,q,r,x=1.1,.8,.2,.02,.15
    v,ok=power_flow(e,p,q,r,x)
    assert ok
    # With receiving voltage real, E=V+Z*conj(S/V); source magnitude must agree.
    source=complex(v,0)+complex(r,x)*complex(p,-q)/v
    assert abs(source)==pytest.approx(e,abs=1e-12)

def test_no_load_and_collapse():
    assert power_flow(1,0,0,.01,.2)==(1,True)
    assert not power_flow(.1,3,2,.1,.5)[1]

@pytest.fixture(scope="module")
def cases():
    return {m:simulate(Config(mitigation=m)) for m in ['baseline','coordinated']}

def test_finite_energy_and_converter_bounds(cases):
    r=cases['coordinated'];s=r['signals'];c=r['config']
    assert np.isfinite(list(r['metrics'].values())).all()
    assert all(.1-1e-9<=v<=.9+1e-9 for v in s['soc'])
    assert max(abs(v) for v in s['bess_mw'])<=c['bess_mw']+1e-6
    assert np.max(np.array(s['bess_mw'])**2+np.array(s['reactive_mvar'])**2)<=2500+1e-4
    pb=np.array(s['bess_mw']);step=c['dt']/(3600*c['bess_mwh'])
    expected=c['initial_soc']-np.sum(np.where(pb>=0,pb/.95,pb*.95))*step
    assert s['soc'][-1]==pytest.approx(expected,abs=1e-7)
    assert r['metrics']['no_equilibrium_samples']==0

def test_tradeoffs_and_no_false_compliance(cases):
    a,b=cases['baseline'],cases['coordinated']
    assert b['metrics']['unserved_mwh']<a['metrics']['unserved_mwh']
    assert b['metrics']['workload_ramp_mw_s']<a['metrics']['workload_ramp_mw_s']
    assert b['metrics']['thdv_percent']<a['metrics']['thdv_percent']
    assert not next(x for x in b['checks'] if x['name']=='AI workload ramp')['passed']
    assert b['national_screen']['whole_facility_disconnection_detected']

def test_timestep_convergence(cases):
    fine=simulate(Config(dt=.0025))['metrics'];normal=cases['coordinated']['metrics']
    assert abs(fine['frequency_nadir_hz']-normal['frequency_nadir_hz'])<.005
    assert abs(fine['min_voltage_pu']-normal['min_voltage_pu'])<.025

def test_harmonics_scale_with_network_impedance():
    assert harmonic_screen(2,100)['thdv_percent']==pytest.approx(2*harmonic_screen(4,100)['thdv_percent'])

def test_ups_and_optimized_candidate_energy_limits():
    r=simulate(Config(bess_mw=60,bess_tau=.01,support_mva=80))
    assert all(c['passed'] for c in r['checks'])
    assert r['national_screen']['status']=='RECOVERY RISK'
    assert np.max(np.array(r['signals']['bess_mw'])**2+np.array(r['signals']['reactive_mvar'])**2)<=80**2+1e-4
    fine=simulate(Config(bess_mw=60,bess_tau=.01,support_mva=80,dt=.001))
    assert fine['metrics']['workload_ramp_mw_s']<20

def test_modes_stable_and_gain_reduces_damping():
    a=controller_modes(gain=100)[0];b=controller_modes(gain=600)[0]
    assert a['real']<0 and b['real']<0
    assert b['damping_ratio']<a['damping_ratio']

@pytest.mark.parametrize('kwargs',[{'scr':float('nan')},{'dt':0},{'scenario':'bogus'},{'bess_mwh':0}])
def test_invalid_inputs(kwargs):
    with pytest.raises(ValueError):simulate(Config(**kwargs))

def test_api_and_export():
    with TestClient(app) as client:
        assert client.get('/').status_code==200
        assert client.get('/api/catalog').status_code==200
        assert client.post('/api/simulate',json={'scr':0}).status_code==422
        assert client.post('/api/simulate',json={'unknown':3}).status_code==422
        r=client.post('/api/export',json={'scenario':'frequency'})
        assert r.status_code==200
        assert r.text.startswith('time_s,voltage_pu,frequency_hz')
        assert len(r.text.strip().splitlines())==2402
