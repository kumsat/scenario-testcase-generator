# 🚀 Scenario-based & Combinational Test Case Generator  
### FastAPI • Automotive QA • AI-Assisted Test Design • Combinatorial Testing Engine

This project generates **structured QA test cases** from high-level scenarios (e.g., login, logout, Bluetooth pairing, audio routing, navigation, OTA, CAN/LIN, etc.).  
It also produces **combinational test suites** using all possible input state permutations to achieve **maximum test coverage**.

---

## ⭐ Key Features

### ✔ Scenario-Based Test Case Generation  

Given a scenario like:

> "bluetooth pairing and reconnection"

the API returns a structured test suite containing:

- Scenario-based test cases (happy path, missing data, invalid data, boundary)
- Preconditions
- Step-by-step actions
- Expected results
- Priority & tags
- Unique IDs (`BLUETOOTH-001`, etc.)
- Markdown-friendly content

---

### ✔ Combinational Test Generation (3-state + 2-state model)

The system uses:

- **3-state text fields** → `Valid`, `Invalid`, `Empty`  
- **2-state binary fields** → `Checked`, `Unchecked`  

and computes:

```text
Total combinations = 3^(number of text fields) × 2^(number of binary fields)


Example (Bluetooth pairing & reconnection):

| Field Type    | Count | States per field | Contribution |
| ------------- | ----- | ---------------- | ------------ |
| Text fields   | 5     | 3                | 3⁵ = 243     |
| Binary fields | 2     | 2                | 2² = 4       |


Total combinations:

Total = 243 × 4 = 972 possible test input combinations

The API can output all combinations or a limited subset via max_cases.


📦 Automotive Scenario Library (Domain Intelligence)

The generator automatically detects the domain based on scenario keywords.

Included automotive domains


| Domain              | Example keywords                          |
| ------------------- | ----------------------------------------- |
| Bluetooth           | bluetooth, pair, reconnect, bt, handsfree |
| Wi-Fi               | wifi, hotspot, wireless                   |
| Audio routing       | audio, routing, volume, media             |
| Navigation          | navigation, gps, route, reroute           |
| HMI / UI            | hmi, ui, screen, menu, touch              |
| Vehicle integration | can, lin, vehicle, signal                 |
| OTA updates         | ota, update, firmware                     |
| Performance         | performance, boot, latency, loadtime      |
| Security            | security, auth, permissions               |
| Robustness          | robust, stress, fault, recovery           |

Each domain has predefined:

-text_fields (3-state)

-binary_fields (2-state)

-Optionally domain_specific info (e.g. phone types, profiles, triggers, power states).

🧪 API Endpoints

1️⃣ Health Check

GET /

Simple status response:

{ "status": "ok" }

2️⃣ Scenario-Based Generator

POST /generate-by-scenario

Purpose: Generate 4 high-level test cases for a given scenario:

-Happy path

-Missing required data

-Invalid data values

-Boundary & edge conditions

Request body example:

{
  "scenario": "bluetooth pairing and reconnection",
  "platform": "automotive",
  "max_cases": 5
}


Response (shortened):

{
  "scenario": "bluetooth pairing and reconnection",
  "platform": "automotive",
  "test_cases": [
    {
      "id": "BLUETOOTH-001",
      "title": "bluetooth pairing and reconnection - happy path",
      "preconditions": [...],
      "steps": [...],
      "expected_result": "...",
      "priority": "High",
      "tags": ["happy_path", "automotive"]
    },
    {
      "id": "BLUETOOTH-002",
      "title": "bluetooth pairing and reconnection - missing required data",
      ...
    },
    {
      "id": "BLUETOOTH-003",
      "title": "bluetooth pairing and reconnection - invalid data values",
      ...
    },
    {
      "id": "BLUETOOTH-004",
      "title": "bluetooth pairing and reconnection - boundary and edge conditions",
      ...
    }
  ]
}

3️⃣ Combinational Test Generator

POST /generate-combinations

Purpose: Generate combinational test cases using all possible input states for a scenario.

If you only pass scenario + platform, the system will:

1. Look up the scenario in the Automotive Scenario Library

2. Auto-detect relevant text_fields and binary_fields

3. Calculate total_combinations using 3-state & 2-state rules

4. Generate up to max_cases detailed combinations

Request example:

{
  "scenario": "bluetooth pairing and reconnection",
  "platform": "automotive",
  "max_cases": 5
}


Response example (shortened):

{
  "scenario": "bluetooth pairing and reconnection",
  "platform": "automotive",
  "text_fields": [
    "phone_bucket",
    "bt_profile",
    "reconnect_trigger",
    "power_state",
    "hu_state"
  ],
  "binary_fields": [
    "is_device_paired_before",
    "is_auto_reconnect_enabled"
  ],
  "total_combinations": 972,
  "returned_count": 5,
  "page": 1,
  "page_size": 5,
  "pages_total": 1,
  "cases": [
    {
      "id": "BLUETOOTH-0001",
      "inputs": {
        "phone_bucket": "Valid",
        "bt_profile": "Valid",
        "reconnect_trigger": "Valid",
        "power_state": "Valid",
        "hu_state": "Valid",
        "is_device_paired_before": "Checked",
        "is_auto_reconnect_enabled": "Checked"
      },
      "steps": [
        "... generated QA steps based on this combination ..."
      ],
      "expected_result": "System behaves correctly for the selected input combination with no crashes or unstable behavior.",
      "markdown": "### BLUETOOTH-0001 — Bluetooth pairing and reconnection combination test\n..."
    }
  ]
}


4️⃣ Download All Test Cases as Markdown

GET /download-markdown

http://127.0.0.1:8000/download-markdown?scenario=bluetooth pairing and reconnection&platform=automotive&max_cases=50

This returns a .md file:

1. One Markdown section per generated test case

2. Ready to use in:

   - GitHub documentation

   - Jira/Xray

   - Confluence

   - OEM test packs


🛠 How to Run Locally

1️⃣ Install dependencies

pip install -r requirements.txt

(If needed, create & activate a venv first.)

2️⃣ Start the FastAPI server

uvicorn src.main:app --reload

3️⃣ Open Swagger UI

Go to:

http://127.0.0.1:8000/docs

You can now:

1.Call /generate-by-scenario for classic tests

2.Call /generate-combinations for full coverage combinations

3.Call /download-markdown to get a .md file with test cases


📂 Project Structure


```text

