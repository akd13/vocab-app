"""Word meaning and synonym utilities."""

from __future__ import annotations

from typing import Any

from nltk.corpus import wordnet


class WordDetailsService:
    """Retrieve definitions and synonyms using NLTK's WordNet."""

    def get_details(self, word: str) -> tuple[str, list[str]]:
        try:
            synsets: list[Any] = wordnet.synsets(word)
            if synsets:
                first_synset = synsets[0]
                definition = first_synset.definition()
                # Get all lemmas and filter out the original word
                all_synonyms = [lemma.name() for synset in synsets for lemma in synset.lemmas()]
                # Remove the original word (case-insensitive) and duplicates
                filtered_synonyms = list(set([
                    synonym for synonym in all_synonyms 
                    if synonym.lower() != word.lower()
                ]))
                return definition, filtered_synonyms[:5]
            return "No definitions found", []
        except Exception as exc:  # pragma: no cover - defensive
            print("Exception is", exc)
            return "An error occurred", []


# Backwards compatible helper

def get_definition_synonyms(word: str) -> tuple[str, list[str]]:
    return WordDetailsService().get_details(word)
