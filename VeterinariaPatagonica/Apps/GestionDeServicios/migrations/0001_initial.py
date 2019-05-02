# Generated by Django 2.1.dev20180423170307 on 2019-04-30 19:30

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('GestionDeProductos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('C', 'Consulta'), ('Q', 'Quirurgica'), ('I', 'Internación')], default='Q', error_messages={'blank': 'El tipo de servicio es obligarotio'}, help_text='Tipo de Servicio (Consulta-Cirugia)', max_length=1)),
                ('nombre', models.CharField(error_messages={'blank': 'El nombre de servicio es obligarotio', 'max_length': 'El nombre puede tener a lo sumo 50 caracteres'}, help_text='Ingrese el nombre del Servicio', max_length=50, unique=True)),
                ('descripcion', models.CharField(blank=True, error_messages={'max_length': 'La descripcion puede tener a lo sumo 200 caracteres'}, help_text='Ingrese la descripcion del Servicio', max_length=200, null=True)),
                ('tiempoEstimado', models.PositiveSmallIntegerField(error_messages={'blank': 'El tiempo estimado del servicio es obligarotio'}, help_text='Tiempo en minutos de Duración del Servicio')),
                ('precioManoDeObra', models.DecimalField(decimal_places=2, error_messages={'blank': 'El precio del servicio es obligarotio'}, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0'), message='El precio no puede ser menor a $0.00'), django.core.validators.MaxValueValidator(Decimal('100000'), message='El precio no puede ser mayor a $100000.00')])),
                ('baja', models.BooleanField(default=False, help_text='Deshabilitado')),
            ],
            options={
                'ordering': ['tipo', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='ServicioProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='producto_servicios', to='GestionDeProductos.Producto')),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicio_productos', to='GestionDeServicios.Servicio')),
            ],
        ),
        migrations.AddField(
            model_name='servicio',
            name='productos',
            field=models.ManyToManyField(through='GestionDeServicios.ServicioProducto', to='GestionDeProductos.Producto'),
        ),
        migrations.AlterUniqueTogether(
            name='servicioproducto',
            unique_together={('servicio', 'producto')},
        ),
        migrations.AlterIndexTogether(
            name='servicioproducto',
            index_together={('servicio', 'producto')},
        ),
    ]
