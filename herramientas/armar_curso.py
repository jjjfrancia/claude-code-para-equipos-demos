"""Arma un curso completo (index.html con portada + simulador-examen.html) desde sus trozos por capítulo.

Uso:  python herramientas/armar_curso.py <curso> <carpeta_de_trozos> [--estricto]
      <curso> es una clave de herramientas/cursos.json (claude-code, arquitecto, prompts, gobierno).
      <carpeta_de_trozos> contiene 00-cabecera.html, cap/capNN.html, 99-final.html y preguntas/capNN.json.

Qué hace:
- concatena cabecera + capítulos + final;
- agrega la portada (lp-0) con el logo del curso, el examen al que prepara, el caso y el índice;
- reconstruye la lista de pestañas (TABS) desde los botones reales de cada capítulo;
- apunta los botones de examen al simulador (#capN) y habilita index.html#seccion desde el simulador;
- copia el banco de preguntas a <carpeta>/banco-preguntas/ y genera <carpeta>/simulador-examen.html.
"""
import glob
import html as H
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURSOS = json.load(open(os.path.join(RAIZ, 'herramientas', 'cursos.json'), encoding='utf-8'))
EXAMENES = json.load(open(os.path.join(RAIZ, 'herramientas', 'examenes.json'), encoding='utf-8'))

ICONOS = {  # trazos blancos dentro del logo, en una caja de 48x48
    'terminal': '<path d="M10 16l8 8-8 8" /><path d="M22 34h16" />',
    'nodos': '<circle cx="24" cy="12" r="5"/><circle cx="11" cy="35" r="5"/><circle cx="37" cy="35" r="5"/><path d="M21 16l-7 14M27 16l7 14M16 35h16"/>',
    'llaves': '<path d="M17 10c-4 0-5 3-5 6v4c0 2-2 4-4 4 2 0 4 2 4 4v4c0 3 1 6 5 6"/><path d="M31 10c4 0 5 3 5 6v4c0 2 2 4 4 4-2 0-4 2-4 4v4c0 3-1 6-5 6"/>',
    'escudo': '<path d="M24 6l14 5v11c0 9-6 16-14 20-8-4-14-11-14-20V11z"/><path d="M17 24l5 5 9-10"/>',
}


def logo(curso: dict, tam: int) -> str:
    c1, c2 = curso['color']
    gid = 'lg-' + curso['sigla']
    return (f'<svg class="portada-logo" width="{tam}" height="{tam}" viewBox="0 0 120 120" role="img" '
            f'aria-label="Logo {H.escape(curso["titulo"])}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/>'
            f'<stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
            f'<rect x="4" y="4" width="112" height="112" rx="28" fill="url(#{gid})"/>'
            f'<g transform="translate(36 16)" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONOS[curso["icono"]]}</g>'
            f'<text x="60" y="97" text-anchor="middle" fill="#fff" font-family="Inter,system-ui,sans-serif" '
            f'font-size="{22 if len(curso["sigla"]) <= 3 else 19}" font-weight="900" letter-spacing="1">{H.escape(curso["sigla"])}</text></svg>')


