---
name: spec
description: Escribe la spec de 7 componentes de una feature del Tutor a partir de una frase de objetivo. Úsalo cuando el usuario diga "spec", "escribe la spec" o "nueva feature".
argument-hint: "[nombre-de-la-feature] [objetivo en una frase]"
arguments: [nombre, objetivo]
disable-model-invocation: true
allowed-tools: Read Write(specs/*)
---

## Specs que ya existen
!`ls specs/`

## Instrucciones
1. Lee `specs/PLANTILLA.md` (los 7 componentes con su explicación) y `CLAUDE.md`.
2. Escribe `specs/SPEC-$nombre.md` con los 7 componentes para este objetivo: "$objetivo".
3. Cada criterio de aceptación es binario y nombra su test: `test_acN_<lo_que_prueba>`.
4. En ⑤ Guardrails incluye SIEMPRE los cuatro guardrails fijos del Tutor (ver CLAUDE.md).
5. Termina listando qué información faltó en la frase del objetivo y qué asumiste.

No implementes nada: este comando solo escribe la spec.