src/
 ├── main.py                          # FastAPI entry point (endpoints)
 ├── models.py                        # Pydantic request/response models
 ├── generators/
 │     ├── scenario_generator.py      # Scenario-based test case generator
 │     ├── combinational_generator.py # 3-state × 2-state combination engine
 │     ├── scenario_library.py        # Automotive domain, fields & keywords
 │     └── __init__.py
 └── __init__.py

tests/
 ├── test_scenarios.py                # Unit tests for scenario generator
 ├── test_api.py                      # API tests via TestClient

.github/workflows/
 └── ci.yml                           # CI pipeline (pytest on push)

```


🧩 Architecture Overview (Mermaid Diagram)

```mermaild

flowchart LR
    %% Client side
    U[QA Engineer / User\n(Postman, Browser, CI)] -->

    %% API layer
    A[FastAPI App\nsrc/main.py]

    subgraph API_Layer[API Layer]
        A --> |/generate-by-scenario\n(ScenarioRequest)| B[Scenario Generator\nsrc/generators/scenario_generator.py]
        A --> |/generate-combinations\n(CombinationRequest)| C[Combinational Generator\nsrc/generators/combinational_generator.py]
        A --> |/download-markdown\n(query params)| D[Markdown Export\n(PlainTextResponse)]
    end

    %% Scenario generator path
    subgraph Scenario_Engine[Scenario-based Engine]
        B --> M1[Scenario Models\nScenarioRequest,\nScenarioResponse,\nTestCase]
        B --> O1[(Scenario-based\nTest Cases\n(happy, negative,\nboundary, etc.))]
    end

    %% Combinational generator path
    subgraph Combination_Engine[Combinational Engine]
        C --> L[Automotive Scenario Library\nsrc/generators/scenario_library.py]
        L --> |auto-detect fields\n(HMI, BT, Audio,\nNavigation, CAN, OTA)| C
        C --> M2[Combination Models\nCombinationRequest,\nCombinationResponse]
        C --> O2[(Combinational\nTest Cases\n+ total_combinations)]
    end

    %% Outputs
    O1 --> A
    O2 --> A
    A --> |JSON response\n(test cases + steps + expected)| U
    D --> |Markdown (.md) file\ndownload| U

    %% Tests & CI
    subgraph Quality[Tests & CI Pipeline]
        T[pytest tests\n/tests] --> A
        CI[GitHub Actions\nCI workflow] --> T
    end

    U -. triggers tests .-> CI

```

🎯 Why This Project Is Useful

1. Automates test design for complex systems (web + automotive)

2. Provides theoretical max coverage via combinational testing

3. Encodes automotive domain knowledge (Bluetooth, Navigation, CAN, OTA, etc.)

4. Produces ready-to-use test documentation (Markdown)

5. Is designed to be integrated into CI/CD pipelines and other tools


👤 Author

Satendra Kumar
Automotive QA & Test Automation Engineer — Germany



