
from django.urls import path
from . import views as practicas_views
from VeterinariaPatagonica import views

app_name = 'practicas'
urlpatterns = [
    path('', practicas_views.verHabilitadas, name='practicaVerHabilitadas'),
    #url(r'altaservicio.html$',views.verdemo, name="alta"),
    #url(r'altaservicio.html/$',servicios_views.alta, name='alta'),
]
