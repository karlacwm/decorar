# Phase 3: The Exporter (Quizlet Formatter)
# Goal: Convert QuizDeck into Quizlet-ready text.
# Step 3.1: In exporter.py, format each card: {question}\t{answer}\n
# (Tabs are much safer than commas
# because Portuguese sentences frequently contain commas!)
# Step 3.2: Write output to data/output/quizlet.txt
# and copy to system clipboard using pyperclip.copy().

import contextlib
from abc import ABC, abstractmethod
from pathlib import Path

import pyperclip  # pyright: ignore

from decorar.models.card import QuizCard, QuizDeck


class BaseExporter(ABC):
    """Abstract interface defining the export contract."""

    @abstractmethod
    def export(
        self,
        deck: QuizDeck,
        output_path: Path | str | None = None,
        copy_to_clipboard: bool = True,
    ) -> str:
        """Export the quiz deck and return formatted text."""


class QuizletExporter(BaseExporter):
    """Formats MCQ cards for Quizlet and saves to file/clipboard."""

    def __init__(self, card_delimiter: str = "\n\n;\n\n") -> None:
        self.card_delimiter = card_delimiter

    def format_card_front(self, card: QuizCard) -> str:
        """Combine question prompt and options on the front side."""
        if card.options:
            options_text = "\n".join(card.options)
            return f"{card.question}\n{options_text}"
        return card.question

    def format_deck(self, deck: QuizDeck) -> str:
        """Convert deck into Tab-delimited with custom card delimiter."""
        card_strings = [
            f"{self.format_card_front(card)}\t{card.answer}"
            for card in deck.cards
        ]
        return self.card_delimiter.join(card_strings)

    def export(
        self,
        deck: QuizDeck,
        output_path: Path | str | None = None,
        copy_to_clipboard: bool = True,
    ) -> str:
        formatted_text = self.format_deck(deck)

        if output_path:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(formatted_text, encoding="utf-8")

        if copy_to_clipboard:
            with contextlib.suppress(pyperclip.PyperclipException, OSError):
                pyperclip.copy(formatted_text)

        return formatted_text
