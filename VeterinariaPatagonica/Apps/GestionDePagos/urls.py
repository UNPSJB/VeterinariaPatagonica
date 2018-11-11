from django.conf.urls import url
from django.urls import path
from . import views as pagos_views


app_name = 'pagos'

urlpatterns = [

    url(r'^$', pagos_views.pagos, name="pago"),
    path('crear/', pagos_views.modificar, name="pagoCrear"),
    path('modificar/<int:id>/', pagos_views.modificar, name="pagoModificar"),
    path('habilitar/<int:id>/', pagos_views.habilitar, name="pagoHabilitar"),
    path('deshabilitar/<int:id>/', pagos_views.deshabilitar, name="pagoDeshabilitar"),
    path('eliminar/<int:id>/', pagos_views.eliminar, name="pagoEliminar"),
    path('ver/<int:id>/', pagos_views.ver, name="pagoVer"),
    path('verHabilitados/', pagos_views.verHabilitados, name="pagoVerHabilitados"),
    path('verDeshabilitados/', pagos_views.verDeshabilitados, name="pagoVerDeshabilitados"),

]
