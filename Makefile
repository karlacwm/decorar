.PHONY: run test lint format clean

run:
	python -m decorar

test:
	pytest tests/

lint:
	ruff check .

format:
	ruff format .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +