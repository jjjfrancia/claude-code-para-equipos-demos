# Doble columna: ordenar por bloques visuales, no por el orden del flujo del PDF
bloques = pagina.get_text("blocks")        # (x0, y0, x1, y1, texto, nº, tipo)
mitad = pagina.rect.width / 2

izquierda = sorted([b for b in bloques if b[0] < mitad], key=lambda b: b[1])
derecha   = sorted([b for b in bloques if b[0] >= mitad], key=lambda b: b[1])
texto_pagina = "\n".join(b[4] for b in izquierda + derecha)

# Sin esto, una página a dos columnas se lee en zigzag: primera línea de la izquierda,
# primera de la derecha, segunda de la izquierda... y cada párrafo queda partido.
