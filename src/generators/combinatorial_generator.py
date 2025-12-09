from typing import List, Dict, Tuple
from itertools import product

from ..models import CombinationRequest, CombinationResponse, CombinationCase
from .field_detector import detect_fields_for_scenario


TEXT_STATES = ["Valid", "Invalid", "Empty"]
BINARY_STATES = ["Checked", "Unchecked"]


def _compute_total_combinations(num_text_fields: int, num_binary_fields: int) -> int:
    return (3 ** num_text_fields) * (2 ** num_binary_fields)


def _categorize_combination(
    scenario: str,
    combination: Dict[str, str],
) -> List[str]:
    """
    Decide which logical categories apply based on the combination.
    Categories: Positive, Negative, Validation, Edge, Security.
    """
    cats: List[str] = []
    s = scenario.strip().lower()

    text_states = [state for field, state in combination.items() if state in TEXT_STATES]
    has_invalid = any(state == "Invalid" for state in text_states)
    has_empty = any(state == "Empty" for state in text_states)
    all_valid_text = text_states and all(state == "Valid" for state in text_states)

    # Positive when all text fields are valid
    if all_valid_text:
        cats.append("Positive")

    # Validation / Edge when there are empty fields
    if has_empty:
        cats.append("Negative")
        cats.append("Validation")
        cats.append("Edge")

    # Negative when invalid values appear
    if has_invalid:
        if "Negative" not in cats:
            cats.append("Negative")

    # Security rules:
    # - login/auth scenarios with invalid or empty sensitive fields
    # - otp/password/username suspicious patterns
    if "login" in s or "auth" in s or "sign in" in s.replace("-", " "):
        for field, state in combination.items():
            lf = field.lower()
            if lf in ["password", "otp", "token"] and state in ["Invalid", "Empty"]:
                if "Security" not in cats:
                    cats.append("Security")
        # Many invalid fields together is also a possible brute-force/security case
        if text_states.count("Invalid") >= 2 and "Security" not in cats:
            cats.append("Security")

    # If no category determined, default to Positive/Functional
    if not cats:
        cats.append("Positive")

    return cats


def _build_steps_for_combination(
    req: CombinationRequest,
    combination: Dict[str, str],
) -> List[str]:
    """
    Create detailed, JIRA-style steps for the given combination.
    """
    steps: List[str] = []

    scenario = req.scenario.strip()
    platform = req.platform

    # Platform-specific opening
    if platform == "web":
        steps.append("Launch a supported web browser (e.g. latest Chrome or Firefox).")
        steps.append("Navigate to the application's URL and ensure the page loads without errors.")
    elif platform == "mobile":
        steps.append("Launch the mobile application on a supported device/emulator.")
        steps.append("Ensure the app loads to the main screen without crashes.")
    elif platform == "api":
        steps.append("Prepare an API client (e.g. Postman, curl, or automated test).")
        steps.append("Ensure the target environment and endpoint are reachable.")
    elif platform == "desktop":
        steps.append("Launch the desktop application on a supported operating system.")
        steps.append("Ensure the application starts successfully without error dialogs.")
    elif platform == "automotive":
        steps.append("Ensure the test vehicle or HIL/SIL environment is powered on and in a safe state.")
        steps.append("Connect diagnostic/tools to the in-vehicle network or test bench as required.")
    else:
        steps.append("Open the system under test using the appropriate client or interface.")
        steps.append("Navigate to the relevant module for this scenario.")

    # Navigate to scenario area
    steps.append(f"Navigate to the part of the system where the '{scenario}' operation is performed (screen, API endpoint, or flow).")

    # Apply each field state
    for field, state in combination.items():
        lf = field.lower()
        if state == "Valid":
            steps.append(
                f"Enter a valid value into '{field}' (e.g. a correctly formatted and allowed {lf})."
            )
        elif state == "Invalid":
            steps.append(
                f"Enter an invalid or not allowed value into '{field}' "
                f"(e.g. wrong format, out-of-range value, or disallowed characters)."
            )
        elif state == "Empty":
            steps.append(
                f"Leave the '{field}' field empty or do not provide this parameter in the request."
            )
        elif state == "Checked":
            steps.append(
                f"Ensure the '{field}' option is enabled/checked before executing the '{scenario}' operation."
            )
        elif state == "Unchecked":
            steps.append(
                f"Ensure the '{field}' option is disabled/unchecked before executing the '{scenario}' operation."
            )

    # Trigger action
    steps.append(
        f"Trigger the '{scenario}' operation (e.g. click the corresponding button, submit the form, or send the API request)."
    )
    steps.append(
        "Observe the system behaviour in the UI, logs, and/or API response, including status codes and returned data."
    )

    return steps


