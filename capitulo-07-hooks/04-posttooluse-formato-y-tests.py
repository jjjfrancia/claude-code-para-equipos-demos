#!/usr/bin/env python
"""PostToolUse (Edit|Write): formatea el archivo tocado y corre la suite.

La edicion ya ocurrio: este hook no la puede deshacer. Lo que impide es que el agente
siga como si nada. exit 2 devuelve el texto de stderr al agente como feedback y el
bucle continua hasta que los tests pasen.
"""
import json
import subprocess
import sys

evento = json.load(sys.stdin)
ruta = (evento.get("tool_input") or {}).get("file_path", "")

if ruta.endswith(".py"):
    subprocess.run(["ruff", "format", ruta], capture_output=True)

r = subprocess.run(["pytest", "-q", "-x"], capture_output=True, text=True)
if r.returncode != 0:
    print(f"pytest FALLA tras editar {ruta}:\n{r.stdout[-1500:]}", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
