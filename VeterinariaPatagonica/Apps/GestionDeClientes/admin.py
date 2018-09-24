from django.contrib.auth.models import Permission
from django.contrib import admin
from Apps.GestionDeClientes.models import Cliente
# Register your models here.

admin.site.register(Permission)
admin.site.register(Cliente)
