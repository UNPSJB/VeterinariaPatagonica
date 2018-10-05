from django.conf.urls import url
#from . import views as insumos_views
#from VeterinariaPatagonica import views
from django.urls import path
from . import views as insumos_views

app_name = 'insumos'

urlpatterns = [
    url(r'^$', insumos_views.insumos, name='insumo'),
    path('', insumos_views.verHabilitados, name='insumoVerHabilitados'),
    path('verDeshabilitados/', insumos_views.verDeshabilitados, name='insumoVerDeshabilitados'),
    path('crear/', insumos_views.crear, name='insumoCrear'),
    path('ver/<int:id>/', insumos_views.ver, name='insumoVer'),
    path('modificar/<int:id>/', insumos_views.modificar, name='insumoModificar'),
    path('deshabilitar/<int:id>/', insumos_views.deshabilitar, name='insumoDeshabilitar'),
    path('habilitar/<int:id>/', insumos_views.habilitar, name='insumoHabilitar'),
    path('eliminar/<int:id>/', insumos_views.eliminar, name='insumoEliminar'),
    #path('verHabilitados/', views.verHabilitados, name='insumoVerHabilitados'),

]






'''
app_name = 'insumos'
urlpatterns = [
    url(r'^$',insumos_views.insumos, name='insumo'),
    url(r'altainsumo.html/$',insumos_views.crear, name='alta'),
    #url(r'altainsumo.html/$',views.verdemo, name='alta'),
]
'''