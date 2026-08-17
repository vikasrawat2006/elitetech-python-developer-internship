import re
import logging
import nltk
from typing import Dict, Any, Optional

class NLPPreprocessor:
    """Enterprise-grade NLP preprocessing pipeline with robust offline fallbacks."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("VREnterpriseLogger")
        self.nltk_available = self._verify_and_download_corpora()
        
        if self.nltk_available:
            from nltk.stem import WordNetLemmatizer
            from nltk.corpus import stopwords
            self.lemmatizer = WordNetLemmatizer()
            try:
                self.stop_words = set(stopwords.words('english'))
            except LookupError:
                self.stop_words = set()
        else:
            self.stop_words = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"}

    def _verify_and_download_corpora(self) -> bool:
        """Attempts to verify/download NLTK resources with a graceful offline fallback."""
        required_resources = [
            ('tokenizers/punkt', 'punkt'),
            ('tokenizers/punkt_tab', 'punkt_tab'),
            ('corpora/wordnet', 'wordnet'),
            ('corpora/stopwords', 'stopwords'),
            ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
            ('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng')
        ]
        
        for path, name in required_resources:
            try:
                nltk.data.find(path)
            except LookupError:
                try:
                    self.logger.info(f"Attempting to download NLTK corpus: {name}")
                    nltk.download(name, quiet=True)
                except Exception as e:
                    self.logger.warning(f"Could not download NLTK corpus '{name}' due to network restriction: {e}. Switching to regex fallback mode.")
                    return False
        return True

    def transform(self, raw_text: str) -> Dict[str, Any]:
        """
        Executes text processing using NLTK if available, 
        otherwise seamlessly falls back to regex tokenization.
        """
        if not raw_text or not isinstance(raw_text, str):
            return {"cleaned_text": "", "tokens": [], "lemmas": [], "pos_tags": []}

        normalized = raw_text.lower()
        normalized = re.sub(r'[^a-z0-9\s\?]', '', normalized)

        if self.nltk_available:
            try:
                from nltk.tokenize import word_tokenize
                from nltk.tag import pos_tag
                tokens = word_tokenize(normalized)
                filtered_tokens = [t for t in tokens if t not in self.stop_words]
                pos_tagged = pos_tag(filtered_tokens)
                lemmas = [
                    self.lemmatizer.lemmatize(word)
                    for word, tag in pos_tagged
                ]
                return {
                    "cleaned_text": " ".join(filtered_tokens),
                    "tokens": filtered_tokens,
                    "lemmas": lemmas,
                    "pos_tags": pos_tagged
                }
            except Exception:
                pass  # Fall through to regex tokenizer if any runtime NLTK error occurs

        # --- Regex Fallback Parser (Offline Safe) ---
        tokens = re.findall(r'\b[a-z0-9]+\b', normalized)
        filtered_tokens = [t for t in tokens if t not in self.stop_words]
        return {
            "cleaned_text": " ".join(filtered_tokens),
            "tokens": filtered_tokens,
            "lemmas": filtered_tokens,  # Fallback lemma representation
            "pos_tags": [(t, 'NOUN') for t in filtered_tokens]
        }