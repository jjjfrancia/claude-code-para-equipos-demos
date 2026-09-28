"""Genera los dos documentos FICTICIOS del Marketplace de Créditos que usan los ejemplos del curso.

    python generar_documentos.py     # escribe reglamento-tarifario.pdf y politica-creditos.pdf en esta carpeta

- reglamento-tarifario.pdf · «Reglamento de Productos y Tarifario» (se cita «Tarifario, p. N»):
  requisitos, tasas por tramo, plazos, comisiones, cómo invertir y cómo reclamar. Caso 1, respuesta a clientes.
- politica-creditos.pdf · «Política de Créditos de Consumo» (se cita «Política de Créditos, p. N»):
  la regla del 30 %, la antigüedad mínima, montos y plazos, niveles de aprobación y excepciones. Caso 2.

Son documentos inventados para el curso: las cifras son verosímiles pero no representan a ningún banco real.
Cada sección empieza en su propia página y el script es determinista, así que las citas de los ejemplos
(«Política de Créditos, p. 7» para la regla del 30 %) siguen valiendo si se regeneran. Las cuotas de los
ejemplos no se escriben a mano: se calculan con la misma fórmula que usa politicas_corpus.py.
Requiere: pip install reportlab
"""
from __future__ import annotations

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, ListFlowable, ListItem, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

AQUI = os.path.dirname(os.path.abspath(__file__))
NOTA_FICTICIA = ('Documento ficticio creado para el curso «Claude Code para Equipos». No corresponde a ningún banco '
                 'real; las cifras son ilustrativas.')
PIE = 'Documento ficticio creado para el curso'


# ── Cálculo de cuotas (el mismo de politicas_corpus.py) ──────────────────────
def cuota(monto: float, plazo: int, tea: float) -> float:
    """Cuota fija mensual (método francés) con la TEA convertida a tasa mensual equivalente."""
    i = (1 + tea) ** (1 / 12) - 1
    return monto * i / (1 - (1 + i) ** -plazo)


def soles(x: float) -> str:
    return f'S/ {x:,.0f}'


# ── Estilos ──────────────────────────────────────────────────────────────────
AZUL = colors.HexColor('#0f3d56')
GRIS = colors.HexColor('#5b6573')
E = {
    'marca': ParagraphStyle('marca', fontName='Helvetica-Bold', fontSize=13, textColor=GRIS, alignment=TA_CENTER,
                            spaceAfter=36),
    'titulo': ParagraphStyle('titulo', fontName='Helvetica-Bold', fontSize=26, leading=32, textColor=AZUL,
                             alignment=TA_CENTER, spaceAfter=18),
    'sub': ParagraphStyle('sub', fontName='Helvetica', fontSize=13, leading=18, alignment=TA_CENTER, spaceAfter=8),
    'nota': ParagraphStyle('nota', fontName='Helvetica-Oblique', fontSize=11, leading=15, alignment=TA_CENTER,
                           textColor=colors.HexColor('#9b1c1c'), borderColor=colors.HexColor('#9b1c1c'),
                           borderWidth=1, borderPadding=10),
    'indice': ParagraphStyle('indice', fontName='Helvetica-Bold', fontSize=18, textColor=AZUL, spaceAfter=18),
    'h1': ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=AZUL, spaceAfter=10),
    'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=11.5, leading=15, textColor=AZUL, spaceBefore=9,
                         spaceAfter=4),
    'p': ParagraphStyle('p', fontName='Helvetica', fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=6),
    'li': ParagraphStyle('li', fontName='Helvetica', fontSize=10.5, leading=14.5, alignment=TA_JUSTIFY),
    'celda': ParagraphStyle('celda', fontName='Helvetica', fontSize=9.5, leading=12),
    'celda_h': ParagraphStyle('celda_h', fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=colors.white),
}
TOC_NIVEL = ParagraphStyle('toc0', fontName='Helvetica', fontSize=11.5, leading=21)


class Documento(BaseDocTemplate):
    """Portada sin pie; páginas interiores con pie y número. Registra las secciones para el índice."""

    def __init__(self, ruta: str, nombre: str):
        super().__init__(ruta, pagesize=A4, leftMargin=2.4 * cm, rightMargin=2.4 * cm, topMargin=2.2 * cm,
                         bottomMargin=2.2 * cm, title=nombre, author='Curso Claude Code para Equipos',
                         invariant=True)   # sin fecha de creación: el mismo PDF en cada corrida
        self.nombre = nombre
        marco = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='marco')
        self.addPageTemplates([PageTemplate('portada', [marco]),
                               PageTemplate('interior', [marco], onPage=self._pie)])

    def _pie(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8.5)
        canvas.setFillColor(GRIS)
        canvas.drawString(2.4 * cm, 1.2 * cm, f'{self.nombre} · {PIE}')
        canvas.drawRightString(A4[0] - 2.4 * cm, 1.2 * cm, f'Página {doc.page}')
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == 'h1':
            self.notify('TOCEntry', (0, flowable.getPlainText(), self.page))


