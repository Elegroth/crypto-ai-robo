# Crypto Robo Runtime

The runtime repository contains the production-oriented application code for the crypto robo MVP. It is designed as one Python package with multiple Lambda-friendly handlers instead of many microservices.

## Core Responsibilities

- Sync market metadata and tradable instruments
- Build the approved trading universe
- Generate deterministic features and target weights
- Produce weekly rebalance plans
- Enforce risk rules before any order is sent
- Persist audit events and reports
- Incorporate AI market memos as a bounded risk overlay

## Local Development

1. Create a Python 3.12 virtual environment.
2. Install dependencies with `pip install -e .[dev]`.
3. Run tests with `pytest`.
4. Run linters with `ruff check .` and `mypy src`.
