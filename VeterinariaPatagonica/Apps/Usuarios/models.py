from django.contrib.auth.models import AbstractUser

from Apps.GestionDePracticas.models.practica import Practica

class Usuario(AbstractUser):

    def grupo(self):
        return self.groups.last()

    def esVeterinario(self):
        return self.groups.filter(name="Veterinarios").count() > 0

    def esAdministrativo(self):
        return self.groups.filter(name="Administrativos").count() > 0

    def esGerente(self):
        return self.groups.filter(name="Gerentes").count() > 0
