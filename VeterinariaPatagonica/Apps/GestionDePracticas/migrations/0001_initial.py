# Generated by Django 2.0.8 on 2018-11-27 19:33

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [

        ('GestionDeMascotas', '0001_initial'),
        ('GestionDeProductos', '0001_initial'),
        ('GestionDeClientes', '0001_initial'),
        ('GestionDeServicios', '0001_initial'),
        ('GestionDeTiposDeAtencion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adelanto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('importe', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=8, validators=[django.core.validators.MinValueValidator(0, 'El importe del adelanto no puede ser negativo')])),
            ],
        ),
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marca', models.DateTimeField(auto_now_add=True)),
                ('tipo', models.PositiveSmallIntegerField(choices=[(0, 'Estado'), (1, 'creada'), (3, 'presupuestada'), (2, 'programada'), (5, 'realizada'), (6, 'facturada'), (4, 'cancelada')])),
            ],
            options={
                'get_latest_by': 'marca',
            },
        ),
        migrations.CreateModel(
            name='Practica',
            fields=[
                ('tipo', models.CharField(choices=[('C', 'Consulta'), ('Q', 'Cirugia'), ('I', 'Internacion')], editable=False, max_length=1)),
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('precio', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=8, validators=[django.core.validators.MinValueValidator(0, 'El precio de la practica no puede ser negativo')])),
                ('turno', models.DateTimeField(blank=True, null=True)),
                ('adelanto', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='practica', to='GestionDePracticas.Adelanto')),
                ('cliente', models.ForeignKey(error_messages={'blank': 'El cliente es obligatorio', 'null': 'El cliente no puede ser null'}, on_delete=django.db.models.deletion.CASCADE, related_name='practicas', to='GestionDeClientes.Cliente')),
                ('mascota', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='practicas', to='GestionDeMascotas.Mascota')),
            ],
        ),
        migrations.CreateModel(
            name='PracticaProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'La cantidad debe ser mayor que cero')])),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0'), message='El precio no puede ser menor a 0.00')])),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='practica_productos', to='GestionDePracticas.Practica')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='producto_practicas', to='GestionDeProductos.Producto')),
            ],
        ),
        migrations.CreateModel(
            name='PracticaServicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'La cantidad debe ser mayor que cero')])),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0'), message='El precio no puede ser menor a 0.00')])),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='practica_servicios', to='GestionDePracticas.Practica')),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicio_practicas', to='GestionDeServicios.Servicio')),
            ],
        ),
        migrations.CreateModel(
            name='RealizadaProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'La cantidad debe ser mayor que cero')])),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0'), message='El precio no puede ser menor a 0.00')])),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='producto_realizadas', to='GestionDeProductos.Producto')),
            ],
        ),
        migrations.CreateModel(
            name='RealizadaServicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'La cantidad debe ser mayor que cero')])),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0'), message='El precio no puede ser menor a 0.00')])),
                ('observaciones', models.TextField(blank=True)),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicio_realizadas', to='GestionDeServicios.Servicio')),
            ],
        ),
        migrations.CreateModel(
            name='Cancelada',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='GestionDePracticas.Estado')),
                ('motivo', models.TextField(blank=True)),
            ],
            bases=('GestionDePracticas.estado',),
        ),
        migrations.CreateModel(
            name='Creada',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='GestionDePracticas.Estado')),
            ],
            options={
                'abstract': False,
            },
            bases=('GestionDePracticas.estado',),
        ),
        migrations.CreateModel(
            name='Facturada',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='GestionDePracticas.Estado')),
            ],
            bases=('GestionDePracticas.estado',),
        ),
        migrations.CreateModel(
            name='Presupuestada',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='GestionDePracticas.Estado')),
                ('diasMantenimiento', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Los dias de mantenimiento del presupuesto deben ser mas que cero')])),
            ],
            options={
                'abstract': False,
            },
            bases=('GestionDePracticas.estado',),
        ),
        migrations.CreateModel(
            name='Programada',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='GestionDePracticas.Estado')),
                ('inicio', models.DateTimeField()),
                ('finalizacion', models.DateTimeField()),
                ('motivoReprogramacion', models.CharField(blank=True, max_length=300, verbose_name='Motivo de reprogramacion')),
            ],
            options={
                'abstract': False,
            },
            bases=('GestionDePracticas.estado',),
        ),
        migrations.CreateModel(
            name='Realizada',
            fields=[
                ('estado_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='GestionDePracticas.Estado')),
                ('inicio', models.DateTimeField()),
                ('finalizacion', models.DateTimeField()),
                ('condicionPreviaMascota', models.TextField(blank=True)),
                ('resultados', models.TextField(blank=True)),
            ],
            bases=('GestionDePracticas.estado',),
        ),
        migrations.AddField(
            model_name='practica',
            name='productos',
            field=models.ManyToManyField(related_name='practicas', related_query_name='practica', through='GestionDePracticas.PracticaProducto', to='GestionDeProductos.Producto'),
        ),
        migrations.AddField(
            model_name='practica',
            name='servicios',
            field=models.ManyToManyField(related_name='practicas', related_query_name='practica', through='GestionDePracticas.PracticaServicio', to='GestionDeServicios.Servicio'),
        ),
        migrations.AddField(
            model_name='practica',
            name='tipoDeAtencion',
            field=models.ForeignKey(error_messages={'blank': 'El tipo de atencion es obligatorio', 'null': 'El tipo de atencion no puede ser null'}, on_delete=django.db.models.deletion.CASCADE, related_name='practicas', to='GestionDeTiposDeAtencion.TipoDeAtencion'),
        ),
        migrations.AddField(
            model_name='estado',
            name='practica',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estados', related_query_name='estado', to='GestionDePracticas.Practica'),
        ),
    ]
