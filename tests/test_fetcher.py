import pytest  # pyright: ignore
from pathlib import Path
from decorar.services.fetcher import FileFetcher


def test_file_fetcher_reads_plain_text(tmp_path: Path):
    # Create a dummy .txt file in the temporary folder
    test_file = tmp_path / "sample.txt"
    test_file.write_text("Hello Portuguese!", encoding="utf-8")

    fetcher = FileFetcher(test_file)
    content = fetcher.fetch()

    assert content == "Hello Portuguese!"


def test_file_fetcher_raises_when_file_not_found():
    fetcher = FileFetcher("non_existent_file.eml")

    with pytest.raises(FileNotFoundError):
        fetcher.fetch()


def test_file_fetcher_reads_eml_if_exists():
    eml_path = Path("data/raw/Quiz #88.eml")
    if eml_path.exists():
        fetcher = FileFetcher(eml_path)
        content = fetcher.fetch()
        assert "QUIZ #88" in content
