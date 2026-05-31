# core/advisor.py

import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_PATH = "data/index/gridiron.index"
DOCS_PATH = "data/index/gridiron_docs.json"
MODEL_NAME = "all-MiniLM-L6-v2"


class Advisor:
    def __init__(self, index_path=INDEX_PATH, docs_path=DOCS_PATH):
        self.index_path = index_path
        self.docs_path = docs_path
        self.model = SentenceTransformer(MODEL_NAME, local_files_only=True)
        self.documents = []
        self.index = None

    def _init_index(self, dim: int):
        # IndexFlatIP with normalized embeddings gives cosine similarity (higher = more similar)
        self.index = faiss.IndexFlatIP(dim)

    _POSITION_NAMES = {
        "QB": "quarterback", "RB": "running back", "WR": "wide receiver",
        "TE": "tight end", "K": "kicker", "DEF": "defense", "UNK": "player",
    }

    _TEAM_NAMES = {
        "ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens",
        "BUF": "Buffalo Bills", "CAR": "Carolina Panthers", "CHI": "Chicago Bears",
        "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns", "DAL": "Dallas Cowboys",
        "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers",
        "HOU": "Houston Texans", "IND": "Indianapolis Colts", "JAX": "Jacksonville Jaguars",
        "KC": "Kansas City Chiefs", "LAC": "Los Angeles Chargers", "LAR": "Los Angeles Rams",
        "LV": "Las Vegas Raiders", "MIA": "Miami Dolphins", "MIN": "Minnesota Vikings",
        "NE": "New England Patriots", "NO": "New Orleans Saints", "NYG": "New York Giants",
        "NYJ": "New York Jets", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers",
        "SEA": "Seattle Seahawks", "SF": "San Francisco 49ers", "TB": "Tampa Bay Buccaneers",
        "TEN": "Tennessee Titans", "WAS": "Washington Commanders",
    }

    def build_from_players(self, players: list):
        """Convert cleaned player dicts into natural-language snippets and index them."""
        texts = []
        for p in players:
            name = p.get("player_name") or p.get("profile_id", "Unknown")
            pos_code = p.get("position", "UNK").upper()
            pos = self._POSITION_NAMES.get(pos_code, pos_code)
            team = p.get("team", "UNK")
            week = p.get("week", "?")
            pts = float(p.get("fantasy_points", 0))
            team_name = self._TEAM_NAMES.get(team, team)
            surface = p.get("surface", "unknown surface")
            environment = p.get("environment", "outdoor")
            venue_desc = f"{environment} on {surface}"
            texts.append(
                f"{name} is a {pos} ({pos_code}) for the {team_name} ({team}), "
                f"scoring {pts:.1f} fantasy points in week {week}. "
                f"Game played {venue_desc}."
            )
        self.add_documents(texts)

    def add_documents(self, texts: list):
        if not texts:
            print("⚠️ No documents to add.")
            return
        print(f"📄 Embedding {len(texts)} documents...")
        embeddings = self.model.encode(texts, normalize_embeddings=True).astype("float32")
        if self.index is None:
            self._init_index(embeddings.shape[1])
        self.index.add(embeddings)
        self.documents.extend(texts)
        print(f"✅ {len(texts)} documents indexed.")

    def query(self, text: str, top_k: int = 5) -> list:
        if self.index is None or self.index.ntotal == 0:
            raise RuntimeError(
                "No index loaded. Run 'espn intake --week <N>' first to build the index."
            )
        embedding = self.model.encode([text], normalize_embeddings=True).astype("float32")
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(embedding, k)
        return [
            {"text": self.documents[i], "similarity": float(scores[0][rank])}
            for rank, i in enumerate(indices[0])
            if i < len(self.documents)
        ]

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.docs_path, "w") as f:
            json.dump(self.documents, f, indent=2)
        print(f"💾 Index saved ({self.index.ntotal} entries) → {self.index_path}")

    def load(self):
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(
                f"No index found at {self.index_path}. "
                "Run 'espn intake --week <N>' to build one."
            )
        self.index = faiss.read_index(self.index_path)
        with open(self.docs_path) as f:
            self.documents = json.load(f)
        print(f"📂 Index loaded — {self.index.ntotal} entries.")
