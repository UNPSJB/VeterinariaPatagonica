from django.urls import path, include
from .config import config
from . import viewsConsultas as consultas
from . import viewsCirugias as cirugias

app_name = config("app_name")

urlpatterns = [

    path("consultas/", include(([
        path("", consultas.listar, name="listar"),
        path("buscar/", consultas.buscar, name="buscar"),
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
            path("observaciones/<int:id>/", consultas.verObservaciones, name="observaciones"),
        ], "ver"))),

        path("actualizaciones/", include(([
            path("realizar/<int:id>/", consultas.realizar, name="realizar"),
            path("cancelar/<int:id>/", consultas.cancelar, name="cancelar"),
        ], "actualizaciones"))),

        path("modificar/", include(([
            path("detalles/<int:id>/", consultas.modificarDetalles, name="detalles"),
            path("observaciones/<int:id>/", consultas.modificarObservaciones, name="observaciones"),
        ], "modificar"))),

    ], "consulta"))),

    path("cirugias/", include(([
        path("", cirugias.listar, name="listar"),
        path("buscar/", cirugias.buscar, name="buscar"),
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
            path("observaciones/<int:id>/", cirugias.verObservaciones, name="observaciones"),
        ], "ver"))),


        path("actualizaciones/", include(([
            path("realizar/<int:id>/", cirugias.realizar, name="realizar"),
            path("cancelar/<int:id>/", cirugias.cancelar, name="cancelar"),
            path("programar/<int:id>/", cirugias.programar, name="programar"),
            path("reprogramar/<int:id>/", cirugias.reprogramar, name="reprogramar"),
        ], "actualizaciones"))),

        path("modificar/", include(([
            path("detalles/<int:id>/", cirugias.modificarDetalles, name="detalles"),
            path("observaciones/<int:id>/", cirugias.modificarObservaciones, name="observaciones"),
        ], "modificar"))),


    ], "cirugia")))

]
