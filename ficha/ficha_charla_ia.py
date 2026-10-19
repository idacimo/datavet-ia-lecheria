"""Ficha «Decisiones ganaderas basadas en datos e IA» — 3 fichas por hoja carta, frente y reverso.

FRENTE = la charla en orden (paso 0 teoría + 4 casos). Cada paso: escanear, marcar y escribir un mini-reto.
REVERSO = para llevar: las IA más usadas, qué es un prompt (con ejemplo) y las apps para la finca.

Cada cara se imprime en UNA sola pasada: no depende de alinear dos impresoras.
Salidas (carpeta OUT):
  Ficha_IA_Lecheria.pdf        -> pág. 1 frente a color (impresora de color) · pág. 2 reverso en grises (láser)
  Ficha_IA_Lecheria_laser.pdf  -> las dos caras en grises, todo en la láser
Uso (desde la raíz del repo):  python ficha/ficha_charla_ia.py ficha/salida ficha ficha/fonts
"""
import io, os, sys
import qrcode
from qrcode.constants import ERROR_CORRECT_H
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

# Colores de marca (versión a color)
NAVY = HexColor("#07193F"); GREEN = HexColor("#209B6C"); TEAL = HexColor("#26B0B3")
AMBER = HexColor("#F5A623"); LGREEN = HexColor("#66BE8F")
# Pasada láser: negro y grises. Texto pequeño siempre negro sólido (el gris se trama).
K = Color(0, 0, 0); K80 = Color(.2, .2, .2); K45 = Color(.55, .55, .55); K12 = Color(.88, .88, .88)

W, H = letter
SH = H / 3
PAD = 6 * mm
LR = 1415 / 4181                     # alto/ancho logos Datavet con eslogan
CR = 565 / 519                       # alto/ancho logo Colanta vertical

LOGO_COLANTA = ImageReader(f"{BRAND}/colanta_vertical.png")
def _gray(path):
    from PIL import Image
    im = Image.open(path).convert("RGBA"); g = im.convert("LA").convert("RGBA"); g.putalpha(im.getchannel("A"))
    b = io.BytesIO(); g.save(b, "PNG"); b.seek(0); return ImageReader(b)
LOGO_COLANTA_K = _gray(f"{BRAND}/colanta_vertical.png")   # Colanta en grises, para la versión solo láser
LOGO_DV = ImageReader(f"{BRAND}/logo_color_ss.png")      # Datavet logo principal (sin eslogan): el eslogan va como texto legible
LOGO_DV_K = ImageReader(f"{BRAND}/logo_negro_ss.png")    # Datavet logo negro (sin eslogan)
SR = 754 / 3040                                          # alto/ancho logos sin eslogan
ISO_V = ImageReader(f"{BRAND}/isotipo_v.png")            # la «V» de Datavet (verde) en el centro de los QR
ISO_V_K = ImageReader(f"{BRAND}/isotipo_v_negro.png")    # la misma «V» en negro, para la cara solo láser
ISO_R = 479 / 347                                        # alto/ancho de la V
SLOGAN = "Analizar para innovar, innovar para evolucionar"
HOLE = 0.27                                              # parte del QR que queda en blanco en el centro (corrección de errores alta: 30 %)

def qr_img(url):
    """QR con corrección alta y un hueco blanco al centro para la V de Datavet."""
    q = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=12, border=0)
    q.add_data(url); q.make(fit=True)
    im = q.make_image(fill_color="black", back_color="white").convert("1")
    n = q.modules_count
    h = int(round(n * HOLE)); h += (n - h) % 2      # hueco centrado sobre módulos enteros
    a = (n - h) // 2 * 12
    from PIL import ImageDraw
    ImageDraw.Draw(im).rectangle([a, a, a + h * 12 - 1, a + h * 12 - 1], fill=1)
    b = io.BytesIO(); im.save(b, "PNG"); b.seek(0)
    return ImageReader(b)

