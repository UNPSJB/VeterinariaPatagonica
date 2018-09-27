from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear, name='tda-crear'),
    path('ver/<int:id>/', views.ver, name='tda-ver'),
    path('modificar/<int:id>/', views.modificar, name='tda-modificar'),
    path('deshabilitar/<int:id>/', views.deshabilitar, name='tda-deshabilitar'),
    path('habilitar/<int:id>/', views.habilitar, name='tda-habilitar'),
    path('eliminar/<int:id>/', views.eliminar, name='tda-eliminar'),
    path('ver_habilitados/', views.ver_habilitados, name='tda-ver-habilitados'),
    path('ver_deshabilitados/', views.ver_deshabilitados, name='tda-ver-deshabilitados'),
    path('', views.ver_habilitados, name='tda-ver-habilitados'),
]

