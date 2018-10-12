from django.conf.urls import url
from . import views as mascotas_views
#from VeterinariaPatagonica import views
from django.urls import path
from . import views
app_name = 'mascotas'

urlpatterns = [
    url(r'^$', mascotas_views.mascota, name='mascota'),
    #url(r'altamascota.html/$', mascotas_views.alta, name='alta'),
    # url(r'altamascota.html/$',views.verdemo, name='alta'),
    #path('ver/<int:id>/', mascotas_views.ver, name='mascotaVer'),

    path('crear/', mascotas_views.crear, name="mascotaCrear"),
    path('modificar/<int:id>/', mascotas_views.modificar, name="mascotaModificar"),

    path('deshabilitar/<int:id>/', mascotas_views.deshabilitar, name='mascotasDeshabilitar'),
    path('habilitar/<int:id>/', mascotas_views.habilitar, name='mascotasHabilitar'),
    path('eliminar/<int:id>/', mascotas_views.eliminar, name='mascotasEliminar'),
    path('ver/<int:id>/', mascotas_views.ver, name="mascotaVer"),
    path('verHabilitados/', mascotas_views.verHabilitados(), name='mascotasVerHabilitados'),
    path('verDeshabilitados/', mascotas_views.verDeshabilitados, name='mascotasVerDeshabilitados'),

    path('', mascotas_views.verHabilitados, name='mascotasVerHabilitados'),

''' 
    #url(r'^$', clientes_views.clientes, name="cliente"),
    path('crear/', clientes_views.crear, name="clienteCrear"),
    path('modificar/<int:id>/', clientes_views.modificar, name="clienteModificar"),
    path('habilitar/<int:id>/', clientes_views.habilitar, name="clienteHabilitar"),
    path('deshabilitar/<int:id>/', clientes_views.deshabilitar, name="clienteDeshabilitar"),
    path('eliminar/<int:id>/', clientes_views.eliminar, name="clienteEliminar"),
    path('ver/<int:id>/', clientes_views.ver, name="clienteVer"),
    path('verHabilitados/', clientes_views.verHabilitados, name="clienteVerHabilitados"),
    path('verDeshabilitados/', clientes_views.verDeshabilitados, name="clienteVerDeshabilitados"),
    path('', clientes_views.verHabilitados, name="clienteVerHabilitados"),
]
'''

]