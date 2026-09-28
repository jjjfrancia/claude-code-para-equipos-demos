# SPEC — Tutor de proyectos · Respuesta con cita de página

## 1. Objetivo
El alumno recibe una respuesta a su pregunta sobre el PMBOK 7 o la Guía Scrum 2020,
redactada solo con párrafos del documento y con la página citada, en menos de 10 s.

## 2. User story
Como alumno del curso, quiero preguntar por WhatsApp «¿qué es el acta de constitución?»
y recibir la explicación con la página exacta, para poder verificarla en el libro.

## 3. Acceptance criteria (numerados, binarios, cada uno con su test)
AC1  Toda respuesta incluye al menos una cita con formato «<Documento>, p. <n>».
     test_ac1_formato_de_cita
AC2  Cada afirmación de la respuesta aparece, con las mismas palabras clave, en alguno de los
     párrafos recuperados. Se verifica por código (tutor/verificar.py), no por el modelo.
     test_ac2_afirmaciones_con_soporte
AC3  Si la búsqueda no devuelve párrafos con score >= 0.35, la respuesta es exactamente
     «No encuentro eso en el documento» y NO se llama al modelo.
     test_ac3_sin_parrafos_no_llama_al_modelo
AC4  Tiempo total (webhook → respuesta enviada) <= 10 s en el p95 de 50 preguntas.
     test_ac4_latencia_p95
AC5  La respuesta cabe en un mensaje de WhatsApp (<= 1.500 caracteres).
     test_ac5_longitud

## 4. Archivos e interfaces involucrados (restricciones técnicas)
- tutor/buscar.py      buscar_hibrido(pregunta, k) -> list[Parrafo]   (existe: NO reescribir)
- tutor/redactar.py    redactar(pregunta, parrafos) -> Respuesta       (cambia aquí)
- tutor/verificar.py   verificar(respuesta, parrafos) -> Veredicto     (contrato: NO tocar)
- tutor/app.py         webhook POST /whatsapp                          (solo el armado del mensaje)
Stack: Python 3.12, FastAPI, PostgreSQL 16 + pgvector, sentence-transformers all-MiniLM-L6-v2.
Toda llamada al modelo pasa por governed_call(); sin dependencias nuevas.

## 5. Fuera de alcance
- Subir documentos propios (es la siguiente spec).
- Cambiar el troceo o los embeddings.
- Cualquier cambio en tutor/verificar.py (va por RFC).

## 6. Guardrails (qué NO hacer)
- NO responder con conocimiento del modelo: solo con párrafos recuperados.
- NO escribir datos personales del alumno en logs ni en fixtures.
- NO llamar al modelo si el guard de prompt injection bloqueó la pregunta.

## 7. Edge cases (cada uno con su test)
- Pregunta en inglés → se responde en español citando el documento en su idioma.
- Pregunta con dos temas → se responde el primero y se ofrece el segundo.
- Documento aún no cargado → «El documento se está procesando, intenta en 1 minuto».
- Chunk sin número de página → se cita la sección y se marca «página no disponible».

## 8. Verificación de punta a punta (Definition of Done)
[ ] pytest -q en verde, con la salida pegada en el PR (no «los tests pasan»).
[ ] Los 4 edge cases con su test.
[ ] 50 preguntas de tests/preguntas_frecuentes.json respondidas por el endpoint real:
    0 citas inventadas (verificar.py) y p95 <= 10 s. Salida del script pegada en el PR.
[ ] Revisión de un subagente con contexto limpio contra esta spec: sin brechas bloqueantes.
[ ] Un humano leyó el diff completo y aprobó el PR.
