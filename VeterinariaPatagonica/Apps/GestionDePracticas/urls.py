from django.urls import path, include
from . import views

app_name = 'practicas'

urlpatterns = [

    path("consultas/", include(([
        path('', views.listarConsultas, name="listar"),
        path('<int:id>/', views.verConsulta, name="ver"),
        path("crear/", include(([
            path('', views.crearConsulta, name="nueva"),
            path('productos/<int:idCreacion>/', views.crearProductos, name="productos"),
            path('presupuestada/<int:idCreacion>/', views.crearPresupuestada, name="presupuestada"),
            path('programada/<int:idCreacion>/', views.crearProgramada, name="programada"),
            path('realizada/<int:idCreacion>/', views.crearRealizada, name="realizada"),
        ], "crear"))),
        path('detalles/<int:id>/', views.detallesConsulta, name="detalles"),
        path('realizar/', views.realizarConsulta, name="realizar"),
        path('cancelar/', views.cancelarConsulta, name="cancelar"),
    ], "consulta"))),

    path("cirugias/", include(([
        path('', views.listarCirugias, name="listar"),
        path('<int:id>/', views.verCirugia, name="ver"),
        path("crear/", include(([
            path('', views.crearCirugia, name="nueva"),
            path('productos/<int:idCreacion>/', views.crearProductos, name="productos"),
            path('presupuestada/<int:idCreacion>/', views.crearPresupuestada, name="presupuestada"),
            path('programada/<int:idCreacion>/', views.crearProgramada, name="programada"),
            path('realizada/<int:idCreacion>/', views.crearRealizada, name="realizada"),
        ], "crear"))),
        path('detalles/<int:id>/', views.detallesCirugia, name="detalles"),
        path('realizar/', views.realizarCirugia, name="realizar"),
        path('cancelar/', views.cancelarCirugia, name="cancelar"),
        path('programar/', views.programarCirugia, name="programar"),
        path("verAgenda/", views.verAgendaCirugia, name="verAgendaCirugia")
    ], "cirugia")))

]

