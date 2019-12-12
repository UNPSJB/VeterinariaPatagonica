from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from .models import Mascota
from .forms import MascotaFormFactory, FiltradoForm
from VeterinariaPatagonica import tools
from dal import autocomplete
from django.db.models import Q
from Apps.GestionDeClientes.models import Cliente
from django.urls import reverse_lazy
from VeterinariaPatagonica.tools import GestorListadoQueryset

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.conf import settings
from io import BytesIO
from reportlab.pdfgen import canvas
from django.views.generic import View
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from openpyxl import Workbook

mascotasFiltradas = []

def mascota(request):
    context = {}
    template = loader.get_template('GestionDeMascotas/GestionDeMascotas.html')
    return HttpResponse(template.render(context, request))


@permission_required('GestionDeMascotas.deshabilitar_mascota', raise_exception=True)
def dispatch(self, *args, **kwargs):
    return super(Mascota, self).dispatch(*args, **kwargs)

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.add_Mascota', raise_exception=True)
def modificar(request, id= None, cliente_id=None):
    mascota = Mascota.objects.get(id=id) if id is not None else None
    cliente = None
    if cliente_id:
        cliente = Cliente.objects.get(pk=cliente_id)
    MascotaForm = MascotaFormFactory(mascota, cliente)

    if (id==None):
        context = {"titulo": 1, 'usuario': request.user}
    else:
        context = {"titulo": 2, 'usuario': request.user}

    if request.method == 'POST':
        formulario = MascotaForm(request.POST, instance=mascota)
        print(formulario.is_valid())
        print(formulario)
        if formulario.is_valid():
            mascota = formulario.save()
            mascota.generadorDePatente(mascota.id)
            mascota = formulario.save()
            return HttpResponseRedirect("/GestionDeMascotas/ver/{}".format(mascota.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = MascotaForm(instance=mascota)
    template = loader.get_template('GestionDeMascotas/formulario.html')
    return HttpResponse(template.render(context, request))

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.delete_Mascota', raise_exception=True)
def habilitar(request, id):

    try:
        mascota= Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    mascota.baja = False
    mascota.save()

    return HttpResponseRedirect( "/GestionDeMascotas/verHabilitados/" )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.delete_Mascotas', raise_exception=True)
def deshabilitar(request, id):
    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    mascota.baja = True
    mascota.save()

    return HttpResponseRedirect( "/GestionDeMascotas/verDeshabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.delete_Mascota', raise_exception=True)
def eliminar(request, id):
    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()
    if request.method == 'POST':
        mascota.delete()
        return HttpResponseRedirect( "/GestionDeMascotas/verDeshabilitados/" )
    else:
        template = loader.get_template('GestionDeMascotas/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }
        return HttpResponse( template.render( context, request) )

def ver(request, id):

    try:
        mascotas = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("No encontrado", "La mascota con patente={} no existe.".format(id))


    template = loader.get_template('GestionDeMascotas/ver.html')
    contexto = {
        'mascota': mascotas,
        'usuario': request.user
    }
    return HttpResponse(template.render(contexto, request))



def verHabilitados(request):

    global mascotasFiltradas
    gestor = GestorListadoQueryset(
        orden=[
            ["orden_patente", "Patente"],
            ["orden_nombre", "Nombre"],
            ["orden_cliente", "Dueño"],
            ["orden_especie", "Especie"],
        ],
        claseFiltros=FiltradoForm,
    )

    mascotas = Mascota.objects.habilitados()
    gestor.cargar(request, mascotas, Mascota)
    gestor.ordenar()
    
    if gestor.formFiltros.is_valid() and gestor.formFiltros.filtros():
        gestor.filtrar()

    mascotasFiltradas = gestor.queryset
    template = loader.get_template('GestionDeMascotas/verHabilitados.html')
    contexto = {"gestor" : gestor,}
    return HttpResponse(template.render(contexto, request))

def verDeshabilitados(request):

    global mascotasFiltradas
    gestor = GestorListadoQueryset(
        orden=[
            ["orden_patente", "Patente"],
            ["orden_nombre", "Nombre"],
            ["orden_cliente", "Dueño"],
            ["orden_especie", "Especie"],
        ],
        claseFiltros=FiltradoForm,
    )

    mascotas = Mascota.objects.deshabilitados()
    gestor.cargar(request, mascotas, Mascota)
    gestor.ordenar()
    if gestor.formFiltros.is_valid() and gestor.formFiltros.filtros():
        gestor.filtrar()

    mascotasFiltradas = gestor.queryset
    template = loader.get_template('GestionDeMascotas/verDeshabilitados.html')
    contexto = {
        'usuario': request.user,
        "gestor" : gestor,
    }
    return HttpResponse(template.render(contexto, request))

def ListadoMascotasExcel(request):
    wb = Workbook()
    ws = wb.active
    ws['B1'] = 'LISTADO DE MASCOTAS'
    ws.merge_cells('B1:E1')
    ws['B3'] = 'PATENTE'
    ws['C3'] = 'NOMBRE'
    ws['D3'] = 'DUEÑO'
    ws['E3'] = 'ESPECIE'
    cont = 4

    for mascota in mascotasFiltradas:
        ws.cell(row=cont, column=2).value = mascota.patente
        ws.cell(row=cont, column=3).value = mascota.nombre
        ws.cell(row=cont, column=4).value = str(mascota.cliente)
        ws.cell(row=cont, column=5).value = mascota.especie
        cont = cont + 1
    
    '''dims = {}
    for row in ws.rows:
        for cell in row:
            if cell.value:
                dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))    
    for col, value in dims.items():
        print("value", value)
        ws.column_dimensions[col].width = str(value)'''


    nombre_archivo = "ListadoMascotas.xlsx"

    response = HttpResponse(content_type="application/ms-excel")
    contenido = "attachment; filename={0}".format(nombre_archivo)
    response["Content-Disposition"] = contenido
    wb.save(response)
    return response

def ListadoMascotasPDF(request):
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    cabecera(pdf)
    y = 500
    tabla(pdf, y, mascotasFiltradas)
    pdf.showPage()
    pdf.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def cabecera(pdf):
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/logo_vetpat2.jpeg'
    pdf.drawImage(archivo_imagen, 20, 750, 120, 90, preserveAspectRatio=True)
    pdf.setFont("Helvetica", 16)
    pdf.drawString(190, 790, u"VETERINARIA PATAGONICA")
    pdf.setFont("Helvetica", 14)
    pdf.drawString(220, 770, u"LISTADO DE MASCOTAS")

def tabla(pdf, y, mascotas):
    encabezados = ('Patente', 'Nombre', 'Dueño', 'Especie')
    detalles = [(mascota.patente, mascota.nombre, mascota.cliente, mascota.especie) for mascota in mascotas]
    detalle_orden = Table([encabezados] + detalles, colWidths=[3 * cm, 4 * cm, 5 * cm, 4 * cm])
    detalle_orden.setStyle(TableStyle(
        [
            ('ALIGN', (0, 0), (3, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]
    ))
    detalle_orden.wrapOn(pdf, 800, 600)
    detalle_orden.drawOn(pdf, 65, y)


@login_required
def documentationMascota(request, tipo):
    if (tipo==1):
        template = loader.get_template('GestionDeMascotas/manual_ayuda_mascota/build/archivos/botonHD.html')
    elif(tipo==2):
        template = loader.get_template('GestionDeMascotas/manual_ayuda_mascota/build/archivos/criteriosBusqueda.html')

    contexto = {
        'usuario': request.user,
    }

    return HttpResponse(template.render(contexto, request))

@login_required
def ayudaContextualMascota(request):

    template = loader.get_template('GestionDeMascotas/ayudaContextualMascota.html')
    contexto = {
        'usuario': request.user,
    }

    return HttpResponse(template.render(contexto, request))

#file:///C:/Users/Lucila/Downloads/images/image15.png

class clienteAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Cliente.objects.all()

        if self.q:
            qs = qs.filter(Q(apellidos__icontains=self.q) |Q(nombres__icontains=self.q) | Q(dniCuit__icontains=self.q))

        return qs
