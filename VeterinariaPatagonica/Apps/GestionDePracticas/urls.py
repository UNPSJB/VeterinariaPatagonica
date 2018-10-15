from django.urls import path
from . import views as practicas_views
from VeterinariaPatagonica import views

app_name = 'practicas'
urlpatterns = [
    path('verCirugias', practicas_views.verCirugiasHabilitadas, name='practicaVerCirugiasHabilitadas'),
    path('verConsultas', practicas_views.verConsultasHabilitadas, name='practicaVerConsultasHabilitadas'),
    path('crearCirugia/', practicas_views.crearCirugia, name='practicaCrearCirugia'),
    path('crearConsulta/', practicas_views.crearConsulta, name='practicaCrearConsulta'),
    path('ver/<int:id>/', practicas_views.ver, name='practicaVer'),

]
