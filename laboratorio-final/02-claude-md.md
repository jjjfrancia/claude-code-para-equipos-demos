# CLAUDE.md
## Comandos verificables
- Tests: pytest -q
- Tipos: mypy src
- Lint: ruff check .

## Guardrails
- Nunca editar migrations aplicadas.
- Nunca imprimir tokens ni contenido de .env.
- Pedir aprobación antes de cambiar contratos públicos.
- Al terminar: ejecutar tests, revisar diff y reportar evidencia.
