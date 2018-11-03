from django.conf.urls import url
from django.urls import path
from . import views as facturas_views
from VeterinariaPatagonica import views

app_name = 'facturas'


urlpatterns = [

    url(r'^$', facturas_views.facturas, name="factura"),
    path('crear/', facturas_views.modificar, name="facturaCrear"),
    path('modificar/<int:id>/', facturas_views.modificar, name="facturaModificar"),
    path('habilitar/<int:id>/', facturas_views.habilitar, name="facturaHabilitar"),
    path('deshabilitar/<int:id>/', facturas_views.deshabilitar, name="facturaDeshabilitar"),
    path('eliminar/<int:id>/', facturas_views.eliminar, name="facturaEliminar"),
    path('ver/<int:id>/', facturas_views.ver, name="facturaVer"),
    path('verHabilitados/', facturas_views.verHabilitados, name="facturaVerHabilitados"),
    path('verDeshabilitados/', facturas_views.verDeshabilitados, name="facturaVerDeshabilitados"),

    path('clienteAutocomplete/', facturas_views.clienteAutocomplete.as_view(), name='facturaClienteAutocomplete'),
]