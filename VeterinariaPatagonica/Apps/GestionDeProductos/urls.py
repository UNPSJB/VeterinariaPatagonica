from django.conf.urls import url
from django.urls import path
from . import views as productos_views

app_name = 'productos'

urlpatterns = [
    path('crear', productos_views.modificar, name='productoCrear'),
    path('modificar/<int:id>/', productos_views.modificar, name='productoModificar'),
    path('habilitar/<int:id>/', productos_views.habilitar, name='productoHabilitar'),
    path('deshabilitar/<int:id>/', productos_views.deshabilitar, name='productoDeshabilitar'),
    path('eliminar/<int:id>/', productos_views.eliminar, name='productoEliminar'),
    path('ver/<int:id>/', productos_views.ver, name='productoVer'),
    path('verHabilitados/', productos_views.verHabilitados, name='productoVerHabilitados'),
    path('verDeshabilitados/', productos_views.verDeshabilitados, name='productoVerDeshabilitados'),

]




'''
app_name = 'insumos'
urlpatterns = [
    url(r'^$',insumos_views.insumos, name='insumo'),
    url(r'altainsumo.html/$',insumos_views.crear, name='alta'),
    #url(r'altainsumo.html/$',views.verdemo, name='alta'),
]
'''
