from django.urls import path
from . import views as servicios_views
from VeterinariaPatagonica import views

app_name = 'servicios'
urlpatterns = [
    path('', servicios_views.verHabilitados, name='servicioVerHabilitados'),
    path('verDeshabilitados/', servicios_views.verDeshabilitados, name='servicioVerDeshabilitados'),
    #path('crear/<int:id>/', servicios_views.crear, name='servicioCrear'),
    path('crear/', servicios_views.crear, name='servicioCrear'),
    path('ver/<int:id>/', servicios_views.ver, name='servicioVer'),
    path('modificar/<int:id>/', servicios_views.crear, name='servicioModificar'),
    path('deshabilitar/<int:id>/', servicios_views.deshabilitar, name='servicioDeshabilitar'),
    path('habilitar/<int:id>/', servicios_views.habilitar, name='servicioHabilitar'),
    path('eliminar/<int:id>/', servicios_views.eliminar, name='servicioEliminar'),

    ]
