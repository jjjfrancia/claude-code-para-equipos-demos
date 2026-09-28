---
paths:
  - "tutor/**/*.py"
  - "tests/**/*.py"
---

# Reglas del código Python del Tutor

- Toda función pública lleva docstring con el «por qué», no solo el «qué».
- Las llamadas al modelo pasan por `governed_call()`; si ves un cliente directo, es un bug.
- Los parámetros de búsqueda (`k`, `SCORE_MINIMO`) son constantes nombradas del módulo,
  nunca literales dentro de una función.
- Un test por criterio de aceptación. El nombre del test lleva el AC.
