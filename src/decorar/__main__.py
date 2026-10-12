import re
from pathlib import Path

from decorar.models.card import QuizCard, QuizDeck
from decorar.services.exporter import QuizletExporter
from decorar.services.extractor import QuizExtractor
from decorar.services.fetcher import ImapFetcher


def sanitize_filename(name: str) -> str:
    """Turn email subjects into clean safe filenames (e.g. 'Quiz_88')."""
    return re.sub(r"[^\w\-_]", "_", name).strip("_")


def fetch_latest_and_copy():
    """Fetch only the latest quiz from Gmail, save it, and copy to clipboard."""
    output_file = Path("data/output/latest_quiz.txt")
    print("Fetching the latest quiz from Gmail...")

    fetcher = ImapFetcher()
    extractor = QuizExtractor()
    exporter = QuizletExporter()

    raw_text = fetcher.fetch()
    deck = extractor.extract(raw_text)

    exporter.export(deck, output_path=output_file, copy_to_clipboard=True)
    print(f"✓ Saved {len(deck.cards)} cards -> {output_file}")
    print("✓ Copied latest cards to clipboard! Ready to paste into Quizlet.")


def fetch_all_to_separate_files():
    """Fetch all quizzes and save each to its own file (no clipboard copy)."""
    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    print("Fetching all quizzes into separate files...")

    fetcher = ImapFetcher()
    extractor = QuizExtractor()
    exporter = QuizletExporter()

    count = 0
    for email_data in fetcher.fetch_all():
        subject = email_data["subject"]
        body = email_data["body"]

        try:
            deck = extractor.extract(body)
            if not deck.cards:
                continue

            file_name = f"{sanitize_filename(subject)}.txt"
            out_file = output_dir / file_name

            exporter.export(deck, output_path=out_file, copy_to_clipboard=False)
            print(f"✓ Saved {len(deck.cards)} cards -> {file_name}")
            count += 1
        except (ValueError, KeyError) as e:
            print(f"⚠ Skipping '{subject}': {e}")

    print(f"\nFinished! Processed {count} quiz decks in {output_dir}")


def fetch_all_to_single_file():
    """Fetch all quizzes, combine them into ONE master file, and copy to clipboard."""
    output_file = Path("data/output/all_quizzes.txt")
    print("Fetching all quizzes and combining into ONE master deck...")

    fetcher = ImapFetcher()
    extractor = QuizExtractor()
    exporter = QuizletExporter()

    all_cards: list[QuizCard] = []
    quizzes_processed = 0

    for email_data in fetcher.fetch_all():
        subject = email_data["subject"]
        body = email_data["body"]

        try:
            deck = extractor.extract(body)
            if not deck.cards:
                continue

            all_cards.extend(deck.cards)
            quizzes_processed += 1
            print(f"✓ Added {len(deck.cards)} cards from '{subject}'")
        except (ValueError, KeyError) as e:
            print(f"⚠ Skipping '{subject}': {e}")

    master_deck = QuizDeck(cards=all_cards)
    exporter.export(master_deck, output_path=output_file, copy_to_clipboard=True)

    print(
        f"\n🎉 Finished! Combined {len(all_cards)} total cards from "
        f"{quizzes_processed} quizzes into {output_file}."
    )
    print("✓ All cards copied to clipboard! Ready to paste into Quizlet.")


if __name__ == "__main__":
    try:
        # Option 1: Fetch all past quizzes into ONE big master file & copy to clipboard
        fetch_all_to_single_file()

        # Option 2: Fetch only the latest weekly quiz and copy to clipboard
        # fetch_latest_and_copy()

        # Option 3: Fetch all quizzes into separate individual files (no clipboard)
        # fetch_all_to_separate_files()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
