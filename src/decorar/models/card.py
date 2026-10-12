from typing import Optional
from pydantic import BaseModel  # pyright: ignore


class QuizCard(BaseModel):
    question: str
    options: list[str] = []
    answer: str
    explanation: Optional[str] = None


class QuizDeck(BaseModel):
    cards: list[QuizCard]
