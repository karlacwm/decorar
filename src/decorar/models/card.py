from pydantic import BaseModel  # pyright: ignore


class QuizCard(BaseModel):
    question: str
    options: list[str] = []
    answer: str
    explanation: str | None = None


class QuizDeck(BaseModel):
    cards: list[QuizCard]
