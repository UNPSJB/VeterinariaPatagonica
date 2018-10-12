from django.urls import path
from . import views as practicas_views
from VeterinariaPatagonica import views

app_name = 'practicas'
urlpatterns = [
    path('', practicas_views.verHabilitadas, name='practicaVerHabilitadas'),
    path('crear/', practicas_views.crear, name='practicaCrear'),
    path('ver/<int:id>/', practicas_views.ver, name='practicaVer'),


    #url(r'altaservicio.html$',views.verdemo, name="alta"),
    #url(r'altaservicio.html/$',servicios_views.alta, name='alta'),
]
