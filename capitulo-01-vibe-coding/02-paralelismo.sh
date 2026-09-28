# Fan-out: la guía de Anthropic, sobre el Tutor
# 1) Claude genera la lista:  "lista los PDF sin trocear y guárdala en pendientes.txt"
# 2) Un script recorre la lista, una invocación por archivo, con permisos acotados
for pdf in $(cat pendientes.txt); do
  claude -p "Trocea $pdf con rag/05_chunking_jerarquico.py y verifica que paper_nodes tiene filas. Devuelve OK o FAIL." \
    --allowedTools "Bash(python rag/*),Bash(psql *)"
done
# 3) Se prueba con 2 o 3 archivos, se ajusta el prompt con lo que salió mal, y recién entonces con todos
