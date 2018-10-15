from django.conf.urls import url
from django.urls import path
from . import views as insumos_views

app_name = 'insumos'

urlpatterns = [
    path('crear/', insumos_views.modificar, name='insumoCrear'),
    path('modificar/<int:id>/', insumos_views.modificar, name='insumoModificar'),
    path('habilitar/<int:id>/', insumos_views.habilitar, name='insumoHabilitar'),
    path('deshabilitar/<int:id>/', insumos_views.deshabilitar, name='insumoDeshabilitar'),
    path('eliminar/<int:id>/', insumos_views.eliminar, name='insumoEliminar'),
    path('ver/<int:id>/', insumos_views.ver, name='insumoVer'),
    path('', insumos_views.verHabilitados, name='insumoVerHabilitados'),
    path('verDeshabilitados/', insumos_views.verDeshabilitados, name='insumoVerDeshabilitados'),

]




'''
app_name = 'insumos'
urlpatterns = [
    url(r'^$',insumos_views.insumos, name='insumo'),
    url(r'altainsumo.html/$',insumos_views.crear, name='alta'),
    #url(r'altainsumo.html/$',views.verdemo, name='alta'),
]
'''
