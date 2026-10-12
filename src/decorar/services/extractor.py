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


class QuizExtractor(BaseExtractor):
    """Extracts question-answer pairs and choices from quizzes."""

    def extract(self, text: str) -> QuizDeck:
        # 1. Clean invisible unicode padding
        cleaned_text = text.replace("\u200c", "").replace("\ufeff", "")

        # 2. Split at 'KEY:' or 'ANSWERS:' heading (must be start of line or followed by colon)
        key_match = re.search(
            r"(?:^|\n)\s*\*?\*?(?:KEY|ANSWERS?|RESPOSTAS?|SOLUÇÕES?|SOLUTIONS?)\*?\*?\s*[:\n]",
            cleaned_text,
            re.IGNORECASE,
        )
        if not key_match:
            raise ValueError(
                "Could not find 'KEY:' or 'ANSWERS:' section in the email text."
            )

        questions_section = cleaned_text[: key_match.start()]
        answers_section = cleaned_text[key_match.end() :]

        # 3. Parse Answers:
        # Matches: "1. A - Outono" OR "1) os edifícios" OR "1. os edifícios"
        answers: dict[int, str] = {}
        answer_pattern = re.compile(
            r"^\s*(\d+)[\.\)]\s*(?:[A-Za-z]\s*[-–—]\s*)?(.+)$", re.MULTILINE
        )
        for match in answer_pattern.finditer(answers_section):
            q_num = int(match.group(1))
            raw_answer = match.group(2).strip()

            # Remove English flag translations (e.g. "está. 🇬🇧 He's sitting...")
            cleaned_answer = re.sub(r"\s*(?:🇬🇧|🇺🇸).*$", "", raw_answer).strip()
            # Remove Portuguese flag tag (e.g. "🇵🇹 escola" -> "escola")
            cleaned_answer = cleaned_answer.replace("🇵🇹", "").strip()
            # Remove any trailing period left behind (e.g. "está." -> "está")
            cleaned_answer = cleaned_answer.rstrip(".").strip()

            answers[q_num] = cleaned_answer or raw_answer

        # 4. Parse Question blocks: Pergunta <N>:
        questions: dict[int, dict] = {}
        block_pattern = re.compile(
            r"Pergunta\s+(\d+)\s*:\s*\n*(.*?)"
            r"(?=(?:Pergunta\s+\d+\s*:|\b(?:KEY|ANSWERS?)\b|__{5,}|\Z))",
            re.DOTALL | re.IGNORECASE,
        )

        for match in block_pattern.finditer(questions_section):
            q_num = int(match.group(1))
            block_text = match.group(2).strip()

            # Find where options begin (e.g. ' a. ', ' A) ', ' 1. ', or '?A) ')
            first_opt_match = re.search(
                r"(?:^|\s+|(?<=[?!:\n]))([A-Da-d1-4][\.\)]\s+)",
                block_text,
            )

            if first_opt_match:
                prompt_raw = block_text[: first_opt_match.start()].strip()
                options_raw = block_text[first_opt_match.start() :].strip()

                # Split before each option marker (must be followed by space)
                raw_options = re.split(
                    r"(?:^|\s+|(?<=[?!:\n]))(?=[A-Da-d1-4][\.\)]\s+)",
                    options_raw,
                )
                options = [
                    " ".join(opt.split()).strip()
                    for opt in raw_options
                    if re.match(r"^[A-Da-d1-4][\.\)]\s+", opt.strip())
                ]
            else:
                prompt_raw = block_text
                options = []

            prompt = " ".join(prompt_raw.split()).strip()
            questions[q_num] = {"prompt": prompt, "options": options}

        # 5. Assemble cards
        cards: list[QuizCard] = []
        for q_num in sorted(questions.keys()):
            if q_num in answers:
                card = QuizCard(
                    question=questions[q_num]["prompt"],
                    options=questions[q_num]["options"],
                    answer=answers[q_num],
                )
                card.needs_review = card.is_unresolved()
                cards.append(card)

        return QuizDeck(cards=cards)
