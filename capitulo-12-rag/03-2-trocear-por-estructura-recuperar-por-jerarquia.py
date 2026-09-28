# Troceo estructural: la sección manda; el tamaño es un tope, no el criterio
def trocear(arbol, tope=900, solape=120):
    """arbol: nodos con seccion, breadcrumb, pagina y texto (lo produce el extractor)."""
    for nodo in arbol.hojas():
        if len(nodo.texto) <= tope:
            yield Chunk(texto=nodo.texto, seccion=nodo.seccion,
                        breadcrumb=nodo.breadcrumb, pagina=nodo.pagina, padre=nodo.padre_id)
            continue
        # Solo si una hoja no cabe se corta, y se corta por frases, con solape
        for trozo in partir_por_frases(nodo.texto, tope, solape):
            yield Chunk(texto=trozo, seccion=nodo.seccion,
                        breadcrumb=nodo.breadcrumb, pagina=nodo.pagina, padre=nodo.padre_id)

# Jerárquico: se BUSCA en la hoja (precisa) y se ENTREGA el padre (con contexto)
def recuperar_jerarquico(pregunta, k=4):
    hojas = buscar_hibrido(pregunta, k=k)
    vistos, salida = set(), []
    for hoja in hojas:
        padre = cargar(hoja.padre) if hoja.padre else hoja
        if padre.id not in vistos:
            vistos.add(padre.id)
            salida.append(padre)
    return salida
