from django.conf.urls import url
from django.urls import path
from . import views


app_name = 'pagos'


urlpatterns = [
    path('crear/<int:id>/', views.crear, name="crear"),
    path('listar/', views.listar, name="listar"),
    path('ver/<int:id>/', views.ver, name="ver"),
]
