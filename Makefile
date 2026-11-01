.PHONY: help setup run test lint clean

VENV=venv
PYTHON=$(VENV)/bin/python

help:
	@echo "make setup     Crea el venv e instala dependencias (uv)"
	@echo "make run       Ejecuta la app"
	@echo "make test      Ejecuta tests"
	@echo "make lint      Ejecuta linters"
	@echo "make clean     Limpia el venv y caches"

setup:
	uv venv $(VENV)
	uv pip install --python $(PYTHON) -r requirements.txt

run:
	$(PYTHON) -m streamlit run app.py

test:
	$(PYTHON) -m tests.reproduce_latex

lint:
	$(PYTHON) -m flake8 .

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
