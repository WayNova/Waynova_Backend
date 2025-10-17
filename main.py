from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import SalesRepDropdownInput, GrantMatch
from data_loader import buyer_indexer, grant_indexer
from match_engine import get_ranked_matches_cosine
from auth.routes import router as auth_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.on_event("startup")
async def load_data():
    buyer_indexer.load_buyers("/Users/sanyamjain/Desktop/waynova/data/buyer_profiles_real.csv")
    grant_indexer.load_grants("/Users/sanyamjain/Desktop/waynova/data/Cal_Grants.csv")

@app.post("/match", response_model=List[GrantMatch])
def match_grants(rep_input: SalesRepDropdownInput):
    if not rep_input:
        raise HTTPException(status_code=400, detail="Request body is missing or invalid.")
    return get_ranked_matches_cosine(rep_input)
