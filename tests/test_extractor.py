import pytest  # pyright: ignore

from decorar.services.extractor import QuizExtractor

SAMPLE_NEW_FORMAT = """
QUIZ #99
Spring in Portugal 🌸

Pergunta 1:
What is the Portuguese word for "spring"?

A) Primavera
B) Outono
C) Verão

_____________________________

KEY:
1. A - Primavera
"""

SAMPLE_OLD_FORMAT = """
QUIZ #20 VOCABULÁRIO DE CIDADE 🇵🇹

Pergunta 1:

buildings

1. os edifícios
2. o edifício
3. a casa

________________

ANSWERS:

1) os edifícios
"""


def test_extractor_handles_new_format_with_key():
    extractor = QuizExtractor()
    deck = extractor.extract(SAMPLE_NEW_FORMAT)

    assert len(deck.cards) == 1
    assert deck.cards[0].question == 'What is the Portuguese word for "spring"?'
    assert deck.cards[0].options == ["A) Primavera", "B) Outono", "C) Verão"]
    assert deck.cards[0].answer == "Primavera"


def test_extractor_handles_old_format_with_answers():
    extractor = QuizExtractor()
    deck = extractor.extract(SAMPLE_OLD_FORMAT)

    assert len(deck.cards) == 1
    assert deck.cards[0].question == "buildings"
    assert deck.cards[0].options == ["1. os edifícios", "2. o edifício", "3. a casa"]
    assert deck.cards[0].answer == "os edifícios"


def test_extractor_raises_error_when_no_delimiter():
    extractor = QuizExtractor()
    bad_text = "Pergunta 1:\nWhat is this?\nA) Yes\nB) No"

    with pytest.raises(ValueError, match="Could not find 'KEY:' or 'ANSWERS:'"):
        extractor.extract(bad_text)


def test_extractor_cleans_flag_and_translation():
    extractor = QuizExtractor()
    text = """
    Pergunta 1:
    Ele __ sentado na cadeira.
    1. estou
    2. está
    3. estamos

    Pergunta 2:
    A Maria amanhã vai à ___.
    a) iscola
    b) scola
    c) escola
    ________________
    ANSWERS:
    1) está. 🇬🇧 He's sitting on the chair.
    2) 🇵🇹 escola 🇬🇧 Maria goes to school tomorrow.
    """
    deck = extractor.extract(text)
    assert len(deck.cards) == 2
    assert deck.cards[0].answer == "está"
    assert deck.cards[1].answer == "escola"


def test_extractor_handles_inline_options():
    extractor = QuizExtractor()
    text = """
    Pergunta 1:
    Easter eggs 🥚 a. Ovos de Natal b. Ovos de Páscoa c. Ogos de Páscoa
    ________________
    ANSWERS:
    1) Ovos de Páscoa
    """
    deck = extractor.extract(text)
    assert len(deck.cards) == 1
    assert deck.cards[0].question == "Easter eggs 🥚"
    assert deck.cards[0].options == [
        "a. Ovos de Natal",
        "b. Ovos de Páscoa",
        "c. Ogos de Páscoa",
    ]
    assert deck.cards[0].answer == "Ovos de Páscoa"
