"""VeterinariaPatagonica URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
#from django.contrib import admin
from django.conf.urls import url
#from django.conf.urls import url, include
from . import views
#from VeterinariaPatagonica.Apps.GestionDeClientes import views as clientes_views
#from VeterinariaPatagonica.Apps.GestionDeInsumos import views as insumos_views
#from VeterinariaPatagonica.Apps.GestionDeServicios import views as servicios_views

urlpatterns = [
    #path(r'admin/', admin.site.urls),
    #url(r'^$',, name='base')
    #url(r'test/', include("Apps.GestionDeClientes.urls"))

    url(r'^$',views.base),#Definimos la url del sitio base.
    #url(r'demos/.+\.html$', views.verdemo),
    #url(r'.+\html/',views.verdemo),
    #url(r'GestionDeServicios/$', servicios_views.servicios, name='servicios'),#Agregamos la direccion url a nuestro alcance.
    #url(r'GestionDeClientes/$', clientes_views.clientes, name= 'clientes'),
    path(r'GestionDeServicios/', include('VeterinariaPatagonica.Apps.GestionDeServicios.urls', namespace= 'servicios')),#Definimos que la url "GestionDeServicios" incluye todas las url que hay en GestionDeServicios.urls
    path(r'GestionDeClientes/', include('VeterinariaPatagonica.Apps.GestionDeClientes.urls', namespace= 'clientes')),#Definimos que la url "GestionDeClientes" incluye todas las url que hay en GestionDeClientes.urls
    #url(r'GestionDeInsumos/$',insumos_views.insumos , name='insumos'),
    path(r'GestionDeInsumos/',include('VeterinariaPatagonica.Apps.GestionDeInsumos.urls', namespace='insumos')),#Definimos que la url "GestionDeInsumos" incluye todas las url que hay en GestionDeInsumos.urls
]
