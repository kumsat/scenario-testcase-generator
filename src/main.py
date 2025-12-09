from typing import List

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from .models import (
    ScenarioRequest,
    ScenarioResponse,
    CombinationRequest,
    CombinationResponse,
)
from .generators.scenario_generator import generate_scenario_tests
from .generators.combinatorial_generator import (
    generate_combinations as generate_combinations_core,
)

app = FastAPI(
    title="Scenario-based & Combinational Test Case Generator",
    version="0.3.0",
)


@app.get("/")
def health_check():
    return {"status": "ok"}


# ---------- SIMPLE SCENARIO-BASED GENERATOR ----------


@app.post("/generate-by-scenario", response_model=ScenarioResponse)
def generate_by_scenario(request: ScenarioRequest):
    """
    Simple generator: given a high-level scenario (e.g. 'login', 'bluetooth pairing'),
    returns a small, readable set of test cases:
      - happy path
      - missing required data
      - invalid data
      - boundary / edge cases
    """
    cases = generate_scenario_tests(request)
    return ScenarioResponse(
        scenario=request.scenario,
        platform=request.platform,
        test_cases=cases,
    )


# ---------- COMBINATIONAL GENERATOR ----------


@app.post("/generate-combinations", response_model=CombinationResponse)
def generate_combinations_endpoint(request: CombinationRequest):
    """
    Generate combinational test cases using 3-state text fields (Valid, Invalid, Empty)
    and 2-state binary fields (Checked, Unchecked).

    Behaviour:
    - If text_fields/binary_fields are provided in the request, they are used directly.
    - Otherwise, the system auto-detects sensible fields based on the scenario name
      (login, logout, bluetooth, audio routing, navigation, OTA, etc.).

    The response returns:
    - total_combinations (theoretical maximum)
    - all generated cases up to max_cases
    - each case in JSON + Markdown form
    - combined_markdown containing all cases in one document
    """
    return generate_combinations_core(request)


# ---------- MARKDOWN DOWNLOAD FOR COMBINATIONS ----------


@app.get("/download-markdown", response_class=PlainTextResponse)
def download_markdown(
    scenario: str,
    platform: str = "web",
    max_cases: int = 200,
):
    """
    Download all generated combinational test cases as a single Markdown document (.md file).
    Example:
      /download-markdown?scenario=bluetooth pairing and reconnection&platform=automotive&max_cases=20
    """
    req = CombinationRequest(
        scenario=scenario,
        platform=platform,
        text_fields=None,
        binary_fields=None,
        max_cases=max_cases,
    )

    result = generate_combinations_core(req)

    filename = scenario.strip().lower().replace(" ", "_") or "test_cases"
    filename = f"{filename}_test_cases.md"

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return PlainTextResponse(content=result.combined_markdown, headers=headers)

