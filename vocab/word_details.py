"""Word meaning and synonym utilities."""

from __future__ import annotations

from nltk.corpus import wordnet


class WordDetailsService:
    """Retrieve definitions and synonyms using NLTK's WordNet."""

    def get_details(self, word: str) -> tuple[str, list[str]]:
        try:
            synsets = wordnet.synsets(word)
            if synsets:
                first_synset = synsets[0]
                definition = first_synset.definition()
                synonyms = [lemma.name() for synset in synsets for lemma in synset.lemmas()]
                return definition, synonyms[:5]
            return "No definitions found", []
        except Exception as exc:  # pragma: no cover - defensive
            print("Exception is", exc)
            return "An error occurred", []


# Backwards compatible helper

def get_definition_synonyms(word: str) -> tuple[str, list[str]]:
    return WordDetailsService().get_details(word)
