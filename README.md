# 🇵🇹 Decorar

> **Decorar** *(Portuguese)*: To memorize / to learn by heart.

**Decorar** automates extracting European Portuguese quiz questions and answers from Anita's newsletter (*"Portuguese With Anita"*) in Gmail directly into Quizlet flashcard sets.

---

## Description

- **Zero-Cloud Email Fetching:** Uses standard Python `imaplib` over SSL. No Google Cloud Console, OAuth screens, or paid APIs required.
- **Smart Quiz Extractor:**
  - **Format Agnostic:** Automatically handles both modern newsletters (`KEY:` with `A)`, `B)`, `C)`) and legacy newsletters (`ANSWERS:` with `1.`, `2.`, `3.`).
  - **Inline Option Splitting:** Detects and formats multiple-choice options onto separate lines even when written together in a single sentence.
  - **Flag & Translation Cleaner:** Strips `🇵🇹` tags and `🇬🇧` English translation explanations, leaving only clean target Portuguese answers.
  - **Homework / Placeholder Isolation:** Detects unfinished answers (`->`) and isolates them into `data/output/needs_review.txt` so your Quizlet flashcards stay 100% complete.
- **Quizlet-Ready Export:**
  - Formats cards with Tab (`\t`) between question & answer, and `;` between cards.
  - Automatically copies formatted text straight to your system clipboard using `pyperclip`.
- **Flexible Modes:**
  - **[1] All-in-One Master File:** Merges all 70+ past quizzes into one master deck (`data/output/all_quizzes.txt`).
  - **[2] Separate Files:** Saves individual text files per quiz for modular study decks.
  - **[3] Latest Weekly Fetch:** Pulls only the single newest quiz email from Anita.

---

## Architecture

```
[Gmail Inbox / .eml File]
          │
          ▼  ImapFetcher / FileFetcher
    [Raw Email Body]
          │
          ▼  QuizExtractor
    [QuizDeck & QuizCard Models]
          │
          ▼  QuizletExporter
  [Quizlet Text + System Clipboard]
```

---

## Instructions

### 1. Prerequisites
- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) package manager

### 2. Installation
Clone the repository and install dependencies:

```bash
uv sync
```

### 3. Setup Gmail App Password
1. Go to your [Google Account Security](https://myaccount.google.com/security) settings and enable **2-Step Verification**.
2. Go to [App Passwords](https://myaccount.google.com/apppasswords).
3. Create an app password named `Decorar` and copy the 16-letter code.
4. In your Gmail web settings under **Forwarding and POP/IMAP**, ensure **Enable IMAP** is turned on.
5. Create a `.env` file in the project root:

```env
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

---

## Usage

Run the pipeline:

```bash
make run
```

### Selecting Modes in `src/decorar/__main__.py`
Open [`src/decorar/__main__.py`](src/decorar/__main__.py) and uncomment the workflow you need:

```python
if __name__ == "__main__":
    try:
        # Option 1: Combine all past quizzes into ONE master deck & copy to clipboard
        fetch_all_to_single_file()

        # Option 2: Fetch only the latest weekly quiz and copy to clipboard
        # fetch_latest_and_copy()

        # Option 3: Fetch all quizzes into separate individual files
        # fetch_all_to_separate_files()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
```

---

## Importing into Quizlet

1. Go to [Quizlet](https://quizlet.com) and click **Create** $\rightarrow$ **Study set**.
2. Click the **+ Import** button.
3. In the import settings:
   - **Between term and definition:** Select **Tab**.
   - **Between cards:** Select **Custom** and enter **`;`**.
4. Press `Ctrl + V` to paste the cards from your clipboard.
5. Click **Import** — your entire multiple-choice deck is ready to study!

---

## Development & Testing

Run unit tests:
```bash
make test
```

Run code formatting & linting:
```bash
make lint
make format
```

Clean temporary files:
```bash
make clean
```

---

## 📁 Project Structure

```text
decorar/
├── src/
│   └── decorar/
│       ├── models/
│       │   └── card.py          # QuizCard and QuizDeck data models
│       ├── services/
│       │   ├── fetcher.py       # IMAP and local file fetchers
│       │   ├── extractor.py     # Regex parser for Anita's newsletters
│       │   └── exporter.py      # Quizlet TSV and clipboard exporter
│       └── __main__.py          # Pipeline entrypoint & orchestration
├── tests/
│   ├── test_fetcher.py          # Unit tests for email/file fetching
│   ├── test_extractor.py        # Unit tests for regex & flag cleaning
│   └── test_exporter.py         # Unit tests for Quizlet export formatting
├── data/
│   ├── raw/                     # Offline sample .eml files
│   └── output/                  # Generated Quizlet text decks
├── Makefile                     # Shortcut commands (run, test, lint)
├── pyproject.toml               # Project metadata & dependencies
└── README.md
```
