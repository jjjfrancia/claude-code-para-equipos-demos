# Plan mode: lee y planifica, no edita nada
claude --permission-mode plan
# (o Shift+Tab dentro de la sesión hasta ver «⏸ plan mode on», o /plan delante del prompt)

# Al aprobar el plan, Claude pregunta cómo seguir:
#   Yes, and use auto mode        → sigue sin preguntarte, con el clasificador revisando
#   Yes, manually approve edits   → apruebas edición por edición
#   No, keep planning             → sigues corrigiendo el plan
# Ctrl+G abre el plan en tu editor para cambiarlo ANTES de aprobar

# Después de implementar
/diff                                               # el working tree, incluidas las ediciones de Claude
git diff --stat                                     # cuántos archivos tocó de verdad
/rewind                                             # o Esc Esc: volver atrás código, conversación o ambos
