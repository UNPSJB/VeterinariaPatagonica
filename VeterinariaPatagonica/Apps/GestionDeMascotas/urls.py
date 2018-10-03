from django.conf.urls import url
from . import views as mascotas_views
from VeterinariaPatagonica import views

app_name = 'mascotas'

urlpatterns = [
    url(r'^$', mascotas_views.mascota, name='mascota'),
    url(r'altamascota.html/$', mascotas_views.alta, name='alta'),
    # url(r'altamascota.html/$',views.verdemo, name='alta'),
]