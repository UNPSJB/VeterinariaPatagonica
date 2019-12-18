from django.conf.urls import url
from django.urls import path, include
from . import views
# from . import views as facturas_views


app_name = 'facturas'


urlpatterns = [
    # url(r'^$', facturas_views.facturas, name="factura"),
    # path('facturaCrear/', facturas_views.modificar, name="facturaCrear"),
    # path('facturaVer/<int:id>/', facturas_views.ver, name="facturaVer"),
    # path('facturaListar/', facturas_views.listar, name="facturaListar"),
    # path('facturarPractica/<int:id>', facturas_views.crearFacturaPractica, name='facturaPractica'),
    # path('ver/<int:irAPagar>/', facturas_views.ver, name="facturaVer"),
    # path('clienteAutocomplete/', facturas_views.clienteAutocomplete.as_view(), name='facturaClienteAutocomplete'),
    # path('productoAutocomplete/', facturas_views.productoAutocomplete.as_view(), name='facturaProductoAutocomplete'),
    # path('verPractica/<int:id>', facturas_views.verPractica, name="verPractica"),

    path('facturar/practica/<int:id>/', views.facturarPractica, name='facturarPractica'),
    path('facturar/', views.facturar, name='facturar'),
    path("listar/", views.listar, name="listar"),
    path("ver/<int:id>/", views.ver, name="ver"),
    path("exportar/", include(([
        path("xlsx/", views.exportar, {"formato" : "xlsx"}, name="xlsx"),
    ], "exportar"))),
    path('ayudaCostos/', views.ayudaContextualCosto, name="ayudaCostos"),
]
