# Generated by Django 2.0.8 on 2018-10-19 15:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestionDeInsumos', '0002_auto_20181006_2320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insumo',
            name='baja',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='insumo',
            name='formaDePresentacion',
            field=models.PositiveSmallIntegerField(choices=[(1, 'g'), (2, 'cm3'), (3, 'unidad'), (4, 'kg'), (5, 'litro'), (6, 'docena')], error_messages={'blank': 'La unidad de medida es obligatoria', 'invalid_choice': 'Opcion invalida'}, help_text='Forma de Presentacion del Insumo'),
        ),
        migrations.AlterField(
            model_name='insumo',
            name='nombre',
            field=models.CharField(error_messages={'blank': 'El nombre es obligatorio', 'max_length': 'El nombre puede tener a lo sumo 50 caracteres', 'unique': 'Otro insumo tiene ese nombre'}, help_text='Nombre del Insumo', max_length=50, unique=True, validators=[django.core.validators.RegexValidator(regex='^[0-9a-zA-Z-_ .]{3,100}$')]),
        ),
        migrations.AlterField(
            model_name='insumo',
            name='precioPorUnidad',
            field=models.DecimalField(decimal_places=2, help_text='Precio del Insumo', max_digits=7),
        ),
    ]