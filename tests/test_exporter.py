from pathlib import Path

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
        "Which sentence is correct?\n"
        "A) Gosto de maçã.\n"
        "B) Gosto a maçã.\t"
        "Gosto de maçã."
        "\n\n;;;\n\n"
        "Como estás?\n"
        "A) Bem\n"
        "B) Mal\t"
        "Bem"
    )
    assert output == expected


def test_quizlet_exporter_writes_to_file(tmp_path: Path):
    deck = QuizDeck(cards=[QuizCard(question="Sol", answer="Sun")])
    output_file = tmp_path / "quizlet.txt"

    exporter = QuizletExporter()
    exporter.export(deck, output_path=output_file)

    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == "Sol\tSun"


def test_quizlet_exporter_without_clipboard(tmp_path: Path):
    deck = QuizDeck(cards=[QuizCard(question="Lua", answer="Moon")])
    output_file = tmp_path / "quizlet_no_clip.txt"

    exporter = QuizletExporter()
    output = exporter.export(deck, output_path=output_file, copy_to_clipboard=False)

    assert output_file.exists()
    assert output == "Lua\tMoon"
