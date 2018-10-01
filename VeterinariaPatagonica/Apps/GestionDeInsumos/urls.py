#from django.conf.urls import url
#from . import views as insumos_views
#from VeterinariaPatagonica import views
from django.urls import path
from . import views
'''
app_name = 'insumos'
urlpatterns = [
    url(r'^$',insumos_views.insumos, name='insumo'),
    url(r'altainsumo.html/$',insumos_views.crear, name='alta'),
    #url(r'altainsumo.html/$',views.verdemo, name='alta'),
]
'''
app_name = 'insumos'

urlpatterns = [
path('', views.verHabilitados, name='insumoVerHabilitados'),
path('crear/', views.crear, name='insumoCrear'),
path('ver/<int:nombre>/', views.ver, name='insumoVer'),
path('modificar/<int:nombre>/', views.modificar, name='insumoModificar'),
path('deshabilitar/<int:nombre>/', views.deshabilitar, name='insumoDeshabilitar'),
path('habilitar/<int:nombre>/', views.habilitar, name='insumoHabilitar'),
path('eliminar/<int:nombre>/', views.eliminar, name='insumoEliminar'),
#path('verHabilitados/', views.verHabilitados, name='insumoVerHabilitados'),
path('verDeshabilitados/', views.verDeshabilitados, name='insumoVerDeshabilitados'),

]
