# Generated by Django 4.2.6 on 2023-11-11 03:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AreaBodega',
            fields=[
                ('id_area', models.AutoField(primary_key=True, serialize=False)),
                ('sector', models.CharField(max_length=4)),
                ('cant_anaq_area', models.IntegerField()),
                ('disponible', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'area_bodega',
            },
        ),
        migrations.CreateModel(
            name='Bodega',
            fields=[
                ('id_bodega', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_bodega', models.CharField(max_length=70)),
                ('direccion', models.CharField(max_length=70)),
            ],
            options={
                'db_table': 'bodega',
            },
        ),
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('rut_empresa', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre_empresa', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'empresa',
            },
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id_pago', models.AutoField(primary_key=True, serialize=False)),
                ('valor_pago', models.IntegerField()),
                ('fecha_pago', models.DateField()),
                ('descripcion_pago', models.CharField(max_length=60)),
            ],
            options={
                'db_table': 'pago',
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id_plan', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_plan', models.CharField(max_length=60)),
                ('valor_plan', models.IntegerField()),
                ('cant_anaquel_plan', models.IntegerField()),
                ('capacidad_anaquel', models.IntegerField()),
            ],
            options={
                'db_table': 'plan',
            },
        ),
        migrations.CreateModel(
            name='TipoBodega',
            fields=[
                ('id_tp_bodega', models.AutoField(primary_key=True, serialize=False)),
                ('nom_tipo_bodega', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'tipo_bodega',
            },
        ),
        migrations.CreateModel(
            name='TipoColaborador',
            fields=[
                ('id_tp_colab', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_colab', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'tipo_colaborador',
            },
        ),
        migrations.CreateModel(
            name='TipoUsuario',
            fields=[
                ('id_usuario', models.AutoField(primary_key=True, serialize=False)),
                ('nom_tp_usuario', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'tipo_usuario',
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('rut', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('primer_nombre', models.CharField(max_length=50)),
                ('segundo_nombre', models.CharField(blank=True, max_length=50, null=True)),
                ('apellido_paterno', models.CharField(max_length=50)),
                ('apellido_materno', models.CharField(max_length=50)),
                ('correo', models.CharField(max_length=100, unique=True)),
                ('id_bodega', models.ForeignKey(blank=True, db_column='id_bodega', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.bodega')),
                ('id_usuario', models.ForeignKey(blank=True, db_column='id_usuario', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.tipousuario')),
            ],
            options={
                'db_table': 'usuario',
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('rut', models.OneToOneField(blank=True, db_column='rut', null=True, on_delete=django.db.models.deletion.SET_NULL, primary_key=True, serialize=False, to='BodegaApp.usuario')),
                ('direccion', models.CharField(max_length=100)),
                ('fecha_nac', models.DateField()),
            ],
            options={
                'db_table': 'cliente',
            },
        ),
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id_sucursal', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_sucursal', models.CharField(max_length=50)),
                ('direccion', models.CharField(max_length=100)),
                ('rut_empresa', models.ForeignKey(blank=True, db_column='rut_empresa', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.empresa')),
            ],
            options={
                'db_table': 'sucursal',
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id_producto', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_producto', models.CharField(max_length=50)),
                ('stock', models.IntegerField()),
                ('foto_prod', models.ImageField(max_length=255, upload_to='producto/')),
                ('id_area', models.ForeignKey(blank=True, db_column='id_area', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.areabodega')),
                ('rut', models.ForeignKey(blank=True, db_column='rut', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.cliente')),
            ],
            options={
                'db_table': 'producto',
            },
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id_perfil', models.AutoField(primary_key=True, serialize=False)),
                ('edad', models.IntegerField()),
                ('notificaciones', models.CharField(max_length=60)),
                ('rut', models.OneToOneField(blank=True, db_column='rut', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.usuario')),
            ],
            options={
                'db_table': 'perfil',
            },
        ),
        migrations.AddField(
            model_name='bodega',
            name='id_tp_bodega',
            field=models.ForeignKey(blank=True, db_column='id_tp_bodega', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.tipobodega'),
        ),
        migrations.AddField(
            model_name='areabodega',
            name='id_bodega',
            field=models.ForeignKey(blank=True, db_column='id_bodega', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.bodega'),
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id_venta', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_venta', models.DateField()),
                ('valor_venta', models.IntegerField()),
                ('id_plan', models.ForeignKey(blank=True, db_column='id_plan', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.plan')),
                ('rut', models.ForeignKey(blank=True, db_column='rut', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.cliente')),
            ],
            options={
                'db_table': 'venta',
            },
        ),
        migrations.CreateModel(
            name='DetallePlan',
            fields=[
                ('id_det_plan', models.AutoField(primary_key=True, serialize=False)),
                ('id_bodega', models.ForeignKey(blank=True, db_column='id_bodega', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.bodega')),
                ('id_plan', models.ForeignKey(blank=True, db_column='id_plan', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.plan')),
            ],
            options={
                'db_table': 'detalle_plan',
                'unique_together': {('id_bodega', 'id_plan')},
            },
        ),
        migrations.CreateModel(
            name='Despacho',
            fields=[
                ('id_despacho', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(choices=[('E', 'Entregado'), ('S', 'En espera'), ('C', 'En camino'), ('R', 'Recibido')], max_length=1)),
                ('tiempo_entrega', models.IntegerField()),
                ('id_producto', models.ForeignKey(blank=True, db_column='id_producto', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.producto')),
                ('rut', models.ForeignKey(blank=True, db_column='rut', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.cliente')),
            ],
            options={
                'db_table': 'despacho',
            },
        ),
        migrations.CreateModel(
            name='Colaborador',
            fields=[
                ('rut', models.OneToOneField(blank=True, db_column='rut', null=True, on_delete=django.db.models.deletion.SET_NULL, primary_key=True, serialize=False, to='BodegaApp.usuario')),
                ('id_tp_colab', models.ForeignKey(blank=True, db_column='id_tp_colab', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.tipocolaborador')),
            ],
            options={
                'db_table': 'colaborador',
            },
        ),
        migrations.AddField(
            model_name='cliente',
            name='id_sucursal',
            field=models.ForeignKey(blank=True, db_column='id_sucursal', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.sucursal'),
        ),
    ]
