from django.urls import path, include
from .settings import APP_NAME
from . import views as practicas
from . import viewsConsultas as consultas
from . import viewsCirugias as cirugias

app_name = APP_NAME

urlpatterns = [

    path("consultas/", include(([
        path("", consultas.listar, name="listar"),
        path("<int:pagina>/", consultas.listar, name="listar"),
        path("ver/<int:id>/", consultas.ver, name="ver"),
        path("crear/", include(([
            path("", consultas.crear, name="nueva"),
            path("<int:idCreacion>/", consultas.modificar, name="modificar"),
            path("productos/<int:idCreacion>/", consultas.modificarProductos, name="modificarProductos"),
            path("presupuestar/<int:idCreacion>/", consultas.crearPresupuestada, name="presupuestar"),
            path("realizar/<int:idCreacion>/", consultas.crearRealizada, name="realizar"),
            path("terminar/<int:idCreacion>/", consultas.terminar, name="terminar"),
        ], "crear"))),
        path("realizacion/<int:id>/", consultas.detallarRealizacion, name="realizacion"),
        path("realizar/<int:id>/", consultas.realizar, name="realizar"),
        path("cancelar/<int:id>/", consultas.cancelar, name="cancelar"),
        path("facturar/<int:id>/", consultas.facturar, name="facturar"),
        path("completarPresupuesto/<int:id>/<int:accion>/", practicas.completarPresupuesto, name="completarPresupuesto"),
        path("detalles/<int:id>/", consultas.detalles, name="detalles"),
    ], "consulta"))),

    path("cirugias/", include(([
        path("", cirugias.listar, name="listar"),
        path("<int:pagina>/", cirugias.listar, name="listar"),
        path("ver/<int:id>/", cirugias.ver, name="ver"),
        path("crear/", include(([
            path("", cirugias.crear, name="nueva"),
            path("<int:idCreacion>/", cirugias.modificar, name="modificar"),
            path("productos/<int:idCreacion>/", cirugias.modificarProductos, name="modificarProductos"),
            path("presupuestar/<int:idCreacion>/", cirugias.crearPresupuestada, name="presupuestar"),
            path("programar/<int:idCreacion>/", cirugias.crearProgramada, name="programar"),
            path("realizar/<int:idCreacion>/", cirugias.crearRealizada, name="realizar"),
            path("terminar/<int:idCreacion>/", cirugias.terminar, name="terminar"),
        ], "crear"))),
        path("realizacion/<int:id>/", cirugias.detallarRealizacion, name="realizacion"),
        path("realizar/<int:id>/", cirugias.realizar, name="realizar"),
        path("cancelar/<int:id>/", cirugias.cancelar, name="cancelar"),
        path("facturar/<int:id>/", cirugias.facturar, name="facturar"),
        path("programar/<int:id>/", cirugias.programar, name="programar"),
        path("reprogramar/<int:id>/", cirugias.reprogramar, name="reprogramar"),
        path('completarPresupuesto/<int:id>/<int:accion>/', practicas.completarPresupuesto, name="completarPresupuesto"),
        path("detalles/<int:id>/", cirugias.detalles, name="detalles"),
        path('verAgenda/', cirugias.verAgendaCirugia, name="verAgendaCirugia"),
    ], "cirugia")))

]
