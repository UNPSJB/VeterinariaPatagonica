from statistics import mean
from datetime import timedelta

from django.db import models as dbmodels

from VeterinariaPatagonica import pdf
from Apps.GestionDeTiposDeAtencion.models import TipoDeAtencion
from .models import *


def recortar(tdas):
    menores = []
    MAX = 15
    if len(tdas) > MAX:
        menores.extend(tdas)
        menores.sort( key=lambda x: x["practicas"], reverse=True )
        menores = menores[MAX:]
        for menor in menores:
            tdas.remove(menor)
    return menores


def clasificar(tdas):

    normales = []
    raros = []
    n = len(tdas)
    x = 100/n

    for tda in tdas:
        if tda["ptjpracticas"] >= x:
            normales.append(tda)
        else:
            raros.append(tda)

    if len(raros)==n:
        normales = raros
        raros = []

    elif raros:
        x = mean(c["ptjpracticas"] for c in raros)
        x /= mean(c["ptjpracticas"] for c in normales)
        x *= (len(normales) / len(raros))
        if x > 0.125:
            normales.extend(raros)
            raros = []
        else:
            agregarOtros(normales, raros)

    descarte = recortar(normales)
    if descarte:
        descarte.extend(raros)
    else:
        descarte = recortar(raros)

    return normales, raros, descarte


def preparar(tdas):
    totalPracticas = 0
    totalRecaudacion = 0
    retorno = []

    for tda in tdas:
        d = {
            "practicas" :   float(tda.cantidad_practicas),
            "recaudacion" : float(tda.recaudacion_practicas),
            "recargo" :     float(tda.recargo),
            "id" :      tda.id,
            "nombre" :  tda.nombre,
            "etiqueta" :"TDA %d" % tda.id,
        }

        retorno.append(d)
        totalPracticas += d["practicas"]
        totalRecaudacion += d["recaudacion"]

    for d in retorno:
        d["ptjpracticas"] = 100.0 * d["practicas"] / totalPracticas
        d["ptjrecaudacion"] = 100.0 * d["recaudacion"] / totalRecaudacion

    return retorno


def agregarOtros(tdas, otros):
    if otros:
        tdas.append({
            "practicas" :    sum(tda["practicas"]    for tda in otros),
            "ptjpracticas" :   sum(tda["ptjpracticas"]   for tda in otros),
            "recaudacion" :  sum(tda["recaudacion"]  for tda in otros),
            "ptjrecaudacion" : sum(tda["ptjrecaudacion"] for tda in otros),
            "recargo" : None,
            "id" :      None,
            "nombre" :  "Otros TDA",
            "etiqueta" :"Otros TDA",
        })


def buscarTDA(practicas, fecha):
    retorno = TipoDeAtencion.objects.none()
    if practicas:
        retorno = TipoDeAtencion.objects.filter(
            practicas__estado__facturada__isnull=False,
            practicas__estado__facturada__marca__date__gte=fecha,
            practicas__in=[x.id for x in practicas]
        ).annotate(
            cantidad_practicas=dbmodels.Count(
                "practicas__id",
                filter=dbmodels.Q(
                    practicas__estado__facturada__isnull=False,
                    practicas__estado__facturada__marca__date__gte=fecha,
                )
            )
        ).annotate(
            recaudacion_practicas=dbmodels.Sum(
                "practicas__precio",
                filter=dbmodels.Q(
                    practicas__estado__facturada__marca__date__gte=fecha,
                    practicas__estado__facturada__isnull=False,
                )
            )
        )
    return retorno


