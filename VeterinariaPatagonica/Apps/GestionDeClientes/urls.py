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
    path('verDeshabilitados/', clientes_views.verDeshabilitados, name="clienteVerDeshabilitados"),
    path('verHabilitados/', clientes_views.verHabilitados, name="clienteVerHabilitados"),
    path('listado_clientes_excel/', clientes_views.ListadoClientesExcel, name="clientesListadoEXCEL"),
    #url(r'^listado_clientes_pdf/(\S+)/$',clientes_views.ListadoClientesPDF, name="clientesListadoPDF" ),
    path('listado_clientes_pdf/', clientes_views.ListadoClientesPDF, name="clientesListadoPDF"),
    #path('', clientes_views.verHabilitados, name="clienteVerHabilitados"),
    path('documentacion/', clientes_views.documentation, name="clienteManual"),
    path('documentacionCliente/<int:tipo>', clientes_views.documentationCliente, name="clienteManual"),
]
