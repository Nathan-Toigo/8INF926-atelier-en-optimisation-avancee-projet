import base64
from pathlib import Path
from typing import Mapping


TURBINE_MESSAGES = [
	"Turbine 1 selected: preparing the first energy stream.",
	"Turbine 2 selected: balancing airflow and rotation speed.",
	"Turbine 3 selected: the system is generating momentum.",
	"Turbine 4 selected: converting wind into steady output.",
	"Turbine 5 selected: output stable and ready for reporting.",
]

TURBINE_NAMES = [f"Turbine {index}" for index in range(1, 6)]


def load_page_html(template_name: str = "index.html") -> str:
	"""Load the raw HTML content from the app directory."""
	template_path = Path(__file__).resolve().parent / template_name
	return template_path.read_text(encoding="utf-8")


def load_turbine_image_data_uri(image_name: str = "turbine.png") -> str:
	"""Load a local turbine image and return it as a data URI."""
	image_path = Path(__file__).resolve().parent / "img" / image_name
	image_bytes = image_path.read_bytes()
	encoded = base64.b64encode(image_bytes).decode("ascii")
	return f"data:image/png;base64,{encoded}"


def build_interaction_script() -> str:
	"""Build the client-side behavior for the turbine tiles."""
	return f"""
<script>
	const messageBox = document.getElementById("messageBox");
	const statusOutput = document.getElementById("statusOutput");
	const sendStatesButton = document.getElementById("sendStatesButton");
	const turbineCards = document.querySelectorAll(".turbine-card");
	const turbineSliders = document.querySelectorAll(".turbine-slider");

	function getTurbineStates() {{
		const states = {{}};

		turbineSliders.forEach((slider) => {{
			states[slider.dataset.name] = Number(slider.value);
		}});

		return states;
	}}

	function refreshCardAppearance(card) {{
		const slider = card.querySelector(".turbine-slider");
		const value = Number(slider.value);
		const stateBadge = card.querySelector(".state-pill");
		slider.style.background = "#d1d5db";

		stateBadge.textContent = `${{value}}%`;

		if (value > 0) {{
			stateBadge.className = "state-pill px-2 py-1 text-xs font-semibold text-slate-700";
			return;
		}}

		stateBadge.className = "state-pill px-2 py-1 text-xs font-semibold text-slate-700";
	}}

	turbineSliders.forEach((slider) => {{
		slider.addEventListener("input", () => {{
			const card = slider.closest(".turbine-card");
			refreshCardAppearance(card);
			messageBox.textContent = `${{slider.dataset.name}} set to ${{slider.value}}%.`;
		}});
	}});

	sendStatesButton.addEventListener("click", async () => {{
		sendStatesButton.disabled = true;
		sendStatesButton.textContent = "Sending...";

		try {{
			const response = await fetch("/api/turbines", {{
				method: "POST",
				headers: {{
					"Content-Type": "application/json",
				}},
				body: JSON.stringify({{ states: getTurbineStates() }}),
			}});

			const payload = await response.json();
			statusOutput.textContent = payload.summary || payload.message || "No response returned.";
			messageBox.textContent = payload.message || "Turbine states sent.";
		}} catch (error) {{
			statusOutput.textContent = `Request failed: ${{error.message}}`;
			messageBox.textContent = "Could not send turbine states.";
		}} finally {{
			sendStatesButton.disabled = false;
			sendStatesButton.textContent = "Send states";
		}}
	}});

		turbineCards.forEach((card) => refreshCardAppearance(card));
		messageBox.textContent = "Use the sliders (0% to 100%), then click Send states.";
</script>
""".strip()


def render_page_html(template_name: str = "index.html") -> str:
	"""Render the page HTML with the interaction script injected."""
	html = load_page_html(template_name)
	html = html.replace("{{ TURBINE_IMAGE_SRC }}", load_turbine_image_data_uri())
	return html.replace("<!-- WEB_APP_SCRIPT -->", build_interaction_script())


def format_turbine_states(states: Mapping[str, int | float]) -> list[dict[str, str | int]]:
	"""Normalize turbine states into a printable structure."""
	formatted_states: list[dict[str, str | int]] = []
	for turbine_name in TURBINE_NAMES:
		raw_value = states.get(turbine_name, 0)
		try:
			percentage = int(raw_value)
		except (TypeError, ValueError):
			percentage = 0
		percentage = max(0, min(100, percentage))
		formatted_states.append(
			{
				"name": turbine_name,
				"percentage": percentage,
				"state": "active" if percentage > 0 else "inactive",
				"label": f"{percentage}%",
			}
		)
	return formatted_states


def build_turbine_state_message(states: Mapping[str, int | float]) -> str:
	"""Build a human-readable message for the API response."""
	formatted_states = format_turbine_states(states)
	lines = [f"{item['name']}: {item['percentage']}% ({item['state']})" for item in formatted_states]
	return "\n".join(lines)
