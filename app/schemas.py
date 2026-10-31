
from typing import Literal
from pydantic import BaseModel

# This class defines what every successful classification of a ticket must return.
class TriageResult(BaseModel):
    team: Literal[
        "billing",
        "technical_support",
        "account_access",
        "general_inquiry",
    ]

    priority: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ]

    reason: str
    suggested_reply: str