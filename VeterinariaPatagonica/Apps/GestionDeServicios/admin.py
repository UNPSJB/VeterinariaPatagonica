from django.contrib import admin
from .models import Servicio
from .models import ServicioProducto

class ServicioProductoInline(admin.TabularInline):
    model = ServicioProducto

class ServicioAdmin(admin.ModelAdmin):
    inlines = [
        ServicioProductoInline,
    ]

admin.site.register(Servicio, ServicioAdmin)
