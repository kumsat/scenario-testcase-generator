from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Optional


# ------------ Existing scenario-based models ------------


class ScenarioRequest(BaseModel):
    """
    Input model for scenario-based test case generation.

    Example:
    {
      "scenario": "login",
      "platform": "web",
      "num_cases": 4
    }
    """
    scenario: str = Field(..., min_length=3, description="Business scenario, e.g. 'login', 'logout', 'add_to_cart'")
    platform: Literal["web", "mobile", "api", "desktop", "automotive", "generic"] = "web"
    num_cases: int = Field(5, ge=1, le=20)


class TestCase(BaseModel):
    """
    One generated test case.
    """
    id: str
    title: str
    preconditions: List[str]
    steps: List[str]
    expected_result: str
    priority: Literal["Low", "Medium", "High", "Critical"] = "Medium"
    tags: List[str] = []


class ScenarioResponse(BaseModel):
    """
    Response model for scenario-based generation.
    """
    scenario: str
    platform: str
    test_cases: List[TestCase]


# ------------ NEW: Combinational generation models ------------


class CombinationRequest(BaseModel):
    """
    Request model for combinational test case generation.

    If text_fields / binary_fields are omitted or empty, the system will
    try to auto-detect reasonable defaults based on the scenario name.
    """
    scenario: str = Field(..., min_length=3, description="Scenario name, e.g. 'login', 'logout', 'checkout'")
    platform: Literal["web", "mobile", "api", "desktop", "automotive", "generic"] = "web"

    # Optional explicit lists; if None or empty, auto-detection is used.
    text_fields: Optional[List[str]] = None
    binary_fields: Optional[List[str]] = None

    # To keep responses manageable if the number explodes.
    max_cases: int = Field(
        200,
        ge=1,
        le=1000,
        description="Maximum number of combinations to materialize in the response."
    )


class CombinationCase(BaseModel):
    """
    One combinational test case, including both structured data and a
    human-readable Markdown block.
    """
    id: str
    category: List[str]
    combination: Dict[str, str]  # field_name -> state string (e.g. 'Valid', 'Invalid', 'Empty', 'Checked')
    steps: List[str]
    expected_result: str
    markdown: str


class CombinationResponse(BaseModel):
    """
    Response model for combinational generation. Returns all cases (up to max_cases)
    together with metadata and a combined Markdown document.
    """
    scenario: str
    platform: str
    text_fields: List[str]
    binary_fields: List[str]
    total_combinations: int      # theoretical total combinations
    returned_count: int          # how many cases included in 'cases'
    page: int                    # for now always 1, but ready for future paging
    page_size: int               # equals returned_count
    pages_total: int             # for now always 1, but keeps API future-proof
    cases: List[CombinationCase]
    combined_markdown: str       # single markdown document with all test cases