def qr_v(c, x, y, s, color=True):
    """Dibuja la V centrada en un QR de lado s ubicado en (x, y). Queda ~1 mm de margen dentro del hueco."""
    vh = s * HOLE * 0.62; vw = vh / ISO_R
    c.drawImage(ISO_V if color else ISO_V_K, x + (s - vw) / 2, y + (s - vh) / 2, vw, vh, mask="auto")

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
# Cada paso: (n, herramienta, color, color texto etiqueta, título, [elementos], url)
# Elementos: ("q", texto) pregunta · ("ops", [opciones]) casillas en 2 columnas (las largas ocupan la fila)
#            ("sino", texto) pregunta con Sí / No · ("tabla", [filas]) filas con Sí / No · ("linea", unidad o "")
STEPS = [
    ("0", "Teoría", NAVY, white, "La IA en 5 minutos",
     [("q", "¿Qué IA usa hoy?"),
      ("ops", ["Ninguna", "ChatGPT", "Gemini", "Claude", "Copilot", "Otra", "Gemini Notebook"])], SITE + "#teoria"),
    ("1", "Gemini Notebook", GREEN, white, "Comprobantes de pago de leche",
     [("q", "¿Estoy obteniendo el mejor precio por mi leche o puede mejorar?"),
      ("ops", ["Sí", "No sé", "Puede mejorar"])], SITE + "#c1"),
    ("2", "Gemini · Copilot", TEAL, white, "Levante de terneras",
     [("sino", "¿Pesa sus terneras periódicamente?"),
      ("q", "Mi meta de ganancia diaria:"), ("linea", "g/día")], SITE + "#c2"),
    ("3", "Claude", AMBER, NAVY, "Rentabilidad por vaca",
     [("q", "¿Lleva estos registros?"),
      ("tabla", ["Control lechero", "Producción", "Tratamientos", "Genómica"]),
      ("campo", ("Crío al año:", "terneras")),
      ("campo", ("Vaca más rentable:", ""))], SITE + "#c3"),
]
QRS = {s[6]: qr_img(s[6]) for s in STEPS}

BW = 44 * mm                         # columna Colanta + título
X0 = BW + 3 * mm
CW = (W - PAD - X0) / len(STEPS)
QS = 21 * mm
TAG_H = 5 * mm
FOOT = 8 * mm                        # franja inferior con Datavet

def tag_font(c, maxw):
    labels = [f"{s[0]} · {s[1].upper()}" for s in STEPS]
    fs = 7.6
    while max(c.stringWidth(l, "Jost-SB", fs) for l in labels) + 3 * mm > maxw:
        fs -= 0.1
    return round(fs, 1)

def sino(c, x, y, labels=("Sí", "No"), fs=6.9):
    """Casillas en línea a partir de x; devuelve el ancho usado."""
    cx = x
    for o in labels:
        box(c, cx, y, 2.6 * mm)
        c.setFont("Jost", fs); c.setFillColor(K); c.drawString(cx + 3.4 * mm, y + 0.5 * mm, o)
        cx += 3.4 * mm + c.stringWidth(o, "Jost", fs) + 2.6 * mm
    return cx - x

