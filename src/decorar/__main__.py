from decorar.services.fetcher import FileFetcher


def run():
    raw_text = FileFetcher("data/raw/Quiz #88.eml").fetch()

    # Clean out zero-width characters and print the first 25 non-empty lines:
    cleaned = raw_text.replace("\u200c", "").replace("\ufeff", "")
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]

    for line in lines[:30]:
        print(line)


if __name__ == "__main__":
    run()
