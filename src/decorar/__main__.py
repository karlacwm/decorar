from pathlib import Path
from decorar.services.fetcher import FileFetcher
from decorar.services.extractor import QuizExtractor
from decorar.services.exporter import QuizletExporter


def run():
    input_file = Path("data/raw/Quiz #88.eml")
    output_file = Path("data/output/quizlet.txt")

    print(f"1. Fetching email: {input_file}...")
    raw_text = FileFetcher(input_file).fetch()

    print("2. Extracting quiz cards...")
    deck = QuizExtractor().extract(raw_text)
    print(f"   -> Extracted {len(deck.cards)} cards.")

    print(f"3. Exporting to: {output_file}...")
    QuizletExporter().export(deck, output_path=output_file)
    print("   -> Success! Saved to file and copied to clipboard.")


if __name__ == "__main__":
    run()
