"""Ficha «Decisiones ganaderas basadas en datos e IA» — 3 fichas por hoja carta, frente y reverso.

FRENTE = la charla en orden (paso 0 teoría + 4 casos). Cada paso: escanear, marcar y escribir un mini-reto.
REVERSO = para llevar: las IA más usadas, qué es un prompt (con ejemplo) y las apps para la finca.

Salidas (carpeta OUT):
  Ficha_IA_Lecheria.pdf             -> ficha completa (2 páginas: frente y reverso)
  Ficha_IA_Lecheria_separacion.pdf  -> pág. 1 COLOR (frente: logos y etiquetas)
                                       pág. 2 LÁSER (frente, misma cara: todo lo demás)
                                       pág. 3 LÁSER (reverso)
Uso (desde la raíz del repo):  python ficha/ficha_charla_ia.py ficha/salida ficha ficha/fonts
"""
import io, os, sys
import qrcode
from qrcode.constants import ERROR_CORRECT_M
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

OUT = sys.argv[1] if len(sys.argv) > 1 else "ficha/salida"
BRAND = sys.argv[2] if len(sys.argv) > 2 else "ficha"
FONTS = sys.argv[3] if len(sys.argv) > 3 else "ficha/fonts"
os.makedirs(OUT, exist_ok=True)

SITE = "https://idacimo.github.io/datavet-ia-lecheria/"
APP_REEMPLAZOS = "https://idacimo.github.io/Reemplazos_Fincas_Lecheras/"
APP_ROI = "https://idacimo.github.io/Roi-automatizacion/"   # app ROI de la automatización del ordeño (repo Roi-automatizacion)

for n, f in (("Jost", "Regular"), ("Jost-M", "Medium"), ("Jost-SB", "SemiBold"), ("Jost-B", "Bold")):
    pdfmetrics.registerFont(TTFont(n, f"{FONTS}/Jost-{f}.ttf"))

# Colores (solo pasada de color)
NAVY = HexColor("#07193F"); GREEN = HexColor("#209B6C"); TEAL = HexColor("#26B0B3")
AMBER = HexColor("#F5A623"); LGREEN = HexColor("#66BE8F")
# Pasada láser: negro y grises. Texto pequeño siempre negro sólido (el gris se trama).
K = Color(0, 0, 0); K80 = Color(.2, .2, .2); K45 = Color(.55, .55, .55); K12 = Color(.88, .88, .88)

W, H = letter
SH = H / 3
PAD = 6 * mm
GAP = 3.5 * mm                       # separación mínima entre un elemento de color y uno láser
LR = 1415 / 4181                     # alto/ancho logos Datavet con eslogan
CR = 565 / 519                       # alto/ancho logo Colanta vertical

LOGO_COLANTA = ImageReader(f"{BRAND}/colanta_vertical.png")
LOGO_DV = ImageReader(f"{BRAND}/slogan_trans.png")
LOGO_DV_K = ImageReader(f"{BRAND}/slogan_negro.png")

def qr_img(url):
    q = qrcode.QRCode(error_correction=ERROR_CORRECT_M, box_size=12, border=0)
    q.add_data(url); q.make(fit=True)
    b = io.BytesIO(); q.make_image(fill_color="black", back_color="white").convert("1").save(b, "PNG"); b.seek(0)
    return ImageReader(b)

def para(c, text, x, y_top, w, size, font="Jost", color=K, lead=None):
    p = Paragraph(text, ParagraphStyle("p", fontName=font, fontSize=size, leading=lead or size * 1.22, textColor=color))
    _, h = p.wrap(w, 200 * mm); p.drawOn(c, x, y_top - h)
    return h

def box(c, x, y, s=2.8 * mm):
    c.setStrokeColor(K); c.setLineWidth(0.7); c.setFillColor(white); c.rect(x, y, s, s, stroke=1, fill=1)

def crop_marks(c):
    c.setStrokeColor(K45); c.setLineWidth(0.4); c.setDash(2, 2)
    for i in (1, 2):
        c.line(0, SH * i, 7 * mm, SH * i); c.line(W - 7 * mm, SH * i, W, SH * i)
    c.setDash()

