# Caso transversal de los cuatro cursos: agentes de IA en la banca

Ficha única. Los cuatro cursos usan este caso: el banco pasa de la automatización rígida (menús, reglas
fijas) a **tres agentes de IA** que atienden operaciones críticas. Un equipo pequeño (una tech lead y dos
developers) los construye con Claude; cada cambio pasa por Riesgos, Cumplimiento, Seguridad de la
Información y Legal. No existe «Sprint 0».

| Pilar | Agente | Qué hace | Métrica objetivo | Escenario del examen CCAR-F |
|-------|--------|----------|------------------|------------------------------|
| 1 · Atención y consultas | Agente front-office | Responde en lenguaje natural («¿por qué retuvieron mi transferencia?»), consulta el core bancario de forma segura y recuerda el contexto del cliente | +40 % de resolución en el primer contacto (FCR) | 1 · Customer Support Resolution Agent |
| 2 · Gestión de reclamos | Agente operativo | Clasifica el reclamo, revisa el historial de transacciones buscando anomalías, aprueba compensaciones pequeñas dentro de la política y escala lo complejo con un expediente | Tiempo de resolución de 5 días a 10 minutos | 1 y 6 · Extracción estructurada |
| 3 · Evaluación de crédito | Agente de riesgo | Lee extractos, declaraciones y la solicitud; simula la capacidad de pago con escenarios de estrés; emite un dictamen con motivos | −15 % de morosidad (NPL) | 3 · Multi-Agent Research System |

### Lo que los cursos enseñan a corregir de este diseño (y que pregunta el examen)

- **Compensación automática «si es menor a S/ 50 y el cliente es VIP»**: una regla de dinero no se
  confía al prompt; se hace cumplir con un **hook o prerrequisito programático** que bloquea montos
  sobre el umbral y deriva a un humano (task 1.4 / 1.5).
- **Escalar por sentimiento (enojo/urgencia)**: el examen lo marca como mal indicador; se escala cuando
  el cliente pide un humano, cuando la política no cubre el caso o cuando no hay avance (task 5.2).
- **«Recuerda interacciones pasadas»**: guardar solo los hechos del caso (montos, fechas, números de
  operación), nunca datos sensibles completos (task 5.1).
- **El dictamen de crédito lo decide un humano**: el agente recomienda con motivos; el analista decide.

## Detalle del pilar 1 · Atención y consultas

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

## Detalle del pilar 3 · Evaluación de crédito

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


### El triángulo de decisión del pilar 3 (arquitectura de debate con juez)

1. **Extractor de datos**: arma un perfil estructurado de la solicitud y envía **el mismo perfil** a
   los dos agentes.
2. **Agente relajado (comercial)**, «el optimista contratado»: busca el cómo *sí*; valora el potencial
   futuro y las justificaciones del cliente («ingresos crecientes», «industria estable»).
3. **Agente estricto (riesgo)**, «el guardián del capital»: busca el cómo *no*; no perdona
   inconsistencias ni falta de garantías («historial muy corto», «deuda externa alta»).
4. **Agente juez (moderador)**, «el árbitro pragmático»: pesa la solidez de ambos argumentos frente al
   **contrato de política bancaria** (las reglas inquebrantables) y dicta sentencia:
   - **Decisión autónoma** (aprobado o rechazado) solo en casos claros y dentro de los límites que la
     política permite automatizar (p. ej. hasta S/ 20,000). Genera una **bitácora de justificación**.
   - **Escalación humana** en casos grises o ambiguos: el analista lee el debate y decide rápido.
   Las reglas inquebrantables (cuota ≤ 30 %, montos, aprobación del jefe sobre S/ 20,000) se hacen
   cumplir en código, no solo en el prompt del juez.

## Detalle del pilar 2 · Gestión de reclamos

1. **Clasificación**: lee el correo o chat del reclamo y lo clasifica (cargo no reconocido,
   transferencia retenida, comisión indebida, fraude).
2. **Investigación**: un agente de consulta revisa el historial de transacciones buscando anomalías.
3. **Ejecución**: si el monto es menor a S/ 50 y la política lo permite, propone la devolución y un
   hook verifica el umbral antes de ejecutarla; si es complejo o es posible fraude, arma el expediente
   (cliente, operación, monto, causa probable, acción recomendada) y lo escala a un analista humano.

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
