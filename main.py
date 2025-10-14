from fastapi import FastAPI, HTTPException
from typing import List
from models import SalesRepDropdownInput, GrantMatch
from data_loader import buyer_indexer, grant_indexer
from match_engine import get_ranked_matches_cosine

app = FastAPI()

@app.on_event("startup")
async def load_data():
    buyer_indexer.load_buyers("data/buyer_profiles_real.csv")
    grant_indexer.load_grants("data/Cal_Grants.csv")

@app.post("/match", response_model=List[GrantMatch])
def match_grants(rep_input: SalesRepDropdownInput):
    if not rep_input:
        raise HTTPException(status_code=400, detail="Request body is missing or invalid.")
    return get_ranked_matches_cosine(rep_input)
