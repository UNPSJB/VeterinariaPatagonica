from django.conf.urls import url
from . import views as mascotas_views
#from VeterinariaPatagonica import views
from django.urls import path
from . import views
app_name = 'mascotas'

urlpatterns = [
    url(r'^$', mascotas_views.mascota, name='mascota'),
    url(r'altamascota.html/$', mascotas_views.alta, name='alta'),
    # url(r'altamascota.html/$',views.verdemo, name='alta'),

    path('ver/<int:id>/', views.ver, name='mascotasVer'),
    path('modificar/<int:id>/', views.modificar, name='mascotasModificar'),
    path('deshabilitar/<int:id>/', views.deshabilitar, name='mascotasDeshabilitar'),
    path('habilitar/<int:id>/', views.habilitar, name='mascotasHabilitar'),
    path('eliminar/<int:id>/', views.eliminar, name='mascotasEliminar'),
    path('ver_habilitados/', views.verHabilitados, name='mascotasVerHabilitados'),
    path('ver_deshabilitados/', views.verDeshabilitados, name='mascotasVerDeshabilitados'),
    path('', views.verHabilitados, name='mascotasVerHabilitados'),


]