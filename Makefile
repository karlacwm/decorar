.PHONY: run test lint format clean

run:
	uv run python3 -m src.decorar

test:
	uv run pytest tests/

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +