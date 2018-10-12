# Generated by Django 2.0.8 on 2018-10-09 17:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestionDeMascotas', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mascota',
            name='fechaNacimiento',
        ),
        migrations.AlterField(
            model_name='mascota',
            name='especie',
            field=models.CharField(error_messages={'blank': 'La especie es obligatorio',
                                                   'max_length': 'La especie puede tener a lo sumo 50 caracteres'},
                                   help_text='Especie de la Mascota',
                                   max_length=50,
                                   validators=[django.core.validators.RegexValidator(regex='^[0-9a-zA-Z-_ .]{3,100}$')]),
        ),
        migrations.AlterField(
            model_name='mascota',
            name='nombre',
            field=models.CharField(error_messages={'blank': 'El nombre es obligatorio',
                                                   'max_length': 'El nombre puede tener a lo sumo 50 caracteres'},
                                   help_text='Nombre de la mascota',
                                   max_length=50,
                                   validators=[django.core.validators.RegexValidator(regex='^[0-9a-zA-Z-_ .]{3,100}$')]),
        ),
        migrations.AlterField(
            model_name='mascota',
            name='raza',
            field=models.CharField(error_messages={'blank': 'La especie es obligatorio',
                                                   'max_length': 'La especie puede tener a lo sumo 50 caracteres'},
                                   help_text='Especie de la Mascota',
                                   max_length=50,
                                   validators=[django.core.validators.RegexValidator(regex='^[0-9a-zA-Z-_ .]{3,100}$')]),
        ),
    ]