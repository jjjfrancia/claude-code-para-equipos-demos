# Que decida Claude, por la descripción
> usa el revisor sobre el diff contra specs/SPEC-documento-propio.md

# Garantizarlo, nombrando el subagente
> @"revisor (agent)" revisa git diff contra specs/SPEC-documento-propio.md

# Encadenarlos
> Usa el revisor sobre el diff. Después el auditor sobre la DoD.
  Júntame los dos informes y dime si abro el PR o no.

# Toda la sesión con ese rol
claude --agent revisor

# Ver lo que corre y lo que terminó
/tasks
