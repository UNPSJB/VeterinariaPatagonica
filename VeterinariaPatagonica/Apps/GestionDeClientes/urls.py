from django.conf.urls import url
from . import views as clientes_views
from VeterinariaPatagonica import views

app_name = 'clientes'

urlpatterns = [
    #url(r'sitio_base.html$',clientes_views.base, name="base"),
    url(r'^$', clientes_views.clientes, name='cliente'),
    url(r'altacliente.html/$',clientes_views.alta, name='alta'),

]





#nuevo
'''url(r'^$', clientes_views.clientes, name="cliente"),
url(r'crear/$', clientes_views.crear, name="clienteCrear"),
url(r'ver/$')'''
