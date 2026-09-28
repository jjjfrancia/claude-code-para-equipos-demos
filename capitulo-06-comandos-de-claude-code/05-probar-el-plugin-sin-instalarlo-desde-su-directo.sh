# Probar el plugin sin instalarlo, desde su directorio padre
claude --plugin-dir tutor-tooling

# Instalarlo desde un marketplace de la organización
/plugin marketplace add mi-org/claude-plugins
/plugin install tutor-tooling@mi-org

# Ver lo que hay, recargar tras un cambio
/plugin list
/reload-plugins
