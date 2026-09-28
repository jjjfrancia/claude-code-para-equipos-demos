# Claude Code para equipos · demos

Todas las demos del curso **Claude Code para equipos** (Cortex Governor Academy), ordenadas por
capítulo. Cada carpeta tiene su `README.md` con la lista de demos en el orden en que aparecen en el
curso. Todo gira sobre el mismo caso: un **Tutor de proyectos por WhatsApp** que responde sobre la
Guía de Scrum 2020 citando la página.

| Capítulo | Carpeta | Demos |
|----------|---------|-------|
| 1 · Vibe Coding | [`capitulo-01-vibe-coding/`](capitulo-01-vibe-coding/) | 3 |
| 2 · Teoría de agentes (según Anthropic) | [`capitulo-02-teoria-de-agentes/`](capitulo-02-teoria-de-agentes/) | 11 ejecutables + 3 |
| 3 · Spec Driven Development | [`capitulo-03-spec-driven-development/`](capitulo-03-spec-driven-development/) | 1 |
| 4 · Fundamentos de Claude Code | [`capitulo-04-fundamentos-de-claude-code/`](capitulo-04-fundamentos-de-claude-code/) | 2 |
| 5 · CLAUDE.md, la memoria de proyecto | [`capitulo-05-claude-md/`](capitulo-05-claude-md/) | 5 |
| 6 · Comandos, skills y plugins | [`capitulo-06-comandos-de-claude-code/`](capitulo-06-comandos-de-claude-code/) | 5 |
| 7 · Hooks | [`capitulo-07-hooks/`](capitulo-07-hooks/) | 6 |
| 8 · Creación de agentes (subagentes) | [`capitulo-08-creacion-de-agentes/`](capitulo-08-creacion-de-agentes/) | 4 |
| 9 · Agent Harness | [`capitulo-09-agent-harness/`](capitulo-09-agent-harness/) | 5 |
| 10 · Multi-agentes y Orquestador | [`capitulo-10-multi-agentes-y-orquestador/`](capitulo-10-multi-agentes-y-orquestador/) | 3 |
| 11 · MCP | [`capitulo-11-mcp/`](capitulo-11-mcp/) | 6 |
| 12 · RAG | [`capitulo-12-rag/`](capitulo-12-rag/) | 4 |
| 13 · Permisos, Seguridad, Inspección y DoD | [`capitulo-13-permisos-seguridad-inspeccion-y-dod/`](capitulo-13-permisos-seguridad-inspeccion-y-dod/) | 4 |
| 14 · Adopción en el equipo y Proyecto Final | [`capitulo-14-adopcion-en-el-equipo-y-proyecto-final/`](capitulo-14-adopcion-en-el-equipo-y-proyecto-final/) | 2 |
| Laboratorio final | [`laboratorio-final/`](laboratorio-final/) | 5 |

## Las 11 demos ejecutables (capítulo 2)

Están en [`capitulo-02-teoria-de-agentes/teoria/`](capitulo-02-teoria-de-agentes/teoria/) y su guía
en [`capitulo-02-teoria-de-agentes/index.html`](capitulo-02-teoria-de-agentes/index.html): patrones
de *Building effective agents* y del Claude Agent SDK. `tutor_corpus.py` es el módulo común: lee el
PDF con pdfplumber, lo parte en fragmentos con su página y expone `buscar` / `formatear`.

```bash
pip install -r requirements.txt

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."
# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."

cd capitulo-02-teoria-de-agentes/teoria
python 01_llm_aumentado.py "¿Quién es responsable de maximizar el valor del producto?"
```

Cada archivo dice en su docstring qué requiere y con qué comando se corre. Las demos 07, 09, 10 y
11 usan el Claude Agent SDK; el resto, solo el SDK `anthropic`.

## El resto de las demos

Son los fragmentos que el curso muestra en cada capítulo, tal cual aparecen: el `CLAUDE.md` del
Tutor, la spec, los skills, los hooks (`.py` y `settings.json`), los subagentes (`.md` con
frontmatter), el servidor MCP, el troceo y la búsqueda híbrida del RAG, la política de permisos y el
workflow de CI. Los de tipo configuración van con la extensión del formato en que se usan.

## Licencia

El código es MIT (ver `LICENSE`). La Guía de Scrum 2020 incluida en `capitulo-02-teoria-de-agentes/teoria/datos/`
es de Ken Schwaber y Jeff Sutherland, descargada de scrumguides.org, bajo Creative Commons BY-SA 4.0.
