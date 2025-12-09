from typing import List

from ..models import ScenarioRequest, TestCase


def _make_id_prefix(scenario: str) -> str:
    """
    Build a short, uppercase ID prefix from the scenario name.
    Example: "bluetooth pairing and reconnection" -> "BLUETOOTH"
    """
    cleaned = "".join(ch for ch in scenario.upper() if ch.isalnum())
    if not cleaned:
        cleaned = "SCENARIO"
    # keep it reasonably short
    return cleaned[:10]


def generate_scenario_tests(request: ScenarioRequest) -> List[TestCase]:
    """
    Simple, generic scenario-based test generator.

    It creates 4 high-level test cases:
    - happy path
    - missing required data
    - invalid data values
    - boundary and edge conditions

    This is the SIMPLE layer.
    The COMBINATIONAL engine is handled separately via /generate-combinations.
    """
    scenario = request.scenario.strip()
    platform = (request.platform or "generic").strip().lower()

    prefix = _make_id_prefix(scenario)
    tag_base = [platform]

    tc1 = TestCase(
        id=f"{prefix}-001",
        title=f"{scenario} - happy path",
        preconditions=[
            "System is available and responsive.",
            "All required preconditions for the scenario are fulfilled (data, configuration, permissions).",
        ],
        steps=[
            f"Open the application or module where '{scenario}' is performed.",
            f"Navigate to the screen or API endpoint responsible for '{scenario}'.",
            "Provide all required inputs with valid and typical data values.",
            f"Trigger the main action to execute '{scenario}' (e.g. click button, call API).",
            "Wait for the system to process the request.",
            "Observe the UI, logs, or API response returned by the system.",
        ],
        expected_result=(
            f"The system successfully completes '{scenario}' without errors. "
            "The expected UI changes, data updates, or API responses are visible, "
            "and logs show no critical errors."
        ),
        priority="High",
        tags=["happy_path"] + tag_base,
    )

    tc2 = TestCase(
        id=f"{prefix}-002",
        title=f"{scenario} - missing required data",
        preconditions=[
            "System is available.",
        ],
        steps=[
            f"Open the part of the application where '{scenario}' would normally be executed.",
            "Identify fields or parameters that are mandatory according to the specification.",
            "Leave one or more mandatory fields empty or unset.",
            f"Attempt to execute '{scenario}' (e.g. click save/submit or call API).",
            "Observe any validation messages or error indicators.",
        ],
        expected_result=(
            "The system does not proceed with the operation. "
            "Clear validation messages are displayed for all missing required fields, "
            "indicating what needs to be provided. No data is saved and no partial "
            "or corrupted state is created."
        ),
        priority="Medium",
        tags=["validation", "negative"] + tag_base,
    )

    tc3 = TestCase(
        id=f"{prefix}-003",
        title=f"{scenario} - invalid data values",
        preconditions=[
            "System is available.",
        ],
        steps=[
            f"Open the screen or endpoint where '{scenario}' is performed.",
            "Identify input fields or parameters that have format or range constraints.",
            "Enter invalid, out-of-range, or syntactically incorrect values "
            "(e.g. wrong format, too long, negative where not allowed).",
            f"Attempt to execute '{scenario}' with these invalid values.",
            "Observe the system response and any messages shown to the user or API client.",
        ],
        expected_result=(
            "The system rejects invalid data inputs. User-friendly error or validation "
            "messages are displayed, no data corruption occurs, and the system remains "
            "stable without crashes or unhandled exceptions."
        ),
        priority="High",
        tags=["negative", "data_validation"] + tag_base,
    )

    tc4 = TestCase(
        id=f"{prefix}-004",
        title=f"{scenario} - boundary and edge conditions",
        preconditions=[
            "System is available.",
            "Boundary values and limits for inputs are known "
            "(e.g. min/max length, numeric ranges).",
        ],
        steps=[
            f"Open the relevant part of the application for '{scenario}'.",
            "Identify fields or parameters with defined limits (length, range, list size, etc.).",
            "Test with minimum allowed values.",
            "Test with maximum allowed values.",
            "If applicable, test just-below-minimum and just-above-maximum values.",
            f"Attempt to perform '{scenario}' with each of these values.",
        ],
        expected_result=(
            "The system correctly enforces boundary conditions. "
            "Values within the allowed range are accepted and processed correctly, "
            "while values outside the allowed range are rejected with appropriate messages. "
            "System stability is maintained throughout testing."
        ),
        priority="Medium",
        tags=["boundary", "edge_case"] + tag_base,
    )

    return [tc1, tc2, tc3, tc4]

