from pydantic import BaseModel


class QuizCard(BaseModel):
    question: str
    answer: str
    explanation: str = None


class QuizDeck(BaseModel):
    cards: list[QuizCard]
