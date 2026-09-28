import anthropic
from tutor_corpus import corpus_completo   # la Guía Scrum 2020 entera (16 páginas): el prefijo estable

client = anthropic.Anthropic()

def preguntar(pregunta):
    r = client.messages.create(
        model="claude-sonnet-5", max_tokens=600,
        system=[
            {"type": "text", "text": "Eres el Tutor. Responde solo con el documento y cita la página."},
            {"type": "text", "text": corpus_completo(),
             "cache_control": {"type": "ephemeral"}},     # breakpoint: último bloque que NO cambia
        ],
        messages=[{"role": "user", "content": pregunta}],  # lo único que cambia entre llamadas
    )
    u = r.usage
    print(f"escritos en caché: {u.cache_creation_input_tokens:>6} | leídos de caché: {u.cache_read_input_tokens:>6} "
          f"| entrada normal: {u.input_tokens:>4}")
    return r.content[0].text

preguntar("¿Quién es responsable de maximizar el valor del producto?")   # 1ª: escribe la caché (1,25×)
preguntar("¿Cuánto dura el Sprint como máximo?")                        # 2ª: lee la caché (0,1×)
