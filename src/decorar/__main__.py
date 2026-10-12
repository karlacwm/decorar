from decorar.services.fetcher import FileFetcher
from decorar.services.extractor import QuizExtractor


def run():
    raw_text = FileFetcher("data/raw/Quiz #88.eml").fetch()
    deck = QuizExtractor().extract(raw_text)

    print(f"Extracted {len(deck.cards)} cards:\n")
    for i, card in enumerate(deck.cards, 1):
        print(f"[{i}] Question: {card.question}")
        print(f"    Answer:   {card.answer}\n")


if __name__ == "__main__":
    run()
