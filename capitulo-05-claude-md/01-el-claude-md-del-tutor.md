# CLAUDE.md — Tutor de proyectos por WhatsApp

## Qué es este repositorio
Agente tutor que responde preguntas sobre el PMBOK 7 y la Guía Scrum 2020 citando la página.
Nunca responde de memoria: busca en el documento (tutor/buscar.py), redacta solo con lo
recuperado (tutor/redactar.py) y verifica cada afirmación (tutor/verificar.py).

## Comandos
- Tests: `pytest -q` — obligatorio antes de reportar cualquier cambio
- Servidor local: `uvicorn tutor.app:app --reload`
- Trocear un PDF: `python rag/05_chunking_jerarquico.py docs/pmbok7.pdf`
- Formato y lint: `ruff format . && ruff check .`

## Convenciones
- Python 3.12, tipado en todas las firmas públicas, sin `print` en producción (usa `logging`).
- Toda llamada al modelo pasa por `governed_call()`; el cliente directo está prohibido.
- Las consultas SQL usan placeholders `%s`; nunca f-strings con datos del usuario.
- Los tests van en `tests/` y se nombran `test_<modulo>.py`; un test por criterio de aceptación,
  con el AC en el nombre: `test_ac3_sin_parrafos_no_llama_al_modelo`.

## Reglas que NO se negocian
- NO modificar `tutor/verificar.py`: es el contrato de verificación. Cambia por RFC.
- NO escribir datos personales del alumno en logs ni en fixtures.
- NO agregar dependencias a `requirements.txt` sin decirlo en el resumen del cambio.
- Si la spec no dice algo, no lo inventes: termina el resumen con una lista de «supuestos».

## Dónde está cada cosa
@docs/ARQUITECTURA.md

## Al resumir la conversación (compactación), conserva siempre
- El objetivo actual y los criterios de aceptación en curso
- Los archivos leídos o modificados
- Los resultados de pytest y los errores vistos
- Las decisiones tomadas y su motivo
