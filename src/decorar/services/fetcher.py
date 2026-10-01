from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path


class BaseFetcher(ABC):
    """Abstract interface defining the fetch contract."""

    @abstractmethod
    def fetch(self, query: str) -> dict:
        """Fetch email content and return it as raw text."""
        pass


class FileFetcher(BaseFetcher):
    """Fetches newsletter content from a local file."""

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)

    def 