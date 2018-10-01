from django.urls import path
from . import views

app_name = "tiposDeAtencion"
urlpatterns = [
    path('crear/', views.crear, name='tipoDeAtencionCrear'),
    path('ver/<int:id>/', views.ver, name='tipoDeAtencionVer'),
    path('modificar/<int:id>/', views.modificar, name='tipoDeAtencionModificar'),
    path('deshabilitar/<int:id>/', views.deshabilitar, name='tipoDeAtencionDeshabilitar'),
    path('habilitar/<int:id>/', views.habilitar, name='tipoDeAtencionHabilitar'),
    path('eliminar/<int:id>/', views.eliminar, name='tipoDeAtencionEliminar'),
    path('ver_habilitados/', views.verHabilitados, name='tipoDeAtencionVerHabilitados'),
    path('ver_deshabilitados/', views.verDeshabilitados, name='tipoDeAtencionVerDeshabilitados'),
    path('', views.verHabilitados, name='tipoDeAtencionVerHabilitados'),
]
