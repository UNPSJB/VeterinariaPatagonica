from django.urls import path
from . import views

app_name="tiposDeAtencion"

urlpatterns = [
    path("", views.listar, name="habilitados"),
    path("habilitados/", views.listar, name="habilitados"),
    path("deshabilitados/", views.listar, {"habilitados" : False}, name="deshabilitados"),
    path("crear/", views.crear, name="crear"),
    path("ver/<int:id>/", views.ver, name="ver"),
    path("modificar/<int:id>/", views.modificar, name="modificar"),
    path("deshabilitar/<int:id>/", views.cambioEstado, {"baja" : True}, name="deshabilitar"),
    path("habilitar/<int:id>/", views.cambioEstado, {"baja" : False}, name="habilitar"),
]