def _tabla(filas: list[list[str]], anchos: list[float]) -> Table:
    datos = [[Paragraph(c, E['celda_h'] if i == 0 else E['celda']) for c in fila] for i, fila in enumerate(filas)]
    t = Table(datos, colWidths=[a * cm for a in anchos], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#b8c2cc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f4f7')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


def construir(archivo: str, portada: dict, secciones: list[tuple[str, list]]) -> int:
    """Portada (p. 1), índice (p. 2) y una sección por página desde la p. 3. Devuelve el número de páginas."""
    doc = Documento(os.path.join(AQUI, archivo), portada['nombre'])
    h: list = [
        Spacer(1, 3 * cm),
        Paragraph('BANCO · MARKETPLACE DE CRÉDITOS', E['marca']),
        Paragraph(portada['titulo'], E['titulo']),
        Paragraph(portada['sub'], E['sub']),
        Paragraph('Versión 1.0 · vigente desde el 1 de marzo de 2026', E['sub']),
        Paragraph(portada['responsable'], E['sub']),
        Paragraph(f'Cómo citarlo: «{portada["cita"]}, p. N»', E['sub']),
        Spacer(1, 2.5 * cm),
        Paragraph(NOTA_FICTICIA, E['nota']),
        NextPageTemplate('interior'),
        PageBreak(),
        Paragraph('Índice', E['indice']),
    ]
    toc = TableOfContents()
    toc.levelStyles = [TOC_NIVEL]
    h += [toc, PageBreak()]
    for n, (titulo, bloques) in enumerate(secciones):
        if n:
            h.append(PageBreak())
        h.append(Paragraph(titulo, E['h1']))
        for tipo, contenido, *extra in bloques:
            if tipo == 'h2':
                h.append(Paragraph(contenido, E['h2']))
            elif tipo == 'p':
                h.append(Paragraph(contenido, E['p']))
            elif tipo == 'lista':
                h.append(ListFlowable([ListItem(Paragraph(x, E['li']), leftIndent=14, value='–') for x in contenido],
                                      bulletType='bullet', start='–', leftIndent=14, spaceAfter=6))
                h.append(Spacer(1, 3))
            elif tipo == 'tabla':
                h.append(KeepTogether([_tabla(contenido, extra[0]), Spacer(1, 8)]))
    doc.multiBuild(h)
    return doc.page


# ── Reglamento de Productos y Tarifario ──────────────────────────────────────
TASAS = [  # (desde, hasta, TEA 6-24 meses, TEA 25-60 meses) · la misma tabla que politicas_corpus.TASAS
    (1_000, 4_999, 0.220, 0.240),
    (5_000, 19_999, 0.140, 0.150),
    (20_000, 50_000, 0.125, 0.135),
]


def _tea(monto: float, plazo: int) -> float:
    for desde, hasta, corta, larga in TASAS:
        if desde <= monto <= hasta:
            return corta if plazo <= 24 else larga
    raise ValueError('monto fuera de rango')


EJEMPLOS_CUOTA = [(10_000, 24), (10_000, 36), (15_000, 36), (15_000, 60), (30_000, 48)]

TARIFARIO = [
    ('1. Objeto y alcance del reglamento', [
        ('h2', '1.1 Qué es el Marketplace de Créditos'),
        ('p', 'El Marketplace de Créditos es la aplicación del banco en la que personas naturales y pequeñas empresas '
              'solicitan un préstamo, el banco lo evalúa y lo aprueba, y los inversionistas registrados lo financian. '
              'El banco administra el préstamo durante toda su vida: cobra las cuotas, las distribuye entre los '
              'inversionistas y atiende las consultas y los reclamos de ambas partes.'),
        ('h2', '1.2 A quién se aplica'),
        ('p', 'Este reglamento se aplica a los solicitantes (personas naturales y pequeñas empresas que piden un '
              'préstamo), a los inversionistas (personas naturales y empresas que financian préstamos) y al personal '
              'del banco que los atiende, incluidos los asistentes automáticos de la aplicación.'),
        ('h2', '1.3 Definiciones'),
        ('lista', [
            '<b>Solicitante</b>: la persona natural o pequeña empresa que pide un préstamo en el Marketplace.',
            '<b>Inversionista</b>: la persona natural o empresa registrada que financia, total o parcialmente, uno o '
            'varios préstamos aprobados por el banco.',
            '<b>Tasa efectiva anual (TEA)</b>: la tasa de interés compensatorio del préstamo expresada en un año.',
            '<b>Tasa de costo efectivo anual (TCEA)</b>: la TEA más el seguro de desgravamen y las comisiones; es el '
            'costo total del préstamo para el solicitante.',
            '<b>Cuota</b>: el pago mensual fijo que incluye capital e interés.',
            '<b>Ejecutivo</b>: la persona del banco que atiende los casos particulares, los reclamos y todo lo que '
            'requiere revisar la cuenta de un cliente.',
        ]),
        ('h2', '1.4 Documentos que lo complementan'),
        ('p', 'Las condiciones con que el banco aprueba los préstamos están en la Política de Créditos de Consumo, un '
              'documento interno. Este reglamento solo recoge lo que el cliente necesita saber para solicitar, pagar, '
              'invertir o reclamar. Si hubiera diferencia entre este reglamento y el contrato firmado por el cliente, '
              'prevalece el contrato.'),
    ]),
    ('2. Requisitos para solicitar un préstamo', [
        ('h2', '2.1 Personas naturales'),
        ('lista', [
            'Tener entre 18 y 70 años de edad.',
            'Presentar DNI vigente o carné de extranjería vigente.',
            'Tener un ingreso neto mensual de al menos S/ 1,200, demostrable.',
            'Tener una antigüedad mínima de 6 meses en el empleo actual si es trabajador dependiente, o 12 meses de '
            'actividad si es trabajador independiente.',
            'Tener una cuenta de ahorros en el banco, donde se recibe el desembolso y se pagan las cuotas.',
            'No registrar deudas vencidas en la central de riesgos al momento de la solicitud.',
        ]),
        ('h2', '2.2 Pequeñas empresas'),
        ('lista', [
            'RUC activo con al menos 12 meses de antigüedad.',
            'Ventas anuales de hasta S/ 1,500,000.',
            'Declaraciones mensuales de impuestos de los últimos 6 meses.',
            'Representante legal con poderes vigentes y cuenta corriente empresarial en el banco.',
        ]),
        ('h2', '2.3 Documentos que se adjuntan en la aplicación'),
        ('p', 'Los trabajadores dependientes adjuntan sus boletas de pago de los últimos 3 meses; los independientes, '
              'sus recibos por honorarios de los últimos 6 meses; las pequeñas empresas, sus 6 últimas declaraciones '
              'mensuales. El banco nunca pide, ni por la aplicación ni por teléfono, la clave de la tarjeta, el código '
              'CVV ni el número completo de la tarjeta.'),
        ('h2', '2.4 Montos y plazos'),
        ('p', 'Se puede solicitar un préstamo de S/ 1,000 a S/ 50,000, a un plazo de 6 a 60 meses. Cumplir los '
              'requisitos no garantiza la aprobación: cada solicitud se evalúa según la Política de Créditos del banco, '
              'que considera sobre todo la capacidad de pago del solicitante.'),
    ]),
    ('3. Cómo se solicita y estados de la solicitud', [
        ('h2', '3.1 Pasos para solicitar'),
        ('lista', [
            'Completar el formulario en la aplicación: monto, plazo y destino del préstamo.',
            'Adjuntar los documentos de la sección 2.3.',
            'Autorizar la consulta a la central de riesgos.',
            'Esperar la evaluación del banco, que toma hasta 3 días hábiles.',
            'Si el banco aprueba, la solicitud se publica para los inversionistas hasta por 15 días calendario.',
            'Cuando la solicitud está financiada al 100 %, el desembolso se hace en 1 día hábil.',
        ]),
        ('h2', '3.2 Estados de la solicitud'),
        ('tabla', [
            ['Estado', 'Qué significa'],
            ['Recibida', 'La solicitud y sus documentos llegaron completos.'],
            ['Observada', 'Falta un documento o un dato; la evaluación se detiene hasta completarlo.'],
            ['En evaluación', 'Un analista de créditos del banco la está revisando.'],
            ['Aprobada', 'El analista la aprobó; se publicará para los inversionistas.'],
            ['Publicada', 'Los inversionistas pueden financiarla.'],
            ['Financiada', 'Alcanzó el 100 % del monto; se prepara el desembolso.'],
            ['Desembolsada', 'El dinero está en la cuenta del solicitante; empieza el cronograma.'],
            ['Rechazada', 'No cumple la Política de Créditos del banco.'],
        ], [3.5, 12.5]),
        ('h2', '3.3 Si la solicitud no se financia por completo'),
        ('p', 'Si al cabo de 15 días la solicitud publicada no alcanza el 100 % de financiamiento, el banco puede '
              'financiar la diferencia con recursos propios o proponer al solicitante un monto menor. El solicitante '
              'decide si acepta la propuesta.'),
        ('h2', '3.4 Consultas sobre una solicitud concreta'),
        ('p', 'El asistente de la aplicación explica qué significa cada estado, pero no revisa cuentas ni solicitudes '
              'particulares. Para conocer el motivo de una observación o de un rechazo, el solicitante pide la '
              'derivación a un ejecutivo, que responde en un máximo de 2 días hábiles.'),
    ]),
    ('4. Tasas de interés por tramo', [
        ('h2', '4.1 Tasa fija según monto y plazo'),
        ('p', 'La tasa de interés de los préstamos del Marketplace es una TEA fija durante toda la vida del préstamo. '
              'Se determina por el monto y el plazo solicitados, según el cuadro siguiente.'),
        ('tabla', [['Monto del préstamo', 'TEA, plazo de 6 a 24 meses', 'TEA, plazo de 25 a 60 meses']] +
         [[f'{soles(d)} a {soles(h)}', f'{c * 100:.1f} %', f'{l * 100:.1f} %'] for d, h, c, l in TASAS],
         [5.6, 5.2, 5.2]),
        ('h2', '4.2 Cómo leer el cuadro'),
        ('p', 'Un préstamo de S/ 10,000 a 24 meses paga una TEA de 14.0 %; el mismo monto a 36 meses paga una TEA de '
              '15.0 %. Un préstamo de S/ 15,000 a 36 meses paga también 15.0 %, y uno de S/ 30,000 a 48 meses, 13.5 %. '
              'Los montos más altos pagan una tasa menor porque el costo de evaluación se reparte en más capital.'),
        ('h2', '4.3 Tasa de costo efectivo anual (TCEA)'),
        ('p', 'La TCEA suma a la TEA el seguro de desgravamen de la sección 6. Como referencia, un préstamo de S/ 10,000 '
              'a 24 meses tiene una TCEA de 15.1 %. La TCEA exacta de cada préstamo figura en la oferta y en el '
              'cronograma que el solicitante acepta en la aplicación.'),
        ('h2', '4.4 Interés moratorio'),
        ('p', 'Si una cuota se paga después de su fecha de vencimiento, se cobra además un interés moratorio de 5.0 % '
              'TEA sobre la cuota vencida, por los días de atraso, y la penalidad de la sección 6.'),
        ('h2', '4.5 Vigencia de las tasas'),
        ('p', 'Las tasas de este cuadro rigen para las solicitudes presentadas desde el 1 de marzo de 2026. Vale la '
              'tasa del día en que el solicitante acepta la oferta en la aplicación; un cambio posterior del cuadro no '
              'modifica los préstamos ya aceptados.'),
    ]),
    ('5. Plazos, cuotas y cronograma', [
        ('h2', '5.1 Plazos admitidos'),
        ('p', 'El plazo del préstamo es de 6 a 60 meses, en meses enteros. Un plazo más largo baja la cuota mensual pero '
              'aumenta el interés total que se paga.'),
        ('h2', '5.2 Cuota fija'),
        ('p', 'Las cuotas se calculan por el método de cuota fija: todas las cuotas mensuales son iguales e incluyen '
              'capital e interés. El seguro de desgravamen se suma aparte en el cronograma.'),
        ('h2', '5.3 Ejemplos de cuota mensual (sin seguro)'),
        ('tabla', [['Monto', 'Plazo', 'TEA', 'Cuota mensual']] +
         [[soles(m), f'{p} meses', f'{_tea(m, p) * 100:.1f} %', soles(cuota(m, p, _tea(m, p)))]
          for m, p in EJEMPLOS_CUOTA], [4, 4, 4, 4]),
        ('h2', '5.4 Fecha de pago'),
        ('p', 'El solicitante elige el día de pago, entre el 1 y el 28 de cada mes. La primera cuota vence entre 30 y 59 '
              'días después del desembolso, según el día elegido.'),
        ('h2', '5.5 Cronograma'),
        ('p', 'El cronograma completo, con el capital, el interés y el seguro de cada cuota, se ve y se descarga gratis en '
              'la aplicación en cualquier momento.'),
    ]),
    ('6. Comisiones y gastos', [
        ('h2', '6.1 Cuadro de comisiones y gastos'),
        ('tabla', [
            ['Concepto', 'Monto', 'Cuándo se cobra'],
            ['Evaluación de la solicitud', 'S/ 0', 'Nunca'],
            ['Desembolso', 'S/ 0', 'Nunca'],
            ['Seguro de desgravamen', '0.08 % mensual sobre el saldo', 'Con cada cuota'],
            ['Pago anticipado, total o parcial', 'S/ 0', 'Nunca'],
            ['Penalidad por pago tardío', 'S/ 25 por cuota vencida', 'Una vez por cuota, desde el primer día de atraso'],
            ['Envío físico del estado de cuenta', 'S/ 5 por envío', 'Solo si el cliente lo pide'],
            ['Constancia de no adeudo', 'S/ 0', 'Nunca'],
            ['Administración (inversionistas)', '3.0 puntos de la TEA', 'Se descuenta de los intereses que recibe'],
            ['Transferencia a otro banco (inversionistas)', 'S/ 7 por operación', 'Al retirar fondos a otro banco'],
        ], [5.8, 4.4, 5.8]),
        ('h2', '6.2 Sin cobros fuera del cuadro'),
        ('p', 'El banco no cobra ninguna comisión ni gasto que no figure en este cuadro. Cualquier cambio se comunica en '
              'la aplicación con 45 días de anticipación y no afecta a los préstamos ya desembolsados.'),
        ('h2', '6.3 Seguro de desgravamen'),
        ('p', 'El seguro de desgravamen cubre el saldo del préstamo en caso de fallecimiento o invalidez total y '
              'permanente del titular. El solicitante puede endosar un seguro propio con coberturas equivalentes; en '
              'ese caso no paga el seguro del banco.'),
    ]),
    ('7. Pagos anticipados, atrasos y mora', [
        ('h2', '7.1 Pago anticipado'),
        ('p', 'El solicitante puede pagar por adelantado todo o parte del saldo en cualquier momento, sin penalidad. En '
              'un pago parcial elige si reduce el monto de la cuota o el número de cuotas.'),
        ('h2', '7.2 Atrasos'),
        ('p', 'Desde el día siguiente al vencimiento se cobra el interés moratorio de 5.0 % TEA sobre la cuota vencida y '
              'la penalidad de S/ 25 por cuota. Los atrasos se reportan a la central de riesgos según la normativa '
              'vigente.'),
        ('h2', '7.3 Reprogramación'),
        ('p', 'Si el solicitante prevé que no podrá pagar una cuota, puede pedir en la aplicación la derivación a un '
              'ejecutivo antes del vencimiento, para evaluar una reprogramación. El asistente de la aplicación no '
              'reprograma ni promete reprogramaciones.'),
        ('h2', '7.4 Qué recibe el inversionista si el solicitante se atrasa'),
        ('p', 'El banco paga a los inversionistas solo lo que el solicitante efectivamente paga. Cuando el solicitante '
              'se pone al día, el inversionista recibe su parte de la cuota y del interés moratorio cobrado.'),
        ('h2', '7.5 Cobranza'),
        ('p', 'La cobranza de los préstamos atrasados la hace el banco, en nombre de todos los inversionistas del '
              'préstamo. Los inversionistas no contactan al solicitante ni conocen su identidad.'),
    ]),
    ('8. Cómo invertir en el Marketplace', [
        ('h2', '8.1 Requisitos para invertir'),
        ('lista', [
            'Ser persona natural mayor de 18 años con DNI, o empresa con RUC activo.',
            'Tener una cuenta en el banco, desde la que se invierte y donde se reciben los pagos.',
            'Completar en la aplicación el test de perfil de inversionista y aceptar la declaración de riesgos.',
        ]),
        ('h2', '8.2 Montos'),
        ('p', 'La inversión mínima es de S/ 500 por préstamo, en múltiplos de S/ 100. Un inversionista puede financiar '
              'como máximo el 25 % de cada préstamo. Se recomienda repartir la inversión entre al menos 10 préstamos.'),
        ('h2', '8.3 Rendimiento'),
        ('p', 'El inversionista recibe la TEA del préstamo menos la comisión de administración de 3.0 puntos de la '
              'sección 6. Un préstamo con TEA de 15.0 % da una tasa neta estimada de 12.0 % anual. Si invierte S/ 5,000 '
              'en préstamos de ese tramo y todos pagan a tiempo, el rendimiento estimado es de alrededor de S/ 600 en un '
              'año si reinvierte lo que recibe cada mes; si no reinvierte, es menor, porque las cuotas le devuelven '
              'capital desde el primer mes.'),
        ('h2', '8.4 Pagos al inversionista'),
        ('p', 'El banco abona en la cuenta del inversionista, al día hábil siguiente del cobro, su parte del capital y '
              'del interés neto de cada cuota pagada.'),
        ('h2', '8.5 Riesgos'),
        ('p', 'El rendimiento no está garantizado. Si un solicitante deja de pagar, el inversionista puede perder parte o '
              'todo el capital invertido en ese préstamo. No se puede retirar el capital de un préstamo antes de su '
              'vencimiento: el capital vuelve a medida que se pagan las cuotas.'),
    ]),
    ('9. Seguridad y datos personales', [
        ('h2', '9.1 Lo que el banco nunca pide'),
        ('p', 'El banco nunca pide por la aplicación, por chat, por correo ni por teléfono el número completo de la '
              'tarjeta, la clave, el código CVV ni los códigos de un solo uso que llegan por SMS. Si alguien los pide '
              'en nombre del banco, es un intento de fraude.'),
        ('h2', '9.2 Lo que muestra el asistente de la aplicación'),
        ('p', 'El asistente responde con este reglamento y cita la página. No muestra datos de cuentas ni de '
              'solicitudes particulares, no inventa tasas ni comisiones y, si no encuentra la respuesta, lo dice y '
              'ofrece derivar la consulta a un ejecutivo.'),
        ('h2', '9.3 Uso de los datos del solicitante'),
        ('p', 'Los datos que entrega el solicitante (DNI, ingresos, deudas) se usan solo para evaluar su solicitud, se '
              'guardan cifrados y no se comparten con los inversionistas. El inversionista ve el monto, el plazo, la '
              'tasa, el destino y una calificación de riesgo del préstamo, nunca la identidad del solicitante.'),
        ('h2', '9.4 Si sospecha de un fraude'),
        ('p', 'Si recibe un mensaje que le pide su clave o sus códigos, no responda y repórtelo desde la opción Ayuda de '
              'la aplicación. El banco bloquea el acceso de forma preventiva mientras lo revisa.'),
    ]),
    ('10. Reclamos y atención', [
        ('h2', '10.1 Canales'),
        ('p', 'Las consultas y los reclamos se presentan en la aplicación (opción Ayuda, luego Reclamos), en el Libro de '
              'Reclamaciones virtual, en cualquier agencia del banco o por la banca telefónica.'),
        ('h2', '10.2 Cómo presentar un reclamo'),
        ('p', 'Indique el número de su solicitud o de su préstamo, describa lo ocurrido y diga qué solución pide. Al '
              'registrarlo recibe un código de reclamo con el que puede seguir su estado en la aplicación.'),
        ('h2', '10.3 Plazo de respuesta'),
        ('p', 'El banco responde los reclamos en un máximo de 15 días hábiles. Si el caso lo requiere, el plazo puede '
              'extenderse por otros 15 días hábiles, avisándole antes de que venza el primero.'),
        ('h2', '10.4 Derivación a un ejecutivo'),
        ('p', 'El asistente de la aplicación deriva la conversación a un ejecutivo cuando el cliente lo pide, cuando se '
              'trata de un reclamo formal, cuando la pregunta es sobre su caso particular y requiere ver su cuenta, o '
              'cuando la respuesta no está en este reglamento.'),
        ('h2', '10.5 Si no está conforme'),
        ('p', 'Si no está conforme con la respuesta, puede pedir una revisión a la Defensoría del Cliente del banco o '
              'acudir a las instancias externas de protección al consumidor financiero.'),
    ]),
]


# ── Política de Créditos de Consumo ──────────────────────────────────────────
C_1042 = cuota(15_000, 36, 0.15)
C_60 = cuota(15_000, 60, 0.15)

POLITICA = [
    ('1. Objeto, alcance y roles', [
        ('h2', '1.1 Objeto'),
        ('p', 'Esta política establece los criterios con los que el banco evalúa y aprueba los préstamos del Marketplace '
              'de Créditos antes de publicarlos a los inversionistas. Su propósito es que toda solicitud se evalúe con '
              'las mismas reglas y que cada decisión quede documentada de modo que un tercero pueda reconstruir por qué '
              'se aprobó, se rechazó o se envió a revisión.'),
        ('h2', '1.2 Alcance'),
        ('p', 'Aplica a los préstamos de consumo a personas naturales y a los préstamos a pequeñas empresas del '
              'Marketplace, por montos de S/ 1,000 a S/ 50,000.'),
        ('h2', '1.3 Roles'),
        ('lista', [
            '<b>Analista de créditos</b>: evalúa la solicitud y decide. Es el responsable de la decisión.',
            '<b>Jefe de créditos</b>: aprueba, además del analista, las solicitudes de más de S/ 20,000, y es el único '
            'que autoriza excepciones.',
            '<b>Asistente de aprobación</b>: herramienta que prepara una recomendación para el analista. Nunca aprueba '
            'ni rechaza una solicitud.',
            '<b>Riesgos</b>: mantiene esta política y propone sus cambios.',
            '<b>Cumplimiento, Seguridad de la Información y Legal</b>: revisan, junto con Riesgos, todo cambio en el '
            'asistente de aprobación antes de que pase a producción.',
        ]),
        ('h2', '1.4 Vigencia'),
        ('p', 'La política rige desde el 1 de marzo de 2026 y se revisa al menos una vez al año, o antes si cambian las '
              'tasas del Tarifario o la morosidad de la cartera.'),
    ]),
    ('2. Principios de evaluación', [
        ('h2', '2.1 Capacidad de pago primero'),
        ('p', 'El criterio principal es la capacidad de pago: la cuota del préstamo, sumada a las deudas que el '
              'solicitante ya tiene, debe caber en su ingreso neto con margen suficiente (sección 5).'),
        ('h2', '2.2 Estabilidad de ingresos'),
        ('p', 'Un ingreso alto pero reciente no basta. La antigüedad en el empleo o en la actividad es la señal de que el '
              'ingreso se mantendrá durante el plazo del préstamo (sección 6).'),
        ('h2', '2.3 Comportamiento de pago'),
        ('p', 'El historial en la central de riesgos muestra cómo paga el solicitante sus otras deudas y si declaró '
              'todas (sección 7).'),
        ('h2', '2.4 Decisión documentada'),
        ('p', 'Toda decisión registra sus motivos y la sección de esta política que aplica. Una decisión sin motivos no '
              'es válida, aunque el resultado sea correcto.'),
        ('h2', '2.5 No discriminación'),
        ('p', 'La evaluación no considera el sexo, la religión, el origen, la opinión política, el estado civil ni '
              'ninguna otra condición personal ajena a la capacidad de pago.'),
        ('h2', '2.6 Proporcionalidad'),
        ('p', 'El monto y el plazo deben corresponder al destino declarado. Un préstamo para un bien de corta duración no '
              'debería pagarse en un plazo mucho mayor que la vida útil del bien.'),
    ]),
    ('3. Información mínima de la solicitud', [
        ('h2', '3.1 Datos que se evalúan'),
        ('lista', [
            'Ingreso neto mensual del solicitante.',
            'Deudas mensuales: las cuotas de todos sus préstamos y tarjetas vigentes.',
            'Antigüedad laboral en el empleo actual, o de actividad si es independiente.',
            'Monto, plazo y destino del préstamo solicitado.',
        ]),
        ('h2', '3.2 Ingreso neto'),
        ('p', 'El ingreso neto mensual es la remuneración bruta menos los descuentos de ley (aportes previsionales e '
              'impuesto a la renta retenido) y los descuentos judiciales. Para trabajadores independientes se toma el '
              'promedio de los recibos de los últimos 6 meses. Para pequeñas empresas se toma el flujo mensual promedio '
              'que muestran sus declaraciones.'),
        ('h2', '3.3 Deudas mensuales'),
        ('p', 'Las deudas mensuales son la suma de las cuotas de todas las deudas vigentes del solicitante. En las '
              'tarjetas de crédito se toma como cuota el 5 % de la línea utilizada. Lo declarado por el solicitante se '
              'contrasta siempre con la central de riesgos (sección 7).'),
        ('h2', '3.4 Solicitudes incompletas'),
        ('p', 'Una solicitud a la que le falta un dato o un documento pasa a estado Observada y no se evalúa hasta que se '
              'complete. Ni el analista ni el asistente de aprobación suponen el dato que falta.'),
    ]),
    ('4. Montos y plazos admitidos', [
        ('h2', '4.1 Monto'),
        ('p', 'El monto del préstamo va de S/ 1,000 a S/ 50,000. Una solicitud fuera de ese rango se rechaza; el analista '
              'puede sugerir al solicitante que presente una nueva por un monto admitido.'),
        ('h2', '4.2 Plazo'),
        ('p', 'El plazo va de 6 a 60 meses. Una solicitud con un plazo fuera de ese rango se rechaza, salvo que el '
              'solicitante acepte un plazo admitido que cumpla las demás reglas.'),
        ('h2', '4.3 Edad al término del préstamo'),
        ('p', 'La edad del solicitante al vencer la última cuota no puede superar los 75 años.'),
        ('h2', '4.4 Tasa y cuota'),
        ('p', 'La cuota se calcula con la TEA del Reglamento de Productos y Tarifario (sección 4 del Tarifario) y el '
              'método de cuota fija. El asistente de aprobación y el analista usan la misma fórmula; la cuota la calcula '
              'un programa, no se estima a ojo.'),
        ('h2', '4.5 Montos que requieren al jefe de créditos'),
        ('p', 'Las solicitudes de más de S/ 20,000 requieren, además de la aprobación del analista, la del jefe de '
              'créditos (sección 8).'),
    ]),
    ('5. Capacidad de pago: la regla del 30 %', [
        ('h2', '5.1 Cuota máxima: 30 % del ingreso neto'),
        ('p', 'La cuota máxima admitida es el 30 % del ingreso neto mensual del solicitante. Para aplicar esta regla se '
              'considera la carga financiera total: la cuota del préstamo solicitado más las deudas mensuales vigentes. '
              '<b>La carga financiera total no puede superar el 30 % del ingreso neto mensual.</b>'),
        ('h2', '5.2 Cómo se calcula'),
        ('lista', [
            'Calcular la cuota del préstamo con la TEA del Tarifario y el plazo solicitado.',
            'Sumar a esa cuota las deudas mensuales del solicitante (sección 3.3).',
            'Dividir la carga financiera total entre el ingreso neto mensual.',
            'Si el resultado es igual o menor que 30 %, la solicitud cumple la regla de capacidad de pago.',
        ]),
        ('h2', '5.3 Ejemplo'),
        ('p', f'Ingreso neto de S/ 3,500, deudas de S/ 400 al mes, préstamo de S/ 15,000 a 36 meses con TEA de 15.0 %: '
              f'la cuota es {soles(C_1042)} y la carga total {soles(C_1042 + 400)}, que es el '
              f'{(C_1042 + 400) / 3500 * 100:.0f} % del ingreso neto. Cumple la regla del 30 %.'),
        ('h2', '5.4 Si la carga supera el 30 %'),
        ('p', 'El analista puede proponer un plazo mayor, dentro del máximo de 60 meses, o un monto menor, que deje la '
              'carga en 30 % o menos. La contrapropuesta se ofrece al solicitante; si la acepta, la solicitud se evalúa '
              'de nuevo con las nuevas condiciones. Si ninguna combinación de monto y plazo admitidos cumple la regla, '
              'la solicitud se rechaza.'),
        ('h2', '5.5 Ejemplo de contrapropuesta'),
        ('p', f'Con deudas de S/ 600 al mes, la carga del ejemplo anterior sube a {soles(C_1042 + 600)} '
              f'({(C_1042 + 600) / 3500 * 100:.0f} %) y no cumple. A 60 meses la cuota baja a {soles(C_60)} y la carga '
              f'a {soles(C_60 + 600)} ({(C_60 + 600) / 3500 * 100:.0f} %): el analista puede enviar la solicitud a '
              f'revisión con esa contrapropuesta.'),
        ('h2', '5.6 Sin redondeos'),
        ('p', 'El límite no se redondea: una carga de 30.4 % no cumple la regla. Las excepciones a este límite solo las '
              'autoriza el jefe de créditos (sección 9).'),
    ]),
    ('6. Estabilidad laboral: antigüedad mínima', [
        ('h2', '6.1 Trabajadores dependientes'),
        ('p', 'La antigüedad laboral mínima es de 6 meses continuos en el empleo actual. Con menos de 6 meses la '
              'solicitud se rechaza, salvo la excepción de la sección 9.'),
        ('h2', '6.2 Trabajadores independientes'),
        ('p', 'Se exigen 12 meses de actividad continua, demostrada con recibos por honorarios o declaraciones de '
              'impuestos.'),
        ('h2', '6.3 Pequeñas empresas'),
        ('p', 'Se exigen 12 meses de RUC activo con ventas declaradas en cada uno de esos meses.'),
        ('h2', '6.4 Antigüedad justa'),
        ('p', 'Si la antigüedad está entre 6 y 8 meses, la solicitud cumple el mínimo, pero el analista debe verificar la '
              'continuidad del empleo: contrato vigente y periodo de prueba superado. Si no puede verificarla, la '
              'solicitud se envía a revisión.'),
        ('h2', '6.5 Cambio de empleo en el mismo rubro'),
        ('p', 'Si el solicitante cambió de empleo en los últimos 6 meses, sin interrupción entre uno y otro y en el mismo '
              'rubro, el jefe de créditos puede autorizar una excepción a la antigüedad mínima (sección 9).'),
    ]),
    ('7. Deudas e historial crediticio', [
        ('h2', '7.1 Consulta a la central de riesgos'),
        ('p', 'Toda solicitud se evalúa con una consulta a la central de riesgos de no más de 30 días de antigüedad, '
              'autorizada por el solicitante.'),
        ('h2', '7.2 Deudas no declaradas'),
        ('p', 'Si la central de riesgos muestra deudas que el solicitante no declaró, la carga financiera se recalcula '
              'con las deudas reales y la solicitud pasa a revisión. Si la carga recalculada supera el 30 %, se aplica '
              'la sección 5.'),
        ('h2', '7.3 Calificación'),
        ('p', 'Se admiten solicitantes con calificación Normal o Con Problemas Potenciales en los últimos 12 meses. Con '
              'calificación Deficiente, Dudoso o Pérdida en ese periodo, la solicitud se rechaza.'),
        ('h2', '7.4 Deudas vencidas'),
        ('p', 'Si el solicitante tiene deudas vencidas al momento de la evaluación, la solicitud se rechaza. Puede '
              'presentarse de nuevo cuando las haya regularizado.'),
        ('h2', '7.5 Número de acreedores'),
        ('p', 'Si el solicitante tiene deudas con más de 4 entidades, la solicitud se envía a revisión aunque cumpla la '
              'regla del 30 %, porque el riesgo de sobreendeudamiento es mayor.'),
    ]),
    ('8. Niveles de aprobación', [
        ('h2', '8.1 Hasta S/ 20,000'),
        ('p', 'Las solicitudes de hasta S/ 20,000, inclusive, las aprueba el analista de créditos.'),
        ('h2', '8.2 Más de S/ 20,000'),
        ('p', 'Las solicitudes de más de S/ 20,000 las aprueba el analista y, además, el jefe de créditos. Sin las dos '
              'aprobaciones la solicitud no se publica.'),
        ('h2', '8.3 El asistente no aprueba'),
        ('p', 'La recomendación del asistente de aprobación no es una aprobación. Ninguna solicitud cambia a estado '
              'Aprobada sin el registro del analista identificado, con su usuario y la fecha, y, cuando corresponde, '
              'el del jefe de créditos.'),
        ('h2', '8.4 Registro de la decisión'),
        ('p', 'El registro guarda la recomendación del asistente, la decisión del analista, los motivos, la sección de '
              'esta política que aplica y, si la decisión difiere de la recomendación, por qué.'),
        ('h2', '8.5 Plazo'),
        ('p', 'La decisión se toma en un máximo de 3 días hábiles desde que la solicitud está completa.'),
    ]),
    ('9. Excepciones', [
        ('h2', '9.1 Quién las autoriza'),
        ('p', 'Solo el jefe de créditos autoriza excepciones, por escrito y con el motivo. El analista puede proponerlas; '
              'el asistente de aprobación puede señalar que un caso las necesita, pero nunca las concede.'),
        ('h2', '9.2 Lo que se puede exceptuar'),
        ('lista', [
            'Una carga financiera de hasta 35 %, si hay un ingreso adicional documentado que no se computó o una '
            'garantía.',
            'La antigüedad mínima, desde 3 meses, en el caso de la sección 6.5.',
        ]),
        ('h2', '9.3 Lo que no se puede exceptuar'),
        ('lista', [
            'Montos fuera del rango de S/ 1,000 a S/ 50,000.',
            'Plazos fuera del rango de 6 a 60 meses.',
            'Deudas vencidas al momento de la evaluación.',
            'Calificación Deficiente, Dudoso o Pérdida en los últimos 12 meses.',
        ]),
        ('h2', '9.4 Límite'),
        ('p', 'Las excepciones no pueden superar el 5 % de las solicitudes aprobadas en el mes. Riesgos revisa cada '
              'trimestre las excepciones concedidas y su comportamiento de pago.'),
    ]),
    ('10. Asistente de aprobación y protección de datos', [
        ('h2', '10.1 Qué hace el asistente'),
        ('p', 'El asistente de aprobación lee la solicitud, aplica las reglas de las secciones 4 a 8 y devuelve una '
              'recomendación (aprobar, rechazar o revisar) con sus motivos y la página de esta política que aplica.'),
        ('h2', '10.2 Tres agentes que debaten'),
        ('p', 'La recomendación sale de un debate, no de un voto: un analista flexible busca cómo la solicitud sí puede '
              'cumplir la política; un analista estricto busca todo motivo de rechazo o de revisión; un juez lee los dos '
              'argumentos con sus citas, les pide otra ronda si discrepan y se detiene cuando las posiciones ya no '
              'cambian. El juez emite la recomendación final con los motivos de ambos lados.'),
        ('h2', '10.3 Cálculos por programa'),
        ('p', 'La cuota, la carga financiera y su porcentaje los calcula un programa con la fórmula de la sección 4.4. '
              'Los agentes argumentan sobre esos números; no los recalculan.'),
        ('h2', '10.4 Datos personales'),
        ('p', 'El DNI, los ingresos y las deudas del solicitante no se escriben en los registros (logs) del sistema ni en '
              'los prompts o casos de prueba. Las pruebas usan solicitudes ficticias.'),
        ('h2', '10.5 Cambios al asistente'),
        ('p', 'Todo cambio en el asistente de aprobación pasa por Riesgos, Cumplimiento, Seguridad de la Información y '
              'Legal antes de salir a producción. La decisión final es siempre del analista.'),
    ]),
]

DOCUMENTOS = [
    ('reglamento-tarifario.pdf', {
        'nombre': 'Reglamento de Productos y Tarifario', 'titulo': 'Reglamento de Productos y Tarifario',
        'sub': 'Marketplace de Créditos: solicitantes e inversionistas', 'cita': 'Tarifario',
        'responsable': 'Área de Productos · Uso público'}, TARIFARIO),
    ('politica-creditos.pdf', {
        'nombre': 'Política de Créditos de Consumo', 'titulo': 'Política de Créditos de Consumo',
        'sub': 'Evaluación y aprobación de solicitudes del Marketplace', 'cita': 'Política de Créditos',
        'responsable': 'Área de Riesgos · Uso interno'}, POLITICA),
]

if __name__ == '__main__':
    for archivo, portada, secciones in DOCUMENTOS:
        paginas = construir(archivo, portada, secciones)
        esperadas = len(secciones) + 2
        estado = 'OK' if paginas == esperadas else f'REVISAR: se esperaban {esperadas} (una sección por página)'
        print(f'{archivo}: {paginas} páginas · {estado}')
