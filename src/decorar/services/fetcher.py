from abc import ABC, abstractmethod
import base64
from html import unescape
from pathlib import Path
import re
from typing import Any


class BaseFetcher(ABC):
    """Abstract interface defining the fetch contract."""

    @abstractmethod
    def fetch(self) -> str:
        """Fetch email content and return it as plain text."""
        raise NotImplementedError


class FileFetcher(BaseFetcher):
    """Fetches newsletter content from a local text or HTML file."""

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)

    def fetch(self) -> str:
        """Read and return the configured file's content."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Source file not found at: {self.file_path}")
        return self.file_path.read_text(encoding="utf-8")


class GmailFetcher(BaseFetcher):
    """Fetches the latest matching newsletter from Gmail."""

    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(
        self,
        credentials_path: Path | str = "credentials.json",
        token_path: Path | str = "token.json",
        query: str = 'from:"Portuguese With Anita"',
    ) -> None:
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.query = query

    def _authenticate(self) -> Any:
        """Authenticate with Gmail and return a Gmail API service client."""
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        credentials = None
        if self.token_path.exists():
            credentials = Credentials.from_authorized_user_file(
                str(self.token_path), self.SCOPES
            )

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Missing OAuth client secret at '{self.credentials_path}'. "
                        "Download it from Google Cloud Console as Desktop app credentials."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.SCOPES
                )
                credentials = flow.run_local_server(port=0)

            self.token_path.write_text(credentials.to_json(), encoding="utf-8")

        return build("gmail", "v1", credentials=credentials)

    @staticmethod
    def _decode_body(data: str) -> str:
        """Decode a Gmail URL-safe base64-encoded body."""
        padding = "=" * (-len(data) % 4)
        decoded = base64.urlsafe_b64decode(data + padding)
        return decoded.decode("utf-8", errors="replace")

    def _extract_body_from_payload(self, payload: dict[str, Any]) -> str:
        """Find and decode the preferred text body in a Gmail MIME payload."""
        plain_text_parts: list[str] = []
        html_parts: list[str] = []

        def collect_parts(part: dict[str, Any]) -> None:
            mime_type = part.get("mimeType", "").lower()
            body_data = part.get("body", {}).get("data")

            if body_data:
                if mime_type == "text/plain":
                    plain_text_parts.append(self._decode_body(body_data))
                elif mime_type == "text/html":
                    html_parts.append(self._decode_body(body_data))

            for nested_part in part.get("parts", []):
                collect_parts(nested_part)

        collect_parts(payload)

        if plain_text_parts:
            return "\n\n".join(plain_text_parts).strip()
        if html_parts:
            return self._clean_html("\n\n".join(html_parts))
        return ""

    @staticmethod
    def _clean_html(html_content: str) -> str:
        """Remove HTML markup while retaining useful text and line breaks."""
        html_content = re.sub(
            r"<(script|style)\b[^>]*>.*?</\1\s*>",
            "",
            html_content,
            flags=re.IGNORECASE | re.DOTALL,
        )
        html_content = re.sub(
            r"<(?:br|hr)\b[^>]*>|</(?:p|div|li|tr|h[1-6])\s*>",
            "\n",
            html_content,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"<[^>]*>", "", html_content)
        text = unescape(text)
        text = re.sub(r"[ \t\f\v]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        return re.sub(r"\n{3,}", "\n\n", text).strip()

    def fetch(self) -> str:
        """Fetch the latest matching email and return its body as plain text."""
        service = self._authenticate()
        results = (
            service.users()
            .messages()
            .list(userId="me", q=self.query, maxResults=1)
            .execute()
        )

        messages = results.get("messages", [])
        if not messages:
            raise ValueError(f"No emails found matching query: '{self.query}'")

        message = (
            service.users()
            .messages()
            .get(userId="me", id=messages[0]["id"], format="full")
            .execute()
        )
        return self._extract_body_from_payload(message.get("payload", {}))
