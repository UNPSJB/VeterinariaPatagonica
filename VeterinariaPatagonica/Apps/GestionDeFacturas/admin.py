from django.contrib import admin
from .models import DetalleFactura
from  .models import Factura
# Register your models here.

class DetalleFacturaInline(admin.TabularInline):
    model = DetalleFactura

class FacturaAdmin(admin.ModelAdmin):
    inlines = (DetalleFacturaInline,)

admin.site.register(Factura, FacturaAdmin)