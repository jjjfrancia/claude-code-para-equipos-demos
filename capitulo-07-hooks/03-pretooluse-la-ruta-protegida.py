#!/usr/bin/env python
"""PreToolUse (Edit|Write): bloquea las rutas protegidas del Tutor.

Entrada  : JSON por stdin -> {"tool_name": "Edit", "tool_input": {"file_path": "..."}, ...}
Salida   : exit 0 sin nada        -> sigue el flujo normal de permisos
           JSON con "deny"        -> la tool NO corre y el motivo vuelve al agente
"""
import fnmatch
import json
import sys

PROTEGIDAS = ["tutor/verificar.py", ".github/workflows/*", "migrations/*.sql", ".env*"]

evento = json.load(sys.stdin)
ruta = (evento.get("tool_input") or {}).get("file_path", "").replace("\\", "/")

for patron in PROTEGIDAS:
    if fnmatch.fnmatch(ruta, f"*{patron}") or ruta.endswith(patron):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"{ruta} es una ruta protegida del Tutor. "
                "Los cambios a verificar.py van por RFC (ver CLAUDE.md). "
                "Si necesitas otro comportamiento, propon la alternativa en el resumen."
            )}}))
        sys.exit(0)

sys.exit(0)
