"""Utility helpers for working with the application's word list."""

from __future__ import annotations

import random
from pathlib import Path
from typing import List


class WordPicker:
    """Load and pick words from ``wordlist.txt``."""

    def __init__(self, word_file: str = "wordlist.txt") -> None:
        self.word_file = Path(word_file)
        self._words: List[str] = self._load_words()

    def _load_words(self) -> List[str]:
        if not self.word_file.exists():
            return []
        with self.word_file.open("r", encoding="utf-8") as f:
            return [w.strip() for w in f.readlines() if w.strip()]

    def pick(self) -> str:
        """Return a random word from the list."""
        if not self._words:
            raise ValueError("word list is empty")
        return random.choice(self._words)


# Maintain backwards compatibility for older imports
def pick_random_word() -> str:
    return WordPicker().pick()

