from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse


from .models import Cliente
from .forms import ClienteFormFactory, FiltradoForm
from VeterinariaPatagonica import tools
from .gestionDeClientes import *

#Vista genérica para mostrar resultados
from django.views.generic.base import TemplateView
#Workbook nos permite crear libros en excel
from openpyxl import Workbook

#Importamos settings para poder tener a la mano la ruta de la carpeta media
from django.conf import settings
from io import BytesIO
from reportlab.pdfgen import canvas
from django.views.generic import View
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib import colors

def clientes(request):
    context = {}#Defino el contexto.
    template = loader.get_template('GestionDeClientes/GestionDeClientes.html')#Cargo el template desde la carpeta templates/GestionDeClientes.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeClientes.add_Cliente', raise_exception=True)
def modificar(request, id = None, irAMascotas=1): #irAMascotas=1 -> False, irAMasotas=0 -> True

    cliente = Cliente.objects.get(id=id) if id is not None else None
    ClienteForm = ClienteFormFactory(cliente)

    if (id==None):
        context = {"titulo": 1, 'usuario': request.user}
    else:
        context = {"titulo": 2, 'usuario': request.user}

    if request.method == 'POST':
        formulario = ClienteForm(request.POST, instance=cliente)
        print(formulario)
        if formulario.is_valid():
            cliente = formulario.save()
            return HttpResponseRedirect("/GestionDeClientes/ver/{}".format(cliente.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = ClienteForm(instance=cliente)
    template = loader.get_template('GestionDeClientes/formulario.html')
    return HttpResponse(template.render(context, request))

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeClientes.delete_Cliente', raise_exception=True)
def habilitar(request, id):
    try:
        cliente = Cliente.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    cliente.baja = False
    cliente.save()

    return HttpResponseRedirect( "/GestionDeClientes/verHabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeCliente.delete_Cliente', raise_exception=True)
def deshabilitar(request, id):

    try:
        cliente = Cliente.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    cliente.baja = True
    cliente.save()

    return HttpResponseRedirect( "/GestionDeClientes/verDeshabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeClientes.delete_Cliente', raise_exception=True)
def eliminar(request, id):
    try:
        cliente = Cliente.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()
    if request.method == 'POST':
        cliente.delete()
        return HttpResponseRedirect( "/GestionDeClientes/verDeshabilitados/" )
    else:
        template = loader.get_template('GestionDeClientes/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }
        return HttpResponse( template.render( context, request) )

def ver(request, id):

    try:
        cliente = Cliente.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("No encontrado", "El cliente con id={} no existe.".format(id))

    template = loader.get_template('GestionDeClientes/ver.html')
    contexto = {
        'cliente': cliente,
        'usuario': request.user
    }

    return HttpResponse(template.render(contexto, request))


def ReporteClientesExcel(request):
    # Obtenemos todos los clientes de nuestra base de datos
    clientes = Cliente.objects.habilitados()
    clientes = clientes.filter(tools.paramsToFilter(request.GET, Cliente))
    print(clientes)
    template = loader.get_template('GestionDeClientes/verHabilitados.html')
    contexto = {
        'clientes' : clientes,
        'usuario' : request.user,
    }
    var=1
    if (var==1):
        # Creamos el libro de trabajo
        wb = Workbook()
        # Definimos como nuestra hoja de trabajo, la hoja activa, por defecto la primera del libro
        ws = wb.active
        # En la celda B1 ponemos el texto 'REPORTE DE CLIENTES'
        ws['B1'] = 'REPORTE DE CLIENTES'
        # Juntamos las celdas desde la B1 hasta la E1, formando una sola celda
        ws.merge_cells('B1:E1')
        # Creamos los encabezados desde la celda B3 hasta la E3
        ws['B3'] = 'DNI'
        ws['C3'] = 'NOMBRES'
        ws['D3'] = 'APELLIDOS'
        ws['E3'] = 'DIRECCION'
        cont = 4
        # Recorremos el conjunto de personas y vamos escribiendo cada uno de los datos en las celdas
        for cliente in clientes:
            ws.cell(row=cont, column=2).value = cliente.dniCuit
            ws.cell(row=cont, column=3).value = cliente.nombres
            ws.cell(row=cont, column=4).value = cliente.apellidos
            ws.cell(row=cont, column=5).value = cliente.direccion
            cont = cont + 1
        # Establecemos el nombre del archivo
        nombre_archivo = "ReporteClientesExcel.xlsx"
        # Definimos que el tipo de respuesta a devolver es un archivo de microsoft excel
        response = HttpResponse(content_type="application/ms-excel")
        contenido = "attachment; filename={0}".format(nombre_archivo)
        response["Content-Disposition"] = contenido
        wb.save(response)
        return response
    return HttpResponse(template.render(contexto,request))




def cabecera(pdf):
    # Utilizamos el archivo logo_vetpat.png que está guardado en la carpeta media/imagenes
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/logo_vetpat.png'
    # Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
    pdf.drawImage(archivo_imagen, 60, 750, 120, 90, preserveAspectRatio=True)
    # Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
    pdf.setFont("Helvetica", 16)
    # Dibujamos una cadena en la ubicación X,Y especificada
    pdf.drawString(230, 790, u"VETERINARIA PATAGONICA")
    pdf.setFont("Helvetica", 14)
    pdf.drawString(260, 770, u"REPORTE DE CLIENTES")


def tabla(pdf, y, clientes):
    # Creamos una tupla de encabezados para neustra tabla
    encabezados = ('DNI', 'Nombres', 'Apellidos', 'Direccion')
    # Creamos una lista de tuplas que van a contener a las personas
    #clientes = Cliente.objects.habilitados().filter(nombres='Karina')
    print("TABLA", clientes)
    detalles = [(cliente.dniCuit, cliente.nombres, cliente.apellidos, cliente.direccion) for cliente in
                clientes]
    # Establecemos el tamaño de cada una de las columnas de la tabla
    detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 5 * cm, 5 * cm, 7 * cm])
    # Aplicamos estilos a las celdas de la tabla
    detalle_orden.setStyle(TableStyle(
        [
            # La primera fila(encabezados) va a estar centrada
            ('ALIGN', (0, 0), (3, 0), 'CENTER'),
            # Los bordes de todas las celdas serán de color negro y con un grosor de 1
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # El tamaño de las letras de cada una de las celdas será de 10
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]
    ))
    # Establecemos el tamaño de la hoja que ocupará la tabla
    detalle_orden.wrapOn(pdf, 800, 600)
    # Definimos la coordenada donde se dibujará la tabla
    detalle_orden.drawOn(pdf, 40, y)

def ReporteClientesPDF(request):
    # Obtenemos los clientes de nuestra base de datos
    print( "GET", request.GET)
    print("Secion", request.session)
    clientes = Cliente.objects.habilitados().filter(tools.paramsToFilter(request.session, Cliente))
    print("Hola desde PDF", clientes)

    template = loader.get_template('GestionDeClientes/verHabilitados.html')
    contexto = {
        'clientes': clientes,
        'usuario': request.user,
    }
    var =1
    if (var==1):
        # Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        # Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer)
        # Llamo al método cabecera donde están definidos los datos que aparecen en la cabecera del reporte.
        cabecera(pdf)
        y = 500
        tabla(pdf, y, clientes)
        print("Adentro", clientes)
        # Con show page hacemos un corte de página para pasar a la siguiente
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    return HttpResponse(template.render(contexto,request))



def guardar(session, etiqueta, datos):

    clave = "filtro_crear_%s" % (etiqueta)
    session[clave] = datos

def verHabilitados(request, irA=0):
    clientes = Cliente.objects.habilitados()
    clientes = clientes.filter(tools.paramsToFilter(request.GET, Cliente))
    print("DESDE HABILITADOS",clientes)
    #guardar(request.session, "filtrar", clientes)
    template = loader.get_template('GestionDeClientes/verHabilitados.html')
    contexto = {
        'clientes' : clientes,
        'usuario' : request.user,
    }

    return HttpResponse(template.render(contexto,request))

@login_required(redirect_field_name='proxima')
def listar(request, pagina=1):
    clientes = Cliente.objects.habilitados()
    formFiltrado = FiltradoForm(request.GET)
    if formFiltrado.is_valid():
        clientes = clientes.ordenar(formFiltrado.criterio(), formFiltrado.ascendente())

    paginas = calcularPaginas(clientes)
    clientes = clientesParaPagina(clientes, pagina, paginas)

    template = loader.get_template('GestionDeClientes/verHabilitados.html')
    contexto = {
        "filtrado" : formFiltrado,
        "pagina" : pagina,
        "clientes" : clientes,
        "paginas" : [ i+1 for i in range(paginas)],
    }

    return HttpResponse(template.render(contexto, request))




def verDeshabilitados(request):
    clientes = Cliente.objects.deshabilitados()
    clientes = clientes.filter(tools.paramsToFilter(request.GET, Cliente))
    print(clientes)
    template = loader.get_template('GestionDeClientes/verDeshabilitados.html')
    contexto = {
        'clientes' : clientes,
        'usuario' : request.user,
    }

    return HttpResponse(template.render(contexto, request))




@login_required
def documentationCliente(request, tipo):
    if (tipo==1):
        template = loader.get_template('GestionDeClientes/manual_ayuda_cliente/build/archivos/botonHD.html')
    elif(tipo==2):
        template = loader.get_template('GestionDeClientes/manual_ayuda_cliente/build/archivos/criteriosBusqueda.html')

    contexto = {
        'clientes': clientes,
        'usuario': request.user,
    }

    return HttpResponse(template.render(contexto, request))

@login_required
def documentation(request):

    template = loader.get_template('GestionDeClientes/manual_ayuda_cliente/build/index.html')
    contexto = {
        'clientes': clientes,
        'usuario': request.user,
    }

    return HttpResponse(template.render(contexto, request))
