# Caso transversal del curso: el Marketplace de Créditos

Ficha única del caso, basada en el business case «Marketplace de Créditos» (Perú, setiembre 2026).
Todo el curso (`index.html`), el banco de preguntas y las demos lo usan tal cual está aquí: nombres,
cifras, socios, tools y ejemplos. Si algo cambia, se cambia primero en esta ficha.

## El producto

El banco está construyendo el **Marketplace de Créditos**: una plataforma donde **empresas (MYPE) y
personas naturales** publican una solicitud de crédito, la plataforma calcula un **score de riesgo con
Open Finance / Open Data** (datos transaccionales del banco con consentimiento + central de riesgo
Equifax/Infocorp y Sentinel), y **uno o varios prestamistas la fondean** de forma parcial o total. Al
llegar al 100 % se desembolsa en **stablecoin o en soles vía una rampa fiat ↔ stablecoin**, con fondeo y
reparto de pagos sobre **blockchain**. Sin colateral cripto y, en esta fase, sin seguro de crédito.

- **Empresas:** score (flujo de caja, facturación, pago a proveedores) **+ pagaré firmado digitalmente
  + factura negociable endosada** → tasa menor. Ilustrativo: solo score ~25 % / ~35 % / ~45 % según
  score alto / medio / bajo; con pagaré + factura, 9 %–37 % según la solvencia del pagador.
- **Personas naturales:** solo score (ingresos, gasto, pago de tarjetas), sin ningún respaldo.
  Ilustrativo: ~28 % / ~40 % / ~55 %. Perfil para prestamistas con mayor tolerancia al riesgo.
- Tiempo: score inmediato y cierre el mismo día, frente a 2-4 semanas de la banca tradicional.

## El ciclo, paso a paso (lo que el sistema tiene que garantizar)

1. Empresa o persona **publica la solicitud** (monto, plazo).
2. **Score de riesgo**: Open Finance + banca tradicional + central de riesgo.
3. **Prestamistas fondean**, parcial o total, hasta el 100 %.
4. *(Solo empresas)* **Verificar la factura** en CAVALI con el socio de factoring (Factrack).
5. *(Solo empresas)* **Enviar el pagaré a firmar** al socio de firma digital (PSC acreditado ante INDECOPI).
6. *(Solo empresas)* La empresa **firma con biometría / OTP**; el socio devuelve el pagaré firmado.
7. *(Solo empresas)* **Orden de endoso**: el socio de factoring transfiere la factura y registra el
   pagaré en CAVALI.
8. **Desembolso** en stablecoin o en soles vía rampa — solo cuando todo lo anterior está confirmado.
9. **Repago**: la empresa o persona paga sus cuotas; la plataforma **reparte cada pago** entre los
   prestamistas según su aporte, hasta liquidar.

Personas naturales pasan directo del paso 3 al 8.

## Integraciones (socios y fuentes)

| Pieza | Quién | Para qué |
|-------|-------|----------|
| Open Finance | Banca tradicional (con consentimiento) | Datos transaccionales para el score |
| Central de riesgo | Equifax/Infocorp, Sentinel | Endeudamiento e historial |
| Socio de factoring | CAVALI / Factrack | Verificar y endosar la factura negociable, registrar el pagaré |
| Socio de firma digital | PSC acreditado ante INDECOPI | Firma digital del pagaré |
| Rampa | Proveedor fiat ↔ stablecoin | Conversión y desembolso |
| Riel blockchain | Pool de fondeo y liquidación | Fondeo colectivo y reparto de pagos |

Marco legal que el equipo debe respetar (el curso lo usa como contexto, no como asesoría legal):
Ley de Protección de Datos Personales (consentimiento libre, previo, expreso e informado), Ley de
Factura Negociable, Ley de Títulos Valores + firma digital, Reglamento SMV de Financiamiento
Participativo Financiero, registro SBS de empresas de factoring. Open Finance directo depende de los
hitos del SFA (2027–2028); hoy se opera con BaaS + factura negociable + FPF.

Economía ilustrativa de una operación (préstamo de USD 10,000 a 12 meses, empresa score alto):
el prestatario paga 25 % TCEA, el prestamista recibe 19 %, la plataforma cobra 2 % de colocación
(USD 200) + spread (USD 600) y paga a socios USD 100 (central de riesgo 15, factoring 25, firma 10,
rampa 50). Todas las cifras del business case son ilustrativas.

## Qué construye el equipo con Claude Code (el hilo del curso)

El equipo que lo desarrolla es de tres personas: **una tech lead y dos developers**. Tienen que llevar
el Marketplace del piloto a producción pasando por las revisiones de **Riesgos, Cumplimiento
(PLA/FT), Seguridad de la Información y Legal**. Durante el curso construyen con Claude Code:

| Pieza agéntica | Escenario del examen |
|----------------|---------------------|
| **Agente de originación**: atiende a solicitantes y prestamistas (estado de la solicitud, por qué ese score, qué falta para el desembolso) con tools MCP y criterios de escalamiento a un analista de Riesgos | 1 · Customer Support Resolution Agent |
| **El equipo desarrollando la plataforma** con CLAUDE.md, comandos, skills, plan mode | 2 · Code Generation with Claude Code |
| **Comité de riesgo multi-agente**: un coordinador reparte el análisis de una solicitud entre subagentes (Open Finance, central de riesgo, factura/pagador) y un subagente de síntesis que emite el informe con fuentes | 3 · Multi-Agent Research System |
| **Explorar el core bancario heredado** y los SDK de los socios con Read, Grep, Glob y subagentes Explore | 4 · Developer Productivity |
| **Revisión automática de PRs** con `claude -p` y `--output-format json` antes del comité de cambios | 5 · Claude Code for CI |
| **Extracción estructurada** de la factura electrónica (XML/PDF) y de los estados financieros de la MYPE, con esquema JSON, campos opcionales y revisión humana | 6 · Structured Data Extraction |

