.PHONY: install, run-demo, ruff, help

install:
	poetry install
	pre-commit install

demo:
	python3 examples/demo.py

async-demo:
	python3 examples/async_demo.py

paranets-demo:
	python3 examples/paranets_demo.py

async-paranets-demo:
	python3 examples/async_paranets_demo.py

ruff:
	ruff check --fix
	ruff format

help:
	@echo "Available commands:"
	@echo "  install   - Install dependencies and set up pre-commit hooks"
	@echo "  ruff      - Format code and fix linting issues using ruff"
	@echo "  demo       - Run /examples/demo.py file"
	@echo "  async-demo - Run /examples/async_demo.py file"
	@echo "  paranet-demo  - Run /examples/paranet_demo.py file"
	@echo "  async-paranet-demo  - Run /examples/async_paranet_demo.py file"

