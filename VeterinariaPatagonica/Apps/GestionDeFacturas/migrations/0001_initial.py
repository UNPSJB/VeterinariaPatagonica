# Generated by Django 2.0.8 on 2018-11-27 19:33

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('GestionDeClientes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetalleFactura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Factura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], default='B', error_messages={'blank': 'El tipo es obligatorio', 'max_length': 'El tipo de factura puede tener a lo sumo 1 caracteres'}, help_text='Tipo de Factura.', max_length=1, validators=[django.core.validators.RegexValidator(regex='^[A-B-C]{1}$')])),
                ('fecha', models.DateField(default=django.utils.timezone.now, error_messages={'blank': 'La fecha es obligatoria'}, help_text='Fecha de la Factura.')),
                ('total', models.IntegerField(default=0, error_messages={'blank': 'El importe es obligatorio'}, help_text='Importe total de la Factura.')),
                ('recargo', models.DecimalField(decimal_places=2, default=Decimal('0'), error_messages={}, max_digits=5)),
                ('descuento', models.DecimalField(decimal_places=2, default=Decimal('0'), error_messages={}, max_digits=5)),
                ('baja', models.BooleanField(default=False)),
                ('cliente', models.ForeignKey(error_messages={'blank': 'El cliente es obligatorio'}, on_delete=django.db.models.deletion.CASCADE, to='GestionDeClientes.Cliente')),
            ],
        ),
    ]
