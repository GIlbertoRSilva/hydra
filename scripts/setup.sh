#!/usr/bin/env bash
set -euo pipefail

PYTHON_VERSION="${HYDRA_PYTHON:-3.12}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv não encontrado. Instale o uv e execute novamente."
  exit 1
fi

if ! uv python find "$PYTHON_VERSION" >/dev/null 2>&1; then
  uv python install "$PYTHON_VERSION"
fi

uv venv --python "$PYTHON_VERSION"
uv sync --extra dev
uv run pytest -q

echo
echo "Ambiente pronto. Execute: uv run hydra"
