from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible



"""
Validator de prueba, no es necesario en ningun lado.
Lo hice para jugar pero lo dejo por las dudas
"""
@deconstructible
class MayorValidator:

    cota = None
    message = 'Ingresar numero.'
    code = 'El numero no es valido.'

    def __init__(self, cota, message=None, code=None):

        self.cota = cota

        if message is not None:
            self.message = message

        if code is not None:
            self.code = code


    def __call__(self, value):

        if value <= self.cota:

            raise ValidationError(self.message, code=self.code)

    def __eq__(self, otra):

        return (
            ( self.cota == otra.cota ) and
            ( self.code == otra.code ) and
            ( self.message == otra.message )
        )

