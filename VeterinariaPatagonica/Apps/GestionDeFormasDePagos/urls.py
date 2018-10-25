from django.conf.urls import url
from django.urls import path
from . import views as formasDePagos_views
from VeterinariaPatagonica import views

app_name = 'formasDePagos'


urlpatterns = [

    url(r'^$', formasDePagos_views.formasDePagos, name="formaDePago"),
    path('crear/', formasDePagos_views.modificar, name="formaDePagoCrear"),
    path('modificar/<int:id>/', formasDePagos_views.modificar, name="formaDePagoModificar"),
    path('habilitar/<int:id>/', formasDePagos_views.habilitar, name="formaDePagoHabilitar"),
    path('deshabilitar/<int:id>/', formasDePagos_views.deshabilitar, name="formaDePagoDeshabilitar"),
    path('eliminar/<int:id>/', formasDePagos_views.eliminar, name="formaDePagoEliminar"),
    path('ver/<int:id>/', formasDePagos_views.ver, name="formaDePagoVer"),
    path('verHabilitados/', formasDePagos_views.verHabilitados, name="formaDePagoVerHabilitados"),
    path('verDeshabilitados/', formasDePagos_views.verDeshabilitados, name="formaDePagoVerDeshabilitados"),
]
