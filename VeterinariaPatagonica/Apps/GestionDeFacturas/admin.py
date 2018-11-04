from django.contrib import admin
from .models import Factura
from .models import DetalleFactura

# Register your models here.

class DetalleFacturaInline(admin.TabularInline):
    model = DetalleFactura

class FacturaAdmin(admin.ModelAdmin):
    inlines = (DetalleFacturaInline,)

admin.site.register(Factura, FacturaAdmin)