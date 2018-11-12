from django.conf.urls import url
from django.urls import path
from . import views as facturas_views
from VeterinariaPatagonica import views

app_name = 'facturas'


urlpatterns = [

    url(r'^$', facturas_views.facturas, name="factura"),
    path('crear/', facturas_views.modificar, name="facturaCrear"),
    path('modificar/<int:id>/', facturas_views.modificar, name="facturaModificar"),
    path('eliminar/<int:id>/', facturas_views.eliminar, name="facturaEliminar"),
    path('ver/<int:id>/', facturas_views.ver, name="facturaVer"),
    path('clienteAutocomplete/', facturas_views.clienteAutocomplete.as_view(), name='facturaClienteAutocomplete'),
    path('facturarPractica/<int:id>', facturas_views.crearFacturaPractica, name='facturaPractica'),
    path('listar/', facturas_views.listar, name="facturaListar"),
    path('productoAutocomplete/', facturas_views.productoAutocomplete.as_view(), name='facturaProductoAutocomplete'),

]