FLUJO_CASO = '''<div class="diagram-wrap zoom-trigger" onclick="openZoom('portadaFlujo','El Marketplace de Créditos: los dos asistentes')" title="Clic para ampliar"><svg id="portadaFlujo" viewBox="0 0 920 300" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block;background:#fff;border-radius:10px;font-family:'Inter',system-ui,sans-serif">
<defs><marker id="pfA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#64748b"/></marker></defs>
<text x="20" y="30" font-size="15" font-weight="800" fill="#1e3a8a">Caso 1 · Respuesta a clientes</text>
<g font-size="13">
<rect x="20" y="44" width="190" height="62" rx="12" fill="#eff6ff" stroke="#2563eb"/><text x="115" y="70" text-anchor="middle" font-weight="800" fill="#1e3a8a">Cliente pregunta</text><text x="115" y="90" text-anchor="middle" fill="#334155">en la app</text>
<rect x="250" y="44" width="200" height="62" rx="12" fill="#ecfeff" stroke="#0891b2"/><text x="350" y="70" text-anchor="middle" font-weight="800" fill="#155e75">Busca en el Tarifario</text><text x="350" y="90" text-anchor="middle" fill="#334155">y el Reglamento</text>
<rect x="490" y="44" width="200" height="62" rx="12" fill="#d1fae5" stroke="#059669"/><text x="590" y="70" text-anchor="middle" font-weight="800" fill="#065f46">Responde y cita</text><text x="590" y="90" text-anchor="middle" fill="#334155">«Tarifario, p. 4»</text>
<rect x="730" y="44" width="170" height="62" rx="12" fill="#f1f5f9" stroke="#64748b"/><text x="815" y="70" text-anchor="middle" font-weight="800" fill="#0f172a">Si no sabe</text><text x="815" y="90" text-anchor="middle" fill="#334155">deriva a un ejecutivo</text>
</g>
<g stroke="#64748b" stroke-width="2" marker-end="url(#pfA)"><path d="M210 75h38"/><path d="M450 75h38"/><path d="M690 75h38"/></g>
<text x="20" y="150" font-size="15" font-weight="800" fill="#065f46">Caso 2 · Aprobación de créditos</text>
<g font-size="12.5">
<rect x="20" y="164" width="120" height="70" rx="12" fill="#eff6ff" stroke="#2563eb"/><text x="80" y="194" text-anchor="middle" font-weight="800" fill="#1e3a8a">Solicitud</text><text x="80" y="213" text-anchor="middle" fill="#334155">S/ 15,000</text>
<rect x="165" y="164" width="130" height="70" rx="12" fill="#ecfeff" stroke="#0891b2"/><text x="230" y="190" text-anchor="middle" font-weight="800" fill="#155e75">Agente de</text><text x="230" y="207" text-anchor="middle" font-weight="800" fill="#155e75">consulta</text><text x="230" y="224" text-anchor="middle" fill="#334155">deudas, historial</text>
<rect x="320" y="160" width="130" height="34" rx="10" fill="#d1fae5" stroke="#059669"/><text x="385" y="182" text-anchor="middle" font-weight="700" fill="#065f46">Flexible</text>
<rect x="320" y="204" width="130" height="34" rx="10" fill="#fee2e2" stroke="#dc2626"/><text x="385" y="226" text-anchor="middle" font-weight="700" fill="#991b1b">Estricto</text>
<rect x="475" y="164" width="110" height="70" rx="12" fill="#fef3c7" stroke="#d97706"/><text x="530" y="194" text-anchor="middle" font-weight="800" fill="#92400e">Juez</text><text x="530" y="213" text-anchor="middle" fill="#334155">recomienda</text>
<rect x="610" y="164" width="140" height="70" rx="12" fill="#0f172a"/><text x="680" y="194" text-anchor="middle" font-weight="800" fill="#fff">Analista</text><text x="680" y="213" text-anchor="middle" fill="#cbd5e1">decide</text>
<rect x="775" y="164" width="125" height="70" rx="12" fill="#f1f5f9" stroke="#64748b"/><text x="837" y="190" text-anchor="middle" font-weight="800" fill="#0f172a">Agente de</text><text x="837" y="207" text-anchor="middle" font-weight="800" fill="#0f172a">registro</text><text x="837" y="224" text-anchor="middle" fill="#334155">sistema + auditoría</text>
</g>
<g stroke="#64748b" stroke-width="2" marker-end="url(#pfA)"><path d="M140 199h23"/><path d="M295 190l23-10"/><path d="M295 208l23 12"/><path d="M450 177l23 12"/><path d="M450 221l23-12"/><path d="M585 199h23"/><path d="M750 199h23"/></g>
<text x="20" y="270" font-size="13" fill="#334155">Regla de la Política de Créditos: la cuota no supera el 30 % del ingreso neto (p. 7). Sobre S/ 20,000 aprueba también el jefe de créditos.</text>
<text x="20" y="290" font-size="13" fill="#991b1b" font-weight="700">Consultar y recomendar lo hacen agentes; decidir, el analista; registrar, un agente solo después de la decisión.</text>
</svg></div>'''

