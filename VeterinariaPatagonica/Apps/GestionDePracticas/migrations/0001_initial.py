# Generated by Django 2.1.3 on 2018-11-08 21:05

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('GestionDeTiposDeAtencion', '0001_initial'),
        ('GestionDeMascotas', '0001_initial'),
        ('GestionDeProductos', '0001_initial'),
        ('GestionDeClientes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('GestionDeServicios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marca', models.DateTimeField(auto_now=True)),
                ('tipo', models.PositiveSmallIntegerField(choices=[(0, 'Estado'), (1, 'creada'), (3, 'presupuestada'), (2, 'programada'), (5, 'realizada'), (6, 'facturada'), (4, 'cancelada')])),
            ],
            options={
                'get_latest_by': 'marca',
            },
        ),
        migrations.CreateModel(
            name='Practica',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('precio', models.DecimalField(blank=True, decimal_places=2, error_messages={'max_digits': 'Cantidad de digitos ingresados supera el máximo.'}, max_digits=8, null=True)),
                ('recargo', models.DecimalField(decimal_places=2, default=Decimal('0'), error_messages={}, max_digits=5)),
                ('descuento', models.DecimalField(decimal_places=2, default=Decimal('0'), error_messages={}, max_digits=5)),
                ('cliente', models.ForeignKey(error_messages={'blank': 'El cliente es obligatorio', 'null': 'El cliente no puede ser null'}, on_delete=django.db.models.deletion.CASCADE, related_name='practicas', to='GestionDeClientes.Cliente')),
                ('mascota', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='practicas', to='GestionDeMascotas.Mascota')),
            ],
        ),
        migrations.CreateModel(
            name='PracticaProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveSmallIntegerField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0'), message='El precio no puede ser menor a 0.00'), django.core.validators.DecimalValidator(decimal_places=2, max_digits=8)])),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='practica_productos', to='GestionDePracticas.Practica')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='producto_practicas', to='GestionDeProductos.Producto')),
            ],
        ),
        migrations.CreateModel(
            name='PracticaServicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveSmallIntegerField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0'), message='El precio no puede ser menor a 0.00'), django.core.validators.DecimalValidator(decimal_places=2, max_digits=8)])),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='practica_servicios', to='GestionDePracticas.Practica')),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicio_practicas', to='GestionDeServicios.Servicio')),
            ],
        ),
        migrations.CreateModel(
            name='RealizadaProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveSmallIntegerField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0'), message='El precio no puede ser menor a 0.00'), django.core.validators.DecimalValidator(decimal_places=2, max_digits=8)])),
                ('observaciones', models.TextField(blank=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='producto_realizadas', to='GestionDeProductos.Producto')),
            ],
        ),
        migrations.CreateModel(
            name='RealizadaServicio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveSmallIntegerField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0'), message='El precio no puede ser menor a 0.00'), django.core.validators.DecimalValidator(decimal_places=2, max_digits=8)])),
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
                ('diasMantenimiento', models.PositiveSmallIntegerField()),
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
                ('duracion', models.PositiveSmallIntegerField()),
                ('motivoReprogramacion', models.CharField(blank=True, default='', max_length=300, verbose_name='Motivo de reprogramacion')),
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
                ('duracion', models.PositiveSmallIntegerField()),
                ('condicionPreviaMascota', models.TextField(blank=True, default='')),
                ('resultados', models.TextField(blank=True, default='')),
            ],
            options={
                'abstract': False,
            },
            bases=('GestionDePracticas.estado',),
        ),
        migrations.AddField(
            model_name='practica',
            name='productos',
            field=models.ManyToManyField(related_name='practicas', through='GestionDePracticas.PracticaProducto', to='GestionDeProductos.Producto'),
        ),
        migrations.AddField(
            model_name='practica',
            name='servicios',
            field=models.ManyToManyField(related_name='practicas', through='GestionDePracticas.PracticaServicio', to='GestionDeServicios.Servicio'),
        ),
        migrations.AddField(
            model_name='practica',
            name='tipoDeAtencion',
            field=models.ForeignKey(error_messages={'blank': 'El tipo de atencion es obligatorio', 'null': 'El tipo de atencion no puede ser null'}, on_delete=django.db.models.deletion.CASCADE, related_name='practicas', to='GestionDeTiposDeAtencion.TipoDeAtencion'),
        ),
        migrations.AddField(
            model_name='estado',
            name='practica',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estados', to='GestionDePracticas.Practica'),
        ),
        migrations.AddField(
            model_name='estado',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='realizadaservicio',
            name='realizada',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='realizada_servicios', to='GestionDePracticas.Realizada'),
        ),
        migrations.AddField(
            model_name='realizadaproducto',
            name='realizada',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='realizada_productos', to='GestionDePracticas.Realizada'),
        ),
        migrations.AddField(
            model_name='realizada',
            name='productos',
            field=models.ManyToManyField(related_name='realizadas', through='GestionDePracticas.RealizadaProducto', to='GestionDeProductos.Producto'),
        ),
        migrations.AddField(
            model_name='realizada',
            name='servicios',
            field=models.ManyToManyField(related_name='realizadas', through='GestionDePracticas.RealizadaServicio', to='GestionDeServicios.Servicio'),
        ),
        migrations.AlterUniqueTogether(
            name='practicaservicio',
            unique_together={('practica', 'servicio')},
        ),
        migrations.AlterIndexTogether(
            name='practicaservicio',
            index_together={('practica', 'servicio')},
        ),
        migrations.AlterUniqueTogether(
            name='practicaproducto',
            unique_together={('practica', 'producto')},
        ),
        migrations.AlterIndexTogether(
            name='practicaproducto',
            index_together={('practica', 'producto')},
        ),
        migrations.AlterUniqueTogether(
            name='realizadaservicio',
            unique_together={('realizada', 'servicio')},
        ),
        migrations.AlterIndexTogether(
            name='realizadaservicio',
            index_together={('realizada', 'servicio')},
        ),
        migrations.AlterUniqueTogether(
            name='realizadaproducto',
            unique_together={('realizada', 'producto')},
        ),
        migrations.AlterIndexTogether(
            name='realizadaproducto',
            index_together={('realizada', 'producto')},
        ),
    ]
