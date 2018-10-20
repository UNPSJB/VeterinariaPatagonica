# Generated by Django 2.0.8 on 2018-10-19 20:39

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TipoDeAtencion',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(error_messages={'blank': 'El nombre es obligatorio', 'max_length': 'El nombre puede tener a lo sumo 100 caracteres', 'unique': 'Otro tipo de atencion tiene ese nombre'}, max_length=100, unique=True, validators=[django.core.validators.RegexValidator(regex='^[0-9a-zA-Z-_ .]{3,100}$')])),
                ('descripcion', models.TextField(blank=True)),
                ('emergencia', models.BooleanField(default=False)),
                ('lugar', models.CharField(choices=[('VET', 'Veterinaria'), ('DOM', 'Domicilio')], default='VET', error_messages={'blank': 'El lugar de atencion es obligatorio', 'invalid_choice': 'Opcion invalida'}, max_length=3)),
                ('recargo', models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0'), message='El recargo no puede ser menor a 0.00'), django.core.validators.MaxValueValidator(Decimal('900'), message='El recargo no puede ser mayor a 900.00'), django.core.validators.DecimalValidator(decimal_places=2, max_digits=5)])),
                ('tipoDeServicio', models.CharField(choices=[('C', 'Consulta'), ('Q', 'Quirurgica')], error_messages={'blank': 'El tipo de servicio es obligatorio', 'invalid_choice': 'Opcion invalida'}, max_length=25)),
                ('inicioFranjaHoraria', models.TimeField(error_messages={'blank': 'El inicio de horario de atencion es obligatorio', 'invalid': 'El formato debe ser HH:MM, por ejemplo "01:23"'})),
                ('finFranjaHoraria', models.TimeField(error_messages={'blank': 'El inicio de horario de atencion es obligatorio', 'invalid': 'El formato debe ser HH:MM, por ejemplo "01:23"'})),
                ('baja', models.BooleanField(default=False, editable=False)),
            ],
        ),
    ]
