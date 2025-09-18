"""Lightweight heuristic sentiment model used for local analysis."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

POSITIVE_WORDS: set[str] = {
    "good",
    "great",
    "excellent",
    "amazing",
    "awesome",
    "love",
    "like",
    "happy",
}

NEGATIVE_WORDS: set[str] = {
    "bad",
    "terrible",
    "awful",
    "hate",
    "dislike",
    "sad",
    "angry",
    "upset",
}


@dataclass
class SentimentResult:
    label: str
    score: float
    positive_matches: int
    negative_matches: int


class HeuristicSentimentModel:
    """Simple rule-based sentiment classifier for local/offline analysis."""

    def __init__(
        self,
        positive: Iterable[str] | None = None,
        negative: Iterable[str] | None = None,
    ) -> None:
        self.positive = {word.lower() for word in (positive or POSITIVE_WORDS)}
        self.negative = {word.lower() for word in (negative or NEGATIVE_WORDS)}

    WORD_PATTERN = re.compile(r"[\w']+")

    def predict(self, text: str) -> SentimentResult:
        tokens = [token.lower() for token in self.WORD_PATTERN.findall(text)]
        pos_matches = sum(1 for token in tokens if token in self.positive)
        neg_matches = sum(1 for token in tokens if token in self.negative)

        if pos_matches == neg_matches:
            label = "NEUTRAL"
        elif pos_matches > neg_matches:
            label = "POSITIVE"
        else:
            label = "NEGATIVE"

        total = max(len(tokens), 1)
        score = (pos_matches - neg_matches) / total
        return SentimentResult(
            label=label,
            score=score,
            positive_matches=pos_matches,
            negative_matches=neg_matches,
        )