def calcularNiveles(practicas, area):

    acciones = Practica.Acciones
    posibles = acciones.actualizaciones(area.codigo())
    data = {}

    presupuestadas = set([
        x.id for x in practicas.filter(estado__presupuestada__isnull=False)
    ])
    programadas = set([
        x.id for x in practicas.filter(estado__programada__isnull=False)
    ])
    realizadas = set([
        x.id for x in practicas.filter(estado__realizada__isnull=False)
    ])
    facturadas = set([
        x.id for x in practicas.filter(estado__facturada__isnull=False)
    ])
    terminadas = set([
        x.id for x in practicas.filter(estado__facturada__isnull=False, factura__pago__isnull=False)
    ])

    if acciones.presupuestar in posibles:
        data["Presupuestos confirmados"] = 0.0
        if presupuestadas:
            actualizadas = presupuestadas.intersection(programadas, realizadas)
            data["Presupuestos confirmados"] = len(actualizadas) / len(presupuestadas)
            data["Presupuestos confirmados"] *= 100.0

    if acciones.programar in posibles:
        data["Turnos realizados"] = 0.0
        if programadas:
            actualizadas = programadas.intersection(realizadas)
            data["Turnos realizados"] = len(actualizadas) / len(programadas)
            data["Turnos realizados"] *= 100.0

    if acciones.realizar in posibles:
        data["Realizaciones facturadas"] = 0.0
        if realizadas:
            actualizadas = realizadas.intersection(facturadas)
            data["Realizaciones facturadas"] = len(actualizadas) / len(realizadas)
            data["Realizaciones facturadas"] *= 100.0

    if acciones.facturar in posibles:
        data["Facturaciones pagas"] = 0.0
        if facturadas:
            actualizadas = facturadas.intersection(terminadas)
            data["Facturaciones pagas"] = len(actualizadas) / len(facturadas)
            data["Facturaciones pagas"] *= 100.0

    return data


def creadasEntre(practicas, fechaAnterior, fechaPosterior):
    return practicas.filter(
        estado__creada__isnull=False,
        estado__creada__marca__date__range=(fechaAnterior, fechaPosterior)
    )


def contarRealizaciones(realizaciones):
    retorno = {}
    retorno["emergenciaDomicilio"] = realizaciones.filter(
        practica__tipoDeAtencion__emergencia=True,
        practica__tipoDeAtencion__lugar=TipoDeAtencion.EN_DOMICILIO
    ).count()
    retorno["emergenciaVeterinaria"] = realizaciones.filter(
        practica__tipoDeAtencion__emergencia=True,
        practica__tipoDeAtencion__lugar=TipoDeAtencion.EN_VETERINARIA
    ).count()
    retorno["domicilio"] = realizaciones.filter(
        practica__tipoDeAtencion__emergencia=False,
        practica__tipoDeAtencion__lugar=TipoDeAtencion.EN_DOMICILIO
    ).count()
    retorno["veterinaria"] = realizaciones.filter(
        practica__tipoDeAtencion__emergencia=False,
        practica__tipoDeAtencion__lugar=TipoDeAtencion.EN_VETERINARIA
    ).count()
    return retorno


def clasificarRealizaciones(practicas, fecha):
    realizaciones = Realizada.objects.filter(practica__in=[x.id for x in practicas])
    antes = realizaciones.filter(inicio__date__lt=fecha)
    despues = realizaciones.filter(inicio__date__gte=fecha)
    return antes, despues


def realizacionesEntre(practicas, fechaAnterior, fechaPosterior):
    retorno = []
    realizaciones = Realizada.objects.filter(practica__in=[x.id for x in practicas])
    d   = timedelta(days=1)
    dia = fechaPosterior
    while dia >= fechaAnterior:
        cuenta = realizaciones.filter(inicio__date=dia).count()
        retorno.insert(0, cuenta)
        dia = dia - d
    return retorno


def datosTiposDeAtencion(tdas, titulo=None):
    practicas = list( tda["ptjpracticas"] for tda in tdas )
    recaudacion = list( tda["ptjrecaudacion"] for tda in tdas )
    datos = {
        "cantidad" : len(tdas),
        "colores" : ["#9A9A9A", "#CBCBCB"],
        "categorias" : ["Porcentaje de prácticas ", "Porcentaje del total recaudado"],
        "data" : [practicas, recaudacion],
        "labels" : [ tda["etiqueta"] for tda in tdas ],
        "titulo" : titulo
    }
    return datos