def _build_expected_result(
    scenario: str,
    categories: List[str],
    combination: Dict[str, str],
) -> str:
    """
    Build a detailed expected result paragraph based on the categories.
    """
    s = scenario.strip()

    if "Positive" in categories and "Negative" not in categories and "Validation" not in categories:
        return (
            f"The system successfully completes the '{s}' operation. The expected UI changes, data updates, "
            "and/or API responses are produced without errors. No validation or error messages are displayed, "
            "and the system state is consistent and correct."
        )

    if "Validation" in categories or "Edge" in categories:
        return (
            "The system does not proceed with the main operation. Clear and descriptive validation messages are "
            "displayed or returned for all fields that are empty or invalid. No partial data is stored, no corrupted "
            "state is created, and any previously valid data remains unchanged."
        )

    if "Security" in categories:
        return (
            "The system protects against unauthorized or suspicious usage of the scenario. Login or privileged "
            "operations are rejected, error messages remain generic (no sensitive information leakage), and no "
            "user session or privileged access is granted. Any relevant security/audit logs are created as per policy."
        )

    # Generic negative case
    if "Negative" in categories:
        return (
            "The system rejects the operation for this combination of inputs. Appropriate error or validation messages "
            "are displayed or returned, and the system remains stable without crashes or unhandled exceptions."
        )

    # Fallback
    return (
        f"The system handles the '{s}' operation in accordance with the specification for this input combination, "
        "without compromising stability, data integrity, or security."
    )


def _build_markdown_for_case(
    case_id: str,
    scenario: str,
    categories: List[str],
    combination: Dict[str, str],
    steps: List[str],
    expected_result: str,
) -> str:
    """
    Create a Markdown block describing a single test case.
    """
    cat_str = ", ".join(categories) if categories else "Unclassified"

    lines: List[str] = []
    lines.append(f"### {case_id} — {scenario.capitalize()} Combination Test")
    lines.append(f"**Category:** {cat_str}")
    lines.append("**Combination:**")

    for field, state in combination.items():
        lines.append(f"- **{field}**: {state}")

    lines.append("")
    lines.append("**Steps:**")
    for idx, step in enumerate(steps, start=1):
        lines.append(f"{idx}. {step}")

    lines.append("")
    lines.append("**Expected Result:**")
    lines.append(f"- {expected_result}")
    lines.append("")

    return "\n".join(lines)


def generate_combinations(req: CombinationRequest) -> CombinationResponse:
    """
    Main entry point for combinational generation.
    - Uses explicit text_fields/binary_fields if provided.
    - Otherwise auto-detects based on scenario.
    - Generates all combinations up to max_cases.
    """
    # 1) Determine fields
    text_fields = list(req.text_fields) if req.text_fields else []
    binary_fields = list(req.binary_fields) if req.binary_fields else []

    if not text_fields and not binary_fields:
        auto_text, auto_binary = detect_fields_for_scenario(req.scenario)
        text_fields = auto_text
        binary_fields = auto_binary

    # If still empty, provide a very simple default
    if not text_fields and not binary_fields:
        text_fields = ["input"]
        binary_fields = []

    num_text = len(text_fields)
    num_binary = len(binary_fields)

    total_combinations = _compute_total_combinations(num_text, num_binary)

    # 2) Generate all raw combinations
    text_state_products = list(product(TEXT_STATES, repeat=num_text)) if num_text > 0 else [()]
    binary_state_products = list(product(BINARY_STATES, repeat=num_binary)) if num_binary > 0 else [()]

    cases: List[CombinationCase] = []
    scenario = req.scenario.strip()
    prefix = scenario.upper().replace(" ", "_")[:8] or "SCEN"

    counter = 0

    for text_states in text_state_products:
        for binary_states in binary_state_products:
            counter += 1
            if counter > req.max_cases:
                break

            combination: Dict[str, str] = {}

            for field_name, state in zip(text_fields, text_states):
                combination[field_name] = state
            for field_name, state in zip(binary_fields, binary_states):
                combination[field_name] = state

            categories = _categorize_combination(scenario, combination)
            steps = _build_steps_for_combination(req, combination)
            expected_result = _build_expected_result(scenario, categories, combination)
            case_id = f"{prefix}-{counter:04d}"
            markdown = _build_markdown_for_case(case_id, scenario, categories, combination, steps, expected_result)

            cases.append(
                CombinationCase(
                    id=case_id,
                    category=categories,
                    combination=combination,
                    steps=steps,
                    expected_result=expected_result,
                    markdown=markdown,
                )
            )

        if counter > req.max_cases:
            break

    # For now we return everything as a single "page"
    returned_count = len(cases)
    page = 1
    page_size = returned_count
    pages_total = 1

    # Combine markdown for all cases
    combined_md_lines: List[str] = []
    for case in cases:
        combined_md_lines.append(case.markdown)
    combined_markdown = "\n".join(combined_md_lines)

    return CombinationResponse(
        scenario=scenario,
        platform=req.platform,
        text_fields=text_fields,
        binary_fields=binary_fields,
        total_combinations=total_combinations,
        returned_count=returned_count,
        page=page,
        page_size=page_size,
        pages_total=pages_total,
        cases=cases,
        combined_markdown=combined_markdown,
    )

