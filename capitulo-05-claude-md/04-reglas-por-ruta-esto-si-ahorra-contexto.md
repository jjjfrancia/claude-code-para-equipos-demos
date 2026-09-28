---
paths:
  - "migrations/**/*.sql"
  - "tutor/almacen.py"
---

# Reglas de base de datos

- El DDL vive en `migrations/*.sql`, nunca en código Python.
- Toda consulta nombra sus columnas: prohibido `SELECT *`.
- Toda consulta de datos del alumno filtra por `alumno_id`.
- Las conexiones se abren con `with get_db() as db:`; sin `with` se agota el pool.
