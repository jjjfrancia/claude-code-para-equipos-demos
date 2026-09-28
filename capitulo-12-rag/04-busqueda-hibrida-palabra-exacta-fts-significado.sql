-- Búsqueda híbrida: palabra exacta (FTS) + significado (coseno), fundidos con RRF.
-- El embedding es all-MiniLM-L6-v2 (384 dimensiones) y el índice, HNSW sobre pgvector.
WITH fts AS (
  SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank_cd(tsv, plainto_tsquery('simple', %s)) DESC) AS pos
  FROM chunks
  WHERE documento_id = ANY(%s) AND tsv @@ plainto_tsquery('simple', %s)
  LIMIT 50
),
vec AS (
  SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> %s::vector) AS pos
  FROM chunks
  WHERE documento_id = ANY(%s)
  ORDER BY embedding <=> %s::vector
  LIMIT 50
)
SELECT c.id, c.texto, c.seccion, c.pagina,
       COALESCE(1.0 / (60 + fts.pos), 0) + COALESCE(1.0 / (60 + vec.pos), 0) AS score
FROM chunks c
LEFT JOIN fts ON fts.id = c.id
LEFT JOIN vec ON vec.id = c.id
WHERE fts.id IS NOT NULL OR vec.id IS NOT NULL
ORDER BY score DESC
LIMIT %s;
