import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
torch.set_num_threads(1)


def normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    """Normalize embeddings so cosine similarity = inner product."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / np.maximum(norms, 1e-12)


# ----------------- Grant Indexer -----------------
class GrantIndexer:
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        self.index = None
        self.grants = []

    def load_grants(self, csv_path):
        df = pd.read_csv(csv_path, encoding="utf-8-sig").fillna("")
        df.columns = df.columns.str.strip()
        self.grants = df.to_dict(orient="records")

        # ✅ Use actual cell values (not column names)
        texts = [
            " ".join(str(value) for value in row.values()) for row in self.grants
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


# ----------------- Buyer Indexer -----------------
class BuyerIndexer:
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        self.index = None
        self.buyers = []

    def load_buyers(self, csv_path):
        df = pd.read_csv(csv_path, encoding="utf-8-sig").fillna("")
        df.columns = df.columns.str.strip()
        self.buyers = df.to_dict(orient="records")

        texts = [
            " ".join(str(value) for value in row.values()) for row in self.buyers
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


# Instantiate globally
buyer_indexer = BuyerIndexer()
grant_indexer = GrantIndexer()
