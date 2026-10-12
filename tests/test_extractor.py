import pytest  # pyright: ignore

from decorar.services.extractor import QuizExtractor


SAMPLE_QUIZ_TEXT = """
QUIZ #99
Spring in Portugal 🌸

Pergunta 1:
What is the Portuguese word for "spring"?

A) Primavera
B) Outono
C) Verão

Pergunta 2:

What does "Está a chover" mean?

A) It is sunny
B) It is raining
C) It is cold

_____________________________

KEY:
1. A - Primavera
2. B - It is raining
"""


def test_quiz_extractor_parses_cards_correctly():
    extractor = QuizExtractor()
    deck = extractor.extract(SAMPLE_QUIZ_TEXT)

    assert len(deck.cards) == 2

    # Card 1
    assert deck.cards[0].question == 'What is the Portuguese word for "spring"?'
    assert deck.cards[0].answer == "Primavera"

    # Card 2
    assert deck.cards[1].question == 'What does "Está a chover" mean?'
    assert deck.cards[1].answer == "It is raining"


def test_quiz_extractor_raises_error_when_key_missing():
    extractor = QuizExtractor()
    bad_text = "Pergunta 1:\nWhat is this?\nA) Yes\nB) No"

    with pytest.raises(ValueError, match="Could not find 'KEY:' section"):
        extractor.extract(bad_text)
