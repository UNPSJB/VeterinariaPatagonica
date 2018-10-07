from django.conf.urls import url
from django.urls import path
from . import views as clientes_views
from VeterinariaPatagonica import views

app_name = 'clientes'

urlpatterns = [
    #url(r'^$', clientes_views.clientes, name="cliente"),
    path('crear/', clientes_views.crear, name="clienteCrear"),
    path('modificar/<int:dniCuit>/', clientes_views.modificar, name="clienteModificar"),
    path('habilitar/<int:dniCuit>/', clientes_views.habilitar, name="clienteHabilitar"),
    path('deshabilitar/<int:dniCuit>/', clientes_views.deshabilitar, name="clienteDeshabilitar"),
    path('eliminar/<int:dniCuit>/', clientes_views.eliminar, name="clienteEliminar"),
    path('ver/<int:dniCuit>/', clientes_views.ver, name="clienteVer"),
    path('verHabilitados/', clientes_views.verHabilitados, name="clienteVerHabilitados"),
    path('verDeshabilitados/', clientes_views.verDeshabilitados, name="clienteVerDeshabilitados"),
    path('', clientes_views.verHabilitados, name="clienteVerHabilitados"),
]

#nuevo
'''url(r'^$', clientes_views.clientes, name="cliente"),
url(r'crear/$', clientes_views.crear, name="clienteCrear"),
url(r'ver/$')'''


#viejo
''''# url(r'sitio_base.html$',clientes_views.base, name="base"),
url(r'^$', clientes_views.clientes, name='cliente'),
url(r'altacliente.html/$', clientes_views.alta, name='alta'),'''