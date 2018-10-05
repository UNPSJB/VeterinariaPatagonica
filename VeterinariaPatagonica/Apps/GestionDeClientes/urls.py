from django.conf.urls import url
from django.urls import path
from . import views as clientes_views
from VeterinariaPatagonica import views

app_name = 'clientes'

urlpatterns = [
    url(r'^$', clientes_views.clientes, name="cliente"),
    path(r'^crear/$', clientes_views.crear, name="clienteCrear"),
    path(r'^modificar/<int:dniCuit>/$', clientes_views.modificar, name="clienteModificar"),
    path(r'^habilitar/<int:dniCuit>/$', clientes_views.hablitar, name="clienteHabilitar"),
    path(r'^deshabilitar/<int:dniCuit>/$', clientes_views.deshablitar, name="clienteDeshabilitar"),
    path(r'^eliminar/<int:dniCuit>/$', clientes_views.eliminar, name="clienteEliminar"),
    path(r'^ver/<int:dniCuit>/$', clientes_views.ver, name="clienteVer"),
    path(r'^verHabilitados/$', clientes_views.verHabilitados, name="clienteVerHabilitados"),
    path(r'^verDeshabilitados/$', clientes_views.verDeshabilitados, name="clienteVerDeshabilitados"),
    path(r'^nada/$', clientes_views.verHabilitados, name="clienteVerHabilitados"),
]





#nuevo
'''url(r'^$', clientes_views.clientes, name="cliente"),
url(r'crear/$', clientes_views.crear, name="clienteCrear"),
url(r'ver/$')'''


#viejo
''''# url(r'sitio_base.html$',clientes_views.base, name="base"),
url(r'^$', clientes_views.clientes, name='cliente'),
url(r'altacliente.html/$', clientes_views.alta, name='alta'),'''