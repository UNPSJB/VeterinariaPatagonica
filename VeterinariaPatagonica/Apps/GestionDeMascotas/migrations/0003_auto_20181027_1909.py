# Generated by Django 2.0.8 on 2018-10-27 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestionDeMascotas', '0002_auto_20181026_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mascota',
            name='fechaNacimiento',
            field=models.DateField(error_messages={'required': 'el cliente es obligatorio'}),
        ),
    ]