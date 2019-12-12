from django.urls import path
from . import views as servicios_views
from VeterinariaPatagonica import views

app_name = 'servicios'
urlpatterns = [
    path('crear/', servicios_views.modificar, name= 'servicioCrear'),
    path('modificar/<int:id>/', servicios_views.modificar, name="servicioModificar"),
    path('ver/<int:id>/', servicios_views.ver, name='servicioVer'),
    path('deshabilitar/<int:id>/', servicios_views.deshabilitar, name='servicioDeshabilitar'),
    path('habilitar/<int:id>/', servicios_views.habilitar, name='servicioHabilitar'),
    path('eliminar/<int:id>/', servicios_views.eliminar, name='servicioEliminar'),
    path('verHabilitados/', servicios_views.verHabilitados, name='servicioVerHabilitados'),
    path('verDeshabilitados/', servicios_views.verDeshabilitados, name='servicioVerDeshabilitados'),
    path('ayudaServicio/', servicios_views.ayudaContextualServicio, name='ayudaServicio'),
    #path('volver/',servicios_views.volver, name='volver'),
]
