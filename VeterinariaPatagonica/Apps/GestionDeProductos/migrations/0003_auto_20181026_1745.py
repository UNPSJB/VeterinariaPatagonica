# Generated by Django 2.0.8 on 2018-10-26 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestionDeProductos', '0002_auto_20181025_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='precioDeCompra',
            field=models.DecimalField(decimal_places=2, help_text='Precio de Compra del Producto', max_digits=7),
        ),
    ]