from django.conf.urls import url
from django.urls import path
from . import views as pagos_views

from Apps.GestionDeFacturas import views as facturas_views


app_name = 'pagos'

urlpatterns = [

    url(r'^$', pagos_views.pago, name="pago"),
    path('crear/', pagos_views.modificar, name="pagoCrear"),
    path('modificar/<int:id>/', pagos_views.modificar, name="pagoModificar"),
    path('eliminar/<int:id>/', pagos_views.eliminar, name="pagoEliminar"),
    path('ver/<int:id>/', pagos_views.ver, name="pagoVer"),
    path('listar/', pagos_views.listar, name="pagoListar"),
]

