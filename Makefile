.PHONY: bootstrap check format lint type unit contract integration security acceptance test api postgres-up postgres-down secret-scan dependency-check license-check

PYTHON ?= python3
VENV ?= .venv
DOCKER_COMPOSE ?= docker-compose
BIN := $(VENV)/bin

bootstrap:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -e '.[dev]'
	VENV=$(VENV) ./scripts/bootstrap-smoke.sh

check: format lint type test

format:
	$(BIN)/ruff format --check .

lint:
	$(BIN)/ruff check .

type:
	$(BIN)/mypy src

unit:
	$(BIN)/pytest -q tests/unit

contract:
	$(BIN)/pytest -q tests/contract

integration:
	$(BIN)/pytest -q tests/integration

security:
	$(BIN)/pytest -q tests/security

acceptance:
	$(BIN)/pytest -q tests/acceptance

test: unit contract integration security acceptance

api:
	$(BIN)/uvicorn apps.api.main:app --host 127.0.0.1 --port 8000

postgres-up:
	$(DOCKER_COMPOSE) up -d postgres

postgres-down:
	$(DOCKER_COMPOSE) down

secret-scan:
	./scripts/check-secrets.sh

dependency-check:
	$(BIN)/pip-audit

license-check:
	$(BIN)/pip-licenses --fail-on='GPL;AGPL' --partial-match
