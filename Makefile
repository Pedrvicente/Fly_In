.PHONY: install run visualize debug clean lint lint-strict

PYTHON := python3
MAIN := main.py
FILE ?= maps/example.txt

install:
	pip3 install -r requirements.txt

run:
	python3 $(MAIN) $(FILE)

visualize:
	python3 $(MAIN) $(FILE) --visual

debug:
	python3 -m pdb $(MAIN) $(FILE)

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
