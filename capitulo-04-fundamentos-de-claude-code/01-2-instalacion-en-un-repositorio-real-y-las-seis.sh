# 1 · Instalar (una vez por máquina)
curl -fsSL https://claude.ai/install.sh | bash      # macOS, Linux, WSL
irm https://claude.ai/install.ps1 | iex             # Windows PowerShell
claude --version                                    # imprime la versión y «(Claude Code)»

# 2 · Entrar al repositorio y arrancar
cd ~/proyectos/tutor-whatsapp
claude                                              # la primera vez pide iniciar sesión

# 3 · Entender antes de tocar
> ¿qué hace este proyecto?
> ¿cómo viaja una pregunta del alumno desde el webhook hasta la respuesta?
> ¿dónde están los tests y con qué comando se corren?

# 4 · Ver qué se cargó de verdad
/context                                            # memoria, tools, MCP, cuánto ocupa cada cosa
/status                                             # versión, modelo, cuenta, conectividad
