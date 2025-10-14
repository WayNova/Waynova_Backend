# Waynova Backend Matching Engine

## Overview
This backend system is designed to match buyer profiles (such as fire departments, EMS agencies, etc.) with relevant grant opportunities using advanced semantic search and custom scoring logic. It leverages state-of-the-art NLP models, fast similarity search, and metadata-based boosting to provide ranked, explainable matches via a FastAPI interface.

## Key Features
- **Semantic Matching:** Uses SentenceTransformer (BAAI/bge-base-en-v1.5) to generate embeddings for buyers and grants, enabling context-aware matching beyond simple keyword search.
- **FAISS Indexing:** Employs FAISS for efficient similarity search on large sets of embeddings.
- **Custom Scoring:** Combines semantic similarity, lexical overlap, geo match, deadline urgency, and keyword boosting for confidence scoring.
- **Explainable Results:** Each match includes a detailed explanation of the score breakdown and keyword contributions.
- **API Access:** Exposes matching functionality via FastAPI endpoints for integration with frontend or other systems.

## Main Components
- `data_loader.py`: Loads buyer and grant profiles from CSV files, builds embedding indices, and provides search functionality.
- `match_engine.py`: Implements the matching logic, scoring, and explanation generation.
- `models.py`: Defines Pydantic models for API request/response validation.
- `requirements.txt`: Lists Python dependencies (pandas, faiss, numpy, sentence-transformers, torch, fastapi, etc.).

## How It Works
1. **Data Loading:**
   - Buyer and grant profiles are loaded from CSV files and converted into text for embedding.
   - Embeddings are generated using SentenceTransformer and indexed with FAISS.
2. **Matching:**
   - When a match request is received, the system constructs a query from the sales rep's input and searches for top buyers and grants.
   - For each buyer-grant pair, a confidence score is calculated using semantic similarity, keyword matches, and metadata.
   - Keyword boosting is applied if buyer product names or agency type match grant fields (Eligible Equipment/Expenses, Purpose, Focus Areas, Eligible Applicants).
   - Results are sorted by confidence score and returned with explanations.
3. **API:**
   - FastAPI serves endpoints for matching requests and returns structured, explainable results.

## Example Usage
- Send a POST request to the matching endpoint with sales rep input (agency_type, product_type, state).
- Receive a ranked list of grant matches, each with confidence score and explanation.

## Customization
- Adjust scoring weights and keyword boosting logic in `match_engine.py` to tune matching behavior.
- Add new buyer or grant profiles by updating the respective CSV files.

## Requirements
- Python 3.8+
- See `requirements.txt` for all dependencies.

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
3. Access the API documentation at `http://localhost:8000/docs`

## Contact
For questions or support, contact the development team.
