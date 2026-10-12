# Phase 1: Local File First, Then IMAP Fetcher
# Goal: Avoid having to fetch from Gmail 50 times while writing code.
# Step 1.1: Save one copy of an Anita quiz email (raw text or .eml/.html) into

# data/raw/
# .
# Step 1.2: Implement

# FileFetcher.fetch()
#  to read that local file.
# Step 1.3: Build ImapFetcher(BaseFetcher) using imaplib and email to search
# for emails from Anita (e.g. FROM "Anita" or SUBJECT "Quiz").

from abc import ABC, abstractmethod
from pathlib import Path
from email import policy

from email.parser import BytesParser


class BaseFetcher(ABC):
    """Abstract interface defining the fetch contract."""

    @abstractmethod
    def fetch(self) -> str:
        """Fetch email content and return it as raw text."""
        pass


class FileFetcher(BaseFetcher):
    """Fetches newsletter content from a local file (.eml or .txt)."""

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)

    def fetch(self) -> str:
        """Read the local file and return the decoded plain text."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        # If it's an .eml email file, parse and decode it
        if self.file_path.suffix.lower() == ".eml":
            with open(self.file_path, "rb") as f:
                msg = BytesParser(policy=policy.default).parse(f)

            body = msg.get_body(preferencelist=("plain",))
            if body:
                return body.get_content()
            raise ValueError(
                f"No plain-text content found in {self.file_path}")

        # Fallback for plain .txt files
        return self.file_path.read_text(encoding="utf-8")


# class EmailFetcher(BaseFetcher):
#     """Fetches quiz content from Gmail."""

#     def __init__(self):
#         pass

#     def fetch(self):
#         pass
