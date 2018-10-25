from django.urls import path, include
from django.conf.urls import url
from django.contrib import admin
from . import views

app_name ='bases'
urlpatterns = [
    #path('accounts/', include('django.contrib.auth.urls')),
    url(r'^$', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('admin/', admin.site.urls),
    #url(r'^$',, name='base')
    #url(r'test/', include("Apps.GestionDeClientes.urls"))
    #url(r'.*/login.html', views.login),
    #url(r'^$',views.base),#Definimos la url del sitio base.
    path(r'GestionDeServicios/', include('Apps.GestionDeServicios.urls', namespace= 'servicios')),#Definimos que la url "GestionDeServicios" incluye todas las url que hay en GestionDeServicios.urls
    path(r'GestionDeClientes/', include('Apps.GestionDeClientes.urls', namespace= 'clientes')),#Definimos que la url "GestionDeClientes" incluye todas las url que hay en GestionDeClientes.urls
    path(r'GestionDeProductos/',include('Apps.GestionDeProductos.urls', namespace='productos')),#Definimos que la url "GestionDeProductos" incluye todas las url que hay en GestionDeProductos.urls
    path(r'GestionDeMascotas/', include('Apps.GestionDeMascotas.urls', namespace= 'mascotas')),#Definimos que la url "GestionDeMascotas" incluye todas las url que hay en GestionDeMascotas.url
    path(r'GestionDePracticas/', include('Apps.GestionDePracticas.urls', namespace='practicas')),
    path('gestion/tiposdeatencion/',include('Apps.GestionDeTiposDeAtencion.urls', namespace= 'tiposdeatencion')),
    path(r'GestionDeRubros/', include('Apps.GestionDeRubros.urls', namespace= 'rubros')),
]

"""
Idea para ordenar las urls de gestion de entidades que representen caracteristicas de la veterinaria (tipos de atencion, servicios, productos, ...)

	gestion/<ENTIDAD>/
	gestion/<ENTIDAD>/<ID>/
	gestion/<ENTIDAD>/crear/
	gestion/<ENTIDAD>/ver/<ID>/
	gestion/<ENTIDAD>/modificar/<ID>/
	gestion/<ENTIDAD>/deshabilitar/<ID>/
	gestion/<ENTIDAD>/habilitar/<ID>/
	gestion/<ENTIDAD>/eliminar/<ID>/
	gestion/<ENTIDAD>/habilitados/
	gestion/<ENTIDAD>/deshabilitados/

"""
