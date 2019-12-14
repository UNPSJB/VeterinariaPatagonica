from django.conf.urls import url
from django.urls import path
from . import views


app_name = 'pagos'


urlpatterns = [
    # url(r'^$', pagos_views.pago, name="pago"),
    # path('pagoCrear/<int:idFactura>/', pagos_views.crear, name="pagoCrear"),
    # path('pagoEliminar/<int:id>/', pagos_views.eliminar, name="pagoEliminar"),
    # path('pagoVer/<int:id>/', pagos_views.ver, name="pagoVer"),
    # path('pagoListar/', pagos_views.listar, name="pagoListar"),

    path('crear/<int:id>/', views.crear, name="crear"),
    path('listar/', views.listar, name="listar"),
    path('ver/<int:id>/', views.ver, name="ver"),
]
