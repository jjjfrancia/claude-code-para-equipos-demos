# pdfplumber — el valor por defecto de x_tolerance fusiona palabras separadas
import pdfplumber

with pdfplumber.open("docs/pmbok7.pdf") as pdf:
    for n, pagina in enumerate(pdf.pages, start=1):
        texto = pagina.extract_text(x_tolerance=1)     # 1, no el valor por defecto
        # sin x_tolerance=1: «actadeconstitución» en vez de «acta de constitución»

# PyMuPDF — tablas SOLO cuando hay líneas reales que las delimitan
import fitz

doc = fitz.open("docs/pmbok7.pdf")
for n, pagina in enumerate(doc, start=1):
    tablas = pagina.find_tables(strategy="lines_strict")
    for t in tablas:
        rejilla = t.extract()          # lista de filas; cada celda conserva su posición
        # 'lines_strict' evita las tablas fantasma que 'text' inventa a partir de columnas
        # de texto alineadas. Preferimos 0 tablas a 12 tablas inventadas.
