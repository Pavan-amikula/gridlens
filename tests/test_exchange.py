import pytest
from gridlens.exchange import compare_traces,read_trace

def test_resampling_and_units(tmp_path):
    a=tmp_path/'a.csv';b=tmp_path/'b.csv'
    a.write_text('time_s,voltage_pu,frequency_hz,grid_mw\n0,1,50,100\n0.5,.95,49.5,110\n1,.9,49,120\n')
    b.write_text('time_s,voltage_pu,frequency_hz,grid_mw\n0,1,50,100\n1,.9,49,120\n')
    assert compare_traces(a,b)['grid_mw']['rmse']==pytest.approx(0)

def test_reject_duplicate_time(tmp_path):
    p=tmp_path/'bad.csv';p.write_text('time_s,voltage_pu,frequency_hz,grid_mw\n0,1,50,100\n0,1,50,100\n')
    with pytest.raises(ValueError):read_trace(p)
