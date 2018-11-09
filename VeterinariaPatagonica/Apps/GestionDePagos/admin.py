from django.contrib.auth.models import Permission
from django.contrib import admin
from Apps.GestionDePagos.models import Pagos
# Register your models here.

admin.site.register(Permission)
admin.site.register(Pagos)