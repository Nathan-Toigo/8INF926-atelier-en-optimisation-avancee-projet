import base64
from pathlib import Path
from typing import Mapping

def load_page_html(template_name: str = "index.html") -> str:
    """Load the raw HTML content from the app directory."""
    template_path = Path(__file__).resolve().parent / template_name
    return template_path.read_text(encoding="utf-8")

def load_turbine_image_data_uri(image_name: str = "turbine.png") -> str:
    """Load a local turbine image and return it as a data URI."""
    image_path = Path(__file__).resolve().parent / "img" / image_name
    if not image_path.exists():
        return ""
    image_bytes = image_path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}"

def build_interaction_script() -> str:
    """Build the client-side behavior for the application."""
    return """
<script>
    const totalFlowInput = document.getElementById("totalFlowInput");
    const upstreamElevationInput = document.getElementById("upstreamElevationInput");
    const algorithmSelect = document.getElementById("algorithmSelect");
    const launchAlgorithmButton = document.getElementById("launchAlgorithmButton");
    
    const statusOutput = document.getElementById("statusOutput");
    const totalPowerOut = document.getElementById("totalPowerOut");
    
    const showGraphButton = document.getElementById("showGraphButton");
    const graphsWrapper = document.getElementById("graphsWrapper");
    
    let combinedChart = null;

    function getTurbineConstraints() {
        const turbineCards = document.querySelectorAll(".turbine-card");
        const constraints = [];
        
        turbineCards.forEach(card => {
            const name = card.dataset.name;
            const maxFlow = card.querySelector(".turbine-max-flow").value;
            const available = card.querySelector(".turbine-available").checked;
            
            constraints.push({
                name: name,
                max_flow: Number(maxFlow),
                available: available
            });
        });
        
        return constraints;
    }

    launchAlgorithmButton.addEventListener("click", async () => {
        launchAlgorithmButton.disabled = true;
        launchAlgorithmButton.textContent = "Calcul en cours...";
        statusOutput.textContent = "Lancement de l'optimisation...";
        
        try {
            const payload = {
                total_flow: Number(totalFlowInput.value),
                upstream_elevation: Number(upstreamElevationInput.value),
                algorithm: algorithmSelect.value,
                turbines: getTurbineConstraints()
            };
            
            const response = await fetch("/api/optimize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            
            if (data.status === "success") {
                statusOutput.textContent = data.message;
                totalPowerOut.textContent = `${data.total_power} MW`;
                
                // Update turbine cards
                data.results.forEach(res => {
                    const card = document.querySelector(`.turbine-card[data-name="${res.name}"]`);
                    if (card) {
                        card.querySelector(".turbine-flow-out").textContent = res.flow;
                        card.querySelector(".turbine-head-out").textContent = res.head;
                        card.querySelector(".turbine-power-out").textContent = res.power;
                    }
                });
            } else {
                statusOutput.textContent = "Erreur: " + (data.message || "Unknown error");
            }
        } catch (error) {
            statusOutput.textContent = `Erreur de requête: ${error.message}`;
        } finally {
            launchAlgorithmButton.disabled = false;
            launchAlgorithmButton.textContent = "Lancer l'algorithme";
        }
    });

    showGraphButton.addEventListener("click", async () => {
        showGraphButton.disabled = true;
        showGraphButton.textContent = "Chargement...";
        graphsWrapper.classList.remove("hidden");
        
        try {
            const payload = {
                total_flow: Number(totalFlowInput.value),
                upstream_elevation: Number(upstreamElevationInput.value),
                algorithm: algorithmSelect.value,
                turbines: getTurbineConstraints()
            };
            
            const response = await fetch("/api/iterations", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            
            if (data.status === "success") {
                const iterations = data.iterations;
                
                // Distinct colors for each turbine
                const colors = ['#0ea5e9', '#14b8a6', '#f59e0b', '#8b5cf6', '#ec4899'];
                const labels = ['Turbine 1', 'Turbine 2', 'Turbine 3', 'Turbine 4', 'Turbine 5'];
                
                // Build one dataset per turbine
                const datasets = labels.map((name, i) => ({
                    label: `${name} (m³/s)`,
                    data: data.data[name],
                    borderColor: colors[i],
                    backgroundColor: colors[i] + '18',
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    fill: false,
                    tension: 0.35
                }));
                
                const ctx = document.getElementById('chartAllTurbines').getContext('2d');
                
                if (combinedChart) {
                    combinedChart.data.labels = iterations;
                    combinedChart.data.datasets = datasets;
                    combinedChart.update();
                } else {
                    combinedChart = new Chart(ctx, {
                        type: 'line',
                        data: { labels: iterations, datasets: datasets },
                        options: {
                            responsive: true,
                            interaction: { mode: 'index', intersect: false },
                            plugins: {
                                legend: { display: true, position: 'top', labels: { usePointStyle: true, padding: 20, font: { size: 13 } } },
                                tooltip: { mode: 'index', intersect: false }
                            },
                            scales: {
                                x: { title: { display: true, text: 'Itération', font: { size: 13, weight: 'bold' } }, grid: { color: 'rgba(0,0,0,0.05)' } },
                                y: { title: { display: true, text: 'Débit (m³/s)', font: { size: 13, weight: 'bold' } }, min: 0, grid: { color: 'rgba(0,0,0,0.05)' } }
                            }
                        }
                    });
                }
            }
        } catch (error) {
            statusOutput.textContent = `Erreur de chargement des graphiques: ${error.message}`;
        } finally {
            showGraphButton.disabled = false;
            showGraphButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" class="inline"><path fill-rule="evenodd" d="M0 0h1v15h15v1H0V0Zm14.817 3.113a.5.5 0 0 1 .07.704l-4.5 5.5a.5.5 0 0 1-.74.037L7.06 6.767l-3.656 5.027a.5.5 0 0 1-.808-.588l4-5.5a.5.5 0 0 1 .758-.06l2.609 2.61 4.15-5.073a.5.5 0 0 1 .704-.07Z"/></svg>
                            Actualiser les graphiques`;
        }
    });

    // Initialize display with a default message
    statusOutput.textContent = "Prêt. Paramétrez les contraintes puis lancez l'algorithme.";
</script>
"""

def render_page_html(template_name: str = "index.html") -> str:
    """Render the page HTML with the interaction script injected."""
    html = load_page_html(template_name)
    html = html.replace("{{ TURBINE_IMAGE_SRC }}", load_turbine_image_data_uri())
    return html.replace("<!-- WEB_APP_SCRIPT -->", build_interaction_script())
