"""Local study API and dashboard; no external services or API keys needed."""
import csv
import io
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from .engine import Config, simulate, SCENARIOS, MITIGATIONS

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="GridLens", version="1.0.0")

class Study(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    scenario: str = "combined"
    mitigation: str = "coordinated"
    scr: float = 4
    load_mw: float = 100
    bess_mw: float = 40
    bess_tau: float = 0.06
    support_mva: float = 50
    fault_voltage: float = 0.55
    q_gain: float = 300

@app.get("/api/catalog")
def catalog():
    return {"scenarios": SCENARIOS, "mitigations": MITIGATIONS}

def run(body):
    try:
        return simulate(Config(**body.model_dump()))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

@app.post("/api/simulate")
def study(body: Study):
    return run(body)

@app.post("/api/export")
def export(body: Study):
    result = run(body)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["time_s", *result["signals"]])
    writer.writerows(zip(result["time_s"], *result["signals"].values()))
    return Response(output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=gridlens-trace.csv"})

@app.get("/api/evidence")
def evidence():
    return FileResponse(ROOT/"results"/"summary.json")

@app.get("/api/workload")
def workload():
    return FileResponse(ROOT/"data"/"pm100_provenance.json")

@app.get("/")
def home():
    return FileResponse(ROOT/"web"/"index.html")

app.mount("/static", StaticFiles(directory=ROOT/"web"), name="static")

def main():
    import uvicorn
    uvicorn.run("gridlens.server:app", host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
