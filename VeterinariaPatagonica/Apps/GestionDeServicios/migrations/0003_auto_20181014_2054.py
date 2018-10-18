# Generated by Django 2.0.8 on 2018-10-14 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestionDeServicios', '0002_auto_20181012_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='baja',
            field=models.BooleanField(default=False, help_text='Deshabilitado'),
        ),
        migrations.AlterField(
            model_name='servicio',
            name='precioManoDeObra',
            field=models.DecimalField(decimal_places=2, error_messages={'blank': 'El precio del servicio es obligarotio'}, max_digits=7),
        ),
    ]
