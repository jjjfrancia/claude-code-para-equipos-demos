# Caso transversal de los cuatro cursos: el Marketplace de Créditos del banco

Ficha única y simple. Los cuatro cursos (Claude Code para Equipos, Agentic AI Enterprise Architect,
Ingeniería de Prompts, AI Governance & LLMOps) usan este mismo caso, con estos nombres y cifras.

## El producto y el equipo

El banco lanza el **Marketplace de Créditos**: una app donde **personas y pequeñas empresas** piden un
préstamo, el banco lo **evalúa y aprueba**, y **inversionistas** lo financian. Es la versión simple del
business case: sin blockchain, stablecoins, factoring ni firma digital; nada de eso aparece en los
cursos.

Un equipo pequeño (**una tech lead y dos developers**) construye con Claude dos asistentes para el
Marketplace. Antes de salir a producción, cada cambio pasa por **Riesgos, Cumplimiento, Seguridad de
la Información y Legal**.

## Caso 1 · Respuesta a clientes

Un asistente que responde en la app las preguntas de solicitantes e inversionistas: requisitos,
tasas, plazos, estado de la solicitud, cómo invertir y cómo reclamar.

- Responde **solo con el Reglamento de Productos y el Tarifario** del banco y cita la página:
  «Tarifario, p. 4».
- Si no encuentra la respuesta, lo dice y ofrece derivar a un ejecutivo. Nunca inventa una tasa ni una
  comisión.
- Nunca pide ni muestra datos sensibles (número completo de tarjeta, clave, CVV).
- Deriva a un humano: si el cliente lo pide, si es un reclamo formal, o si la pregunta es sobre su
  caso particular y requiere ver su cuenta.

Ejemplos de preguntas: «¿qué necesito para pedir un préstamo?», «¿qué tasa pagaría por S/ 10,000 a
24 meses?», «¿cuánto gano si invierto S/ 5,000?», «¿cómo presento un reclamo?».

## Caso 2 · Aprobación de créditos

Un asistente que ayuda al **analista de créditos** a evaluar las solicitudes del Marketplace antes de
publicarlas a los inversionistas.

- Lee la solicitud (ingresos, deudas, antigüedad laboral, monto y plazo) y la compara con la
  **Política de Créditos**: cuota máxima = 30 % del ingreso neto, antigüedad laboral mínima de 6
  meses, montos de S/ 1,000 a S/ 50,000, plazo de 6 a 60 meses.
- Devuelve una **recomendación** (aprobar, rechazar o revisar) con los motivos y la página de la
  política que aplica: «Política de Créditos, p. 7».
- El flujo lo hacen **agentes con roles distintos**, en este orden:
  1. **Agente de consulta**: reúne la información de la solicitud sin modificar nada: datos del cliente,
     ingresos, deudas vigentes, historial de pagos en el banco y reporte de la central de riesgo.
  2. **Tres agentes de evaluación** (abajo) debaten y emiten la recomendación.
  3. **El analista humano** revisa y decide.
  4. **Agente de registro**: anota en el sistema del banco la solicitud, la recomendación, la decisión
     del analista y sus motivos, con fecha y responsable (trazabilidad para auditoría). Es el único
     agente que escribe, y solo después de la decisión humana.
- La recomendación sale de **tres agentes que debaten**, no de uno solo:
  - **Analista flexible**: busca cómo la solicitud *sí* puede cumplir la política (p. ej. un plazo más
    largo que baja la cuota por debajo del 30 %).
  - **Analista estricto**: busca todo motivo de rechazo o de revisión (antigüedad justa, deudas no
    declaradas, monto sobre S/ 20,000).
  - **Juez**: lee los dos argumentos con sus citas de la Política de Créditos, les pide una ronda más
    si discrepan y se detiene cuando las posiciones ya no cambian; entonces emite la recomendación
    final con los motivos de ambos lados.
  Por qué así y no un voto por mayoría: un voto suma respuestas sin mirar los argumentos y puede
  fallar aunque un agente tuviera razón; el debate obliga a justificar con la política y hace visible
  el desacuerdo (idea tomada de los trabajos sobre *multi-agent debate* como juez).
- **La decisión final es siempre del analista.** Por encima de S/ 20,000 la aprueba además el jefe de
  créditos.
- Los datos del cliente (DNI, ingresos, deudas) no se escriben en logs ni en prompts de prueba.

Ejemplo: «Solicitud S-1042: ingreso neto S/ 3,500, deudas S/ 400 al mes, 2 años en su empleo, pide
S/ 15,000 a 36 meses» → cuota S/ 513, carga total S/ 913 = 26 % del ingreso → **aprobar**,
dentro del límite del 30 % (Política de Créditos, p. 7). El flexible y el estricto coinciden, así que el
juez cierra en una ronda. Si sus deudas fueran S/ 600 al mes, la carga subiría a S/ 1,113 = 32 %: el estricto pediría
rechazar, el flexible propondría 60 meses (cuota S/ 349, carga S/ 949 = 27 %) y el juez recomendaría
**revisar** con esa contrapropuesta. (Cuotas calculadas con una TEA ilustrativa de 15 %.)

## Solo en el curso Agentic AI Enterprise Architect: firma digital y desembolso simulado en bitcoin

Cuando el analista aprueba, el cliente **firma digitalmente el contrato del préstamo** antes del
desembolso. El Marketplace se integra con un **proveedor de firma digital** acreditado: envía el
contrato, el cliente firma con OTP o biometría en la app, el proveedor devuelve el documento firmado y
recién entonces se libera el dinero. Sirve para los temas de integración de ese curso: API del
proveedor, reintentos, webhooks de «firmado», estados pendientes y la regla de nunca desembolsar sin
contrato firmado.

Además, el inversionista puede elegir recibir sus pagos o el cliente su desembolso **en bitcoin, en
modo simulado**: una integración con una **billetera de prueba (testnet / sandbox)**, sin dinero real.
Sirve para practicar patrones de integración con un sistema externo lento e incierto: cotización
BTC/soles con vencimiento, confirmaciones que tardan, idempotencia para no enviar dos veces, límites de
monto y aprobación humana antes de cada envío. En los cursos siempre se dice que es una simulación.

## Los documentos (ficticios, creados para el curso)

| Documento | Cita | Para qué caso |
|-----------|------|---------------|
| Reglamento de Productos y Tarifario | «Tarifario, p. N» | Respuesta a clientes |
| Política de Créditos de Consumo | «Política de Créditos, p. N» | Aprobación de créditos |

## La escena que abre el curso de Claude Code

La tech lead escribe en Claude Code una sola línea: «haz que el asistente de créditos apruebe solo las
solicitudes que cumplan la política». Se va a una reunión. Al volver: 14 archivos cambiados y el
mensaje «Listo, todos los tests pasan». Lo que no se ve: el asistente ahora **aprueba** directamente,
sin pasar por el analista; guarda el DNI y los ingresos en los logs; y el test «pasa» porque compara
la salida consigo misma. Nadie decidió eso. Nadie lo revisó. El curso enseña a evitarlo.

## Nombres que cambian respecto de los cursos originales

| Antes | Ahora |
|-------|-------|
| Tutor de proyectos por WhatsApp · Grupo Vitalis · Andes Retail · Andina Salud | el Marketplace de Créditos del banco y sus dos asistentes |
| alumnos · pacientes · clientes de retail | solicitantes, inversionistas y analistas de créditos |
| PMBOK, Guía Scrum, manuales de salud o retail | Reglamento de Productos y Tarifario · Política de Créditos |

Se mantiene Scrum como forma de trabajo del equipo, pero **no existe «Sprint 0»**.
