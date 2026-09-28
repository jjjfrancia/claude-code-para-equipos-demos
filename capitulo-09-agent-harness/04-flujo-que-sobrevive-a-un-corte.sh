# El flujo que sobrevive a un corte, un reinicio o un fin de jornada
# 1) El agente lee el estado ANTES de empezar, no la conversación
> Lee estado/troceo_pmbok.json. Trocea SOLO el primer pendiente con
  rag/05_chunking_jerarquico.py, comprueba que la tabla de chunks tiene filas nuevas,
  y actualiza el JSON moviendo ese archivo de pendientes a hechos.
  Si falla, escribe el error en ultimo_error y para. No sigas con el siguiente.

# 2) Se repite hasta vaciar pendientes. Cada vuelta es idempotente:
#    si el archivo ya está en hechos, no se vuelve a trocear.

# 3) Si la sesión se corta, se retoma sin repetir nada:
claude --resume troceo-corpus
# o, sin sesión previa, una sesión nueva leyendo el mismo JSON
