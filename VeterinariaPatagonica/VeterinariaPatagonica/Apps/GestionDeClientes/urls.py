from django.conf.urls import url
from . import views


app_name = "clientes"
urlpatterns = [
    url(r'$',views.clientes, name="cliente"),
    url(r'alta/$',views.alta, name="alta")
]
