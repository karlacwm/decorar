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

import contextlib
import imaplib
import os
from abc import ABC, abstractmethod
from email import policy
from email.parser import BytesParser
from pathlib import Path

from dotenv import load_dotenv  # pyright: ignore

load_dotenv()


class BaseFetcher(ABC):
    """Abstract interface defining the fetch contract."""

    @abstractmethod
    def fetch(self) -> str:
        """Fetch email content and return it as raw text."""


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
            raise ValueError(f"No plain-text content found in {self.file_path}")

        # Fallback for plain .txt files
        return self.file_path.read_text(encoding="utf-8")


class ImapFetcher(BaseFetcher):
    """Fetches quiz emails directly from Gmail via IMAP."""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        host: str = "imap.gmail.com",
    ) -> None:
        raw_user = username or os.getenv("GMAIL_USER") or ""
        raw_pass = password or os.getenv("GMAIL_APP_PASSWORD") or ""
        # Strip any quotes or trailing whitespace
        self.username = raw_user.strip().strip("'\"")
        self.password = raw_pass.replace(" ", "").strip().strip("'\"")
        self.host = host
        if not self.username or not self.password:
            raise ValueError(
                "Gmail credentials missing. Please set GMAIL_USER and "
                "GMAIL_APP_PASSWORD in your .env file."
            )

        # Diagnostic print (safe: never prints the password)
        print(f"   -> Username: '{self.username}'")
        print(
            f"   -> Password length: {len(self.password)} \
                characters (should be 16)"
        )

    def fetch(
        self, search_criteria: str = '(FROM "portuguesewithanita" SUBJECT "Quiz")'
    ) -> str:
        """Connects to Gmail, finds the email, and returns its plain text."""
        # 1. Connect & Login
        mail = imaplib.IMAP4_SSL(self.host)
        try:
            mail.login(self.username, self.password)
            mail.select("INBOX")
            # 2. Search
            status, messages = mail.search(None, search_criteria)
            if status != "OK" or not messages[0]:
                raise ValueError(f"No emails found matching search: {search_criteria}")
            # 3. Get the latest email ID
            email_ids = messages[0].split()
            latest_id = email_ids[-1]
            # 4. Fetch RFC822 raw bytes
            status, data = mail.fetch(latest_id, "(RFC822)")
            if status != "OK" or not data or not isinstance(data[0], tuple):
                raise RuntimeError(f"Failed to fetch email ID {latest_id}")
            raw_bytes = data[0][1]
            if not isinstance(raw_bytes, bytes):
                raise TypeError(f"Invalid email payload for ID {latest_id}")
            msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
            body = msg.get_body(preferencelist=("plain",))
            if body:
                return body.get_content()
            raise ValueError("No plain text found in the fetched email.")
        finally:
            with contextlib.suppress(imaplib.IMAP4.error, OSError):
                mail.close()
            with contextlib.suppress(imaplib.IMAP4.error, OSError):
                mail.logout()

    def fetch_all(
        self,
        search_criteria: str = '(FROM "portuguesewithanita" SUBJECT "Quiz")',
    ):
        """Connects to Gmail and yields (email_id, subject, plain_text)."""
        mail = imaplib.IMAP4_SSL(self.host)
        try:
            mail.login(self.username, self.password)
            mail.select("INBOX")

            status, messages = mail.search(None, search_criteria)
            if status != "OK" or not messages[0]:
                return

            email_ids = messages[0].split()
            print(f"Found {len(email_ids)} quiz emails!")

            for email_id in email_ids:
                status, data = mail.fetch(email_id, "(RFC822)")
                if status != "OK" or not data or not isinstance(data[0], tuple):
                    continue

                raw_bytes = data[0][1]
                if not isinstance(raw_bytes, bytes):
                    continue

                msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)

                subject = str(msg["Subject"] or "Unknown Quiz")
                body_part = msg.get_body(preferencelist=("plain",))
                if body_part:
                    yield {
                        "id": email_id.decode("utf-8"),
                        "subject": subject,
                        "body": body_part.get_content(),
                    }
        finally:
            with contextlib.suppress(imaplib.IMAP4.error, OSError):
                mail.close()
            with contextlib.suppress(imaplib.IMAP4.error, OSError):
                mail.logout()
