from django.conf.urls import url
from django.urls import path, include
from . import views


app_name = 'facturas'


urlpatterns = [
    path('facturar/practica/<int:id>/', views.facturarPractica, name='facturarPractica'),
    path('facturar/', views.facturar, name='facturar'),
    path("listar/", views.listar, name="listar"),
    path("ver/<int:id>/", views.ver, name="ver"),
    path("exportar/", include(([
        path("xlsx/", views.exportar, {"formato" : "xlsx"}, name="xlsx"),
    ], "exportar"))),
    path('ayudaCostos/', views.ayudaContextualCosto, name="ayudaCostos"),
]
