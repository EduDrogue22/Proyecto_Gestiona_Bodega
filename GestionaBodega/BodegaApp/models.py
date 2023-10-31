from django.db import models

# Create your models here.

class AreaBodega(models.Model):
    id_area = models.AutoField(primary_key=True)
    sector = models.CharField(max_length=4)
    cant_anaq_area = models.IntegerField()
    disponible = models.CharField(max_length=1)
    id_bodega = models.ForeignKey('Bodega', models.DO_NOTHING, db_column='id_bodega')

    class Meta:
        db_table = 'area_bodega'


class Banco(models.Model):
    id_banco = models.AutoField(primary_key=True)
    nombre_banco = models.CharField(max_length=50)

    class Meta:
        db_table = 'banco'


class Bodega(models.Model):
    id_bodega = models.AutoField(primary_key=True)
    nombre_bodega = models.CharField(max_length=70)
    direccion = models.CharField(max_length=70)
    id_tp_bodega = models.ForeignKey('TipoBodega', models.DO_NOTHING, db_column='id_tp_bodega')

    class Meta:
        db_table = 'bodega'


class Cliente(models.Model):
    rut = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='rut', primary_key=True)
    direccion = models.CharField(max_length=100)
    fecha_nac = models.DateField()
    id_sucursal = models.ForeignKey('Sucursal', models.DO_NOTHING, db_column='id_sucursal')

    class Meta:
        db_table = 'cliente'


class Colaborador(models.Model):
    rut = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='rut', primary_key=True)
    id_tp_colab = models.ForeignKey('TipoColaborador', models.DO_NOTHING, db_column='id_tp_colab')

    class Meta:
        db_table = 'colaborador'


class Despacho(models.Model):
    id_despacho = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=1)
    tiempo_entrega = models.IntegerField()
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='id_producto')
    rut = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='rut')

    class Meta:
        db_table = 'despacho'


class DetallePlan(models.Model):
    id_bodega = models.OneToOneField(Bodega, models.DO_NOTHING, db_column='id_bodega', primary_key=True)  # The composite primary key (id_bodega, id_plan) found, that is not supported. The first column is selected.
    id_plan = models.ForeignKey('Plan', models.DO_NOTHING, db_column='id_plan')

    class Meta:
        db_table = 'detalle_plan'
        unique_together = (('id_bodega', 'id_plan'),)


class DetalleVenta(models.Model):
    total_venta = models.IntegerField()
    pago_id_pago = models.OneToOneField('Pago', models.DO_NOTHING, db_column='pago_id_pago', primary_key=True)  # The composite primary key (pago_id_pago, venta_id_venta) found, that is not supported. The first column is selected.
    venta_id_venta = models.ForeignKey('Venta', models.DO_NOTHING, db_column='venta_id_venta')

    class Meta:
        db_table = 'detalle_venta'
        unique_together = (('pago_id_pago', 'venta_id_venta'),)


class Empresa(models.Model):
    rut_empresa = models.IntegerField(primary_key=True)
    nombre_empresa = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)

    class Meta:
        db_table = 'empresa'


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    valor_pago = models.IntegerField()
    fecha_pago = models.DateField()
    descripcion_pago = models.CharField(max_length=60)
    id_banco = models.ForeignKey(Banco, models.DO_NOTHING, db_column='id_banco')
    id_tipo_pago = models.ForeignKey('TipoPago', models.DO_NOTHING, db_column='id_tipo_pago')

    class Meta:
        db_table = 'pago'


class Perfil(models.Model):
    id_perfil = models.AutoField(primary_key=True)
    edad = models.IntegerField()
    notificaciones = models.CharField(max_length=60)
    rut = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='rut')

    class Meta:
        db_table = 'perfil'


class Plan(models.Model):
    id_plan = models.AutoField(primary_key=True)
    valor_plan = models.IntegerField()
    cant_anaquel_plan = models.IntegerField()
    capacidad_anaquel = models.IntegerField()

    class Meta:
        db_table = 'plan'


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=50)
    stock = models.IntegerField()
    foto_prod = models.BinaryField()
    id_area = models.ForeignKey(AreaBodega, models.DO_NOTHING, db_column='id_area')
    rut = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='rut')

    class Meta:
        db_table = 'producto'


class Sucursal(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    nombre_sucursal = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    rut_empresa = models.ForeignKey(Empresa, models.DO_NOTHING, db_column='rut_empresa')

    class Meta:
        db_table = 'sucursal'


class TipoBodega(models.Model):
    id_tp_bodega = models.AutoField(primary_key=True)
    nom_tipo_bodega = models.CharField(max_length=50)

    class Meta:
        db_table = 'tipo_bodega'
       


class TipoColaborador(models.Model):
    id_tp_colab = models.AutoField(primary_key=True)
    nombre_colab = models.CharField(max_length=50)

    class Meta:
        db_table = 'tipo_colaborador'


class TipoPago(models.Model):
    id_tipo_pago = models.AutoField(primary_key=True)
    nombre_pago = models.CharField(max_length=50)

    class Meta:
        
        db_table = 'tipo_pago'


class TipoUsuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nom_tp_usuario = models.CharField(max_length=50)

    class Meta:
        
        db_table = 'tipo_usuario'


class Usuario(models.Model):
    rut = models.IntegerField(primary_key=True)
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    correo = models.CharField(max_length=100)
    contrasena = models.CharField(max_length=128)
    id_bodega = models.ForeignKey(Bodega, models.DO_NOTHING, db_column='id_bodega')
    id_usuario = models.ForeignKey(TipoUsuario, models.DO_NOTHING, db_column='id_usuario')

    class Meta:
        
        db_table = 'usuario'


class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    fecha_venta = models.DateField()
    valor_venta = models.IntegerField()
    id_plan = models.ForeignKey(Plan, models.DO_NOTHING, db_column='id_plan')
    rut = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='rut')

    class Meta:
        
        db_table = 'venta'