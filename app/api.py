from typing import Dict

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from web_app import build_turbine_state_message, format_turbine_states, render_page_html


app = FastAPI(title="Turbine Control API")


class TurbineStatePayload(BaseModel):
	states: Dict[str, int] = Field(default_factory=dict)


@app.get("/", response_class=HTMLResponse)
def homepage() -> str:
	return render_page_html("index.html")


@app.post("/api/turbines")
def submit_turbine_states(payload: TurbineStatePayload) -> dict[str, object]:
	formatted_states = format_turbine_states(payload.states)
	message = build_turbine_state_message(payload.states)
	# NOMAD : temps de resolution par test
	# NOMAD + Prog Dynamique : puissance optimisé
	# NOMAD + Prog Dynamique : 
	# NOMAD + Prog Dynamique : 
	return {
		"message": "Turbine states received.",
		"summary": message,
		"states": formatted_states,
	}
