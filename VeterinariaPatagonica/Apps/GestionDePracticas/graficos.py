from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.axes import XValueAxis, YValueAxis
from reportlab.graphics.charts.doughnut import Doughnut
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import HorizontalBarChart, VerticalBarChart
from reportlab.graphics.charts.lineplots import ScatterPlot, SimpleTimeSeriesPlot
from reportlab.graphics.renderPM import PMCanvas, _PMRenderer as PMRenderer
from reportlab.graphics.renderPDF import _PDFRenderer as PDFRenderer
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen.textobject import PDFTextObject


__all__ = [
    "barras",
    "torta",
    "radar",
    "cartesiano",
    "crear",
    "adjunto",
    "imagenes",
    "titulo",
    "texto",
    "referencias",
    "tabla",
]


FONTSIZE = 9.0
MARGEN = 20.0


def etiquetar(dibujo, etiqueta, x, y):
    etiqueta.setOrigin(x,y)
    dibujo.add(etiqueta)
    x1,y1,x2,y2 = dibujo.getBounds()
    dibujo.width = x2-x1
    dibujo.height = y2-y1
    dibujo.translate(-x1, -y1)


def crearDrawing(grafico):
    x1, y1, x2, y2 = grafico.getBounds()
    w = x2-x1
    h = y2-y1
    dibujo = Drawing(w, h)
    dibujo.add(grafico)
    dibujo.translate(-x1, -y1)
    return dibujo


def barras(datos):
    alto = datos["alto"]
    ancho = datos["ancho"]
    data = datos["data"]
    labels = datos["labels"]
    colores = datos["colores"]

    grafico = VerticalBarChart()
    grafico.x = 30
    grafico.y = 0
    grafico.height = alto
    grafico.width = ancho
    grafico.data = data
    grafico.barSpacing = 1.25
    for i in range(len(colores)):
        color = colors.HexColor(colores[i])
        grafico.bars[i].strokeColor = color
        grafico.bars[i].fillColor = color
    grafico.valueAxis.labels.fontName = "Helvetica"
    grafico.valueAxis.labels.fontSize = FONTSIZE
    grafico.valueAxis.valueMin = 0
    grafico.valueAxis.valueMax = 100
    grafico.valueAxis.valueStep = 10
    grafico.categoryAxis.categoryNames = labels
    grafico.categoryAxis.labels.fontName = "Helvetica"
    grafico.categoryAxis.labels.fontSize = FONTSIZE
    grafico.categoryAxis.labels.dy = -FONTSIZE
    grafico.categoryAxis.labels.boxAnchor = 'c'
    grafico.categoryAxis.labels.angle = 0
    retorno = crearDrawing(grafico)
    etiqueta = Label()
    etiqueta.setOrigin(0, alto)
    etiqueta.fontSize = FONTSIZE
    etiqueta.fontName = "Helvetica"
    etiqueta.setText("(%)")
    retorno.add(etiqueta)
    return retorno


def torta(datos):
    tamanio = datos["tamanio"]
    data = datos["data"]
    labels = datos["labels"]
    colores = datos["colores"]
    titulo = datos["titulo"]

    grafico = Pie()
    grafico.x = 10
    grafico.y = 10
    grafico.startAngle = 45
    grafico.width = tamanio
    grafico.height = tamanio
    grafico.data = data
    grafico.labels = labels
    grafico.slices.fontName = "Helvetica"
    grafico.slices.fontSize = FONTSIZE
    grafico.simpleLabels = False
    grafico.sideLabels = 1
    grafico.sideLabelsOffset = 0.075
    grafico.slices.label_simple_pointer = False
    grafico.slices.label_pointer_elbowLength = 0.5
    grafico.slices.label_pointer_piePad = 3
    grafico.slices.label_pointer_edgePad = 3
    grafico.slices.label_pointer_strokeColor = colors.black
    grafico.slices.label_pointer_strokeWidth = 0.75
    grafico.slices.strokeWidth=1.5
    grafico.slices.strokeColor=colors.white
    for i in range(len(colores)):
        grafico.slices[i].fillColor = colors.HexColor(colores[i])
    retorno = crearDrawing(grafico)
    if titulo:
        etiqueta = Label()
        etiqueta.fontSize = FONTSIZE
        etiqueta.fontName = "Helvetica-Bold"
        etiqueta.setText(titulo)
        etiquetar(retorno, etiqueta, tamanio/2.0, 0.0)
    return retorno

def radar(datos):
    tamanio = datos["tamanio"]
    data = datos["data"]
    labels = datos["labels"]
    colores = datos["colores"]
    titulo = datos["titulo"]

    grafico = SpiderChart()
    grafico.width = tamanio
    grafico.height = tamanio
    grafico.x = 0
    grafico.y = 0
    grafico.data = data
    grafico.labels = labels
    grafico.spokes.labelRadius = 1.125
    grafico.spokes.strokeDashArray = (10,5)
    grafico.spokeLabels.fontSize = FONTSIZE
    grafico.spokeLabels.fontName = "Helvetica"
    grafico.strands[0].fillColor = colors.HexColor(colores[0])
    grafico.strands[0].strokeColor = None
    grafico.strands[0].strokeWidth = 1
    grafico.strands[1].fillColor = None
    grafico.strands[1].strokeColor = colors.HexColor(colores[1])
    grafico.strands[1].strokeWidth = 2
    grafico.strandLabels.format = 'values'
    grafico.strandLabels.fontSize = FONTSIZE-1
    grafico.strandLabels.fontName = "Helvetica"
    grafico.strandLabels.fillColor = colors.black
    for i in range(len(datos["data"][0])):
        grafico.strandLabels[0,i]._text = "%2.2f" % data[0][i]
        grafico.strandLabels[0,i].dy = FONTSIZE
        grafico.strandLabels[1,i]._text = "%2.2f" % data[1][i]
        grafico.strandLabels[1,i].dy = -FONTSIZE
    retorno = crearDrawing(grafico)
    if titulo:
        etiqueta = Label()
        etiqueta.fontSize = FONTSIZE
        etiqueta.fontName = "Helvetica-Bold"
        etiqueta.setText(titulo)
        etiquetar(retorno, etiqueta, tamanio/2.0, 0.0)
    return retorno


