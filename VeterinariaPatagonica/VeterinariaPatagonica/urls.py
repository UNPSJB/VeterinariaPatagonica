from django.urls import path, include
from django.conf.urls import url
from django.contrib import admin
from . import views, viewsAutocomplete

app_name ="bases"
urlpatterns = [
    path("", views.index, name='index'),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("admin/", admin.site.urls),
    path('password/',include ('Apps.Usuarios.urls',namespace='usuarios')),
    path('ayuda/', views.ayuda, name='ayuda'),
    path("GestionDeClientes/", include("Apps.GestionDeClientes.urls", namespace= "clientes")),
    path("GestionDeMascotas/", include("Apps.GestionDeMascotas.urls", namespace= "mascotas")),
    path("GestionDeProductos/",include("Apps.GestionDeProductos.urls", namespace="productos")),
    path("GestionDeRubros/", include("Apps.GestionDeRubros.urls", namespace= "rubros")),
    path("GestionDeServicios/", include("Apps.GestionDeServicios.urls", namespace= "servicios")),
    path("GestionDeTiposDeAtencion/",include("Apps.GestionDeTiposDeAtencion.urls", namespace= "tiposdeatencion")),
    path("GestionDePagos/",include("Apps.GestionDePagos.urls", namespace="pagos")),
    path("GestionDeFormasDePagos/", include("Apps.GestionDeFormasDePagos.urls", namespace="formasDePagos")),
    path("GestionDeFacturas/", include("Apps.GestionDeFacturas.urls", namespace="facturas")),
    path("GestionDePracticas/", include("Apps.GestionDePracticas.urls", namespace="practicas")),

    path("autocomplete/", include(([
        path("servicio/<str:area>/", viewsAutocomplete.ServicioAutocomplete.as_view(), name="servicio"),
        path("servicio/", viewsAutocomplete.ServicioAutocomplete.as_view(), name="servicio"),
        path("producto/<str:tipo>/", viewsAutocomplete.ProductoAutocomplete.as_view(), name="producto"),
        path("producto/", viewsAutocomplete.ProductoAutocomplete.as_view(), name="producto"),
        path("tipoDeAtencion/", viewsAutocomplete.TipoDeAtencionAutocomplete.as_view(), name="tipoDeAtencion"),
        path("cliente/", viewsAutocomplete.ClienteAutocomplete.as_view(), name="cliente"),
        path("mascota/<int:cliente>/", viewsAutocomplete.MascotaAutocomplete.as_view(), name="mascota"),
        path("mascota/", viewsAutocomplete.MascotaAutocomplete.as_view(), name="mascota"),
        path("practicaRealizada/", viewsAutocomplete.PracticaRealizadaAutocomplete.as_view(), name="practicaRealizada"),
    ], "autocomplete")))
]