# ====================================================================== FRENTE
# (n, etiqueta, color, color texto etiqueta, título, reto, tipo de respuesta, url)
STEPS = [
    ("0", "Teoría", NAVY, white, "La IA en 5 minutos",
     "¿Qué IA usa hoy?", "opciones", SITE + "#teoria"),
    ("1", "NotebookLM", GREEN, white, "El cuaderno de la finca",
     "Primer documento que subiría:", "linea", SITE + "#c1"),
    ("2", "Gemini", TEAL, white, "Levante de terneras",
     "Mi meta de ganancia diaria:", "g/día", SITE + "#c2"),
    ("3", "Genómica", AMBER, NAVY, "Qué terneras criar",
     "Terneras que crío al año:", "terneras", SITE + "#c3"),
    ("4", "Claude", LGREEN, NAVY, "Rentabilidad por vaca",
     "Mi vaca más rentable es:", "linea", SITE + "#c4"),
]
QRS = {s[7]: qr_img(s[7]) for s in STEPS}

BW = 44 * mm                         # columna Colanta + título
X0 = BW + 3 * mm
CW = (W - PAD - X0) / 5
QS = 21 * mm
TAG_H = 5 * mm
FOOT = 8 * mm                        # franja inferior con Datavet

def tag_font(c, maxw):
    labels = [f"{n} · {t.upper()}" for n, t, *_ in STEPS]
    fs = 7.6
    while max(c.stringWidth(l, "Jost-SB", fs) for l in labels) + 3 * mm > maxw:
        fs -= 0.1
    return round(fs, 1)

