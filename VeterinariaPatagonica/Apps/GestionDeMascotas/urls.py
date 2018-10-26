from django.conf.urls import url
from django.urls import path
from . import views as mascotas_views
#from VeterinariaPatagonica import views


app_name = 'mascotas'

urlpatterns = [
    url(r'^$', mascotas_views.mascota, name='mascota'),
    path('crear/', mascotas_views.modificar, name="mascotaCrear"),
    path('modificar/<int:id>/', mascotas_views.modificar, name="mascotaModificar"),
    path('habilitar/<int:id>/', mascotas_views.habilitar, name='mascotaHabilitar'),
    path('deshabilitar/<int:id>/', mascotas_views.deshabilitar, name='mascotaDeshabilitar'),
    path('eliminar/<int:id>/', mascotas_views.eliminar, name='mascotaEliminar'),
    path('ver/<int:id>/', mascotas_views.ver, name="mascotaVer"),
    path('verHabilitados/', mascotas_views.verHabilitados, name='mascotaVerHabilitados'),
    path('verDeshabilitados/', mascotas_views.verDeshabilitados, name='mascotaVerDeshabilitados'),
    path('busqueda/<int:id>/', mascotas_views.busqueda, name='mascotaBusqueda'),



]