def front(c, y0, mono=False):
    """Frente en UNA sola pasada (sin registro entre impresoras). mono=True: versión en grises para láser."""
    top = y0 + SH - PAD
    bot = y0 + PAD
    # ---- columna izquierda: Colanta (principal) + título
    lw = 22 * mm
    c.drawImage(LOGO_COLANTA_K if mono else LOGO_COLANTA, PAD + (BW - 2 * PAD - lw) / 2 - 2 * mm, top - lw * CR,
                width=lw, height=lw * CR, mask="auto")
    ty = top - lw * CR - 5.5 * mm
    TS = min(13.5, 13.5 * (BW - PAD - 2 * mm) / pdfmetrics.stringWidth("Decisiones ganaderas", "Jost-B", 13.5))
    c.setFillColor(K); c.setFont("Jost-B", TS)
    for k, line in enumerate(("Decisiones ganaderas", "basadas en", "datos e IA")):
        c.drawString(PAD, ty - k * TS * 1.15, line)
    para(c, "Tres casos de inteligencia artificial en lechería especializada.",
         PAD, ty - 2 * TS * 1.15 - 3 * mm, BW - PAD - 2 * mm, 7.4, "Jost", K80, 8.8)
    iy = bot + 15 * mm
    c.setFont("Jost-B", 7.6); c.setFillColor(K); c.drawString(PAD, iy, "En cada paso:")
    for k, t in enumerate(("Escanee el QR", "Marque la casilla", "Escriba su respuesta")):
        yy = iy - (k + 1) * 4.2 * mm
        c.setFont("Jost-B", 7.2); c.drawString(PAD, yy, f"{k + 1}.")
        c.setFont("Jost", 7.2); c.drawString(PAD + 3.5 * mm, yy, t)
    c.setStrokeColor(K45); c.setLineWidth(0.6); c.line(BW, bot, BW, top)

    # ---- 5 pasos
    fs = tag_font(c, CW - 3 * mm)
    for i, (n, tool, col, tcol, title, items, url) in enumerate(STEPS):
        x = X0 + i * CW
        inner = CW - 3 * mm
        qx, qy = x + (inner - QS) / 2, bot + FOOT + 4.6 * mm
        label = f"{n} · {tool.upper()}"
        tw = c.stringWidth(label, "Jost-SB", fs) + 3 * mm
        c.setFillColor(K if mono else col); c.roundRect(x, top - TAG_H, tw, TAG_H, 1.2 * mm, stroke=0, fill=1)
        c.setFillColor(white if mono else tcol); c.setFont("Jost-SB", fs); c.drawString(x + 1.5 * mm, top - 3.4 * mm, label)
        if i:
            c.setStrokeColor(K45); c.setLineWidth(0.5)
            c.line(x - 1.5 * mm, bot + FOOT, x - 1.5 * mm, top)
        y = top - TAG_H - 2 * mm
        y -= para(c, title, x, y, inner, 9.6, "Jost-B", K, 10.8) + 1.6 * mm
        c.setStrokeColor(K); c.setLineWidth(0.6)
        for kind, val in items:
            if kind == "q":
                y -= para(c, val, x, y, inner, 7.2, "Jost", K80, 8.4) + 1 * mm
            elif kind == "sino":
                y -= para(c, val, x, y, inner, 7.2, "Jost", K80, 8.4) + 3.4 * mm
                sino(c, x, y); y -= 2.6 * mm
            elif kind == "ops":
                col_k = 0
                for o in val:
                    long_ = c.stringWidth(o, "Jost", 6.9) + 3.6 * mm > inner / 2
                    if long_ and col_k == 1:
                        y -= 3.9 * mm; col_k = 0
                    if col_k == 0:
                        y -= 3.4 * mm if o == val[0] else 0
                    ox = x + col_k * (inner / 2)
                    box(c, ox, y, 2.6 * mm)
                    c.setFont("Jost", 6.9); c.setFillColor(K); c.drawString(ox + 3.6 * mm, y + 0.5 * mm, o)
                    if long_ or col_k == 1:
                        col_k = 0; y -= 3.9 * mm
                    else:
                        col_k = 1
                if col_k == 1:
                    y -= 3.9 * mm
                y += 1.2 * mm
            elif kind == "tabla":
                c.setFont("Jost-SB", 6.4); c.setFillColor(K)
                sx = x + inner - 11.5 * mm
                c.drawString(sx, y - 2.6 * mm, "Sí"); c.drawString(sx + 6 * mm, y - 2.6 * mm, "No")
                y -= 2.8 * mm
                for r in val:
                    y -= 3.9 * mm
                    c.setFont("Jost", 6.9); c.setFillColor(K); c.drawString(x, y + 0.5 * mm, r)
                    box(c, sx - 0.2 * mm, y, 2.6 * mm); box(c, sx + 5.8 * mm, y, 2.6 * mm)
                y -= 1 * mm
            elif kind == "campo":
                lab, unit = val
                y -= 4.6 * mm
                c.setFont("Jost", 7.2); c.setFillColor(K80); c.drawString(x, y + 0.6 * mm, lab)
                lx = x + c.stringWidth(lab, "Jost", 7.2) + 1.2 * mm
                ux = x + inner - (c.stringWidth(unit, "Jost", 7) + 1 * mm if unit else 0)
                c.setStrokeColor(K); c.line(lx, y, ux - 0.8 * mm, y)
                if unit:
                    c.setFont("Jost", 7); c.setFillColor(K); c.drawString(ux, y + 0.6 * mm, unit)
            elif kind == "linea":
                y -= 4.2 * mm
                if val:
                    c.line(x, y, x + inner - 12 * mm, y)
                    c.setFont("Jost", 7); c.setFillColor(K); c.drawString(x + inner - 11 * mm, y + 0.2 * mm, val)
                else:
                    c.line(x, y, x + inner, y)
        assert y > qy + QS + 0.8 * mm, f"el paso {n} no cabe: sobran {(qy + QS + 0.8 * mm - y) / mm:.1f} mm"
        # QR + casilla
        c.drawImage(QRS[url], qx, qy, QS, QS)
        qr_v(c, qx, qy, QS, not mono)
        box(c, x + (inner - QS) / 2, bot + FOOT + 0.4 * mm, 2.8 * mm)
        c.setFont("Jost-SB", 6.9); c.setFillColor(K)
        c.drawString(x + (inner - QS) / 2 + 4 * mm, bot + FOOT + 1 * mm, "Lo escaneé")

    # ---- franja Datavet (al final de los casos)
    dl = 17 * mm; dh = dl * SR
    dy = bot - 0.8 * mm
    lx = X0 + 21.5 * mm
    ty = dy + dh / 2 - 1.1 * mm
    c.setFont("Jost-M", 7.2); c.setFillColor(K80)
    c.drawRightString(lx - 1.5 * mm, ty, "Desarrollado por")
    c.drawImage(LOGO_DV_K if mono else LOGO_DV, lx, dy, width=dl, height=dh, mask="auto")
    c.setFont("Jost-M", 7.6); c.setFillColor(K)
    c.drawString(lx + dl + 2.5 * mm, ty, SLOGAN)
    c.setFont("Jost", 7); c.setFillColor(K80)
    c.drawRightString(W - PAD - 1.5 * mm, ty, SITE)

