# Crypto Robo Research

This repository isolates experiments from the production runtime. Use it for backtests, data-provider evaluations, prompt and schema experiments, and golden test datasets.

## Responsibilities

- Strategy experiments that should not block runtime packaging
- Golden datasets for regression tests
- AI prompt and response evaluation assets
- Provider mapping and exchange behavior comparisons

## Local Workflow

1. Create a Python 3.12 virtual environment.
2. Install dependencies with `pip install -e .[dev]`.
3. Run tests with `pytest`.
4. Keep runtime-facing schemas aligned with the production repo.
