from typing import List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from web_app import render_page_html
from algo_dp import dp_optimizer

app = FastAPI(title="Turbine Control API")

class TurbineConstraint(BaseModel):
    name: str
    max_flow: float
    available: bool

class OptimizationPayload(BaseModel):
    total_flow: float
    upstream_elevation: float
    algorithm: str
    turbines: List[TurbineConstraint]

@app.get("/", response_class=HTMLResponse)
def homepage() -> str:
    return render_page_html("index.html")

@app.post("/api/optimize")
def optimize_turbines(payload: OptimizationPayload) -> dict[str, object]:
    qmax_by_turbine = [t.max_flow if t.available else 0.0 for t in payload.turbines]
    
    sol = dp_optimizer.optimize(
        qtot=payload.total_flow,
        niv_amont=payload.upstream_elevation,
        qmax_by_turbine=qmax_by_turbine
    )
    
    results = []
    for i, t in enumerate(payload.turbines):
        qi = sol['q_opt'][i]
        head = dp_optimizer.model.hnet(payload.upstream_elevation, payload.total_flow, qi) if qi > 0 else 0.0
        
        results.append({
            "name": t.name,
            "flow": round(qi, 2),
            "head": round(head, 2),
            "power": round(sol['p_opt_by_turbine'][i], 2)
        })
            
    return {
        "status": "success",
        "message": f"Algorithme {payload.algorithm} terminé.",
        "results": results,
        "total_power": round(sol['p_opt_total'], 2)
    }

import pandas as pd
import pathlib

_CACHED_ROWS = None

def _get_qtot_niv_iter() -> list[tuple[float, float]]:
    global _CACHED_ROWS
    if _CACHED_ROWS is not None:
        return _CACHED_ROWS
        
    xlsx_path = pathlib.Path(__file__).parent.parent / "DataProjet2026.xlsx"
    df = pd.read_excel(xlsx_path, header=2, engine='openpyxl')
    df = df.dropna(how='all')
    
    # Clean up column names
    df.columns = [str(c).replace('\n', ' ').replace('\r', ' ').strip() for c in df.columns]
    
    res = []
    qtot_col = next(c for c in df.columns if 'qtot' in c.lower())
    niv_col = next(c for c in df.columns if 'niv amont' in c.lower() or 'nivamont' in c.lower())
    
    for _, row in df.iterrows():
        qtot = row[qtot_col]
        niv = row[niv_col]
        if pd.isna(qtot) or pd.isna(niv):
            continue
        try:
            res.append((float(qtot), float(niv)))
            if len(res) == 20:
                break
        except Exception:
            pass
            
    _CACHED_ROWS = res
    return res

@app.post("/api/iterations")
def get_iterations(payload: OptimizationPayload) -> dict[str, object]:
    iterations_data = {f"Turbine {i}": [] for i in range(1, 6)}
    qmax_by_turbine = [t.max_flow if t.available else 0.0 for t in payload.turbines]
    
    try:
        rows = _get_qtot_niv_iter()
    except Exception as e:
        return {"status": "error", "message": f"Erreur de lecture du dataset: {str(e)}"}
        
    for qtot_val, niv_val in rows:
        sol = dp_optimizer.optimize(
            qtot=qtot_val, 
            niv_amont=niv_val, 
            qmax_by_turbine=qmax_by_turbine
        )
        for t_idx in range(5):
            iterations_data[f"Turbine {t_idx+1}"].append(round(sol['q_opt'][t_idx], 2))
            
    return {
        "status": "success",
        "iterations": list(range(1, len(rows) + 1)),
        "data": iterations_data
    }
