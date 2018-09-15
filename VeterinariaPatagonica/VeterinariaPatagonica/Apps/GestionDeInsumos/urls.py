from django.conf.urls import url
from . import views as insumos_views
from VeterinariaPatagonica import views

app_name = "insumos"
urlpatterns = [
    url(r'$',insumos_views.insumos, name="insumo"),
    url(r'altainsumo.html/$',views.verdemo, name="alta"),
]
