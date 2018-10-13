from django.conf.urls import url
from . import views as mascotas_views
#from VeterinariaPatagonica import views
from django.urls import path
from . import views
app_name = 'mascotas'

urlpatterns = [
    url(r'^$', mascotas_views.mascota, name='mascota'),

    path('crear/', mascotas_views.modificar, name="mascotaCrear"),
    path('modificar/<int:id>/', mascotas_views.modificar, name="mascotaModificar"),
    path('deshabilitar/<int:id>/', mascotas_views.deshabilitar, name='mascotaDeshabilitar'),
    path('habilitar/<int:id>/', mascotas_views.habilitar, name='mascotaHabilitar'),
    path('eliminar/<int:id>/', mascotas_views.eliminar, name='mascotaEliminar'),
    path('ver/<int:id>/', mascotas_views.ver, name="mascotaVer"),
    path('verHabilitados/', mascotas_views.verHabilitados, name='mascotaVerHabilitados'),
    path('verDeshabilitados/', mascotas_views.verDeshabilitados, name='mascotaVerDeshabilitados'),

    path('', mascotas_views.verHabilitados, name='mascotaVerHabilitados'),

]