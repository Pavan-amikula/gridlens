import argparse,json
from gridlens.exchange import compare_traces
p=argparse.ArgumentParser(description='Compare aligned PSCAD, PowerFactory or PSS/E exported CSV traces')
p.add_argument('reference');p.add_argument('candidate');a=p.parse_args()
print(json.dumps(compare_traces(a.reference,a.candidate),indent=2))
