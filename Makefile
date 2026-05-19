SRCS_DIR = src
UV_PY = uv run python3

MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

install:
	uv sync

run:
	@$(UV_PY) -m src $(ARGS)

debug:
	@$(UV_PY) -m src -v $(ARGS)

test:
	@$(UV_PY) -m tests $(ARGS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf __pycache__ .mypy_cache .pytest_cache

fclean: clean
	rm -rf .venv

lint:
	$(UV_PY) -m flake8 $(SRCS_DIR)
	$(UV_PY) -m mypy $(SRCS_DIR) $(MYPY_FLAGS)

lint-strict:
	$(UV_PY) -m flake8 $(SRCS_DIR)
	$(UV_PY) -m mypy $(SRCS_DIR) --strict

.PHONY: install run debug clean fclean lint lint-strict
