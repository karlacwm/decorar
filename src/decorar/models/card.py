from pydantic import BaseModel  # pyright: ignore


class QuizCard(BaseModel):
    question: str
    options: list[str] = []
    answer: str
    explanation: str | None = None
    needs_review: bool = False

    def is_unresolved(self) -> bool:
        """Returns True if the answer is a placeholder like '->' or empty."""
        cleaned = self.answer.strip()
        return "->" in cleaned or cleaned in {"-", "?", ""}


class QuizDeck(BaseModel):
    cards: list[QuizCard]

    def valid_cards(self) -> list[QuizCard]:
        """Cards that have real answers ready for Quizlet."""
        return [c for c in self.cards if not c.is_unresolved()]

    def unresolved_cards(self) -> list[QuizCard]:
        """Cards where Anita left '->' for self-study."""
        return [c for c in self.cards if c.is_unresolved()]
