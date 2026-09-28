claude --permission-mode plan          # explorar sin tocar nada
claude --model opus                    # decisión de arquitectura
claude --worktree cita-pagina          # sesión aislada en su propio checkout de git
claude --add-dir ../libreria-comun     # acceso a otro directorio
claude -p "…" --output-format json     # no interactivo, para scripts y CI (capítulo 13)
claude --bare -p "…"                   # sin hooks, skills, MCP ni CLAUDE.md: arranque limpio en CI
claude --resume cita-pagina            # retomar una sesión por su nombre
