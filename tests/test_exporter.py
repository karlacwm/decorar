from decorar.models.card import QuizCard, QuizDeck
from decorar.services.exporter import QuizletExporter


def test_quizlet_exporter_format_with_options():
    deck = QuizDeck(
        cards=[
            QuizCard(
                question="Which sentence is correct?",
                options=["A) Gosto de maçã.", "B) Gosto a maçã."],
                answer="Gosto de maçã.",
            ),
            QuizCard(
                question="Como estás?",
                options=["A) Bem", "B) Mal"],
                answer="Bem",
            ),
        ]
    )

    exporter = QuizletExporter()
    output = exporter.format_deck(deck)

    expected = (
        "Which sentence is correct?\nA) Gosto de maçã.\
            \nB) Gosto a maçã.\tGosto de maçã."
        "\n\n;;;\n\n"
        "Como estás?\nA) Bem\nB) Mal\tBem"
    )
    assert output == expected
