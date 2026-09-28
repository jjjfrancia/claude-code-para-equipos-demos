from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob"],
    permission_mode="plan",
    max_turns=8,
)

async for event in query(
    prompt="Revisa la spec y devuelve impactos, riesgos y archivos. No edites.",
    options=options,
):
    print(event)
