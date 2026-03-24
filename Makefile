PYTHON     := python3
VENV       := .venv
BIN        := $(VENV)/bin
PIP        := $(BIN)/pip

.DEFAULT_GOAL := help

# ── Colores para output ──────────────────────────────────────
BOLD  := \033[1m
RESET := \033[0m
GREEN := \033[32m
CYAN  := \033[36m

# ============================================================
#  AYUDA
# ============================================================

.PHONY: help
help:  ## Muestra esta ayuda
	@echo ""
	@echo "$(BOLD)Uso:$(RESET) make $(CYAN)<target>$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*##"}; {printf "  $(CYAN)%-18s$(RESET) %s\n", $$1, $$2}'
	@echo ""


# ============================================================
#  INSTALL
# ============================================================

.PHONY: install
install: $(VENV)/bin/activate  ## Crea el virtualenv e instala dependencias dev


$(VENV)/bin/activate: pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip -q
	$(PIP) install -e ".[dev]" -q
	@touch $(VENV)/bin/activate
	@echo "$(GREEN)✓ Entorno listo$(RESET)"


.PHONY: clean
clean:  ## Elimina artefactos de build, cache y cobertura
	rm -rf dist/ build/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ Limpio$(RESET)"

.PHONY: clean-all
clean-all: clean  ## Elimina también el virtualenv
	rm -rf $(VENV)
	@echo "$(GREEN)✓ Virtualenv eliminado$(RESET)"

# ============================================================
#  PRE-COMMIT
# ============================================================

.PHONY: pre-commit
pre-commit: install  ## Corre todos los hooks manualmente
	$(BIN)/pre-commit run --all-files
