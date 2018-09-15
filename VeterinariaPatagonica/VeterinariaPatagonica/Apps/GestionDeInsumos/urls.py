from django.conf.urls import url
from . import views

app_name = "insumos"
urlpatterns = [
    url(r'$',views.insumos, name="insumo"),
    url(r'alta/$',views.alta, name="alta"),
]
