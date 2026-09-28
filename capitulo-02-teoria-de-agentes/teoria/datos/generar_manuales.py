"""Genera los dos manuales FICTICIOS que usa el Asistente de Normativa en todos los ejemplos del curso.

    python generar_manuales.py        # escribe manual-credito-consumo.pdf y manual-pla-ft.pdf en esta carpeta

Los manuales son inventados para el curso: las cifras, los niveles de aprobación y los plazos son verosímiles
pero no representan la política de ningún banco real. El script es determinista (mismo contenido, mismas
páginas), así que las citas «Manual de Crédito, p. N» de los ejemplos siguen valiendo si se regeneran.
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
NOTA_FICTICIA = 'Documento ficticio creado para el curso. No representa la política de ningún banco real.'

# ── Estilos ──────────────────────────────────────────────────────────────────
AZUL = colors.HexColor('#12355b')
GRIS = colors.HexColor('#5b6573')
E = {
    'portada_banco': ParagraphStyle('pb', fontName='Helvetica-Bold', fontSize=13, textColor=GRIS, alignment=TA_CENTER,
                                    spaceAfter=40),
    'portada_titulo': ParagraphStyle('pt', fontName='Helvetica-Bold', fontSize=26, leading=32, textColor=AZUL,
                                     alignment=TA_CENTER, spaceAfter=18),
    'portada_sub': ParagraphStyle('ps', fontName='Helvetica', fontSize=13, leading=18, alignment=TA_CENTER,
                                  spaceAfter=8),
    'portada_nota': ParagraphStyle('pn', fontName='Helvetica-Oblique', fontSize=11, leading=15, alignment=TA_CENTER,
                                   textColor=colors.HexColor('#9b1c1c'), borderColor=colors.HexColor('#9b1c1c'),
                                   borderWidth=1, borderPadding=10),
    'indice_titulo': ParagraphStyle('it', fontName='Helvetica-Bold', fontSize=18, textColor=AZUL, spaceAfter=18),
    'h1': ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=AZUL, spaceAfter=12),
    'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=AZUL, spaceBefore=12,
                         spaceAfter=5),
    'p': ParagraphStyle('p', fontName='Helvetica', fontSize=11, leading=16.5, alignment=TA_JUSTIFY, spaceAfter=7),
    'li': ParagraphStyle('li', fontName='Helvetica', fontSize=11, leading=16, alignment=TA_JUSTIFY),
    'celda': ParagraphStyle('c', fontName='Helvetica', fontSize=9.5, leading=12),
    'celda_h': ParagraphStyle('ch', fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=colors.white),
}
TOC_NIVEL = ParagraphStyle('toc0', fontName='Helvetica', fontSize=11.5, leading=20, leftIndent=0)


class Manual(BaseDocTemplate):
    """Plantilla con portada sin pie y páginas interiores con pie; registra los capítulos para el índice."""

    def __init__(self, ruta: str, pie: str):
        super().__init__(ruta, pagesize=A4, leftMargin=2.5 * cm, rightMargin=2.5 * cm, topMargin=2.6 * cm,
                         bottomMargin=2.6 * cm, title=pie, author='Curso Claude Code para equipos')
        self.pie = pie
        marco = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='marco')
        self.addPageTemplates([PageTemplate('portada', [marco]),
                               PageTemplate('interior', [marco], onPage=self._pie)])

    def _pie(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8.5)
        canvas.setFillColor(GRIS)
        canvas.drawString(2.5 * cm, 1.3 * cm, f'{self.pie} · Uso interno')
        canvas.drawRightString(A4[0] - 2.5 * cm, 1.3 * cm, f'Página {doc.page}')
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == 'h1':
            self.notify('TOCEntry', (0, flowable.getPlainText(), self.page))


# ── Construcción ─────────────────────────────────────────────────────────────
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


def construir(archivo: str, portada: dict, capitulos: list[tuple[str, list]]) -> int:
    ruta = os.path.join(AQUI, archivo)
    doc = Manual(ruta, portada['pie'])
    h: list = [
        Spacer(1, 3 * cm),
        Paragraph('BANCO · GERENCIA DE NORMATIVA INTERNA', E['portada_banco']),
        Paragraph(portada['titulo'], E['portada_titulo']),
        Paragraph(portada['version'], E['portada_sub']),
        Paragraph(portada['vigencia'], E['portada_sub']),
        Paragraph(portada['responsable'], E['portada_sub']),
        Spacer(1, 2.5 * cm),
        Paragraph(NOTA_FICTICIA, E['portada_nota']),
        NextPageTemplate('interior'),
        PageBreak(),
        Paragraph('Índice', E['indice_titulo']),
    ]
    toc = TableOfContents()
    toc.levelStyles = [TOC_NIVEL]
    toc.dotsMinLevel = 0
    h += [toc, PageBreak()]
    for n, (titulo, bloques) in enumerate(capitulos):
        if n:
            h.append(PageBreak())
        h.append(Paragraph(titulo, E['h1']))
        for tipo, contenido, *extra in bloques:
            if tipo == 'h2':
                h.append(Paragraph(contenido, E['h2']))
            elif tipo == 'p':
                h.append(Paragraph(contenido, E['p']))
            elif tipo == 'lista':
                h.append(ListFlowable([ListItem(Paragraph(x, E['li']), leftIndent=14, value='•') for x in contenido],
                                      bulletType='bullet', start='•', leftIndent=14, spaceAfter=7))
                h.append(Spacer(1, 4))
            elif tipo == 'tabla':
                h.append(KeepTogether([_tabla(contenido, extra[0]), Spacer(1, 9)]))
    doc.multiBuild(h)
    return doc.page


# ── Manual de Crédito de Consumo v4.2 ────────────────────────────────────────
CREDITO = [
    ('1. Disposiciones generales', [
        ('h2', '1.1 Objetivo'),
        ('p', 'El presente Manual establece las políticas, límites y procedimientos que rigen el otorgamiento, la '
              'instrumentación y el seguimiento de los créditos de consumo que el Banco concede a personas naturales. '
              'Su propósito es que toda operación de consumo se origine con un análisis homogéneo de la capacidad de '
              'pago del cliente, dentro del apetito de riesgo aprobado por el Directorio, y que cada decisión quede '
              'documentada de modo que un tercero pueda reconstruir por qué se aprobó o se negó.'),
        ('h2', '1.2 Alcance'),
        ('p', 'El Manual es de cumplimiento obligatorio para los asesores comerciales de la red de oficinas, los jefes '
              'de oficina, los gerentes zonales, los analistas de la Unidad de Admisión de Crédito y los miembros de los '
              'comités de crédito. Aplica a los productos de consumo ordinario, crédito por convenio de nómina y '
              'consolidación de deudas. Los créditos hipotecarios, vehiculares con financiamiento de concesionario, '
              'tarjetas de crédito y microcréditos se rigen por sus propios manuales y solo se mencionan aquí cuando '
              'afectan el cálculo del endeudamiento del cliente.'),
        ('h2', '1.3 Definiciones'),
        ('p', 'Para efectos de este Manual se entiende por <b>ingreso neto mensual</b> el ingreso bruto comprobado del '
              'solicitante menos los aportes obligatorios a la seguridad social, el impuesto a la renta retenido y los '
              'descuentos judiciales. Se entiende por <b>carga financiera</b> la suma de las cuotas mensuales de todas las '
              'deudas del solicitante en el sistema financiero, incluida la cuota del crédito solicitado. La '
              '<b>relación cuota/ingreso</b> es el cociente entre la cuota del nuevo crédito y el ingreso neto mensual. '
              'El <b>nivel de autonomía</b> es el monto máximo que un funcionario o comité puede aprobar según el '
              'capítulo 8. Una <b>excepción</b> es toda aprobación que se aparta de un límite de este Manual y que solo '
              'procede en las condiciones del capítulo 9.'),
        ('h2', '1.4 Responsabilidades'),
        ('p', 'El asesor comercial es responsable de la veracidad del expediente que presenta: verifica la identidad '
              'del solicitante, recaba los documentos del capítulo 10, registra la solicitud en el sistema de originación '
              'y emite una recomendación fundamentada. El asesor no puede aprobar operaciones fuera del motor de decisión '
              'automático ni modificar los datos de ingresos que arroja la verificación. El jefe de oficina revisa la '
              'calidad de los expedientes de su oficina y responde por el uso de su nivel de autonomía. La Gerencia de '
              'Riesgo de Crédito mantiene este Manual, calibra el modelo de calificación y reporta trimestralmente al '
              'Comité de Riesgos el uso de excepciones.'),
        ('p', 'Ante una duda de interpretación, prevalece el texto de este Manual sobre cualquier instructivo, correo o '
              'guía rápida. Las consultas se dirigen a la Unidad de Admisión de Crédito; sus respuestas escritas se '
              'incorporan a la siguiente versión del Manual cuando establezcan un criterio general.'),
    ]),
    ('2. Sujetos de crédito', [
        ('h2', '2.1 Personas elegibles'),
        ('p', 'Son sujetos de crédito de consumo las personas naturales, nacionales o extranjeras con residencia legal, '
              'que cumplan simultáneamente las condiciones de este capítulo. El cumplimiento de estas condiciones es '
              'necesario pero no suficiente: la operación debe además superar el análisis de capacidad de pago '
              '(capítulo 4), los límites de endeudamiento (capítulo 5) y la evaluación del historial crediticio '
              '(capítulo 6).'),
        ('h2', '2.2 Edad'),
        ('p', 'El solicitante debe tener al menos 21 años cumplidos a la fecha de la solicitud. La edad del solicitante '
              'al vencimiento de la última cuota no puede superar los 75 años. Para un solicitante de 70 años, por '
              'tanto, el plazo máximo es de 60 meses aunque el producto admita plazos mayores. El límite de 75 años '
              'responde a las condiciones de la póliza de seguro de desgravamen y solo puede exceptuarse hasta los 78 '
              'años en los términos del capítulo 9.'),
        ('h2', '2.3 Estabilidad de ingresos'),
        ('p', 'Los trabajadores dependientes deben acreditar una antigüedad laboral mínima de 12 meses continuos, de los '
              'cuales al menos 6 meses con el empleador actual. Los trabajadores con contrato a plazo fijo son elegibles '
              'siempre que el plazo del crédito no supere en más de 12 meses la fecha de término del contrato vigente. '
              'Los trabajadores independientes y profesionales en libre ejercicio deben acreditar al menos 24 meses de '
              'actividad continua mediante su registro tributario y las declaraciones de impuestos de los dos últimos '
              'ejercicios. Los jubilados acreditan su pensión con el último comprobante de pago del ente previsional.'),
        ('h2', '2.4 Ingreso mínimo'),
        ('p', 'El ingreso neto mensual mínimo para acceder a un crédito de consumo es de USD 600. Para el producto de '
              'consolidación de deudas el mínimo es de USD 900. Cuando se presenten ingresos del cónyuge o conviviente '
              'como ingresos conjuntos, este debe firmar la solicitud como codeudor y cumplir por sí mismo las '
              'condiciones de los numerales 2.2 y 2.3.'),
        ('h2', '2.5 Personas no elegibles'),
        ('p', 'No son sujetos de crédito de consumo, sin posibilidad de excepción:'),
        ('lista', [
            'quienes figuren en las listas restrictivas o de observación señaladas en el Manual PLA/FT, o tengan un '
            'reporte de operación inusual en análisis por el Oficial de Cumplimiento;',
            'quienes registren créditos castigados en cualquier entidad del sistema financiero en los últimos 36 meses;',
            'quienes presenten documentos adulterados o información falsa en cualquier solicitud anterior al Banco;',
            'los menores de edad y las personas declaradas en interdicción;',
            'quienes tengan una calificación de riesgo D según el capítulo 6.',
        ]),
        ('p', 'Los funcionarios del Banco acceden al crédito de consumo por el canal de beneficios al personal, con '
              'aprobación del Comité de Crédito Regional cualquiera sea el monto, y no por la red de oficinas.'),
    ]),
    ('3. Productos de crédito de consumo', [
        ('h2', '3.1 Catálogo'),
        ('p', 'El Banco ofrece tres productos de crédito de consumo a través de la red de oficinas. Las condiciones de '
              'monto y plazo de la tabla siguiente son límites de producto: el monto efectivamente aprobado es el menor '
              'entre el límite del producto y el que resulta de los capítulos 4 y 5.'),
        ('tabla', [
            ['Producto', 'Monto mínimo', 'Monto máximo', 'Plazo', 'Destino'],
            ['Consumo ordinario', 'USD 500', 'USD 40.000', '6 a 60 meses', 'Libre destino personal o familiar'],
            ['Convenio de nómina', 'USD 500', 'USD 50.000', '6 a 72 meses',
             'Libre destino; cuota descontada por el empleador con convenio vigente'],
            ['Consolidación de deudas', 'USD 2.000', 'USD 40.000', '12 a 60 meses',
             'Pago de deudas de consumo y tarjetas en otras entidades'],
        ], [3.4, 2.2, 2.3, 2.3, 5.8]),
        ('h2', '3.2 Consumo ordinario'),
        ('p', 'Es el producto de libre destino para clientes con ingresos comprobables que no cuentan con convenio de '
              'nómina. La cuota se debita de una cuenta del cliente en el Banco. La tasa se fija según la calificación '
              'del cliente (capítulo 6) y el tarifario vigente publicado por la Gerencia de Productos.'),
        ('h2', '3.3 Convenio de nómina'),
        ('p', 'Se otorga a trabajadores de empleadores con convenio de descuento por planilla vigente con el Banco. '
              'Como la cuota se descuenta antes de que el ingreso llegue al cliente, el riesgo de impago es menor y el '
              'Manual admite una carga financiera más alta (capítulo 5). El asesor debe verificar en el sistema que el '
              'convenio esté activo y que el empleador no registre atrasos en la remisión de descuentos en los últimos '
              '6 meses; si los registra, la operación se evalúa como consumo ordinario.'),
        ('h2', '3.4 Consolidación de deudas'),
        ('p', 'Su destino es cancelar deudas de consumo y tarjetas de crédito en otras entidades. El desembolso se '
              'realiza directamente a las entidades acreedoras contra certificado de saldo con vigencia no mayor a 10 '
              'días; solo el remanente, si lo hay, se abona al cliente y no puede superar el 20 % del monto aprobado. '
              'Para el cálculo de la carga financiera se excluyen las cuotas de las deudas que se cancelan con el '
              'crédito, siempre que figuren en los certificados de saldo.'),
        ('h2', '3.5 Seguros asociados'),
        ('p', 'Todo crédito de consumo lleva seguro de desgravamen por el saldo insoluto. El cliente puede endosar una '
              'póliza propia equivalente, que la Unidad de Admisión debe validar antes del desembolso. El seguro de '
              'desempleo es opcional y no puede condicionarse la aprobación a su contratación.'),
    ]),
    ('4. Análisis de capacidad de pago', [
        ('h2', '4.1 Principio'),
        ('p', 'La decisión de crédito se basa en la capacidad del solicitante para pagar con sus ingresos recurrentes, '
              'no en las garantías que ofrece. Una garantía mitiga la pérdida si el cliente incumple, pero no convierte '
              'en viable una operación cuya cuota el cliente no puede pagar. Ningún crédito de consumo se aprueba sobre '
              'la base exclusiva de una garantía.'),
        ('h2', '4.2 Ingresos computables'),
        ('p', 'Para trabajadores dependientes se computa el 100 % del ingreso fijo neto, promediando los tres últimos '
              'roles de pago. Los ingresos variables (comisiones, horas extra, bonificaciones) se computan al 80 % del '
              'promedio de los últimos 6 meses y solo si se han percibido en al menos 5 de esos 6 meses. Para '
              'trabajadores independientes se computa el 70 % del promedio mensual de ingresos netos declarados en los '
              'dos últimos ejercicios fiscales, contrastado con los movimientos de los últimos 6 meses de sus cuentas; '
              'si los movimientos son menores que lo declarado, se toma el menor de los dos valores. Los ingresos por '
              'arriendos se computan al 60 % siempre que exista contrato escrito con vigencia superior al plazo del '
              'crédito o al menos 12 meses. Las remesas del exterior y los ingresos sin respaldo documental no se '
              'computan.'),
        ('h2', '4.3 Verificación'),
        ('p', 'El asesor verifica los ingresos del dependiente con el certificado laboral emitido dentro de los 30 días '
              'previos y la consulta a la base de aportes a la seguridad social. Si el ingreso reportado en la base de '
              'aportes es menor que el del certificado, se computa el de la base. Para independientes, la verificación '
              'incluye la consulta del registro tributario. Toda diferencia mayor al 15 % entre el ingreso declarado '
              'en la solicitud y el verificado debe registrarse en el expediente con la explicación del cliente.'),
        ('h2', '4.4 Relación cuota/ingreso'),
        ('p', 'La cuota del crédito solicitado no puede superar el 30 % del ingreso neto mensual computable. Este '
              'límite es independiente del límite de carga financiera total del capítulo 5: ambos deben cumplirse, '
              'y el monto aprobado es el que respeta el más restrictivo de los dos.'),
        ('h2', '4.5 Gastos familiares'),
        ('p', 'El sistema de originación descuenta del ingreso neto un gasto familiar presunto de USD 250 por el '
              'solicitante y USD 120 por cada dependiente económico declarado. Si el ingreso neto, menos el gasto '
              'familiar presunto y la carga financiera total, resulta inferior a USD 150, la operación se rechaza por '
              'insuficiencia de ingreso disponible, aunque se cumplan los porcentajes de los numerales anteriores.'),
    ]),
    ('5. Endeudamiento máximo', [
        ('h2', '5.1 Límite de carga financiera total'),
        ('p', 'El endeudamiento máximo de un cliente se mide por su carga financiera total: la suma de todas sus cuotas '
              'mensuales en el sistema financiero, incluida la del crédito solicitado, dividida entre su ingreso neto '
              'mensual computable. El endeudamiento máximo permitido para un crédito de consumo es el siguiente:'),
        ('tabla', [
            ['Tipo de solicitante', 'Carga financiera total máxima', 'Con excepción (capítulo 9)'],
            ['Trabajador dependiente', '40 % del ingreso neto', 'hasta 45 %'],
            ['Trabajador independiente', '35 % del ingreso neto', 'hasta 40 %'],
            ['Convenio de nómina con descuento directo', '45 % del ingreso neto', 'hasta 50 %'],
            ['Jubilado', '35 % de la pensión neta', 'sin excepción'],
        ], [6.0, 5.0, 5.0]),
        ('h2', '5.2 Límite por saldo'),
        ('p', 'Además del límite de carga financiera, la deuda total del cliente en el sistema financiero, incluido el '
              'nuevo crédito y excluidas las deudas hipotecarias, no puede superar 12 veces su ingreso neto mensual '
              'computable si es dependiente, ni 10 veces si es independiente. La suma de los créditos de consumo '
              'vigentes del cliente con el Banco no puede superar USD 60.000, cualquiera sea su ingreso.'),
        ('h2', '5.3 Cómputo de tarjetas y líneas de crédito'),
        ('p', 'Las tarjetas de crédito y las líneas rotativas se computan con una cuota presunta del 5 % del cupo '
              'utilizado o del 3 % del cupo total aprobado, el mayor de los dos, aunque el cliente pague el mínimo o '
              'nada en el mes. Las tarjetas sin utilizar en los últimos 12 meses y que el cliente cancele antes del '
              'desembolso no se computan, previo certificado de cancelación.'),
        ('h2', '5.4 Ejemplo de cálculo'),
        ('p', 'Un trabajador dependiente con ingreso neto computable de USD 2.000 tiene una carga financiera máxima de '
              'USD 800 (40 %). Si ya paga USD 350 mensuales en otras deudas, la cuota disponible es de USD 450. Por la '
              'relación cuota/ingreso del numeral 4.4, la cuota del nuevo crédito tampoco puede superar USD 600 (30 %). '
              'La cuota máxima es el menor de los dos valores, USD 450. El monto máximo del crédito es el que genera esa '
              'cuota al plazo y tasa aplicables, siempre que la deuda total resultante no supere USD 24.000 (12 veces '
              'el ingreso) y se respeten los límites del producto.'),
        ('h2', '5.5 Deudas del cónyuge'),
        ('p', 'Cuando se computan ingresos conjuntos, se computan también todas las deudas del cónyuge o conviviente. '
              'No está permitido sumar el ingreso del cónyuge y omitir sus deudas. Si el régimen patrimonial es de '
              'separación de bienes y solo se computa el ingreso del solicitante, las deudas del cónyuge no se suman.'),
    ]),
    ('6. Historial crediticio y calificación', [
        ('h2', '6.1 Consulta al buró de crédito'),
        ('p', 'Antes de registrar la solicitud, el asesor obtiene la autorización firmada del cliente para consultar '
              'el buró de crédito y la central de riesgos. La consulta tiene una vigencia de 30 días; si el desembolso '
              'ocurre después, debe repetirse. El resultado se adjunta al expediente y no puede entregarse en copia al '
              'cliente por el asesor: el cliente lo solicita directamente al buró.'),
        ('h2', '6.2 Modelo de calificación'),
        ('p', 'El motor de decisión asigna a cada solicitante una puntuación entre 300 y 900 que combina el '
              'comportamiento de pago, el nivel de endeudamiento, la antigüedad en el sistema financiero y la '
              'relación con el Banco. La puntuación se traduce en una calificación con las siguientes consecuencias:'),
        ('tabla', [
            ['Calificación', 'Puntuación', 'Tratamiento'],
            ['A', '750 o más', 'Elegible. Sin garantía hasta USD 15.000. Aprobación por el nivel que corresponda al monto.'],
            ['B', '650 a 749', 'Elegible. Requiere codeudor o garante para montos superiores a USD 15.000.'],
            ['C', '550 a 649', 'Elegible solo hasta USD 5.000, con garante, y con aprobación mínima del Jefe de Oficina.'],
            ['D', 'menos de 550', 'No elegible. No admite excepción.'],
        ], [2.6, 2.8, 10.6]),
        ('h2', '6.3 Morosidad'),
        ('p', 'No es elegible el solicitante que registre, a la fecha de la consulta, cualquier deuda vencida en el '
              'sistema financiero, salvo que presente el certificado de cancelación. Tampoco lo es quien haya registrado '
              'atrasos superiores a 30 días en los últimos 12 meses, o superiores a 60 días en los últimos 24 meses. '
              'Los atrasos de hasta 15 días por única vez en los últimos 12 meses no afectan la elegibilidad, pero el '
              'asesor debe dejar constancia de la explicación del cliente.'),
        ('h2', '6.4 Clientes sin historial'),
        ('p', 'Un solicitante sin historial crediticio no es por ello inelegible. El motor le asigna una calificación '
              'C provisional y la operación se limita a USD 5.000 y 36 meses. Si el cliente tiene cuenta de nómina en '
              'el Banco con al menos 6 meses de acreditaciones, la calificación provisional es B.'),
    ]),
    ('7. Garantías', [
        ('h2', '7.1 Criterio general'),
        ('p', 'La garantía se exige en función del monto y de la calificación del cliente. Recordando el numeral 4.1, '
              'la garantía no sustituye la capacidad de pago: un crédito que no cumple los capítulos 4 y 5 se niega '
              'aunque el cliente ofrezca una garantía que cubra el monto.'),
        ('h2', '7.2 Garantía requerida según monto'),
        ('tabla', [
            ['Monto del crédito', 'Garantía mínima', 'Cobertura exigida'],
            ['Hasta USD 15.000', 'Sin garantía (quirografario) para calificación A o B', 'No aplica'],
            ['USD 15.001 a USD 30.000', 'Codeudor o garante solvente', 'Ingreso neto del garante de al menos 1,5 veces la cuota'],
            ['Más de USD 30.000', 'Garantía real (prenda o hipoteca) o depósito a plazo pignorado',
             '140 % del monto para garantía real; 100 % para depósito pignorado'],
        ], [4.0, 6.0, 6.0]),
        ('h2', '7.3 Codeudores y garantes'),
        ('p', 'El codeudor o garante debe cumplir por sí mismo las condiciones del capítulo 2 y tener calificación A '
              'o B. Su propia carga financiera, incluyendo la cuota del crédito que garantiza, no puede superar el '
              '50 % de su ingreso neto. Una misma persona no puede ser garante de más de dos créditos de consumo '
              'vigentes en el Banco. El garante firma la solicitud y el pagaré en presencia del asesor o mediante '
              'firma electrónica calificada.'),
        ('h2', '7.4 Garantías reales'),
        ('p', 'La prenda sobre vehículos solo se acepta para vehículos livianos con antigüedad no mayor a 5 años al '
              'vencimiento del crédito, valorados por un perito del registro del Banco con avalúo de no más de 90 días. '
              'La hipoteca se valora con avalúo de un perito calificado y se inscribe antes del desembolso. Los bienes '
              'en garantía deben contar con seguro endosado a favor del Banco durante toda la vigencia del crédito.'),
        ('h2', '7.5 Depósitos pignorados'),
        ('p', 'Un depósito a plazo en el Banco puede pignorarse como garantía por el 100 % del monto. En ese caso el '
              'crédito puede aprobarse aunque la carga financiera exceda en hasta 5 puntos porcentuales el límite del '
              'capítulo 5, sin tratarse como excepción, siempre que el vencimiento del depósito sea igual o posterior '
              'al del crédito.'),
    ]),
    ('8. Niveles de autonomía y aprobación', [
        ('h2', '8.1 Principio de doble firma'),
        ('p', 'Toda operación de crédito de consumo requiere, al menos, dos intervenciones: la de quien origina y '
              'recomienda (el asesor comercial) y la de quien aprueba. Nadie puede aprobar una operación que él mismo '
              'originó. El motor de decisión automático cuenta como aprobador solo en el tramo del asesor y solo cuando '
              'su resultado es «aprobado sin observaciones».'),
        ('h2', '8.2 Tabla de autonomías'),
        ('p', 'Los niveles de aprobación se determinan por el riesgo total del cliente con el Banco (el monto '
              'solicitado más los saldos de consumo vigentes), no solo por el monto de la nueva operación:'),
        ('tabla', [
            ['Nivel', 'Riesgo total del cliente', 'Condiciones'],
            ['Asesor comercial con motor automático', 'Hasta USD 5.000', 'Calificación A, sin excepciones, motor en «aprobado»'],
            ['Jefe de Oficina', 'Hasta USD 15.000', 'Calificación A, B o C; sin excepciones'],
            ['Gerente Zonal de Crédito', 'Hasta USD 30.000', 'Puede aprobar excepciones de operaciones de hasta USD 15.000'],
            ['Comité de Crédito Regional', 'Hasta USD 60.000', 'Puede aprobar excepciones de operaciones de hasta USD 30.000'],
            ['Comité de Riesgos (central)', 'Más de USD 60.000', 'Toda excepción de más de USD 30.000 y todo crédito a PEP'],
        ], [5.0, 4.2, 6.8]),
        ('h2', '8.3 Operaciones con personas expuestas políticamente'),
        ('p', 'Todo crédito a una persona expuesta políticamente, a sus familiares o colaboradores cercanos, en los '
              'términos del Manual PLA/FT, requiere la aprobación previa del Oficial de Cumplimiento a la vinculación '
              'y la aprobación del Comité de Riesgos, cualquiera sea el monto.'),
        ('h2', '8.4 Registro de la decisión'),
        ('p', 'La aprobación o negación se registra en el sistema de originación con el nombre del aprobador, la fecha, '
              'las condiciones aprobadas y, en caso de negación, el motivo codificado. Las aprobaciones por correo, '
              'mensajería o verbales no tienen validez. La aprobación tiene una vigencia de 30 días calendario; vencido '
              'el plazo sin desembolso, la operación debe volver a evaluarse.'),
    ]),
    ('9. Excepciones', [
        ('h2', '9.1 Qué es una excepción'),
        ('p', 'Es excepción toda aprobación que se aparta de un límite cuantitativo de este Manual. Las excepciones '
              'existen para casos en los que el análisis documenta factores mitigantes que el modelo general no '
              'captura; no son un mecanismo para cumplir metas comerciales. El uso de excepciones por oficina se '
              'supervisa mensualmente.'),
        ('h2', '9.2 Excepciones permitidas'),
        ('p', 'Solo pueden exceptuarse los siguientes límites, y únicamente dentro de los márgenes indicados:'),
        ('lista', [
            'carga financiera total: hasta 5 puntos porcentuales sobre el límite del numeral 5.1, salvo jubilados;',
            'antigüedad laboral del dependiente: hasta un mínimo de 6 meses continuos si el solicitante acredita '
            'al menos 3 años de experiencia en el mismo sector;',
            'edad al vencimiento: hasta 78 años, con aceptación expresa de la aseguradora de desgravamen;',
            'antigüedad del vehículo en prenda: hasta 7 años al vencimiento, con cobertura del 160 %.',
        ]),
        ('h2', '9.3 Límites que no admiten excepción'),
        ('p', 'No admiten excepción: las personas no elegibles del numeral 2.5, la calificación D, la relación '
              'cuota/ingreso del numeral 4.4, el ingreso disponible mínimo del numeral 4.5, el tope de USD 60.000 por '
              'cliente del numeral 5.2 y la exigencia de doble firma del numeral 8.1. Tampoco puede exceptuarse '
              'ningún requisito del Manual PLA/FT.'),
        ('h2', '9.4 Quién aprueba'),
        ('p', 'Una excepción siempre la aprueba el nivel inmediatamente superior al que correspondería por monto según '
              'el numeral 8.2. Si concurren dos o más excepciones en la misma operación, la aprueba el Comité de Crédito '
              'Regional o el Comité de Riesgos, según el monto. El asesor no puede solicitar una excepción sin una '
              'justificación escrita que identifique el factor mitigante y la evidencia que lo respalda.'),
        ('h2', '9.5 Límite de uso y reporte'),
        ('p', 'Las operaciones aprobadas con excepción no pueden superar el 5 % del número de operaciones de consumo '
              'desembolsadas por cada oficina en el mes. Superado ese porcentaje, toda nueva excepción de la oficina '
              'pasa al Comité de Crédito Regional hasta el cierre del mes. La Gerencia de Riesgo de Crédito reporta al '
              'Comité de Riesgos, cada trimestre, el número de excepciones, su tipo y la morosidad de las operaciones '
              'exceptuadas frente a las no exceptuadas.'),
    ]),
    ('10. Documentación y expediente', [
        ('h2', '10.1 Documentos mínimos'),
        ('p', 'El expediente de cada operación debe contener, antes de su envío a aprobación:'),
        ('lista', [
            'la solicitud de crédito (formulario SC-01) completa y firmada por el solicitante y, si los hay, el '
            'cónyuge, codeudores y garantes;',
            'copia de la cédula de identidad vigente de cada firmante, verificada contra el registro civil;',
            'para dependientes: certificado laboral de no más de 30 días y los tres últimos roles de pago;',
            'para independientes: declaraciones de impuestos de los dos últimos ejercicios y extractos bancarios de '
            'los últimos 6 meses;',
            'autorización firmada de consulta al buró de crédito y el resultado de la consulta;',
            'el formulario de conocimiento del cliente actualizado conforme al Manual PLA/FT;',
            'para consolidación de deudas: certificados de saldo de las deudas a cancelar.',
        ]),
        ('h2', '10.2 Solicitud en formato digital'),
        ('p', 'Cuando la solicitud SC-01 se recibe en PDF por canales digitales, el asesor verifica que los datos '
              'capturados por el sistema coincidan con el documento: nombre, número de cédula, ingresos declarados, '
              'monto y plazo solicitados. Los campos que el sistema no pueda leer con certeza se marcan como '
              'pendientes y los completa el asesor a la vista del documento; nunca se completan con supuestos. La '
              'firma electrónica debe ser verificable.'),
        ('h2', '10.3 Custodia y confidencialidad'),
        ('p', 'El expediente contiene datos personales y financieros del cliente. Se custodia exclusivamente en el '
              'gestor documental del Banco; está prohibido guardar copias en equipos personales, correo, carpetas '
              'compartidas no autorizadas o herramientas de mensajería. El expediente se conserva durante 7 años '
              'contados desde la cancelación total del crédito, sin perjuicio de plazos mayores del Manual PLA/FT.'),
        ('h2', '10.4 Calidad del expediente'),
        ('p', 'La Unidad de Admisión revisa una muestra del 10 % de los expedientes de cada oficina al mes. Un '
              'expediente con documentos faltantes o vencidos al momento de la aprobación se registra como hallazgo '
              'y se comunica al jefe de oficina, que debe regularizarlo en 5 días hábiles.'),
    ]),
    ('11. Desembolso, seguimiento y reestructuración', [
        ('h2', '11.1 Condiciones previas al desembolso'),
        ('p', 'El desembolso procede solo cuando la aprobación está vigente, el pagaré y la tabla de amortización han '
              'sido firmados, las garantías están constituidas e inscritas cuando corresponda, y el seguro de '
              'desgravamen está activo. El sistema bloquea el desembolso si alguna de estas condiciones no está '
              'registrada. El desembolso se abona en una cuenta del titular en el Banco, salvo en consolidación de '
              'deudas (numeral 3.4).'),
        ('h2', '11.2 Seguimiento de la cartera'),
        ('p', 'La oficina que originó la operación es responsable de su gestión preventiva y de la cobranza '
              'temprana. Los atrasos de 1 a 30 días los gestiona la oficina por teléfono y mensajes; de 31 a 90 días, '
              'la Unidad de Cobranza; a partir de 91 días, la operación pasa a cobranza judicial previa evaluación de '
              'la Gerencia Legal.'),
        ('h2', '11.3 Reestructuración'),
        ('p', 'Una operación de consumo puede reestructurarse por una sola vez cuando el cliente demuestre una '
              'disminución temporal de ingresos. La reestructuración requiere que el cliente haya pagado al menos 3 '
              'cuotas del crédito original, que el nuevo plazo no exceda en más de 24 meses el remanente y que la nueva '
              'cuota cumpla los límites de los capítulos 4 y 5 con el ingreso actual. La aprueba el nivel superior al '
              'que aprobó la operación original. La operación reestructurada mantiene la calificación de riesgo que '
              'tenía al momento de reestructurarse durante al menos 6 meses de pagos puntuales.'),
    ]),
    ('12. Control de cambios', [
        ('p', 'Este Manual es mantenido por la Gerencia de Riesgo de Crédito y aprobado por el Comité de Riesgos. Toda '
              'modificación se publica en el repositorio de manuales aprobados, que es la única fuente oficial; las '
              'copias impresas o descargadas no están controladas.'),
        ('tabla', [
            ['Versión', 'Fecha', 'Cambios principales'],
            ['4.0', 'Febrero 2024', 'Reestructuración del manual; nuevo modelo de calificación de 300 a 900 puntos.'],
            ['4.1', 'Agosto 2025', 'Producto de consolidación de deudas; cuota presunta de tarjetas al 5 % del cupo utilizado.'],
            ['4.2', 'Marzo 2026', 'Límite de 5 % de excepciones por oficina; verificación de solicitudes en PDF (10.2); '
                                  'tope de USD 60.000 por cliente.'],
        ], [2.0, 3.0, 11.0]),
        ('p', 'Las sugerencias de cambio se envían a la Gerencia de Riesgo de Crédito con la justificación y, cuando '
              'corresponda, el análisis de impacto en morosidad. Los cambios que afectan límites cuantitativos requieren '
              'además la opinión previa de Riesgo Operativo y de Cumplimiento.'),
    ]),
]

# ── Manual PLA/FT v3.0 ───────────────────────────────────────────────────────
PLAFT = [
    ('1. Disposiciones generales', [
        ('h2', '1.1 Objetivo'),
        ('p', 'Este Manual establece las políticas y procedimientos que el Banco aplica para prevenir que sus productos '
              'y servicios sean utilizados para el lavado de activos o el financiamiento del terrorismo (PLA/FT). '
              'Desarrolla el sistema de prevención aprobado por el Directorio y es de cumplimiento obligatorio para '
              'todos los directores, funcionarios y empleados del Banco.'),
        ('h2', '1.2 Definiciones'),
        ('p', '<b>Lavado de activos</b> es el proceso por el cual se da apariencia de legitimidad a bienes o recursos '
              'provenientes de actividades ilícitas. <b>Financiamiento del terrorismo</b> es la provisión o recolección '
              'de fondos, de origen lícito o ilícito, con la intención de que se utilicen para actos terroristas. Una '
              '<b>operación inusual</b> es aquella cuyo monto, frecuencia o características no guardan relación con el '
              'perfil del cliente o con su actividad económica declarada. Una <b>operación sospechosa</b> es la '
              'operación inusual que, tras el análisis del Oficial de Cumplimiento, no tiene una justificación '
              'razonable. El <b>beneficiario final</b> es la persona natural que en último término posee o controla '
              'al cliente o en cuyo nombre se realiza la operación.'),
        ('h2', '1.3 Enfoque basado en riesgo'),
        ('p', 'El Banco aplica un enfoque basado en riesgo: la intensidad de las medidas de conocimiento y monitoreo '
              'es proporcional al riesgo de cada cliente, producto, canal y zona geográfica. Ningún objetivo comercial '
              'justifica omitir una medida de este Manual. Ante una contradicción entre este Manual y el Manual de '
              'Crédito de Consumo, prevalece este Manual.'),
    ]),
    ('2. Estructura y responsabilidades', [
        ('h2', '2.1 Oficial de Cumplimiento'),
        ('p', 'El Oficial de Cumplimiento es designado por el Directorio, tiene independencia funcional y reporta '
              'directamente al Comité de Cumplimiento. Es el único funcionario autorizado para evaluar las operaciones '
              'inusuales reportadas por la red y decidir si constituyen operaciones sospechosas que deban reportarse a '
              'la unidad de inteligencia financiera competente. También aprueba la vinculación de personas expuestas '
              'políticamente y de clientes de riesgo alto.'),
        ('h2', '2.2 Asesores comerciales'),
        ('p', 'El asesor comercial es la primera línea de defensa. Le corresponde aplicar la debida diligencia de '
              'conocimiento del cliente al vincularlo y en cada actualización, verificar las listas restrictivas antes '
              'de abrir cualquier producto, estar atento a las señales de alerta del capítulo 7 y reportar al Oficial '
              'de Cumplimiento toda operación inusual que detecte, en los plazos del capítulo 8. El asesor no califica '
              'una operación como sospechosa ni decide si se reporta a las autoridades: su obligación es reportar '
              'internamente lo inusual.'),
        ('h2', '2.3 Jefes de oficina'),
        ('p', 'El jefe de oficina supervisa que los expedientes de conocimiento del cliente de su oficina estén '
              'completos y actualizados, aprueba la vinculación de clientes de riesgo medio con información '
              'incompleta subsanable en un plazo de 15 días y colabora con el Oficial de Cumplimiento en los '
              'análisis que este requiera.'),
        ('h2', '2.4 Deber de reserva'),
        ('p', 'Está prohibido informar al cliente, o a cualquier tercero, que su operación ha sido reportada como '
              'inusual, que está siendo analizada o que se ha enviado un reporte a las autoridades. La revelación de '
              'esta información constituye una falta grave, además de las responsabilidades legales que correspondan. '
              'El asesor que necesite suspender o demorar una operación mientras consulta al Oficial de Cumplimiento '
              'lo hará invocando motivos operativos generales.'),
    ]),
    ('3. Conocimiento del cliente (KYC)', [
        ('h2', '3.1 Identificación'),
        ('p', 'Antes de abrir cualquier producto, el asesor identifica al cliente con su cédula de identidad o '
              'pasaporte vigente, verifica los datos contra el registro civil o, para extranjeros, contra el registro '
              'migratorio, y registra la verificación biométrica cuando el canal lo permita. No se abren productos a '
              'nombre de personas que no se presenten o no se identifiquen por un canal digital aprobado.'),
        ('h2', '3.2 Información mínima'),
        ('p', 'El formulario de conocimiento del cliente registra, como mínimo: datos de identificación y contacto, '
              'actividad económica y empleador, ingresos mensuales y patrimonio aproximado, origen de los fondos, '
              'propósito de la relación comercial, perfil transaccional esperado (monto y número de operaciones '
              'mensuales por producto), condición de persona expuesta políticamente, y si actúa por cuenta propia o de '
              'un tercero. Si actúa por cuenta de un tercero, se identifica también al beneficiario final.'),
        ('h2', '3.3 Listas restrictivas'),
        ('p', 'Antes de vincular al cliente y antes de cada desembolso de crédito, el sistema verifica al cliente, '
              'codeudores y garantes contra las listas de sanciones del Consejo de Seguridad de las Naciones Unidas, '
              'las listas de sanciones internacionales adoptadas por el Banco y la lista interna de personas no '
              'vinculables. Una coincidencia bloquea la operación y genera un aviso automático al Oficial de '
              'Cumplimiento. El asesor no puede descartar por su cuenta una coincidencia, aunque crea que se trata de '
              'un homónimo.'),
        ('h2', '3.4 Actualización'),
        ('p', 'La información del cliente se actualiza con una periodicidad que depende de su nivel de riesgo: cada '
              '12 meses para riesgo alto, cada 24 meses para riesgo medio y cada 36 meses para riesgo bajo. También se '
              'actualiza cuando el cliente solicita un nuevo producto de crédito, cuando cambia su actividad económica '
              'o cuando sus operaciones se apartan de su perfil transaccional. Un cliente con información vencida no '
              'puede contratar nuevos productos hasta actualizarla.'),
    ]),
    ('4. Segmentación y matriz de riesgo', [
        ('h2', '4.1 Factores de riesgo'),
        ('p', 'Cada cliente recibe una calificación de riesgo PLA/FT calculada por el sistema a partir de cuatro '
              'factores: el propio cliente (actividad económica, condición de PEP, nacionalidad y residencia), los '
              'productos que utiliza, los canales por los que opera y las zonas geográficas de origen y destino de sus '
              'fondos. Cada factor se puntúa de 1 a 5 y la calificación es el promedio ponderado.'),
        ('tabla', [
            ['Factor', 'Ponderación', 'Ejemplos de puntuación alta (4 o 5)'],
            ['Cliente', '40 %', 'PEP; actividades intensivas en efectivo; casas de cambio; comercio de metales preciosos'],
            ['Producto', '20 %', 'Transferencias internacionales; depósitos en efectivo frecuentes'],
            ['Canal', '15 %', 'Vinculación no presencial; operaciones por terceros autorizados'],
            ['Zona geográfica', '25 %', 'Países con deficiencias estratégicas según listas internacionales; zonas de frontera'],
        ], [3.2, 2.6, 10.2]),
        ('h2', '4.2 Niveles de riesgo'),
        ('p', 'Una calificación menor a 2,5 corresponde a riesgo bajo; entre 2,5 y 3,49, a riesgo medio; de 3,5 en '
              'adelante, a riesgo alto. Son de riesgo alto, cualquiera sea su puntuación, las personas expuestas '
              'políticamente y los clientes con un reporte de operación sospechosa en los últimos 24 meses. El asesor '
              'no puede modificar la calificación; si considera que no refleja el riesgo real, lo informa al Oficial '
              'de Cumplimiento.'),
        ('h2', '4.3 Consecuencias de la calificación'),
        ('p', 'La calificación determina el tipo de debida diligencia (simplificada, estándar o reforzada), la '
              'periodicidad de actualización del numeral 3.4 y la intensidad del monitoreo transaccional. Los clientes '
              'de riesgo alto requieren debida diligencia reforzada conforme al capítulo 5.'),
    ]),
    ('5. Debida diligencia reforzada', [
        ('h2', '5.1 Cuándo se aplica'),
        ('p', 'La debida diligencia reforzada es obligatoria para: los clientes de riesgo alto según el capítulo 4; las '
              'personas expuestas políticamente, sus familiares y colaboradores cercanos; los clientes con residencia '
              'o fondos provenientes de países con deficiencias estratégicas; los clientes que realicen depósitos en '
              'efectivo por un total igual o superior a USD 10.000 en un mes calendario; y las solicitudes de crédito '
              'en las que el pago anticipado o la cancelación se prevea con fondos de terceros.'),
        ('h2', '5.2 Medidas'),
        ('p', 'La debida diligencia reforzada comprende, además de las medidas estándar:'),
        ('lista', [
            'documentar el origen de los fondos y del patrimonio con respaldos verificables (contratos, escrituras, '
            'declaraciones fiscales, estados financieros);',
            'verificar el domicilio y la actividad económica mediante visita o fuentes independientes;',
            'obtener la aprobación del Jefe de Oficina y el visto bueno del Oficial de Cumplimiento antes de '
            'activar el producto;',
            'aplicar monitoreo transaccional reforzado con umbrales de alerta más bajos;',
            'actualizar la información al menos cada 12 meses.',
        ]),
        ('h2', '5.3 Negativa a proporcionar información'),
        ('p', 'Si el cliente se niega a proporcionar la información de la debida diligencia reforzada, o la que '
              'entrega no resulta verificable, el Banco no inicia la relación comercial ni aprueba el crédito '
              'solicitado. Si el cliente ya está vinculado, el asesor lo reporta como operación inusual y el Oficial '
              'de Cumplimiento decide si procede terminar la relación.'),
        ('h2', '5.4 Relación con la evaluación de crédito'),
        ('p', 'La debida diligencia reforzada es independiente del análisis de crédito. Una solicitud puede cumplir '
              'todos los límites del Manual de Crédito de Consumo y, aun así, no poder aprobarse mientras la debida '
              'diligencia reforzada no esté completa y aprobada.'),
    ]),
    ('6. Personas expuestas políticamente (PEP)', [
        ('h2', '6.1 Definición'),
        ('p', 'Son personas expuestas políticamente quienes desempeñan o han desempeñado en los últimos 2 años '
              'funciones públicas prominentes, en el país o en el extranjero: jefes de Estado o de gobierno, ministros '
              'y viceministros, legisladores, magistrados de las cortes superiores, altos mandos de las fuerzas armadas '
              'y de la policía, directores de empresas públicas, embajadores, autoridades de organismos de control y '
              'dirigentes nacionales de partidos políticos. También lo son los altos directivos de organizaciones '
              'internacionales.'),
        ('h2', '6.2 Familiares y colaboradores cercanos'),
        ('p', 'Reciben el mismo tratamiento que la PEP su cónyuge o conviviente, sus parientes hasta el segundo grado '
              'de consanguinidad (padres, hijos, hermanos, abuelos y nietos) y primero de afinidad (suegros, yernos y '
              'nueras), y las personas con quienes mantenga una relación comercial o societaria estrecha conocida.'),
        ('h2', '6.3 Identificación'),
        ('p', 'El asesor pregunta al cliente si es PEP, familiar o colaborador cercano de una PEP y registra su '
              'declaración firmada. El sistema contrasta además al cliente con la base de datos de PEP que mantiene '
              'Cumplimiento. Si el cliente adquiere la condición de PEP después de vinculado, el asesor que lo detecte '
              'lo informa al Oficial de Cumplimiento en un plazo de 5 días hábiles.'),
        ('h2', '6.4 Aprobación y monitoreo'),
        ('p', 'La vinculación de una PEP, y la contratación de cualquier producto de crédito por su parte, requiere la '
              'aprobación previa del Oficial de Cumplimiento. Los créditos a PEP requieren además la aprobación del '
              'Comité de Riesgos conforme al Manual de Crédito de Consumo, cualquiera sea el monto. La relación con '
              'una PEP se revisa al menos una vez al año, con debida diligencia reforzada, y su condición se mantiene '
              'durante los 2 años siguientes a la fecha en que dejó el cargo.'),
    ]),
    ('7. Señales de alerta', [
        ('h2', '7.1 Uso de las señales'),
        ('p', 'Las señales de alerta son situaciones que, sin constituir por sí mismas un delito, justifican un '
              'examen más atento. La presencia de una señal no obliga a rechazar la operación, pero sí a analizarla '
              'y, si no se encuentra una explicación razonable y documentada, a reportarla como inusual al Oficial de '
              'Cumplimiento. La lista no es exhaustiva.'),
        ('h2', '7.2 Señales en la vinculación y en el crédito'),
        ('lista', [
            'el cliente se muestra reacio a proporcionar información, entrega datos inconsistentes o documentos que '
            'parecen alterados;',
            'el cliente solicita un crédito que no necesita según su patrimonio declarado, y ofrece cancelarlo '
            'anticipadamente en poco tiempo;',
            'el crédito se cancela anticipadamente con fondos en efectivo o de terceros sin relación aparente;',
            'el cliente ofrece como garantía depósitos o bienes cuyo origen no puede explicar;',
            'un tercero acompaña al cliente, responde por él o da instrucciones sobre el destino de los fondos;',
            'el destino declarado del crédito no guarda relación con la actividad o necesidades del cliente;',
            'el cliente pregunta cómo evitar los registros o reportes de operaciones en efectivo.',
        ]),
        ('h2', '7.3 Señales en las operaciones'),
        ('lista', [
            'depósitos en efectivo fraccionados por debajo de USD 10.000 en días consecutivos o en varias oficinas;',
            'movimientos que no corresponden al perfil transaccional declarado, sin explicación del cliente;',
            'transferencias frecuentes hacia o desde países con deficiencias estratégicas;',
            'cuentas que reciben muchos depósitos de terceros y se vacían rápidamente;',
            'cambios frecuentes e injustificados de domicilio, teléfono o representante.',
        ]),
    ]),
    ('8. Operaciones inusuales y reporte al Oficial de Cumplimiento', [
        ('h2', '8.1 Obligación de reportar'),
        ('p', 'Todo funcionario que detecte una operación inusual debe reportarla al Oficial de Cumplimiento mediante '
              'el formulario de reporte interno ROI-01 del sistema de cumplimiento, dentro de las 24 horas siguientes '
              'a su detección. El reporte es obligatorio aunque la operación no se haya concretado (por ejemplo, un '
              'crédito que el cliente desistió al pedírsele información) y aunque el funcionario no tenga certeza de '
              'que exista un delito.'),
        ('h2', '8.2 Contenido del reporte'),
        ('p', 'El reporte ROI-01 describe los hechos de manera objetiva: quién es el cliente, qué operación intentó o '
              'realizó, montos, fechas, qué señal de alerta se observó y qué explicación dio el cliente, si la dio. Se '
              'adjuntan los documentos disponibles. El reporte no debe incluir opiniones sobre la culpabilidad del '
              'cliente ni conclusiones que corresponden al Oficial de Cumplimiento.'),
        ('h2', '8.3 Qué hace el asesor mientras tanto'),
        ('p', 'El asesor no informa al cliente del reporte (numeral 2.4). Si la operación está pendiente, consulta al '
              'Oficial de Cumplimiento antes de ejecutarla; el Oficial responde en un plazo máximo de 2 días hábiles. '
              'Si la operación es un crédito, su evaluación queda suspendida hasta la respuesta del Oficial. El asesor '
              'conserva el número de reporte asignado y no guarda copias del reporte fuera del sistema de '
              'cumplimiento.'),
        ('h2', '8.4 Análisis y reporte externo'),
        ('p', 'El Oficial de Cumplimiento analiza el reporte, puede solicitar información adicional a la oficina y '
              'decide si la operación es sospechosa. Si lo es, la reporta a la unidad de inteligencia financiera '
              'competente dentro de los plazos legales. La decisión y sus fundamentos se documentan aunque se '
              'concluya que la operación no es sospechosa.'),
        ('h2', '8.5 Registro de operaciones en efectivo'),
        ('p', 'Toda operación en efectivo igual o superior a USD 10.000, o el conjunto de operaciones en efectivo de un '
              'mismo cliente que sumen ese monto en 30 días, se registra en el formulario de origen de fondos firmado '
              'por el cliente. Este registro es independiente del reporte de operación inusual: una operación puede '
              'requerir ambos.'),
    ]),
    ('9. Conservación de registros, capacitación y sanciones', [
        ('h2', '9.1 Conservación de registros'),
        ('p', 'Los documentos de conocimiento del cliente, los registros de operaciones y los reportes internos y '
              'externos se conservan durante 10 años, contados desde la terminación de la relación comercial o desde '
              'la fecha de la operación ocasional. Se conservan en el gestor documental y en el sistema de '
              'cumplimiento, con acceso restringido y trazabilidad de consultas. Está prohibido conservarlos en '
              'equipos personales, correo o herramientas no autorizadas.'),
        ('h2', '9.2 Capacitación'),
        ('p', 'Todos los funcionarios reciben una capacitación anual de al menos 8 horas en PLA/FT y deben aprobar la '
              'evaluación con una nota mínima del 80 %. Los asesores comerciales nuevos completan la capacitación '
              'dentro de los 30 días de su ingreso y no pueden vincular clientes antes de aprobarla.'),
        ('h2', '9.3 Sanciones'),
        ('p', 'El incumplimiento de este Manual constituye falta disciplinaria. Omitir un reporte de operación '
              'inusual, revelar al cliente la existencia de un reporte o vincular a una persona en listas restrictivas '
              'son faltas graves que pueden dar lugar a la terminación de la relación laboral, sin perjuicio de las '
              'responsabilidades civiles y penales.'),
    ]),
    ('10. Control de cambios', [
        ('tabla', [
            ['Versión', 'Fecha', 'Cambios principales'],
            ['2.0', 'Junio 2023', 'Matriz de riesgo con cuatro factores.'],
            ['3.0', 'Enero 2026', 'Plazo de 24 horas para el ROI-01; PEP hasta 2 años después del cargo; '
                                  'verificación de listas antes de cada desembolso.'],
        ], [2.0, 3.0, 11.0]),
        ('p', 'Este Manual es mantenido por el Oficial de Cumplimiento y aprobado por el Directorio. La versión '
              'vigente es la publicada en el repositorio de manuales aprobados.'),
    ]),
]


def main() -> None:
    n1 = construir('manual-credito-consumo.pdf', {
        'titulo': 'Manual de Crédito de Consumo',
        'version': 'Versión 4.2',
        'vigencia': 'Vigente desde marzo de 2026',
        'responsable': 'Responsable: Gerencia de Riesgo de Crédito',
        'pie': 'Manual de Crédito de Consumo v4.2',
    }, CREDITO)
    n2 = construir('manual-pla-ft.pdf', {
        'titulo': 'Manual de Prevención de Lavado de Activos y Financiamiento del Terrorismo (PLA/FT)',
        'version': 'Versión 3.0',
        'vigencia': 'Vigente desde enero de 2026',
        'responsable': 'Responsable: Oficial de Cumplimiento',
        'pie': 'Manual PLA/FT v3.0',
    }, PLAFT)
    print(f'manual-credito-consumo.pdf: {n1} páginas · manual-pla-ft.pdf: {n2} páginas')


if __name__ == '__main__':
    main()