CSS_PORTADA = '''
/* ── Portada ── */
.topbar-title{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
@media (max-width:1180px){.topbar-title{display:none}}
.topbar .course-badge{display:none}
[class*="extra-links"]{flex-wrap:nowrap!important;overflow-x:auto;min-width:0;scrollbar-width:thin;align-items:center}
@media (max-width:1500px){[class*="extra-links"] a:not(.cc-exam-link){display:none!important}}
#li-0{color:#e2e8f0;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:9px 12px;cursor:pointer}
#li-0.active{background:#2563eb;border-color:#2563eb;color:#fff}
.portada{max-width:1080px;margin:0 auto;padding:36px 32px 60px}
.portada-hero{display:grid;grid-template-columns:auto minmax(0,1fr);gap:28px;align-items:center;background:#fff;border:1px solid var(--border);border-radius:18px;padding:32px;box-shadow:var(--shadow-md)}
.portada-eyebrow{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--blue2)}
.portada-hero h1{font-size:34px;line-height:1.15;margin:6px 0 10px;color:var(--navy);text-wrap:balance}
.portada-hero p{font-size:16px;color:var(--text2);line-height:1.6;margin:0 0 16px;max-width:62ch}
.portada-cta{display:flex;flex-wrap:wrap;gap:10px}
.portada-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;margin-top:18px}
.portada-card{background:#fff;border:1px solid var(--border);border-radius:14px;padding:20px}
.portada-card h2{font-size:15px;margin:0 0 12px;color:var(--navy);text-transform:uppercase;letter-spacing:.06em}
.portada-exam{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.portada-exam span{font-size:12px;font-weight:700;background:#f1f5f9;border:1px solid var(--border);border-radius:999px;padding:3px 10px;color:var(--text2)}
.portada-dom{display:grid;grid-template-columns:minmax(0,1fr) 44px;gap:3px 10px;font-size:13px;margin-bottom:7px;color:var(--text)}
.portada-dom b{font-variant-numeric:tabular-nums;text-align:right}
.portada-dom i{grid-column:1/-1;height:6px;border-radius:9px;background:#e2e8f0;overflow:hidden}
.portada-dom i s{display:block;height:100%}
.portada-caps{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.portada-caps a{display:grid;grid-template-columns:34px minmax(0,1fr);gap:10px;align-items:center;padding:8px 10px;border-radius:10px;border:1px solid var(--border);text-decoration:none;color:var(--text);font-size:14px;cursor:pointer}
.portada-caps a:hover{background:var(--blue-light);border-color:var(--blue-border)}
.portada-caps em{font-style:normal;display:grid;place-items:center;width:30px;height:30px;border-radius:8px;background:var(--navy);color:#fff;font-weight:800;font-size:13px}
@media (max-width:720px){.portada{padding:18px 16px 40px}.portada-hero{grid-template-columns:1fr;padding:22px}.portada-hero h1{font-size:26px}}
'''



def introduccion_banca() -> str:
    """Las infografías de material-de-clase como introducción del curso, con el CSS acotado a .ib."""
    ruta = os.path.join(RAIZ, 'material-de-clase', 'infografias-agentes-banca.html')
    if not os.path.exists(ruta):
        return ''
    doc = open(ruta, encoding='utf-8').read()
    css = re.search(r'<style>(.*?)</style>', doc, re.S).group(1)
    cuerpo = doc[doc.index('<div class="wrap">'):doc.index('<section class="poster" aria-labelledby="i3">')] + '</div>'
    js = re.search(r'<script>(.*?)</script>', doc[doc.rindex('<script>'):], re.S).group(1)
    css = re.sub(r'@media \(prefers-color-scheme: dark\)\{.*?\}\}', '', css, flags=re.S)
    css = re.sub(r':root\[data-theme="dark"\][^{]*\{[^}]*\}', '', css)
    fuera = []
    for sel, dec in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        sel = sel.strip()
        if not sel or sel.startswith('@'):
            continue
        if sel in (':root', 'body'):
            fuera.append('.ib{' + dec + '}')
            continue
        partes = []
        for x in sel.split(','):
            x = x.strip()
            if x.startswith(':root'):
                x = x.replace(':root', '').strip()
            partes.append('.ib ' + x if x not in ('*',) else '.ib *')
        fuera.append(','.join(partes) + '{' + dec + '}')
    for viejo in ('i1', 'i2', 'i3', 'i4', 't1', 't2', 't3', 'p1', 'p2', 'p3'):
        cuerpo = re.sub(rf'(id|aria-controls|aria-labelledby)="{viejo}"', rf'\1="ib-{viejo}"', cuerpo)
    cuerpo = cuerpo.replace('<div class="wrap">', '<div class="ib-wrap">', 1)
    js = js.replace("document.querySelectorAll('[role=\"tab\"]')", "document.querySelectorAll('.ib [role=\"tab\"]')")
    js = js.replace("document.querySelectorAll('.copy')", "document.querySelectorAll('.ib .copy')")
    return ('<style>' + ''.join(fuera) + '.ib .ib-wrap{padding:0}.ib h1{display:none}.ib .poster h2{text-transform:none;letter-spacing:-.01em;font-size:clamp(22px,3vw,30px);margin:0 0 6px}</style>'
            '<section class="portada-card ib" style="margin-top:16px"><h2 style="font-size:15px;margin:0 0 12px;'
            'color:var(--navy);text-transform:uppercase;letter-spacing:.06em">Introducción · Agentes de IA en la banca</h2>'
            + cuerpo + '</section>')

