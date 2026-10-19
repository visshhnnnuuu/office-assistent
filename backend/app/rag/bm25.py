import math
import re
from typing import List, Dict, Any, Tuple

class BM25Okapi:
    """
    BM25 implementation for lexical keyword search over documents/chunks.
    Supports exact token matching, acronym matching, and error code lookups.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len: List[int] = []
        self.avg_doc_len: float = 0.0
        self.corpus_size: int = 0
        self.idf: Dict[str, float] = {}
        self.doc_freqs: List[Dict[str, int]] = []
        self.chunk_ids: List[str] = []

    def _tokenize(self, text: str) -> List[str]:
        # Keeps alphanumeric tokens, hyphens, and underscores for policy codes (e.g. "HR-POL-02")
        tokens = re.findall(r'[a-zA-Z0-9_\-]+', text.lower())
        return tokens

    def fit(self, chunks: List[Dict[str, Any]]) -> None:
        self.corpus_size = len(chunks)
        self.doc_len = []
        self.doc_freqs = []
        self.chunk_ids = []
        df: Dict[str, int] = {}

        for chunk in chunks:
            self.chunk_ids.append(chunk["chunk_id"])
            text = f"{chunk.get('section_title', '')} {chunk.get('content', '')}"
            tokens = self._tokenize(text)
            self.doc_len.append(len(tokens))

            frequencies: Dict[str, int] = {}
            for t in tokens:
                frequencies[t] = frequencies.get(t, 0) + 1
            self.doc_freqs.append(frequencies)

            for token in frequencies.keys():
                df[token] = df.get(token, 0) + 1

        self.avg_doc_len = sum(self.doc_len) / self.corpus_size if self.corpus_size > 0 else 0.0

        self.idf = {}
        for token, freq in df.items():
            # BM25 standard smoothed idf
            self.idf[token] = math.log(1 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        if self.corpus_size == 0:
            return []

        tokens = self._tokenize(query)
        scores = [0.0] * self.corpus_size

        for token in tokens:
            if token not in self.idf:
                continue
            idf_val = self.idf[token]
            for i, freqs in enumerate(self.doc_freqs):
                tf = freqs.get(token, 0)
                if tf == 0:
                    continue
                num = tf * (self.k1 + 1)
                denom = tf + self.k1 * (1 - self.b + self.b * (self.doc_len[i] / self.avg_doc_len))
                scores[i] += idf_val * (num / denom)

        results = [(self.chunk_ids[i], scores[i]) for i in range(self.corpus_size) if scores[i] > 0]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