# ====================================================================== REVERSO (láser)
IAS = [
    ("Gemini Notebook", "Google · antes NotebookLM",
     "Responde solo con SUS fuentes: PDF, documentos, páginas web, audios y videos de YouTube. "
     "Cita de dónde sale cada dato y crea resúmenes en audio y video, mapas mentales y cuestionarios."),
    ("Gemini", "Google",
     "Ve videos de YouTube y lee fotos, PDF y Excel. Se conecta con Gmail, Drive y Maps. "
     "Hace investigaciones profundas en internet y conversa por voz desde el celular."),
    ("Claude", "Anthropic",
     "Analiza archivos grandes de Excel y PDF, cruza muchos datos y entrega tablas, gráficas, "
     "informes y hasta pequeñas apps. Muy bueno para razonar con detalle y escribir."),
    ("ChatGPT", "OpenAI",
     "La más conocida. Conversa por voz, lee fotos y documentos, analiza tablas y crea imágenes. "
     "Útil para redactar, calcular y explicar cualquier tema."),
    ("Copilot", "Microsoft",
     "Trabaja dentro de Word, Excel, Outlook y Teams, y en Windows. Resume correos y reuniones, "
     "y ayuda con fórmulas y tablas de Excel."),
]
PROMPT = [
    ("Rol", "quién quiere que sea la IA", "«Eres un asesor experto en calidad de leche.»"),
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
    ax, aw = PAD, 70 * mm
    y = header(c, ax, top, aw, "Las IA más usadas")
    rh = (y - (bot + 4 * mm)) / len(IAS)
    st = ParagraphStyle("u", fontName="Jost", fontSize=6.7, leading=7.7, textColor=K)
    for k, (name, co, use) in enumerate(IAS):
        ry = y - k * rh
        if k % 2 == 0:
            c.setFillColor(K12); c.rect(ax, ry - rh, aw, rh, stroke=0, fill=1)
        c.setFont("Jost-B", 8); c.setFillColor(K); c.drawString(ax + 1.5 * mm, ry - 3.3 * mm, name)
        c.setFont("Jost", 6.3); c.setFillColor(K80)
        c.drawString(ax + 2.5 * mm + c.stringWidth(name, "Jost-B", 8), ry - 3.3 * mm, "· " + co)
        pu = Paragraph(use, st); _, ph = pu.wrap(aw - 3 * mm, rh)
        assert ph <= rh - 4.4 * mm, f"{name}: texto muy largo ({ph / mm:.1f} mm)"
        pu.drawOn(c, ax + 1.5 * mm, ry - 4.4 * mm - ph)
    c.setFont("Jost", 6.5); c.setFillColor(K80)
    c.drawString(ax, bot, "Todas tienen versión gratuita para empezar.")

    # ---- B: qué es un prompt
    bx = ax + aw + 4.5 * mm; bw = 71 * mm
    y = header(c, bx, top, bw, "¿Qué es un prompt?")
    h = para(c, "Es la <b>instrucción</b> que usted le escribe a la IA. Entre más clara, mejor la respuesta. "
                "Un buen prompt tiene <b>4 partes</b>:", bx, y, bw, 7.3, "Jost", K, 8.7)
    y -= h + 1.8 * mm
    rh = 10.0 * mm
    for k, (part, what, ex) in enumerate(PROMPT):
        ry = y - k * rh
        c.setFillColor(K); c.circle(bx + 2.6 * mm, ry - 2.8 * mm, 2.4 * mm, stroke=0, fill=1)
        c.setFillColor(white); c.setFont("Jost-B", 8); c.drawCentredString(bx + 2.6 * mm, ry - 3.8 * mm, str(k + 1))
        c.setFillColor(K); c.setFont("Jost-B", 8.2); c.drawString(bx + 6.5 * mm, ry - 3.6 * mm, part)
        c.setFont("Jost", 6.8); c.setFillColor(K80)
        c.drawString(bx + 6.5 * mm + c.stringWidth(part, "Jost-B", 8.2) + 1.5 * mm, ry - 3.6 * mm, f"· {what}")
        para(c, ex, bx + 6.5 * mm, ry - 4.6 * mm, bw - 6.5 * mm, 7.1, "Jost", K, 8.2)
    # el prompt completo, armado con las 4 partes
    full = ("Eres un asesor experto en calidad de leche. Adjunto el control lechero de mi finca de los últimos "
            "12 meses. Dime qué vacas aportan más células al tanque y cuáles repiten. Entrégalo en una tabla, "
            "con 3 acciones y en lenguaje sencillo.")
    st = ParagraphStyle("f", fontName="Jost", fontSize=7, leading=8.3, textColor=K)
    pf = Paragraph("«" + full + "»", st); _, ph = pf.wrap(bw - 4 * mm, 40 * mm)
    bh = ph + 7.4 * mm
    c.setFillColor(K12); c.roundRect(bx, bot - 0.5 * mm, bw, bh, 1.5 * mm, stroke=0, fill=1)
    c.setFont("Jost-B", 7.4); c.setFillColor(K); c.drawString(bx + 2 * mm, bot - 0.5 * mm + bh - 3.8 * mm, "El prompt completo, listo para pegar:")
    pf.drawOn(c, bx + 2 * mm, bot + 1.2 * mm)

    # ---- C: apps + compromiso + contacto
    cx = bx + bw + 5 * mm; cw = W - PAD - cx
    c.setStrokeColor(K45); c.setLineWidth(0.5); c.line(cx - 2.5 * mm, bot, cx - 2.5 * mm, top)
    y = header(c, cx, top, cw, "Apps para su finca")
    qs = 19 * mm
    for k, (img, t1, t2) in enumerate(((QR_REEMP, "Reemplazos", "terneras y novillas"),
                                       (QR_ROI, "ROI ordeño", "retorno de automatizar"))):
        qx = cx + k * (cw / 2)
        c.drawImage(img, qx, y - qs, qs, qs)
        qr_v(c, qx, y - qs, qs, False)
        c.setFont("Jost-B", 7.4); c.setFillColor(K); c.drawString(qx, y - qs - 3.2 * mm, t1)
        c.setFont("Jost", 6.5); c.setFillColor(K80); c.drawString(qx, y - qs - 6 * mm, t2)
    y -= qs + 9.5 * mm
    for u in (APP_REEMPLAZOS, APP_ROI):                 # dirección completa, por si el QR no lee
        fz = 6.4
        while c.stringWidth(u, "Jost", fz) > cw and fz > 5: fz -= 0.1
        c.setFont("Jost", fz); c.setFillColor(K); c.drawString(cx, y + 0.6 * mm, u); y -= 3 * mm
    y -= 3.2 * mm
    c.setFont("Jost-B", 7.4); c.setFillColor(K); c.drawString(cx, y, "Mi compromiso: el primer dato")
    c.drawString(cx, y - 3.4 * mm, "que voy a organizar es")
    c.setStrokeColor(K); c.setLineWidth(0.6); c.line(cx, y - 8.5 * mm, cx + cw, y - 8.5 * mm)
    # contacto
    lw = 27 * mm
    c.drawImage(LOGO_DV_K, cx, bot + 17.2 * mm, width=lw, height=lw * SR, mask="auto")
    c.setFont("Jost-M", 7.2); c.setFillColor(K); c.drawString(cx, bot + 13.6 * mm, SLOGAN)
    c.setFont("Jost-SB", 7.2); c.drawString(cx, bot + 9.6 * mm, "Iván Darío Cifuentes M.")
    c.setFont("Jost", 7); c.drawString(cx, bot + 6.4 * mm, "WhatsApp 315 501 0037")
    c.drawString(cx, bot + 3.2 * mm, "ivan.cifuentes@datavet.info")
    c.drawString(cx, bot, "idacimo@gmail.com")

def doc(name, title):
    c = canvas.Canvas(os.path.join(OUT, name), pagesize=letter)
    c.setTitle(title); c.setAuthor("Iván Darío Cifuentes Moreno · Datavet"); return c

for f in ("Ficha_IA_Lecheria_separacion.pdf",):          # ya no se usa: el frente va en una sola pasada
    if os.path.exists(os.path.join(OUT, f)): os.remove(os.path.join(OUT, f))

c = doc("Ficha_IA_Lecheria.pdf", "Ficha IA lechería · Frente a color y reverso")
for i in range(3): front(c, SH * i)
crop_marks(c); c.showPage()
for i in range(3): back(c, SH * i)
crop_marks(c); c.showPage(); c.save()

c = doc("Ficha_IA_Lecheria_laser.pdf", "Ficha IA lechería · Todo en láser (grises)")
for i in range(3): front(c, SH * i, mono=True)
crop_marks(c); c.showPage()
for i in range(3): back(c, SH * i)
crop_marks(c); c.showPage(); c.save()
print("ok", OUT)
