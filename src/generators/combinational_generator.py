import itertools
from .scenario_library import detect_scenario_fields


def generate_combinations(scenario: str, max_cases: int = 20):
    config = detect_scenario_fields(scenario)

    text_fields = config.get("text_fields", [])
    binary_fields = config.get("binary_fields", [])

    # 3 states for text fields
    text_states = ["Valid", "Invalid", "Empty"]

    # 2 states for binary fields
    binary_states = ["Checked", "Unchecked"]

    # Build Cartesian product
    text_combos = list(itertools.product(text_states, repeat=len(text_fields)))
    binary_combos = list(itertools.product(binary_states, repeat=len(binary_fields)))

    total_combinations = len(text_combos) * len(binary_combos)

    final_cases = []
    count = 0

    for t in text_combos:
        for b in binary_combos:
            if count >= max_cases:
                break

            case = {
                "inputs": {
                    text_fields[i]: t[i] for i in range(len(text_fields))
                } | {
                    binary_fields[i]: b[i] for i in range(len(binary_fields))
                }
            }

            final_cases.append(case)
            count += 1

    return total_combinations, final_cases

