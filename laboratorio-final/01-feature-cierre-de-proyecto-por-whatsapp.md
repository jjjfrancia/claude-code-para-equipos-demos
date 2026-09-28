# Feature: cierre de proyecto por WhatsApp

## Contexto
El tutor recibe el comando /cerrar <proyecto>.

## Restricciones
- No cerrar proyectos con entregables pendientes.
- No exponer datos de otros equipos.
- Toda transición se registra con actor y timestamp.

## Criterios de aceptación
- [ ] Usuario autorizado + proyecto completo → 200 y estado CLOSED.
- [ ] Entregable pendiente → 409, sin modificación.
- [ ] Usuario de otro equipo → 404, sin revelar existencia.
- [ ] Tests unitarios, integración y autorización pasan.
- [ ] Migración reversible y log de auditoría verificado.
