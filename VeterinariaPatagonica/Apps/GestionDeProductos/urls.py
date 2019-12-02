from django.conf.urls import url
from django.urls import path
from . import views as productos_views

app_name = 'productos'

urlpatterns = [
    url(r'^$', productos_views.producto, name='producto'),
    path('crear', productos_views.modificar, name='productoCrear'),
    path('modificar/<int:id>/', productos_views.modificar, name='productoModificar'),
    path('habilitar/<int:id>/', productos_views.habilitar, name='productoHabilitar'),
    path('deshabilitar/<int:id>/', productos_views.deshabilitar, name='productoDeshabilitar'),
    path('eliminar/<int:id>/', productos_views.eliminar, name='productoEliminar'),
    path('ver/<int:id>/', productos_views.ver, name='productoVer'),
    path('verHabilitados/', productos_views.verHabilitados, name='productoVerHabilitados'),
    path('verDeshabilitados/', productos_views.verDeshabilitados, name='productoVerDeshabilitados'),
    path('rubroAutocomplete/', productos_views.rubroAutocomplete.as_view(), name='productoRubroAutocomplete'),
    path('listado_productos_excel/', productos_views.ListadoProductosExcel, name="productosListadoEXCEL"),
    #path('documentacionProducto/<int:tipo>', productos_views.documentationProducto, name="productoManual"),
]