def portada(curso: dict, examen: dict, capitulos: list[tuple[int, str]]) -> str:
    c1, c2 = curso['color']
    pesos = max(d['peso'] for d in examen['dominios'].values())
    dominios = ''.join(
        f'<div class="portada-dom"><span>{H.escape(d["es"])} <span style="color:var(--slate)">· {H.escape(d["n"])}</span></span>'
        f'<b>{d["peso"]:g}%</b><i><s style="width:{d["peso"] / pesos * 100:.0f}%;background:linear-gradient(90deg,{c1},{c2})"></s></i></div>'
        for d in examen['dominios'].values())
    caps = ''.join(f'<li><a onclick="goToLesson({n})"><em>{n}</em><span>{H.escape(t)}</span></a></li>' for n, t in capitulos)
    return f'''
  <!-- ═══════════════ PORTADA ═══════════════ -->
  <div id="lp-0">
    <div class="portada">
      <section class="portada-hero">
        {logo(curso, 132)}
        <div>
          <div class="portada-eyebrow">Cortex Governor™ Academy · Discovery Fast</div>
          <h1>{H.escape(curso["titulo"])}</h1>
          <p>{H.escape(curso["bajada"])}</p>
          <div class="portada-cta">
            <button class="btn btn-primary" onclick="goToLesson(1)">Empezar: capítulo 1 →</button>
            <a class="btn btn-outline" href="simulador-examen.html" target="_blank" rel="noopener">🎓 Simulador de examen · {curso["preguntas"]} preguntas</a>
          </div>
        </div>
      </section>
      <div class="portada-grid">
        <section class="portada-card">
          <h2>Prepara para el examen</h2>
          <p style="font-size:16px;font-weight:800;margin:0 0 8px;color:var(--navy)">{H.escape(examen["nombre"])} <span style="color:var(--blue2)">({H.escape(curso["examen"])})</span></p>
          <div class="portada-exam"><span>{examen["preguntas"]} preguntas</span><span>{examen["minutos"]} min</span><span>aprueba con {examen["aprobado"]}/1000</span><span>{H.escape(examen["precio"])}</span></div>
          {dominios}
        </section>
        <section class="portada-card">
          <h2>Contenido</h2>
          <ol class="portada-caps">{caps}</ol>
        </section>
      </div>
      {introduccion_banca()}
    </div>
  </div><!-- /lp-0 -->
'''


