# Uso (desde la raíz del repo): python ficha/ficha_charla_ia.py . ficha/Ficha_Datos_IA_Lecheria.pdf ficha ficha/fonts
"""Ficha 'Decisiones ganaderas con datos e IA': 3 fichas por hoja carta, frente y reverso."""
import io, sys
import qrcode
from qrcode.constants import ERROR_CORRECT_M
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

REPO = sys.argv[1]
OUT = sys.argv[2]
BASE = "https://idacimo.github.io/Reemplazos_Fincas_Lecheras/"
CHARLA = "https://idacimo.github.io/datavet-ia-lecheria/"

F = (sys.argv[4] if len(sys.argv) > 4 else REPO + "/vendor/fonts") + "/"
pdfmetrics.registerFont(TTFont("Jost", F + "Jost-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Jost-M", F + "Jost-Medium.ttf"))
pdfmetrics.registerFont(TTFont("Jost-SB", F + "Jost-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("Jost-B", F + "Jost-Bold.ttf"))

NAVY = HexColor("#07193F"); GREEN = HexColor("#209B6C"); TEAL = HexColor("#26B0B3")
AMBER = HexColor("#F5A623"); INK = HexColor("#1B2333"); MUTED = HexColor("#4F5B73")
LINE = HexColor("#D5DCD8"); WASH = HexColor("#F1F6F3")

W, H = letter
SH = H / 3            # alto de cada ficha
PAD = 6 * mm          # margen de seguridad interno

def qr_img(url):
    q = qrcode.QRCode(error_correction=ERROR_CORRECT_M, box_size=12, border=0)
    q.add_data(url); q.make(fit=True)
    im = q.make_image(fill_color="#07193F", back_color="white").convert("RGB")
    b = io.BytesIO(); im.save(b, "PNG"); b.seek(0)
    return ImageReader(b)

BRAND = sys.argv[3] if len(sys.argv) > 3 else REPO + "/assets"
LOGO_NEG = ImageReader(BRAND + "/slogan_blanco.png")   # Logo Datavet con slogan blanco (oficial)
LOGO = ImageReader(BRAND + "/slogan_trans.png")       # Logo Datavet con slogan trans (oficial)
LR = 1415 / 4181

CASES = [
    ("1", "NotebookLM", GREEN, white, "El cuaderno de la finca",
     "Capacitar al personal y leer 12 meses de control lechero de una vez.", CHARLA + "#c1"),
    ("2", "Gemini", TEAL, white, "Levante de terneras",
     "Ganancia diaria, curva de crecimiento y novillas listas para servicio.", CHARLA + "#c2"),
    ("3", "Genómica", AMBER, INK, "Qué terneras criar",
     "Ordenar las hembras por su genética y decidir el semen de cada grupo.", CHARLA + "#c3"),
    ("4", "Claude", NAVY, white, "Rentabilidad por vaca",
     "De la vaca más rentable a la menos rentable, con su decisión.", CHARLA + "#c4"),
]
QRS = {c[6]: qr_img(c[6]) for c in CASES}
QR_TEO = qr_img(CHARLA + "#teoria")
QR_APP = qr_img(BASE)

def para(c, text, x, y_top, w, size, font="Jost", color=INK, lead=None):
    st = ParagraphStyle("p", fontName=font, fontSize=size, leading=lead or size * 1.22, textColor=color)
    p = Paragraph(text, st)
    _, h = p.wrap(w, 200 * mm)
    p.drawOn(c, x, y_top - h)
    return h

def crop_marks(c):
    c.setStrokeColor(HexColor("#9AA5B1")); c.setLineWidth(0.4); c.setDash(2, 2)
    for i in (1, 2):
        y = SH * i
        c.line(0, y, 7 * mm, y); c.line(W - 7 * mm, y, W, y)
    c.setDash()

# ---------------------------------------------------------------- FRENTE
def front(c, y0):
    # banda izquierda
    bw = 58 * mm
    c.setFillColor(NAVY); c.rect(0, y0, bw, SH, stroke=0, fill=1)
    c.drawImage(LOGO_NEG, PAD, y0 + SH - PAD - 46 * mm * LR, width=46 * mm, height=46 * mm * LR, mask="auto")
    top = y0 + SH - PAD - 46 * mm * LR - 6 * mm
    h = para(c, "Decisiones ganaderas basadas en <font color='#66BE8F'>datos e IA</font>",
             PAD, top, bw - 2 * PAD, 14.5, "Jost-B", white, 16)
    top -= h + 2.5 * mm
    h = para(c, "Cuatro casos de inteligencia artificial en lechería especializada.",
             PAD, top, bw - 2 * PAD, 8.6, "Jost", HexColor("#C9D6E8"), 10.6)
    # instrucción
    para(c, "Escanee el QR de cada caso: abre el prompt listo para copiar y usar con los datos de su finca.",
         PAD, y0 + PAD + 13 * mm, bw - 2 * PAD, 7.6, "Jost-M", HexColor("#66BE8F"), 9.4)

    # casos
    x0 = bw + 4 * mm
    cw = (W - x0 - PAD + 0 * mm) / 4
    qs = 30 * mm
    for i, (n, tool, col, tcol, title, desc, url) in enumerate(CASES):
        x = x0 + i * cw
        inner = cw - 4 * mm
        if i:
            c.setStrokeColor(LINE); c.setLineWidth(0.5)
            c.line(x - 2 * mm, y0 + PAD, x - 2 * mm, y0 + SH - PAD)
        ty = y0 + SH - PAD
        # etiqueta
        c.setFont("Jost-SB", 7.4)
        label = f"CASO {n} · {tool.upper()}"
        tw = c.stringWidth(label, "Jost-SB", 7.4) + 4 * mm
        c.setFillColor(col); c.roundRect(x, ty - 5 * mm, tw, 5 * mm, 1.2 * mm, stroke=0, fill=1)
        c.setFillColor(tcol); c.drawString(x + 2 * mm, ty - 3.45 * mm, label)
        ty -= 7.5 * mm
        h = para(c, title, x, ty, inner, 10.5, "Jost-B", NAVY, 12)
        ty -= h + 1.5 * mm
        para(c, desc, x, ty, inner, 7.6, "Jost", MUTED, 9.4)
        # QR
        qx = x + (inner - qs) / 2
        qy = y0 + PAD + 5.5 * mm
        c.drawImage(QRS[url], qx, qy, qs, qs)
        c.setFont("Jost-SB", 7.2); c.setFillColor(GREEN)
        c.drawCentredString(x + inner / 2, y0 + PAD + 2 * mm, "Escanee: prompt listo")

# ---------------------------------------------------------------- REVERSO
ROWS = [
    ("1", "Protocolos, videos y PDF del control lechero", "NotebookLM", "Capacitación y metas a 90 días"),
    ("2", "Pesajes, fecha de nacimiento y raza", "Gemini", "Servicio, alimentación, atrasadas"),
    ("3", "Resultados genómicos en Excel", "Claude / Gemini", "Sexado, convencional o carne"),
    ("4", "Leche, calidad, reproducción, sanidad, costos", "Claude", "Mantener, tratar o descartar"),
]

def back(c, y0):
    tx = PAD; tw = 130 * mm
    ty = y0 + SH - PAD
    c.setFont("Jost-B", 11.5); c.setFillColor(NAVY)
    c.drawString(tx, ty - 4 * mm, "Mi ruta de datos")
    c.setFont("Jost", 7.6); c.setFillColor(MUTED)
    c.drawString(tx + 33 * mm, ty - 4 * mm, "Marque lo que ya tiene y póngase una fecha para lo que falta.")
    ty -= 7.5 * mm
    cols = [7 * mm, 43 * mm, 20 * mm, 33 * mm, 12 * mm, 15 * mm]   # 130 mm
    heads = ["", "Datos que necesita", "Herramienta", "Decisión que apoya", "Lo tengo", "Fecha meta"]
    rh = 9.6 * mm
    c.setFillColor(NAVY); c.rect(tx, ty - 5.5 * mm, tw, 5.5 * mm, stroke=0, fill=1)
    c.setFont("Jost-SB", 7.2); c.setFillColor(white)
    xx = tx
    for wcol, hd in zip(cols, heads):
        c.drawString(xx + 1.4 * mm, ty - 3.8 * mm, hd); xx += wcol
    ty -= 5.5 * mm
    for r, row in enumerate(ROWS):
        if r % 2 == 0:
            c.setFillColor(WASH); c.rect(tx, ty - rh, tw, rh, stroke=0, fill=1)
        xx = tx
        for j, (wcol, val) in enumerate(zip(cols, row)):
            if j == 0:
                c.setFillColor(GREEN); c.circle(xx + 3.6 * mm, ty - rh / 2, 2.4 * mm, stroke=0, fill=1)
                c.setFillColor(white); c.setFont("Jost-B", 8)
                c.drawCentredString(xx + 3.6 * mm, ty - rh / 2 - 1 * mm, val)
            else:
                st = ParagraphStyle("t", fontName="Jost-M" if j == 2 else "Jost", fontSize=7.5, leading=8.6, textColor=INK)
                p = Paragraph(val, st); _, ph = p.wrap(wcol - 2.8 * mm, rh)
                p.drawOn(c, xx + 1.4 * mm, ty - rh / 2 - ph / 2)
            xx += wcol
        c.setStrokeColor(MUTED); c.setLineWidth(0.7)
        c.rect(xx + 4 * mm, ty - rh / 2 - 2 * mm, 4 * mm, 4 * mm, stroke=1, fill=0)
        xx += cols[4]
        c.setStrokeColor(LINE); c.line(xx + 1.5 * mm, ty - rh / 2 - 2 * mm, xx + cols[5] - 1 * mm, ty - rh / 2 - 2 * mm)
        ty -= rh
    # receta del prompt
    ty -= 3.5 * mm
    c.setFont("Jost-B", 8.2); c.setFillColor(NAVY)
    c.drawString(tx, ty - 1 * mm, "Un buen prompt tiene 4 partes:")
    parts = [("Rol", "«Eres un asesor en…»"), ("Datos", "qué archivo adjunta"), ("Tarea", "qué calcular, paso a paso"), ("Entrega", "tablas y gráfica")]
    px = tx + 46 * mm; pw = (tw - 46 * mm) / 2
    for k, (a, b) in enumerate(parts):
        xx = px + (k % 2) * pw; yy = ty - 1 * mm - (k // 2) * 4.2 * mm
        c.setFont("Jost-SB", 7.4); c.setFillColor(GREEN); c.drawString(xx, yy, f"{k+1}. {a}")
        c.setFont("Jost", 7.2); c.setFillColor(MUTED); c.drawString(xx + c.stringWidth(f"{k+1}. {a}", "Jost-SB", 7.4) + 1.5 * mm, yy, b)
    ty -= 10.5 * mm
    c.setFont("Jost-SB", 7.8); c.setFillColor(NAVY)
    c.drawString(tx, ty - 1 * mm, "El primer dato que voy a organizar:")
    c.setStrokeColor(LINE); c.setLineWidth(0.7)
    c.line(tx + 50 * mm, ty - 1.5 * mm, tx + tw, ty - 1.5 * mm)
    c.setFont("Jost", 6.6); c.setFillColor(MUTED)
    c.drawString(tx, y0 + PAD - 1 * mm,
                 "Use la IA con sus datos, no con cédulas, cuentas ni contraseñas. Verifique los números antes de decidir.")

    # columna derecha: QRs
    rx = tx + tw + 6 * mm
    rw = W - rx - PAD
    c.setStrokeColor(LINE); c.setLineWidth(0.5)
    c.line(rx - 3 * mm, y0 + PAD, rx - 3 * mm, y0 + SH - PAD)
    qs = 24 * mm
    blocks = [
        (QR_TEO, "Teoría de IA", "Cuaderno NotebookLM: «Inteligencia artificial aplicada en la ganadería»."),
        (QR_APP, "App de reemplazos", "¿Cuántas terneras y novillas necesita su finca? Plan en Excel y PDF."),
    ]
    by = y0 + SH - PAD
    for img, ttl, desc in blocks:
        c.drawImage(img, rx, by - qs, qs, qs)
        tx2 = rx + qs + 3 * mm; w2 = rw - qs - 3 * mm
        c.setFont("Jost-B", 9.5); c.setFillColor(NAVY); c.drawString(tx2, by - 4 * mm, ttl)
        para(c, desc, tx2, by - 6 * mm, w2, 7.3, "Jost", MUTED, 8.6)
        by -= qs + 3.5 * mm
    # contacto
    c.drawImage(LOGO, rx, y0 + PAD + 6.5 * mm, width=36 * mm, height=36 * mm * LR, mask="auto")
    c.setFont("Jost-M", 7); c.setFillColor(INK)
    c.drawString(rx, y0 + PAD + 3.2 * mm, "Iván Darío Cifuentes M. · WhatsApp 315 501 0037")
    c.setFont("Jost", 6.8); c.setFillColor(MUTED)
    c.drawString(rx, y0 + PAD, "ivan.cifuentes@datavet.info")

c = canvas.Canvas(OUT, pagesize=letter)
c.setTitle("Ficha · Decisiones ganaderas basadas en datos e IA")
c.setAuthor("Iván Darío Cifuentes Moreno · Datavet")
for i in range(3):
    front(c, SH * i)
crop_marks(c); c.showPage()
for i in range(3):
    back(c, SH * i)
crop_marks(c); c.showPage()
c.save()
print("ok", OUT)
