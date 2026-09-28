# Una comprobación con salida estructurada que un script puede leer
claude -p "/dod" \
  --permission-mode dontAsk \
  --permission-prompts none \
  --allowedTools "Read,Grep,Bash(pytest *),Bash(ruff *)" \
  --max-turns 25 --max-budget-usd 1.50 \
  --output-format json \
  --json-schema '{
    "type": "object",
    "required": ["veredicto", "items", "bloqueantes"],
    "properties": {
      "veredicto":   { "enum": ["LISTO", "NO_LISTO"] },
      "items":       { "type": "array" },
      "bloqueantes": { "type": "array", "items": { "type": "string" } }
    }
  }' | jq -r '.structured_output.veredicto'

# El script decide con el veredicto, no leyendo prosa. Y mira el código de salida:
# claude sale con 0 si la corrida terminó bien, y distinto de 0 si falló.