def main() -> None:
    clave, trozos = sys.argv[1], sys.argv[2]
    estricto = '--estricto' in sys.argv
    curso = CURSOS[clave]
    examen = EXAMENES[curso['examen']]
    salida = os.path.normpath(os.path.join(RAIZ, curso['carpeta']))
    os.makedirs(salida, exist_ok=True)

    cab = open(f'{trozos}/00-cabecera.html', encoding='utf-8').read()
    fin = open(f'{trozos}/99-final.html', encoding='utf-8').read()
    archivos = sorted(glob.glob(f'{trozos}/cap/cap*.html'))
    cuerpo = ''.join(open(f, encoding='utf-8').read() for f in archivos)
    total = len(archivos)

    cuerpo = re.sub(r'simulador-examen\.html\?cap=(\d+)', r'simulador-examen.html#cap\1', cuerpo)
    cuerpo = cuerpo.replace('<div id="lp-1">', '<div id="lp-1" style="display:none">', 1)
    cuerpo = re.sub(r'(<button class="btn btn-outline" onclick="goToLesson\(0\)"[^>]*?)\s*disabled>', r'\1>', cuerpo)
    cuerpo = cuerpo.replace('\n          Inicio\n', '\n          Portada\n', 1)

    # Título de capítulo por lección, para la portada y el simulador.
    capitulos = [(int(n), H.unescape(t).strip()) for n, t in
                 re.findall(r'<div id="lp-(\d+)".*?<h1 class="lesson-hero-title">(.*?)</h1>', cuerpo, re.S)]
    capitulos = [(n, re.sub(r'<[^>]+>', '', t)) for n, t in capitulos]

    # Pestañas desde los botones reales.
    tabs, faltan_total = {}, []
    for n in range(1, total + 1):
        m = re.search(rf'<div class="lesson-tabs" id="tabs{n}">(.*?)</div>', cuerpo, re.S)
        tabs[str(n)] = re.findall(rf"tabScroll\({n},'([^']+)'", m.group(1)) if m else []
        faltan = [t for t in tabs[str(n)] if f'id="{t}"' not in cuerpo]
        if faltan:
            faltan_total.append((n, faltan))
    if faltan_total:
        print('aviso: pestañas sin sección:', faltan_total)
        if estricto:
            sys.exit(1)
    fin = re.sub(r'const TABS = \{.*?\};', 'const TABS = ' + json.dumps(tabs, ensure_ascii=False) + ';', fin, count=1, flags=re.S)

    # Navegación: la portada es la lección 0.
    fin = fin.replace('if(n < 1 || n > TOTAL_LESSONS) return;\n  for(let i=1;i<=TOTAL_LESSONS;i++){',
                      'if(n < 0 || n > TOTAL_LESSONS) return;\n  for(let i=0;i<=TOTAL_LESSONS;i++){')
    fin = fin.replace("if(history.replaceState) history.replaceState(null, '', '#lp-'+n);",
                      "if(history.replaceState) history.replaceState(null, '', n ? '#lp-'+n : '#portada');")
    extra = '''
// ─── Portada y enlace profundo desde el simulador (index.html#seccion) ───
(function(){
  function abrirDesdeHash(){
    const id = decodeURIComponent((location.hash||'').slice(1));
    if(!id || id==='portada') return;
    if(/^lp-\\d+$/.test(id)) return;
    const el = document.getElementById(id); if(!el) return;
    const lp = el.closest('[id^="lp-"]'); if(!lp) return;
    goToLesson(+lp.id.slice(3));
    setTimeout(()=>{ scrollToId(id); }, 120);
  }
  window.addEventListener('hashchange', abrirDesdeHash);
  window.addEventListener('load', abrirDesdeHash);
})();
'''
    i = fin.rfind('</script>')
    fin = fin[:i] + extra + fin[i:]

    # Cabecera: CSS de portada, logo del curso en la barra, entrada «Portada» en el índice lateral.
    cab = cab.replace('</style>', CSS_PORTADA + '</style>', 1)
    cab = cab.replace('<span class="course-badge">', logo(curso, 30).replace('class="portada-logo"', 'class="portada-logo" style="flex-shrink:0"') + '\n  <span class="course-badge">', 1)
    cab = cab.replace('<div class="module-group">', '<div class="lesson-item" id="li-0" onclick="goToLesson(0)" style="margin:8px 10px;font-weight:700">🏠 Portada del curso</div>\n    <div class="module-group">', 1)
    cab = re.sub(r'<div class="lesson-item active" id="li-1"', '<div class="lesson-item" id="li-1"', cab, count=1)
    cab = cab.replace('<div class="lesson-item" id="li-0"', '<div class="lesson-item active" id="li-0"', 1)
    cab = re.sub(r'<a href="[^"]*simulador[^"]*"[^>]*>[^<]*</a>',
                 f'<a href="simulador-examen.html" class="cc-exam-link">🎓 Simulador de examen · {curso["preguntas"]} preguntas</a>', cab, count=1)
    if 'cc-exam-link{' not in cab:
        cab = cab.replace('</style>', '.cc-exam-link{background:#2563eb!important;color:#fff!important;border-color:#2563eb!important}\n.cc-exam-link:hover{background:#1d4ed8!important}\n</style>', 1)
    cab = re.sub(r'<title>[^<]*</title>', f'<title>{H.escape(curso["titulo"])}</title>', cab, count=1)

    main_abre = '<main class="content-area" id="mainContent">'
    assert main_abre in cab
    cab = cab.replace(main_abre, main_abre + portada(curso, examen, capitulos), 1)

    html = cab + cuerpo + fin
    open(os.path.join(salida, 'index.html'), 'w', encoding='utf-8').write(html)

    # Banco de preguntas + simulador.
    destino = os.path.join(salida, 'banco-preguntas')
    os.makedirs(destino, exist_ok=True)
    n_preg = 0
    for f in sorted(glob.glob(f'{trozos}/preguntas/cap*.json')):
        datos = json.load(open(f, encoding='utf-8'))
        n_preg += len(datos)
        json.dump(datos, open(os.path.join(destino, os.path.basename(f)), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    import shutil
    for img in glob.glob(os.path.join(RAIZ, 'material-de-clase', '*.webp')) + glob.glob(os.path.join(RAIZ, 'material-de-clase', '*.png')):
        shutil.copyfile(img, os.path.join(salida, os.path.basename(img)))
    subprocess.run([sys.executable, os.path.join(RAIZ, 'herramientas', 'armar_simulador.py'), clave], check=True)
    print(f'{clave}: {total} capítulos · {len(html) // 1024} KB · {n_preg} preguntas → {os.path.relpath(salida, RAIZ)}/')


if __name__ == '__main__':
    main()
