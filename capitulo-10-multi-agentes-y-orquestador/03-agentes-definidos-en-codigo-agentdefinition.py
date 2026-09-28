from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions

# Los mismos revisor y auditor del capítulo 8, ahora definidos en código.
# Ojo: AgentDefinition usa camelCase (maxTurns, permissionMode, disallowedTools);
# ClaudeAgentOptions usa snake_case. Mezclarlos lanza TypeError al construir.
agentes = {
    "revisor": AgentDefinition(
        description="Revisa un diff contra su spec. Úsalo antes de abrir el PR.",
        prompt=open(".claude/agents/revisor.md").read().split("---")[-1],
        tools=["Read", "Grep", "Glob", "Bash(git diff *)"],
        model="sonnet", permissionMode="plan", maxTurns=12,
    ),
    "auditor": AgentDefinition(
        description="Corre la Definition of Done y devuelve el veredicto con evidencia literal.",
        prompt="Ejecutas comprobaciones y transcribes su salida. No opinas y no arreglas nada.",
        tools=["Read", "Bash(pytest *)", "Bash(ruff *)"],
        model="haiku", maxTurns=10,
    ),
}

opciones = ClaudeAgentOptions(
    agents=agentes,
    allowed_tools=["Read", "Edit", "Bash(pytest *)", "Agent"],   # Agent: puede delegar
    setting_sources=["project"],
)
