---
name: dod
description: Verifica la Definition of Done del Tutor sobre el cambio actual y produce el informe de evidencia. Úsalo antes de abrir un PR.
context: fork
agent: general-purpose
background: false
allowed-tools: Read Grep Bash(pytest *) Bash(git diff *) Bash(git status *) Bash(ruff *)
---

## Cambio actual
!`git status --short`
!`git diff --stat`

## Instrucciones
Corre `pytest -q` y `ruff check .`. Después, por cada ítem de `dod/DoD.md`, escribe
PASA o FALLA con la evidencia literal: la salida del comando, la ruta del test o la
línea del diff.

No des por hecho nada que no hayas ejecutado. Si un ítem no se puede verificar desde
aquí, escribe NO VERIFICABLE y por qué.

Formato de salida:
VEREDICTO: LISTO PARA PR | NO LISTO
ÍTEM POR ÍTEM: <nombre> — PASA/FALLA/NO VERIFICABLE — <evidencia literal>
BLOQUEANTES: lista o «ninguno»
