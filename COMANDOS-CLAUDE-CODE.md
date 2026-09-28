# Inventario de comandos de Claude Code

Referencia usada para que los cursos cubran todos los comandos. Fuente: documentación oficial
(code.claude.com/docs/en/commands.md, interactive-mode.md, cli-reference.md, skills.md,
plugins/cli-reference.md), consultada el 28 de septiembre de 2026. Algunos comandos dependen del
plan, de la plataforma o de la versión; `/help` dentro de una sesión muestra los disponibles.

## Ruta del curso «Claude Code para Equipos»: dónde se introduce cada comando

Cada comando se presenta una sola vez, en el capítulo donde el equipo del Marketplace lo necesita por
primera vez, con: para qué sirve, cuándo usarlo, qué escribes, qué ves y una práctica de un minuto.
Después se reutiliza sin volver a explicarlo. El capítulo 14 cierra con la tabla completa.

| Cap | Tema | Comandos, atajos y flags que se introducen |
|-----|------|---------------------------------------------|
| 1 | Primera sesión | `claude`, `claude "pregunta"`, `/help`, `?` (panel de atajos), `/model` (Opus / Sonnet / Haiku: calidad, latencia, costo), `Option+P`/`Alt+P`, `/effort`, `/fast`, `Esc` (detener), corrección a mitad de turno, `Esc Esc`, `/rewind`, `/clear`, `Ctrl+C`, `Ctrl+D`, entrada multilínea (`\`+`Enter`, `Shift+Enter`, `Ctrl+J`), `↑`/`↓` historial, `Ctrl+R`, `/status`, `/login`, `/logout`, `/upgrade`, `claude update`, `claude auth login\|status\|logout` |
| 2 | El bucle y el contexto | `/context`, `/usage` (alias `/cost`), `Ctrl+O` visor de transcripción (`{` `}` `[` `v` `q`), `Ctrl+T` lista de tareas, `Option+T`/`Alt+T` pensamiento extendido, `/advisor`, `/btw`, `/copy`, `/export` |
| 3 | La spec | `Shift+Tab` (ciclar modos), `/plan`, `claude --permission-mode plan`, `Ctrl+G` (redactar la spec en tu editor) |
| 4 | Fundamentos | `/init`, `@archivo`, `!` modo shell, `Ctrl+B` (bash en segundo plano), `/add-dir`, `--add-dir`, `/cd`, `/diff`, `/ide`, `/terminal-setup`, `/permissions`, `Ctrl+V` pegar imagen, `Tab` autocompletar, `/keybindings`, edición (`Ctrl+A/E/K/U/W/Y`, `Alt+B/F/D`, `Ctrl+_`) |
| 5 | CLAUDE.md | `/memory`, `/import` (traer configuración de otras herramientas) |
| 6 | Comandos, skills, plugins | comandos propios en `.claude/commands/`, skills (`/nombre`, `$ARGUMENTS`, apilar skills), `/skills`, `/skill-doctor`, `/plugin` (`list`, `install`, `manage`, `enable`, `disable`, `configure`, `validate`, `marketplace`), `/reload-plugins`, `claude plugin install\|list\|update\|uninstall\|details\|validate\|init\|tag\|prune\|marketplace add\|list\|update\|remove`, `claude plugin eval`, `/simplify`, `/claude-api`, `/recipe`, `/powerup`, `/insights` |
| 7 | Hooks | `/hooks`, `/goal` (condición de parada), `/session-start-hook`, `--init`, `--init-only`, `--maintenance`, `--include-hook-events` |
| 8 | Subagentes | `/agents`, `/subtask`, `/tasks`, `/list-agents`, `--agent`, `--agents`, `--append-subagent-system-prompt`, `Ctrl+X Ctrl+K` (detener subagentes en segundo plano) |
| 9 | Harness y sesiones | `/compact`, `/autocompact`, `--autocompact`, `/resume`, `claude -c`/`--continue`, `claude -r`/`--resume <nombre>`, `-n`/`--name`, `/branch`, `/fork`, `--fork-session`, `/background` (`/bg`), `--bg`, `claude agents\|attach\|logs\|stop\|respawn\|rm`, `claude daemon status\|stop`, `/loop`, `--worktree`, `--no-session-persistence`, `Ctrl+S`, `Ctrl+Z` |
| 10 | Multi-agentes | `/batch`, `claude --cloud`, `/teleport`, `/web-setup`, `/remote-control` (`--remote-control`), `/desktop`, `Ctrl+X Ctrl+S` (enviar mensajes en cola) |
| 11 | MCP | `/mcp`, `claude mcp add\|list\|remove\|login\|logout`, `--scope project` (`.mcp.json`), `--mcp-config`, prompts MCP como `/mcp__servidor__prompt`, `--channels`, `/chrome`, `--chrome` |
| 12 | RAG | `/deep-research`, `/dataviz` |
| 13 | Permisos, seguridad y CI | modos `default`/`acceptEdits`/`plan`/`auto`/`dontAsk`/`bypassPermissions`, `--allowed-tools`, `--disallowed-tools`, `--dangerously-skip-permissions` (y por qué no en el banco), `/sandbox`, `/fewer-permission-prompts`, `claude -p`, `--output-format text\|json\|stream-json`, `--json-schema`, `--input-format`, `--max-turns`, `--max-budget-usd`, `--system-prompt`, `--append-system-prompt(-file)`, `--settings`, `--bare`, `--verbose`, `/code-review` (`/review`), `/security-review`, `claude ultrareview`, `/install-github-app`, `claude setup-token`, `claude auto-mode defaults\|reset` |
| 14 | Adopción en el equipo | `/config` (`/settings`), `/theme`, `/color`, `/tui`, `/focus`, `/doctor`, `claude doctor`, `/debug`, `--debug`, `/feedback`, `/bug`, `/install-slack-app`, `/design`, `/slides`, `claude project purge`, dictado por voz, y la tabla resumen de todos los comandos del curso |

Fuera del temario por ser muy específicos (se mencionan en la tabla final): `/design-sync`,
`/design-login`, `/heapdump`, `claude gateway`, `--betas`, `--exec`, atajos de Claude Code Desktop y
de la extensión de VS Code.