def datosPerfiles(cantidades, titulo=None):
    retorno = None
    data = [0.0, 0.0, 0.0, 0.0]
    total = sum(cantidades.values())
    if total>0:
        data[0] = cantidades["veterinaria"] / total
        data[1] = cantidades["domicilio"] / total
        data[2] = cantidades["emergenciaDomicilio"] / total
        data[3] = 1.0 - (data[0] + data[1] + data[2])
        retorno = {
            "tamanio" : 75,
            "categorias" : [
                "En veterinaria",
                "En domicilio",
                "Emergencia en domicilio",
                "Emergencia en veterinaria"
            ],
            "colores" : [
                "#F79646",
                "#AA5523",
                "#772200",
                "#E36C0A"
            ],
            "data" : data,
            "labels" : [ "%.2f %%"%(100*n) for n in data ],
            "titulo" : titulo
        }
    return retorno


def datosRealizacionesPorDia(cantidades, titulo=None):
    retorno = None
    rango = (min(cantidades), max(cantidades))
    if rango[0] < rango[1]:
        retorno = {
            "labels" : {"x" : "Tiempo transcurrido", "y" : "Número de realizaciones"},
            "rango" : rango,
            "data" : [ [ x for x in zip(range(1-len(cantidades),1), cantidades) ] ],
            "colores" : ["#AC1123"],
            "ancho" : 400,
            "alto" : 150,
            "titulo" : titulo,
        }
    return retorno


def datosPorcentajesActualizacion(niveles, titulo=None):
    etiquetas = [ clave for clave in (
        "Presupuestos confirmados",
        "Turnos realizados",
        "Realizaciones facturadas",
        "Facturaciones pagas",
    ) if clave in niveles ]
    data = [ niveles[clave] for clave in etiquetas ]
    retorno = {
        "data" : [ data ],
        "labels" : etiquetas,
        "colores" : ["#46BFBD"],
        "alto" : 160,
        "ancho" : 420,
        "titulo" : titulo,
    }
    return retorno


def graficar(datos):
    grafico = None
    if 1 < datos["cantidad"] < 5:
        datos["ancho"] = 360
        datos["alto"] = 100
        grafico = pdf.barras(datos)
    elif datos["cantidad"] >= 5:
        datos["tamanio"] = 450
        grafico = pdf.radar(datos)
    return grafico


def tabular(canvas, y, tdas):
    columnas = [pdf.MARGEN, 50, 230, 280, 350, 420, 480]

    encabezados = [
        "Id",
        "Nombre",
        "Recargo",
        "Prácticas",
        "Recaudación",
        "Prácticas(%)",
        "Recaudación(%)",
    ]

    textoTabla = [ [
        "%-6d" % tda["id"] if tda["id"] is not None else "",
        tda["nombre"][0:35] + ("..." if len(tda["nombre"])>35 else ""),
        "%%%-3.2f" % tda["recargo"] if tda["recargo"] is not None else "",
        "%-9d" % tda["practicas"],
        "$%-8.2f" % tda["recaudacion"],
        "%%%-3.2f" % tda["ptjpracticas"],
        "%%%-3.2f" % tda["ptjrecaudacion"],
    ] for tda in tdas ]

    return pdf.tabla(canvas, y, columnas, encabezados, textoTabla)


def perfiles(canvas, y, practicas, hasta, dias):
    fecha = hasta - timedelta(days=dias)
    antes, despues = clasificarRealizaciones(practicas, fecha)
    cantidadesAntes = contarRealizaciones(antes)
    cantidadesDespues = contarRealizaciones(despues)
    da = datosPerfiles(cantidadesAntes, "Hasta el día " + fecha.strftime("%d/%m/%y"))
    dd = datosPerfiles(cantidadesDespues, "Desde el día " + fecha.strftime("%d/%m/%y"))

    y = -10 + pdf.titulo(canvas, y, "Perfil del tipo de atención en prácticas realizadas (últimos %d días)"%dias)
    if dd is not None:
        g = [pdf.torta(dd)]
        if da is not None:
            g.insert(0, pdf.torta(da))
        y = -10 + pdf.graficos(canvas, y, *g)
        y = pdf.referencias(canvas, pdf.MARGEN, y, pdf.A4[0]-(2*pdf.MARGEN), 20, dd)
    else:
        y = -5 + pdf.texto(canvas, y, "No hay prácticas realizadas desde el día %s."%fecha.strftime("%d/%m/%y"))
    return y


