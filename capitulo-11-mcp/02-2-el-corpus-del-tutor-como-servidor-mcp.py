"""mcp/servidor_documentos.py — el corpus del Tutor como servidor MCP (stdio).

Tres cosas importan en el diseño, y ninguna es del protocolo:
  1. La descripción dice QUÉ devuelve y CUÁNDO usarla. Con eso decide el modelo.
  2. El esquema es tipado y mínimo. Un parámetro de más es un parámetro que se inventa.
  3. «Sin resultados» es un resultado explícito, no una lista vacía que parezca un fallo.
"""
import os

from mcp.server.fastmcp import FastMCP

from tutor.buscar import buscar_hibrido

servidor = FastMCP("documentos")
CORPUS = os.environ.get("CORPUS_DIR", "docs/")


@servidor.tool()
def leer_documento(pregunta: str, k: int = 4) -> str:
    """Busca en el PMBOK 7 y la Guía Scrum 2020 los párrafos que responden a la pregunta.

    Devuelve hasta k párrafos, cada uno con su documento, su página y su score de
    similitud. Úsala SIEMPRE antes de responder cualquier pregunta sobre metodología:
    el Tutor no responde de memoria. Si no hay párrafos por encima del umbral,
    devuelve exactamente SIN_RESULTADOS.
    """
    parrafos = buscar_hibrido(pregunta, k=k, corpus_dir=CORPUS)
    if not parrafos:
        return "SIN_RESULTADOS"
    return "\n\n".join(
        f"[{p.doc} p.{p.pagina} score={p.score:.2f}] {p.texto}" for p in parrafos
    )


@servidor.resource("corpus://catalogo")
def catalogo() -> str:
    """Los documentos cargados, su versión y su fecha de troceo."""
    return open(f"{CORPUS}/catalogo.json").read()


if __name__ == "__main__":
    servidor.run()
