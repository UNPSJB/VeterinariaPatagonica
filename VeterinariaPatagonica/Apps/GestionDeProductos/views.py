from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from .models import Producto
from .forms import ProductoFormFactory, FiltradoForm
from VeterinariaPatagonica import tools

from dal import autocomplete
from django.db.models import Q
from Apps.GestionDeRubros.models import Rubro

from VeterinariaPatagonica.tools import GestorListadoQueryset

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#Workbook nos permite crear libros en excel
from openpyxl import Workbook

productosFiltrados = [] 

def producto(request):
    context = {}#Defino un contexto.
    template = loader.get_template('GestionDeProductos/GestionDeProductos.html')#Cargo el template desde la carpeta templates/GestionDeProductos.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeProductos.add_Producto', raise_exception=True)
def modificar(request, id = None):
    producto = Producto.objects.get(id=id) if id is not None else None
    ProductoForm = ProductoFormFactory(producto)

    if (id==None):
        context = {"titulo": 1, 'usuario': request.user}
    else:
        context = {"titulo": 2, 'usuario': request.user}

    if request.method == 'POST':
        formulario = ProductoForm(request.POST, instance=producto)
        print(formulario.is_valid())
        print(formulario)
        if formulario.is_valid():
            producto = formulario.save()
            return HttpResponseRedirect("/GestionDeProductos/ver/{}".format(producto.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = ProductoForm(instance=producto)
    template = loader.get_template('GestionDeProductos/formulario.html')

    return HttpResponse(template.render(context, request))

def verHabilitados(request):
    """ Listado de productos habilitados """

    global productosFiltrados
    gestor = GestorListadoQueryset(
        orden=[
            ["orden_nombre", "Nombre"],
            ["orden_marca", "Marca"],
        ],
        claseFiltros=FiltradoForm,
    )

    productos = Producto.objects.habilitados()
    gestor.cargar(request, productos, Producto)
    gestor.ordenar()

    if gestor.formFiltros.is_valid() and gestor.formFiltros.filtros():
        gestor.filtrar()

    productosFiltrados = gestor.queryset
    template = loader.get_template('GestionDeProductos/verHabilitados.html')
    contexto = {
        "gestor": gestor,
    }
    return HttpResponse(template.render(contexto, request))


def verDeshabilitados(request):
    """ Listado de clientes deshabilitados """
    global productosFiltrados
    gestor = GestorListadoQueryset(
        orden=[
            ["orden_nombre", "Nombre"],
            ["orden_marca", "Marca"],
        ],
        claseFiltros=FiltradoForm,
    )

    productos = Producto.objects.deshabilitados()
    gestor.cargar(request, productos, Producto)
    gestor.ordenar()
    if gestor.formFiltros.is_valid() and gestor.formFiltros.filtros():
        gestor.filtrar()

    productosFiltrados = gestor.queryset
    template = loader.get_template('GestionDeProductos/verDeshabilitados.html')
    contexto = {
        "usuario": request.user,
        "gestor": gestor
    }
    return HttpResponse(template.render(contexto, request))

def ver(request, id):
    try:
        productos = Producto.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404( "No encontrado", "El Producto con id={} no existe.".format(id))

    template = loader.get_template('GestionDeProductos/ver.html')
    context = {
        'producto': productos,
        'usuario': request.user
    }
    return HttpResponse(template.render(context, request))


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeProductos.delete_Producto', raise_exception=True)
def deshabilitar(request, id):

    try:
        producto = Producto.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    producto.baja = True
    producto.save()

    return HttpResponseRedirect( "/GestionDeProductos/verDeshabilitados/" )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeProductos.delete_Producto', raise_exception=True)
def habilitar(request, id):
    try:
        producto = Producto.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    producto.baja = False
    producto.save()

    return HttpResponseRedirect( "/GestionDeProductos/verHabilitados/" )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeProductos.delete_Producto', raise_exception=True)
def eliminar(request, id):

    try:
        producto = Producto.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()
    if request.method == 'POST':
        producto.delete()
        return HttpResponseRedirect( "/GestionDeProductos/verDeshabilitados/" )
    else:
        template = loader.get_template('GestionDeProductos/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }
        return HttpResponse( template.render( context, request) )

def ListadoProductosExcel(request):
    # Creamos el libro de trabajo
    wb = Workbook()
    # Definimos como nuestra hoja de trabajo, la hoja activa, por defecto la primera del libro
    ws = wb.active
    # En la celda B1 ponemos el texto 'LISTADO DE PRODUCTOS'
    ws['B1'] = 'LISTADO DE PRODUCTOS'
    # Juntamos las celdas desde la B1 hasta la E1, formando una sola celda
    ws.merge_cells('B1:F1')
    # Creamos los encabezados desde la celda B3 hasta la E3
    ws['B3'] = 'NOMBRE'
    ws['C3'] = 'MARCA'
    cont = 5
    # Recorremos el conjunto de productos y vamos escribiendo cada uno de los datos en las celdas
    for producto in productosFiltrados:
        ws.cell(row=cont, column=2).value = producto.nombre
        ws.cell(row=cont, column=3).value = producto.marca
        cont = cont + 1
    
    '''dims = {}
    for row in ws.rows:
        for cell in row:
            if cell.value:
                dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))    
    for col, value in dims.items():
        print("value", value)
        ws.column_dimensions[col].width = str(value)'''
    
    # Establecemos el nombre del archivo
    nombre_archivo = "ListadoProductos.xlsx"
    # Definimos que el tipo de respuesta a devolver es un archivo de microsoft excel
    response = HttpResponse(content_type="application/ms-excel")
    contenido = "attachment; filename={0}".format(nombre_archivo)
    response["Content-Disposition"] = contenido
    wb.save(response)
    return response

class rubroAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        qs = Rubro.objects.all()
        if self.q:
            qs = qs.filter(Q(nombre__icontains=self.q))

        return qs
""""@login_required
def documentationProducto(request, tipo):
    if (tipo==1):
        template = loader.get_template('GestionDeProductos/manual_ayuda_producto/build/archivos/botonHD.html')
    elif(tipo==2):
        template = loader.get_template('GestionDeMascotas/manual_ayuda_mascota/build/archivos/criteriosBusqueda.html')

    contexto = {
        'usuario': request.user,
    }

    return HttpResponse(template.render(contexto, request))

@login_required
def documentation(request):

    template = loader.get_template('GestionDeMascotas/manual_ayuda_mascota/build/index.html')
    contexto = {
        'usuario': request.user,
    }

    return HttpResponse(template.render(contexto, request))
"""