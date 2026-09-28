# macOS / Linux
curl -fsSL https://claude.ai/install.sh | bash
# Windows (PowerShell)
irm https://claude.ai/install.ps1 | iex
# o con npm
npm install -g @anthropic-ai/claude-code

cd demos/caso
claude --permission-mode plan
