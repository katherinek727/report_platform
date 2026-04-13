.PHONY: lint format typecheck test

lint:
	ruff check app/

format:
	black app/
	ruff check --fix app/

typecheck:
	mypy app/

test:
	pytest -v
