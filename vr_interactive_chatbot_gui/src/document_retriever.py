import os
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class VastDataRetriever:
    def __init__(self, docs_dir: str = "data/knowledge_docs", logger=None):
        self.docs_dir = docs_dir
        self.logger = logger
        self.chunks = []
        self.sources = []
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = None
        self.reload_documents()

    def _chunk_text(self, text: str, source_name: str, chunk_size: int = 600, overlap: int = 100):
        clean_text = " ".join(text.split())
        for i in range(0, len(clean_text), chunk_size - overlap):
            piece = clean_text[i:i + chunk_size].strip()
            if len(piece) > 50:
                self.chunks.append(piece)
                self.sources.append(source_name)

    def add_document_from_bytes(self, file_bytes, filename: str):
        """Supports live file uploads from Streamlit web UI."""
        try:
            text = ""
            if filename.lower().endswith(".pdf"):
                reader = PdfReader(file_bytes)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            else:
                text = file_bytes.read().decode("utf-8", errors="ignore")

            if text.strip():
                self._chunk_text(text, filename)
                self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)
                if self.logger:
                    self.logger.info(f"Indexed uploaded file '{filename}' ({len(self.chunks)} total chunks).")
                return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed indexing uploaded file {filename}: {e}")
        return False

    def reload_documents(self):
        self.chunks = []
        self.sources = []
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir, exist_ok=True)
            return

        for fname in os.listdir(self.docs_dir):
            fpath = os.path.join(self.docs_dir, fname)
            try:
                if fname.lower().endswith((".txt", ".md")):
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        self._chunk_text(f.read(), fname)
                elif fname.lower().endswith(".pdf"):
                    reader = PdfReader(fpath)
                    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                    self._chunk_text(full_text, fname)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error reading {fname}: {e}")

        if self.chunks:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)
            if self.logger:
                self.logger.info(f"Loaded {len(self.chunks)} knowledge chunks from {self.docs_dir}.")

    def retrieve_context(self, query: str, top_k: int = 3) -> tuple[str, list[str]]:
        if not self.chunks or self.tfidf_matrix is None:
            return "", []

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = scores.argsort()[-top_k:][::-1]

        matched_chunks = []
        matched_sources = []
        for idx in top_indices:
            if scores[idx] > 0.12:
                matched_chunks.append(f"[{self.sources[idx]}]: {self.chunks[idx]}")
                if self.sources[idx] not in matched_sources:
                    matched_sources.append(self.sources[idx])

        return "\n\n".join(matched_chunks), matched_sources