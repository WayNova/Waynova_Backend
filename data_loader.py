import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import csv
import os
import torch
torch.set_num_threads(1) 


def load_buyer_profiles_csv(csv_path):
    indexer = BuyerIndexer()
    indexer.load_buyers(csv_path)
    return indexer.buyers

def normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    """Normalize embeddings so cosine similarity = inner product."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / np.maximum(norms, 1e-12)

class GrantIndexer:
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        self.index = None
        self.grants = []

    def load_grants(self, csv_path="data/Cal_Grants.csv"):
        df = pd.read_csv(csv_path, header=0).fillna("")
        self.grants = df.to_dict(orient="records")

        
        texts = [
            " ".join(str(g.get(col, "")) for col in df.columns)
            for g in self.grants
        ]

        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        embeddings = normalize_embeddings(embeddings)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings.astype("float32"))

    def search(self, query_text, top_k=5):
        query_vec = self.model.encode([query_text], convert_to_numpy=True)
        query_vec = normalize_embeddings(query_vec)

        scores, indices = self.index.search(query_vec.astype("float32"), top_k)
        results = []
        for j, i in enumerate(indices[0]):
            grant = self.grants[i]
            score = float(scores[0][j])  
            results.append((grant, round(score, 3)))
        return results


grant_indexer = GrantIndexer()


class BuyerIndexer:
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        self.index = None
        self.buyers = []

    def load_buyers(self, csv_path="data/buyer_profiles_real.csv"):

    
        with open(csv_path, "rb") as f:

            df = pd.read_csv(csv_path, header=0, encoding="utf-8-sig").fillna("")
            df.columns = df.columns.str.strip()
            # print("DEBUG CSV Columns:", df.columns.tolist())
            # print("DEBUG First Buyer Row:", df.iloc[0].to_dict())

            self.buyers = [
                {
                    "Agency Name": b.get("Agency Name", "Unknown Agency"),
                    "Point of Contact": b.get("Point of Contact", "Unknown Contact"),
                    "Email": b.get("Email ", "Unknown Email"),
                    "CAGE/DUNS Code": b.get("CAGE/DUNS Code", "Unknown Code"),
                    "Agency Type": b.get("Agency Type", "Unknown Type"),
                    "State": b.get("State", "Unknown State"),
                    "Zip Code": b.get("Zip Code", "Unknown Zip"),
                    "Population": b.get("Population", "Unknown Population"),
                    "Opportunity Zone": b.get("Opportunity Zone", "Unknown"),
                    "FEMA-declared disaster area": b.get("FEMA-declared disaster area", "Unknown"),
                    "Tribal land": b.get("Tribal land", "Unknown"),
                    "Department Size (FTE / volunteers)": b.get("Department Size (FTE / volunteers)", "Unknown"),
                    "Annual Budget Range": b.get("Annual Budget Range", "Unknown"),
                    "Call Volume": b.get("Call Volume", "Unknown"),
                    "Past Grant Use": b.get("Past Grant Use", "Unknown"),
                    "Procurement Status": b.get("Procurement Status", "Unknown"),
                    "Product Name": b.get("Product Name", "Unknown Product"),
                    "Use Case": b.get("Use Case", "Unknown Use Case"),
                    "Is the product capital equipment or recurring?": b.get("Is the product capital equipment or recurring?", "Unknown"),
                }
                for b in df.to_dict(orient="records")
            ]

            texts = [
                " ".join(str(b.get(col, "")) for col in df.columns)
                for b in self.buyers
            ]

        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        embeddings = normalize_embeddings(embeddings)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings.astype("float32"))

    def search(self, query_text, top_k=5):
        query_vec = self.model.encode([query_text], convert_to_numpy=True)
        query_vec = normalize_embeddings(query_vec)

        scores, indices = self.index.search(query_vec.astype("float32"), top_k)
        results = []
        for j, i in enumerate(indices[0]):
            buyer = self.buyers[i]
            score = float(scores[0][j])
            results.append((buyer, round(score, 3)))
        return results


buyer_indexer = BuyerIndexer()