def front(c, y0, color=True, laser=True):
    top = y0 + SH - PAD
    bot = y0 + PAD
    # ---- columna izquierda: Colanta (principal) + título
    lw = 22 * mm
    if color:
        c.drawImage(LOGO_COLANTA, PAD + (BW - 2 * PAD - lw) / 2 - 2 * mm, top - lw * CR, width=lw, height=lw * CR, mask="auto")
    if laser:
        ty = top - lw * CR - GAP - 3.5 * mm
        TS = min(13.5, 13.5 * (BW - PAD - 2 * mm) / pdfmetrics.stringWidth("Decisiones ganaderas", "Jost-B", 13.5))
        c.setFillColor(K); c.setFont("Jost-B", TS)
        for k, line in enumerate(("Decisiones ganaderas", "basadas en", "datos e IA")):
            c.drawString(PAD, ty - k * TS * 1.15, line)
        para(c, "Cuatro casos de inteligencia artificial en lechería especializada.",
             PAD, ty - 2 * TS * 1.15 - 3 * mm, BW - PAD - 2 * mm, 7.4, "Jost", K80, 8.8)
        # instrucción de la dinámica
        iy = bot + 15 * mm
        c.setFont("Jost-B", 7.6); c.setFillColor(K); c.drawString(PAD, iy, "En cada paso:")
        for k, t in enumerate(("Escanee el QR", "Marque la casilla", "Escriba su respuesta")):
            yy = iy - (k + 1) * 4.2 * mm
            c.setFont("Jost-B", 7.2); c.drawString(PAD, yy, f"{k + 1}.")
            c.setFont("Jost", 7.2); c.drawString(PAD + 3.5 * mm, yy, t)
        c.setStrokeColor(K45); c.setLineWidth(0.6); c.line(BW, bot, BW, top)

    # ---- 5 pasos
    fs = tag_font(c, CW - 3 * mm)
    for i, (n, tool, col, tcol, title, reto, kind, url) in enumerate(STEPS):
        x = X0 + i * CW
        inner = CW - 3 * mm
        if color:
            label = f"{n} · {tool.upper()}"
            tw = c.stringWidth(label, "Jost-SB", fs) + 3 * mm
            c.setFillColor(col); c.roundRect(x, top - TAG_H, tw, TAG_H, 1.2 * mm, stroke=0, fill=1)
            c.setFillColor(tcol); c.setFont("Jost-SB", fs); c.drawString(x + 1.5 * mm, top - 3.4 * mm, label)
        if not laser:
            continue
        if i:
            c.setStrokeColor(K45); c.setLineWidth(0.5)
            c.line(x - 1.5 * mm, bot + FOOT, x - 1.5 * mm, top - TAG_H - GAP)
        ty = top - TAG_H - GAP
        h = para(c, title, x, ty, inner, 9.6, "Jost-B", K, 10.8)
        ry = ty - h - 2 * mm
        h2 = para(c, reto, x, ry, inner, 7.2, "Jost", K80, 8.4)
        ay = ry - h2 - 1.2 * mm                          # zona de respuesta
        c.setStrokeColor(K); c.setLineWidth(0.6)
        if kind == "opciones":
            ops = ("Ninguna", "ChatGPT", "Gemini", "Otra")
            for k, o in enumerate(ops):
                ox = x + (k % 2) * (inner / 2); oy = ay - 3.4 * mm - (k // 2) * 4.2 * mm
                box(c, ox, oy, 2.6 * mm)
                c.setFont("Jost", 6.9); c.setFillColor(K); c.drawString(ox + 3.6 * mm, oy + 0.5 * mm, o)
        elif kind == "linea":
            c.line(x, ay - 4.5 * mm, x + inner, ay - 4.5 * mm)
        else:
            c.line(x, ay - 4.5 * mm, x + inner - 12 * mm, ay - 4.5 * mm)
            c.setFont("Jost", 7); c.setFillColor(K); c.drawString(x + inner - 11 * mm, ay - 4.3 * mm, kind)
        # QR + casilla
        qy = bot + FOOT + 4.6 * mm
        c.drawImage(QRS[url], x + (inner - QS) / 2, qy, QS, QS)
        box(c, x + (inner - QS) / 2, bot + FOOT + 0.4 * mm, 2.8 * mm)
        c.setFont("Jost-SB", 6.9); c.setFillColor(K)
        c.drawString(x + (inner - QS) / 2 + 4 * mm, bot + FOOT + 1 * mm, "Lo escaneé")

    # ---- franja Datavet (al final de los casos)
    dl = 17 * mm; dh = dl * LR
    dy = bot - 1.5 * mm
    if laser:
        c.setFont("Jost-M", 7); c.setFillColor(K80)
        c.drawRightString(X0 + 20 * mm, dy + dh / 2 - 0.5 * mm, "Desarrollado por")
        c.setFont("Jost", 7); c.setFillColor(K)
        c.drawRightString(W - PAD - 1.5 * mm, dy + dh / 2 - 0.5 * mm, "Todo el material: idacimo.github.io/datavet-ia-lecheria")
    if color:
        c.drawImage(LOGO_DV, X0 + 20 * mm + GAP, dy, width=dl, height=dh, mask="auto")

# ====================================================================== REVERSO (láser)
IAS = [
    ("NotebookLM", "Google", "Responde solo con SUS documentos: protocolos, informes, manuales."),
    ("Gemini", "Google", "Lee Excel y fotos. Funciona con Gmail y Drive."),
    ("Claude", "Anthropic", "Análisis largos: cruza muchos datos y arma informes y tablas."),
    ("ChatGPT", "OpenAI", "Asistente general: redactar, calcular, explicar."),
    ("Copilot", "Microsoft", "Dentro de Excel, Word y Outlook."),
]
PROMPT = [
    ("Rol", "quién quiere que sea la IA", "«Eres un veterinario asesor en calidad de leche.»"),
    ("Datos", "qué le entrega", "«Adjunto el control lechero de mi finca de los últimos 12 meses.»"),
    ("Tarea", "qué debe hacer, paso a paso", "«Dime qué vacas aportan más células al tanque y cuáles repiten.»"),
    ("Entrega", "cómo quiere la respuesta", "«En una tabla, con 3 acciones y en lenguaje sencillo.»"),
]
QR_REEMP = qr_img(APP_REEMPLAZOS)
QR_ROI = qr_img(APP_ROI)

def header(c, x, y, w, txt):
    c.setFont("Jost-B", 10.5); c.setFillColor(K); c.drawString(x, y - 3.8 * mm, txt)
    c.setStrokeColor(K); c.setLineWidth(1.2); c.line(x, y - 5.4 * mm, x + w, y - 5.4 * mm)
    return y - 7.5 * mm

def back(c, y0):
    top = y0 + SH - PAD; bot = y0 + PAD
    # ---- A: las IA más usadas
    ax, aw = PAD, 64 * mm
    y = header(c, ax, top, aw, "Las IA más usadas")
    rh = (y - (bot + 5 * mm)) / len(IAS)
    for k, (name, co, use) in enumerate(IAS):
        ry = y - k * rh
        if k % 2 == 0:
            c.setFillColor(K12); c.rect(ax, ry - rh, aw, rh, stroke=0, fill=1)
        c.setFont("Jost-B", 8.2); c.setFillColor(K); c.drawString(ax + 1.5 * mm, ry - rh / 2 + 0.2 * mm, name)
        c.setFont("Jost", 6.4); c.setFillColor(K80); c.drawString(ax + 1.5 * mm, ry - rh / 2 - 2.8 * mm, co)
        st = ParagraphStyle("u", fontName="Jost", fontSize=7, leading=8.2, textColor=K)
        pu = Paragraph(use, st); _, ph = pu.wrap(aw - 23.5 * mm, rh); pu.drawOn(c, ax + 22 * mm, ry - rh / 2 - ph / 2)
    c.setFont("Jost", 6.5); c.setFillColor(K80)
    c.drawString(ax, bot, "Todas tienen versión gratuita para empezar.")

    # ---- B: qué es un prompt
    bx = ax + aw + 5 * mm; bw = 76 * mm
    y = header(c, bx, top, bw, "¿Qué es un prompt?")
    h = para(c, "Es la <b>instrucción</b> que usted le escribe a la IA. Entre más clara, mejor la respuesta. "
                "Un buen prompt tiene <b>4 partes</b>:", bx, y, bw, 7.3, "Jost", K, 8.7)
    y -= h + 1.8 * mm
    rh = 11.2 * mm
    for k, (part, what, ex) in enumerate(PROMPT):
        ry = y - k * rh
        c.setFillColor(K); c.circle(bx + 2.6 * mm, ry - 2.8 * mm, 2.4 * mm, stroke=0, fill=1)
        c.setFillColor(white); c.setFont("Jost-B", 8); c.drawCentredString(bx + 2.6 * mm, ry - 3.8 * mm, str(k + 1))
        c.setFillColor(K); c.setFont("Jost-B", 8.2); c.drawString(bx + 6.5 * mm, ry - 3.6 * mm, part)
        c.setFont("Jost", 6.8); c.setFillColor(K80)
        c.drawString(bx + 6.5 * mm + c.stringWidth(part, "Jost-B", 8.2) + 1.5 * mm, ry - 3.6 * mm, f"· {what}")
        para(c, ex, bx + 6.5 * mm, ry - 4.6 * mm, bw - 6.5 * mm, 7.1, "Jost", K, 8.2)
    c.setFont("Jost-SB", 6.9); c.setFillColor(K)
    c.drawString(bx, bot, "Ejemplo completo: pegue las 4 partes en un solo mensaje.")

    # ---- C: apps + compromiso + contacto
    cx = bx + bw + 5 * mm; cw = W - PAD - cx
    c.setStrokeColor(K45); c.setLineWidth(0.5); c.line(cx - 2.5 * mm, bot, cx - 2.5 * mm, top)
    y = header(c, cx, top, cw, "Apps para su finca")
    qs = 19 * mm
    for k, (img, t1, t2) in enumerate(((QR_REEMP, "Reemplazos", "terneras y novillas"),
                                       (QR_ROI, "ROI ordeño", "retorno de automatizar"))):
        qx = cx + k * (cw / 2)
        c.drawImage(img, qx, y - qs, qs, qs)
        c.setFont("Jost-B", 7.4); c.setFillColor(K); c.drawString(qx, y - qs - 3.2 * mm, t1)
        c.setFont("Jost", 6.5); c.setFillColor(K80); c.drawString(qx, y - qs - 6 * mm, t2)
    y -= qs + 9.5 * mm
    c.setFont("Jost-B", 7.4); c.setFillColor(K); c.drawString(cx, y, "Mi compromiso: el primer dato")
    c.drawString(cx, y - 3.4 * mm, "que voy a organizar es")
    c.setStrokeColor(K); c.setLineWidth(0.6); c.line(cx, y - 8.5 * mm, cx + cw, y - 8.5 * mm)
    # contacto
    lw = 25 * mm
    c.drawImage(LOGO_DV_K, cx, bot + 9.8 * mm, width=lw, height=lw * LR, mask="auto")
    c.setFont("Jost-SB", 6.8); c.setFillColor(K); c.drawString(cx, bot + 6.6 * mm, "Iván Darío Cifuentes M. · WhatsApp 315 501 0037")
    c.setFont("Jost", 6.6); c.drawString(cx, bot + 3.3 * mm, "ivan.cifuentes@datavet.info")
    c.drawString(cx, bot, "idacimo@gmail.com")

def doc(name, title):
    c = canvas.Canvas(os.path.join(OUT, name), pagesize=letter)
    c.setTitle(title); c.setAuthor("Iván Darío Cifuentes Moreno · Datavet"); return c

c = doc("Ficha_IA_Lecheria.pdf", "Ficha IA lechería · Frente y reverso")
for i in range(3): front(c, SH * i)
crop_marks(c); c.showPage()
for i in range(3): back(c, SH * i)
crop_marks(c); c.showPage(); c.save()

c = doc("Ficha_IA_Lecheria_separacion.pdf", "Ficha IA lechería · Separación color / láser")
for i in range(3): front(c, SH * i, color=True, laser=False)
c.showPage()
for i in range(3): front(c, SH * i, color=False, laser=True)
crop_marks(c); c.showPage()
for i in range(3): back(c, SH * i)
crop_marks(c); c.showPage(); c.save()
print("ok", OUT)
