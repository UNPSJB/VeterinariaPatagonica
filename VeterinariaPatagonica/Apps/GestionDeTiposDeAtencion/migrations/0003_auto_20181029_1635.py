# Generated by Django 2.0.8 on 2018-10-29 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestionDeTiposDeAtencion', '0002_auto_20181028_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipodeatencion',
            name='lugar',
            field=models.CharField(choices=[('DOM', 'Domicilio'), ('VET', 'Veterinaria')], default='VET', error_messages={'blank': 'El lugar de atencion es obligatorio', 'invalid_choice': 'Opcion invalida'}, max_length=3),
        ),
    ]
