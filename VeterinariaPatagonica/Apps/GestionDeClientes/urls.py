from django.conf.urls import url
from django.urls import path
from . import views as clientes_views
from VeterinariaPatagonica import views

app_name = 'clientes'

urlpatterns = [

    url(r'^$', clientes_views.clientes, name="cliente"),
    path('crear/', clientes_views.modificar, name="clienteCrear"),
    path('crear/<int:irAMascotas>', clientes_views.modificar, name="clienteCrear"),
    path('modificar/<int:id>/', clientes_views.modificar, name="clienteModificar"),
    path('habilitar/<int:id>/', clientes_views.habilitar, name="clienteHabilitar"),
    path('deshabilitar/<int:id>/', clientes_views.deshabilitar, name="clienteDeshabilitar"),
    path('eliminar/<int:id>/', clientes_views.eliminar, name="clienteEliminar"),
    path('ver/<int:id>/', clientes_views.ver, name="clienteVer"),
    path('verHabilitados/', clientes_views.verHabilitados, name="clienteVerHabilitados"),
    path('verDeshabilitados/', clientes_views.verDeshabilitados, name="clienteVerDeshabilitados"),
    #path('verHabilitados/<int:irA> ', clientes_views.verHabilitados, name="clienteVerHabilitados"),
    #path('verDeshabilitados/', clientes_views.verDeshabilitados, name="clienteVerDeshabilitados"),
    path('reporte_clientes_excel/', clientes_views.ReporteClientesExcel, name="clientesReporteEXCEL"),
    path('reporte_clientes_pdf/', clientes_views.ReporteClientesPDF, name="clientesReportePDF"),
    #path('', clientes_views.verHabilitados, name="clienteVerHabilitados"),
    path('documentacion/', clientes_views.documentation, name="clienteManual"),
    path('documentacionCliente/<int:tipo>', clientes_views.documentationCliente, name="clienteManual"),
]