def realizacionesPorDia(canvas, y, practicas, hasta, dias):
    desde=hasta - timedelta(days=dias)
    cantidades = realizacionesEntre(practicas, desde, hasta)
    datos = datosRealizacionesPorDia(cantidades)

    y = -10 + pdf.titulo(canvas, y, "Número diario de prácticas realizadas (últimos %d días)"%dias)
    if datos:
        g = pdf.cartesiano(datos)
        y = pdf.graficos(canvas, y, g)
    else:
        y = -5 + pdf.texto(canvas, y, "No hay prácticas realizadas desde el día %s."%desde.strftime("%d/%m/%y"))
    return y


def porcentajesActualizacion(canvas, y, practicas, area, hasta, dias):
    desde = hasta - timedelta(days=dias)
    practicas = creadasEntre(practicas, desde, hasta)

    y = -10 + pdf.titulo(canvas, y, "Prácticas actualizadas según estado (últimos %d días)"%dias)
    if practicas:
        niveles = calcularNiveles(practicas, area)
        datos = datosPorcentajesActualizacion(niveles)
        g = pdf.barras(datos)
        y = pdf.graficos(canvas, y, g)
    else:
        y = -5 + pdf.texto(canvas, y, "No hay prácticas creadas desde el día %s."%desde.strftime("%d/%m/%y"))
    return y


def tiposDeAtencion(canvas, y, practicas, hasta, dias):
    fecha = hasta-timedelta(days=dias)
    tdas = buscarTDA(practicas, fecha)
    y = -10 + pdf.titulo(canvas, y, "Tipos de atención más frecuentes (últimos %d días)"%dias)
    if tdas:
        habilitados = tdas.filter(baja=False)
        deshabilitados = tdas.filter(baja=True)
        if deshabilitados:
            y = -5 + pdf.texto(canvas, y, "Hay registradas %d prácticas con tipos de atención deshabilitados facturadas desde el día %s." % (sum(tda.cantidad_practicas for tda in deshabilitados), fecha.strftime("%d/%m/%y")))
        if habilitados:
            normales, raros, descarte = clasificar(preparar(habilitados))
            if raros:
                y = -5 + pdf.texto(canvas, y, "Se analizan por separado %d de los tipos de atención por presentar menor frecuencia de uso (Otros TDA)."%len(excepcionales))
            if descarte:
                y = -5 + pdf.texto(canvas, y, "Se limita el reporte a %d de los tipos de atención con mayor frecuencia de uso."%(len(regulares)+len(excepcionales)) )
            datos = datosTiposDeAtencion(normales, "Tipos de atención")
            grafico = graficar(datos)
            if grafico:
                y = -10 + pdf.graficos(canvas, y, grafico)
                y = -10 + pdf.referencias(canvas, pdf.MARGEN, y, pdf.A4[0]-(2*pdf.MARGEN), 20, datos)
            y = -45 + tabular(canvas, y, normales)
            if raros:
                datos  = datosTiposDeAtencion(raros, "Otros tipos de atención")
                grafico = graficar(datos)
                if grafico:
                    y = -10 + pdf.graficos(canvas, y, grafico)
                    y = -10 + pdf.referencias(canvas, pdf.MARGEN, y, pdf.A4[0]-(2*pdf.MARGEN), 20, datos)
                y = -45 + tabular(canvas, y, raros)
            if descarte:
                y = -5 + pdf.texto(canvas, y, "Los tipos de atención sin analizar son:")
                y = -45 + tabular(canvas, y, descarte)
        else:
            y = -5 + pdf.texto(canvas, y, "No se han facturado prácticas con ninguno de los tipos de atención habilitados desde el día %s." % fecha.strftime("%d/%m/%y"))
    else:
        y = -5 + pdf.texto(canvas, y, "No se han facturado prácticas desde el día %s."%fecha.strftime("%d/%m/%y"))
    return y
