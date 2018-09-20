from django.conf.urls import url
from . import views as servicios_views
from VeterinariaPatagonica import views

app_name = 'servicios'
urlpatterns = [
    url(r'^$',servicios_views.servicios, name="servicio"),
    #url(r'altaservicio.html$',views.verdemo, name="alta"),
    url(r'altaservicio.html/$',servicios_views.alta, name='alta'),
]
