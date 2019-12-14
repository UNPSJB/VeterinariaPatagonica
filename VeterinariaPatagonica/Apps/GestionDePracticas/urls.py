from django.urls import path, include
from .config import config
from . import viewsConsultas as consultas
from . import viewsCirugias as cirugias
from . import views

app_name = config("app_name")

urlpatterns = [

    path("consultas/", include(([
        path("", consultas.listar, name="listar"),
        path("crear/", include(([
            path("", consultas.crear, name="practica"),
            path("<int:idCreacion>/", consultas.modificar, name="modificarPractica"),
            path("productos/<int:idCreacion>/", consultas.modificarProductos, name="modificarProductos"),
            path("presupuestar/<int:idCreacion>/", consultas.crearPresupuestada, name="presupuestar"),
            path("realizar/<int:idCreacion>/", consultas.crearRealizada, name="realizar"),
            path("terminar/<int:idCreacion>/", consultas.terminarCreacion, name="terminar"),
        ], "crear"))),

        path("ver/", include(([
            path("<int:id>/", consultas.ver, name="practica"),
            path("informacionclinica/<int:id>/", consultas.verInformacionClinica, name="informacionClinica"),
        ], "ver"))),

        path("actualizaciones/", include(([
            path("realizar/<int:id>/", consultas.realizar, name="realizar"),
        ], "actualizaciones"))),

        path("modificar/", include(([
            path("realizacion/<int:id>/", consultas.modificarRealizacion, name="realizacion"),
            path("informacionclinica/<int:id>/", consultas.modificarInformacionClinica, name="informacionClinica"),
        ], "modificar"))),

        path("exportar/", include(([
            path("xlsx/", consultas.exportar, {"formato" : "xlsx"}, name="xlsx"),
        ], "exportar"))),

        path("reporte/", consultas.reporte, name="reporte"),
        path("ayudaConsulta/", consultas.ayudaContextualConsulta, name="ayudaConsulta"),

    ], "consulta"))),

    path("cirugias/", include(([
        path("", cirugias.listar, name="listar"),
        path("turnos/", cirugias.turnos, name="turnos"),
        path("crear/", include(([
            path("", cirugias.crear, name="practica"),
            path("<int:idCreacion>/", cirugias.modificar, name="modificarPractica"),
            path("productos/<int:idCreacion>/", cirugias.modificarProductos, name="modificarProductos"),
            path("presupuestar/<int:idCreacion>/", cirugias.crearPresupuestada, name="presupuestar"),
            path("programar/<int:idCreacion>/", cirugias.crearProgramada, name="programar"),
            path("realizar/<int:idCreacion>/", cirugias.crearRealizada, name="realizar"),
            path("terminar/<int:idCreacion>/", cirugias.terminarCreacion, name="terminar"),
        ], "crear"))),

        path("ver/", include(([
            path("<int:id>/", cirugias.ver, name="practica"),
            path("informacionclinica/<int:id>/", cirugias.verInformacionClinica, name="informacionClinica"),
        ], "ver"))),


        path("actualizaciones/", include(([
            path("realizar/<int:id>/", cirugias.realizar, name="realizar"),
            path("cancelar/<int:id>/", cirugias.cancelar, name="cancelar"),
            path("programar/<int:id>/", cirugias.programar, name="programar"),
            path("reprogramar/<int:id>/", cirugias.reprogramar, name="reprogramar"),
        ], "actualizaciones"))),

        path("modificar/", include(([
            path("realizacion/<int:id>/", cirugias.modificarRealizacion, name="realizacion"),
            path("informacionclinica/<int:id>/", cirugias.modificarInformacionClinica, name="informacionClinica"),
        ], "modificar"))),

        path("exportar/", include(([
            path("xlsx/", cirugias.exportar, {"formato" : "xlsx"}, name="xlsx"),
        ], "exportar"))),

        path("reporte/", cirugias.reporte, name="reporte"),
        path("ayudaCirugia/", cirugias.ayudaContextualCirugia, name="ayudaCirugia"),


    ], "cirugia"))),
    path("realizaciones/", views.realizaciones, name="realizaciones"),
]
