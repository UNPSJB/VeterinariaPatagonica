from django.contrib import admin
from .models import detalleFactura
from  .models import factura
# Register your models here.

class detalleFacturaInline(admin.TabularInline):
    model = detalleFactura

class facturaAdmin(admin.ModelAdmin):
    inlines = (detalleFacturaInline,)

admin.site.register(factura, facturaAdmin)