# Generated by Django 2.0.8 on 2019-12-05 23:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestionDeClientes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='dniCuit',
            field=models.CharField(error_messages={'blank': 'El dni/cuit es obligatorio', 'max_length': 'El dni/cuit puede tener a lo sumo 14 caracteres', 'unique': 'El dni/cuit ingresado ya existe'}, help_text='Dni/Cuit del Cliente', max_length=14, unique=True, validators=[django.core.validators.MinValueValidator(7, message='El dni/cuit debe tener mas de 7 caracteres')]),
        ),
    ]