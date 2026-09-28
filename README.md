# Claude Code para equipos · demos

Demostraciones del curso **Claude Code para equipos** (Cortex Governor Academy). Once ejemplos
en Python que recorren, uno por uno, los patrones de *Building effective agents* de Anthropic y
los del Claude Agent SDK, todos sobre el mismo caso: un tutor que responde preguntas sobre la
Guía de Scrum 2020 citando la página.

Abre `index.html` en el navegador para ver la guía de cada demo (qué concepto ilustra, qué
observar en la salida y cómo correrla).

## Las demos

| # | Archivo | Patrón |
|---|---------|--------|
| 01 | `teoria/01_llm_aumentado.py` | El LLM aumentado: una tool de recuperación y el bucle de tool use escrito a mano |
| 02 | `teoria/02_prompt_chaining.py` | Prompt chaining |
| 03 | `teoria/03_routing.py` | Routing |
| 04 | `teoria/04_paralelizacion.py` | Paralelización |
| 05 | `teoria/05_orquestador_workers.py` | Orquestador y workers |
| 06 | `teoria/06_evaluador_optimizador.py` | Evaluador y optimizador |
| 07 | `teoria/07_agente_autonomo.py` | Agente autónomo (Claude Agent SDK) |
| 08 | `teoria/08_prompt_caching.py` | Prompt caching |
| 09 | `teoria/09_guardrails_prompt_injection.py` | Guardrails y prompt injection |
| 10 | `teoria/10_subagentes.py` | Subagentes |
| 11 | `teoria/11_memoria_sesiones.py` | Memoria y sesiones |

`teoria/tutor_corpus.py` es el módulo común: lee el PDF con pdfplumber, lo parte en fragmentos
con su página y expone `buscar` / `formatear` a todas las demos. La primera corrida genera la
caché `teoria/datos/guia_fragmentos.json` (ignorada por git).

## Cómo correrlas

```bash
pip install -r requirements.txt

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."
# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."

cd teoria
python 01_llm_aumentado.py "¿Quién es responsable de maximizar el valor del producto?"
```

Cada archivo dice en su docstring qué requiere y con qué comando se corre. Las demos 07, 09, 10
y 11 usan el Claude Agent SDK (`claude-agent-sdk`), el resto solo el SDK `anthropic`.

## Licencia

El código es MIT (ver `LICENSE`). La Guía de Scrum 2020 incluida en `teoria/datos/` es de Ken
Schwaber y Jeff Sutherland, descargada de scrumguides.org, bajo Creative Commons BY-SA 4.0.
