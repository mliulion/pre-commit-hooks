PYTHON     := python3
VENV       := .venv
BIN        := $(VENV)/bin
PIP        := $(BIN)/pip

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


# ============================================================
#  PRE-COMMIT
# ============================================================

.PHONY: pre-commit
pre-commit: install  ## Corre todos los hooks manualmente
	$(BIN)/pre-commit run --all-files
