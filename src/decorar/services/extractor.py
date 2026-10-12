# Phase 2: The Extractor (Parsing Questions & Answers)
# Goal: Extract questions from the top and match them
# with the answer keys at the bottom.
# Step 2.1: Inspect the email's plain text layout:
# Are questions numbered (1., 2., Q1:)?
# How are choices formatted (a), b), c))?
# What delimiter separates the questions from the answers
# (e.g. ---, Answers:, Respostas:)?
# Step 2.2: Write a parsing function in extractor.py:
# Split the email into Questions Section and Answers Section.
# Extract the questions.
# Extract the answers and map them by number/identifier.
# Return your validated
# QuizDeck(cards=[QuizCard(...)])

import re
from abc import ABC, abstractmethod

from decorar.models.card import QuizCard, QuizDeck


class BaseExtractor(ABC):
    """Abstract interface defining the extraction contract."""

    @abstractmethod
    def extract(self, text: str) -> QuizDeck:
        """Extract quiz cards from raw text."""
        pass


class QuizExtractor(BaseExtractor):
    """Extracts question-answer pairs from Anita's newsletter quizzes."""

    def extract(self, text: str) -> QuizDeck:
        # 1. Clean invisible unicode padding
        cleaned_text = text.replace("\u200c", "").replace("\ufeff", "")

        # 2. Split into Questions and Answers sections at 'KEY:'
        key_match = re.search(r"\bKEY\s*:", cleaned_text, re.IGNORECASE)
        if not key_match:
            raise ValueError(
                "Could not find 'KEY:' section in the email text.")

        questions_section = cleaned_text[: key_match.start()]
        answers_section = cleaned_text[key_match.end():]

        # 3. Parse Answers: e.g. "1. A - Outono"
        # Matches: (1). A - (Outono)
        answers: dict[int, str] = {}
        answer_pattern = re.compile(
            r"^\s*(\d+)\.\s*[A-Za-z]\s*[-–—]\s*(.+)$", re.MULTILINE
        )
        for match in answer_pattern.finditer(answers_section):
            q_num = int(match.group(1))
            answer_text = match.group(2).strip()
            answers[q_num] = answer_text

        # 4. Parse Questions: e.g. Pergunta 1:\n What is ...?\n\nA)
        # Matches text between 'Pergunta <N>:' and the first option 'A)'
        questions: dict[int, str] = {}
        question_pattern = re.compile(
            r"Pergunta\s+(\d+)\s*:\s*\n*(.*?)(?=\n\s*[A-Ca-c]\)|\Z)",
            re.DOTALL,
        )
        for match in question_pattern.finditer(questions_section):
            q_num = int(match.group(1))
            # Clean up line breaks within multi-line questions
            q_text = " ".join(match.group(2).split()).strip()
            questions[q_num] = q_text

        # 5. Pair questions and answers
        cards: list[QuizCard] = []
        for q_num in sorted(questions.keys()):
            if q_num in answers:
                cards.append(
                    QuizCard(
                        question=questions[q_num],
                        answer=answers[q_num],
                    )
                )

        return QuizDeck(cards=cards)
