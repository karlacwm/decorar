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
    """Extracts question-answer pairs and choices from quizzes."""

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
        answers: dict[int, str] = {}
        answer_pattern = re.compile(
            r"^\s*(\d+)\.\s*[A-Za-z]\s*[-–—]\s*(.+)$", re.MULTILINE
        )
        for match in answer_pattern.finditer(answers_section):
            q_num = int(match.group(1))
            answers[q_num] = match.group(2).strip()

        # 4. Parse Question blocks: Pergunta <N>
        questions: dict[int, dict] = {}
        # Matches each question block starting from "Pergunta <N>:"
        block_pattern = re.compile(
            r"Pergunta\s+(\d+)\s*:\s*\n*(.*?)(?=(?:Pergunta\s+\d+\s*:|\
                KEY\s*:|__{5,}|\Z))",
            re.DOTALL | re.IGNORECASE,
        )

        for match in block_pattern.finditer(questions_section):
            q_num = int(match.group(1))
            block_text = match.group(2).strip()

            # Find all options (e.g. A) ..., B) ..., C) ...)
            options = [
                line.strip()
                for line in block_text.splitlines()
                if re.match(r"^[A-Ca-c]\)\s*", line.strip())
            ]

            # The question prompt is everything before the first option 'A)'
            prompt_part = re.split(r"\n\s*[A-Ca-c]\)", block_text)[0].strip()
            prompt = " ".join(prompt_part.split())

            questions[q_num] = {"prompt": prompt, "options": options}

        # 5. Assemble cards
        cards: list[QuizCard] = []
        for q_num in sorted(questions.keys()):
            if q_num in answers:
                cards.append(
                    QuizCard(
                        question=questions[q_num]["prompt"],
                        options=questions[q_num]["options"],
                        answer=answers[q_num],
                    )
                )

        return QuizDeck(cards=cards)
