from django.conf.urls import url
from django.urls import path
from . import views as rubros_views
from VeterinariaPatagonica import views

app_name = 'rubros'


urlpatterns = [

    url(r'^$', rubros_views.rubros, name="rubro"),
    path('crear/', rubros_views.modificar, name="rubroCrear"),
    path('modificar/<int:id>/', rubros_views.modificar, name="rubroModificar"),
    path('habilitar/<int:id>/', rubros_views.habilitar, name="rubroHabilitar"),
    path('deshabilitar/<int:id>/', rubros_views.deshabilitar, name="rubroDeshabilitar"),
    path('eliminar/<int:id>/', rubros_views.eliminar, name="rubroEliminar"),
    path('ver/<int:id>/', rubros_views.ver, name="rubroVer"),
    path('verHabilitados/', rubros_views.verHabilitados, name="rubroVerHabilitados"),
    path('verDeshabilitados/', rubros_views.verDeshabilitados, name="rubroVerDeshabilitados"),
]

