from pydantic import BaseModel
from typing import List

# Input from Sales Rep dropdowns
class SalesRepDropdownInput(BaseModel):
    agency_type: str
    product_type: str
    state: str

# Output grant match
class GrantMatch(BaseModel):
    grant_title: str
    description: str
    agency: str
    amount: str
    deadline: str
    confidence_score: float
    buyer_agency: str
    buyer_score: float
    grant_score: float
    explanation: str