### Tools canónicas del agente (servidor MCP del Marketplace)

`consultar_solicitud(id_solicitud)`, `calcular_score(id_solicitud)`, `consultar_fondeo(id_solicitud)`,
`verificar_factura_cavali(numero_factura, ruc_emisor)`, `enviar_pagare_a_firma(id_solicitud)`,
`ordenar_endoso(id_solicitud)`, `desembolsar(id_solicitud, via: "stablecoin"|"fiat")`,
`buscar_politica(consulta)` (busca en el Manual de Políticas del Marketplace y cita la página),
`escalar_a_riesgos(id_solicitud, resumen)`.

Reglas de negocio que se usan como ejemplo de **enforcement determinista** (hooks / prerrequisitos
programáticos, nunca solo el prompt):
- `desembolsar` se bloquea si el fondeo no está al 100 %, o si es empresa y no hay pagaré firmado +
  endoso registrado en CAVALI.
- `calcular_score` se bloquea si no hay consentimiento de Open Finance registrado para ese cliente.
- Montos sobre el umbral de aprobación automática (p. ej. USD 50,000) van a `escalar_a_riesgos`.
- Ningún DNI, RUC, número de cuenta ni dato de Open Finance se escribe en logs ni en prompts de CI.

### Corpus del RAG (ficticio, creado para el curso)

| Documento | Cita corta |
|-----------|-----------|
| Manual de Políticas de Crédito del Marketplace, v1.0 (segmentos, tramos de score y tasa, respaldo documentario, umbrales, excepciones, repago y mora) | «Manual de Políticas, p. N» |
| Reglamento de Participación de Prestamistas, v1.0 (quién puede fondear, límites por solicitud, riesgo asumido, reparto de pagos, PLA/FT y conocimiento del cliente) | «Reglamento de Prestamistas, p. N» |

Se generan con `capitulo-02-teoria-de-agentes/teoria/datos/generar_manuales.py` a partir de este
caso. No representan la política de ninguna entidad real.

## La escena que abre el curso

Un martes a las 10:05, la tech lead abre Claude Code en el repositorio del Marketplace y escribe una
sola línea: «cuando una solicitud llegue al 100 % de fondeo, desembolsa automáticamente en
stablecoin». Entra al comité de cambios. A las 11:00 vuelve: 14 archivos modificados, un job nuevo,
una migración de base de datos, tests nuevos y el mensaje «Listo. El desembolso automático está
implementado. Todos los tests pasan».

Lo que no se ve en ese mensaje: el job desembolsa también a empresas **sin esperar el pagaré firmado
ni el endoso de la factura en CAVALI**; el agente añadió una librería de wallets que Seguridad no ha
aprobado; guarda el RUC, el DNI del representante y los datos de Open Finance **en texto plano en los
logs**; y el test «pasa» porque el propio agente escribió un test que compara la salida consigo misma.
Nadie decidió nada de eso. Nadie lo revisó. En un banco eso no es deuda técnica: es dinero de los
prestamistas entregado sin respaldo y un hallazgo de auditoría. La velocidad fue real (una hora para lo
que al equipo le habría tomado una semana); el riesgo también.

## Nombres canónicos (cambian respecto del curso original)

| Antes | Ahora |
|-------|-------|
| Tutor de proyectos / el Tutor | el Marketplace de Créditos (la plataforma) / el agente de originación |
| WhatsApp | la app y la web del Marketplace |
| alumno(s) | solicitante(s) (empresa o persona) y prestamista(s) |
| 400 alumnos | salida a producción del piloto |
| PMBOK 7, Guía Scrum 2020 | Manual de Políticas de Crédito del Marketplace, Reglamento de Participación de Prestamistas |
| `leer_documento` / `buscar_documento` | `buscar_politica` |
| `tutor_corpus.py` | `politicas_corpus.py` |
| profesor / coordinador académico | Riesgos, Cumplimiento, Seguridad de la Información, Legal |

Se mantiene: el equipo trabaja con Scrum (sprints, Definition of Done, revisión), pero **no existe
«Sprint 0»**. Moneda: soles (S/) y USD, como en el business case.

## Alineación con el examen

El curso prepara para **Claude Certified Architect – Foundations** (60 preguntas de opción múltiple,
120 minutos, aprobación con 720/1000, 4 escenarios de un banco de 6). Cada capítulo indica qué
dominios y *task statements* de la guía oficial cubre y termina con preguntas de práctica en el
formato del examen, ambientadas en el Marketplace.

| Dominio oficial | Peso | Task statements | Capítulos |
|-----------------|------|-----------------|-----------|
| 1 · Agentic Architecture & Orchestration | 27 % | 1.1–1.7 | 2, 7, 8, 9, 10 |
| 2 · Tool Design & MCP Integration | 18 % | 2.1–2.5 | 2, 4, 8, 11 |
| 3 · Claude Code Configuration & Workflows | 20 % | 3.1–3.6 | 1, 3, 4, 5, 6, 13 |
| 4 · Prompt Engineering & Structured Output | 20 % | 4.1–4.6 | 1, 2, 3, 12, 13 |
| 5 · Context Management & Reliability | 15 % | 5.1–5.6 | 8, 9, 10, 12, 14 |
