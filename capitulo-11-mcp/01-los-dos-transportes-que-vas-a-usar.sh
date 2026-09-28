# stdio — el servidor corre como proceso local. Para código propio y herramientas del sistema
claude mcp add --transport stdio documentos -- python mcp/servidor_documentos.py

# http — el servidor es remoto. Es el recomendado para servicios en la nube
claude mcp add --transport http notion https://mcp.notion.com/mcp
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer $GITHUB_PAT"

# Gestión
claude mcp list          # estado de cada uno: conectado, necesita autenticación, falló
claude mcp get github    # el detalle de uno
claude mcp remove github # al quitarlo se borran también sus credenciales OAuth
/mcp                     # dentro de la sesión: estado, autenticar, activar o desactivar