def cartesiano(datos):
    alto = datos["alto"]
    ancho = datos["ancho"]
    data = datos["data"]
    colores = datos["colores"]
    labels = datos["labels"]
    menor = datos["rango"][0]
    mayor = datos["rango"][1]

    grafico = ScatterPlot()
    grafico.x = 20
    grafico.y = 40
    grafico.width = ancho
    grafico.height = alto
    grafico.data = data
    grafico.joinedLines = 1
    grafico.lineLabelFormat = None
    grafico.outerBorderOn = 0
    grafico.outerBorderColor = None
    grafico.background = None
    for i in range(len(colores)):
        color = colors.HexColor(colores[i])
        grafico.lines[i].strokeColor = color
        grafico.lines[i].symbol.strokeColor = color
        grafico.lines[i].symbol.fillColor = color
        grafico.lines[i].symbol.strokeWidth = 0
    grafico.xLabel=labels["x"]
    grafico.xValueAxis.labels.fontSize = FONTSIZE
    grafico.xValueAxis.labelTextFormat = lambda x: " Hace\n%d días" % abs(x)
    grafico.xValueAxis.valueStep = 10
    grafico.xValueAxis.labels.dy = -5
    grafico.xValueAxis.strokeColor = colors.black
    grafico.xValueAxis.strokeWidth = 1
    grafico.xValueAxis.tickDown = 5
    grafico.yLabel=labels["y"]
    grafico.yValueAxis.labels.fontSize = FONTSIZE
    grafico.yValueAxis.labelTextFormat = "%d"
    grafico.yValueAxis.labels.dx = -5
    grafico.yValueAxis.strokeColor = colors.black
    grafico.yValueAxis.strokeWidth = 1
    grafico.yValueAxis.tickLeft = 5
    grafico.yValueAxis.valueStep = 1
    grafico.yValueAxis.valueMin = menor
    grafico.yValueAxis.valueMax = mayor
    return crearDrawing(grafico)


def avanzar(canvas, y, salto):
    y -= salto
    if y < MARGEN:
        canvas.showPage()
        y = A4[1]-MARGEN-salto
    return y


def crear():
    return Canvas("")


def adjunto(canvas, nombre):
    if canvas.pageHasData():
        canvas.showPage()
    response = HttpResponse(canvas.getpdfdata(), content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=%s.pdf" % nombre
    return response


def imagenes(canvas, y, *args):
    imagenes = [imagen for imagen in args if imagen is not None]
    dy = max(imagen.height for imagen in imagenes)
    dx = (A4[0] - sum(imagen.width for imagen in imagenes)) / (len(imagenes)+1)
    y = avanzar(canvas, y, dy)
    x = dx
    r = PDFRenderer()
    for imagen in imagenes:
        r.draw(imagen, canvas, x, y)
        x += dx + imagen.width
    return y


def titulo(canvas, y, titulo, fontSize=12):
    fontName = "Helvetica-Bold"
    y = avanzar(canvas, y, fontSize)
    texto = PDFTextObject(canvas, MARGEN, y)
    texto.setFont(fontName, fontSize)
    texto.textOut(titulo)
    canvas.drawText(texto)
    canvas.line(MARGEN, y, A4[0]-MARGEN, y)
    return y


def texto(canvas, y, linea):
    fontName = "Helvetica"
    fontSize = 10
    y = avanzar(canvas, y, fontSize)
    texto = PDFTextObject(canvas, MARGEN, y)
    texto.setFont(fontName, fontSize)
    texto.textOut(linea)
    canvas.drawText(texto)
    return y


def referencias(canvas, x, y, w, h, datos):
    fontName = "Helvetica"
    fontSize = 9
    medioFontSize = fontSize/2
    y = avanzar(canvas, y, h)
    canvas.setFont(fontName, fontSize)
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(0.5)
    canvas.rect(x, y, w, h, fill=0, stroke=1)
    x += medioFontSize
    y += medioFontSize
    w -= fontSize
    n = len(datos["colores"])
    d = w/n
    for i in range(n):
        p = x + (i*d)
        canvas.setFillColor(colors.HexColor( datos["colores"][i] ))
        canvas.rect(p, y, fontSize, fontSize, fill=1, stroke=0)
        p += fontSize+medioFontSize
        canvas.setFillColor(colors.black)
        canvas.drawString(p, y, datos["categorias"][i])
    return y-medioFontSize


def tabla(canvas, y, columnas, encabezado, texto):
    fontSize = 9
    salto = fontSize+2

    y = avanzar(canvas, y, salto)
    canvas.setFont("Helvetica-Bold", fontSize)
    for i in range(len(columnas)):
        canvas.drawString(columnas[i], y, encabezado[i])

    canvas.setFont("Helvetica", fontSize)
    for fila in texto:
        y = avanzar(canvas, y, salto)
        for i in range(len(columnas)):
            canvas.drawString(columnas[i], y, fila[i])
    return y
