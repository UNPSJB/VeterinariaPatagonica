from django.urls import path
from . import views

app_name='tiposDeAtencion'

urlpatterns = [
    path('crear/', views.crear, name='crear'),
    path('ver/<int:id>/', views.ver, name='ver'),
    path('modificar/<int:id>/', views.modificar, name='modificar'),
    path('deshabilitar/<int:id>/', views.deshabilitar, name='deshabilitar'),
    path('habilitar/<int:id>/', views.habilitar, name='habilitar'),
    path('eliminar/<int:id>/', views.eliminar, name='eliminar'),
    path('habilitados/', views.habilitados, name='habilitados'),
    path('deshabilitados/', views.deshabilitados, name='deshabilitados'),
    #path('', views.habilitados, name='habilitados'),
]

