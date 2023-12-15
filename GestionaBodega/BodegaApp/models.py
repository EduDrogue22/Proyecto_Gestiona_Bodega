from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class AreaBodega(models.Model):
    id_area = models.AutoField(primary_key=True)
    sector = models.CharField(max_length=4)
    cant_anaq_area = models.IntegerField()
    disponible = models.CharField(max_length=1)
    id_bodega = models.ForeignKey('Bodega', on_delete=models.SET_NULL, null = True, blank = True, db_column='id_bodega')

    class Meta:
        db_table = 'area_bodega'

class Bodega(models.Model):
    id_bodega = models.AutoField(primary_key=True)
    nombre_bodega = models.CharField(max_length=70)
    direccion = models.CharField(max_length=70)
    id_tp_bodega = models.ForeignKey('TipoBodega', on_delete=models.SET_NULL, null = True, blank = True, db_column='id_tp_bodega')

    class Meta:
        db_table = 'bodega'


class Cliente(models.Model):
    rut = models.OneToOneField('Usuario', on_delete=models.CASCADE, db_column='rut', primary_key=True)
    direccion = models.CharField(max_length=100)
    fecha_nac = models.DateField()
    id_sucursal = models.ForeignKey('Sucursal', on_delete=models.SET_NULL, null = True, blank = True, db_column='id_sucursal')

    class Meta:
        db_table = 'cliente'


class Colaborador(models.Model):
    rut = models.OneToOneField('Usuario', on_delete=models.CASCADE, db_column='rut', primary_key=True)
    id_tp_colab = models.ForeignKey('TipoColaborador', on_delete=models.SET_NULL, null = True, blank = True, db_column='id_tp_colab')

    class Meta:
        db_table = 'colaborador'


class Despacho(models.Model):
    ESTADO_CHOICES = [
        ('E','Entregado'),
        ('S','En espera'),
        ('C','En camino'),
        ('R','Recibido'),
     ]
    id_despacho = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES)
    tiempo_entrega = models.IntegerField()
    cant_despachada = models.IntegerField()
    id_producto = models.ForeignKey('Producto', on_delete=models.SET_NULL, null = True, blank = True, db_column='id_producto')
    rut = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null = True, blank = True, db_column='rut')

    class Meta:
        db_table = 'despacho'

class Empresa(models.Model):
    rut_empresa = models.CharField(primary_key=True, max_length = 10)
    nombre_empresa = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)

    class Meta:
        db_table = 'empresa'


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    estado = models.CharField(max_length = 64)
    orden_compra = models.CharField(max_length = 26)
    descripcion_pago = models.CharField(max_length = 61)
    valor_pago = models.IntegerField()
    tipo_pago = models.CharField(max_length = 4)
    fecha_pago = models.DateTimeField()
    monto_cuotas = models.IntegerField(blank=True, null=True)
    cant_cuotas = models.IntegerField()
    rut = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null = True, blank = True, db_column='rut')
    id_plan = models.ForeignKey('Plan', on_delete=models.SET_NULL, null = True, blank = True, db_column='id_plan')

    class Meta:
        db_table = 'pago'


class Perfil(models.Model):
    id_perfil = models.AutoField(primary_key=True)
    edad = models.IntegerField()
    notificaciones = models.CharField(max_length=60, blank=True, null=True)
    rut = models.OneToOneField('Usuario', on_delete=models.SET_NULL, null = True, blank = True, db_column='rut')

    class Meta:
        db_table = 'perfil'


class Plan(models.Model):
    id_plan = models.AutoField(primary_key=True)
    nombre_plan = models.CharField(max_length=60)
    valor_plan = models.IntegerField()
    cant_anaquel_plan = models.IntegerField()
    capacidad_anaquel = models.IntegerField()

    class Meta:
        db_table = 'plan'

class DetallePlan(models.Model):
    id_det_plan = models.AutoField(primary_key=True)
    id_bodega = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null = True, blank = True, db_column='id_bodega')
    id_plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null = True, blank = True, db_column='id_plan')

    class Meta:
        db_table = 'detalle_plan'
        unique_together = (('id_bodega', 'id_plan'),)

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=50)
    stock = models.IntegerField()
    foto_prod = models.ImageField(upload_to='producto/', max_length=255)
    id_area = models.ForeignKey(AreaBodega, on_delete=models.SET_NULL, null = True, blank = True, db_column='id_area')
    rut = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null = True, blank = True, db_column='rut')

    class Meta:
        db_table = 'producto'


class Sucursal(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    nombre_sucursal = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    rut_empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null = True, blank = True, db_column='rut_empresa')

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

class TipoUsuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nom_tp_usuario = models.CharField(max_length=50)

    class Meta:
        
        db_table = 'tipo_usuario'

class CustomUserManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError('El correo electrónico es obligatorio')
        # Asignar un valor predeterminado a rut si no se proporciona
         # Reemplaza DEFAULT_RUT_VALUE con el valor que desees
        user = self.model(
            correo=self.normalize_email(correo),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, correo, password=None, rut=None, id_bodega=None, id_usuario=None, **extra_fields):
        # Lógica para crear un superusuario
        # Asignar un valor predeterminado a rut si no se proporciona
        rut = '1111111-1'   # Reemplaza DEFAULT_RUT_VALUE con el valor que desees
        id_bodega = Bodega.objects.get(pk=1)
        id_usuario = TipoUsuario.objects.get(pk=3)
        user = self.create_user(correo, password, rut=rut, id_bodega=id_bodega, id_usuario=id_usuario, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
  
class Usuario(AbstractBaseUser):
    rut = models.CharField(primary_key=True, max_length=10)
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    correo = models.CharField(max_length=100, unique=True)
    id_bodega = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null = True, blank = True, db_column='id_bodega')
    id_usuario = models.ForeignKey(TipoUsuario, on_delete=models.SET_NULL, null = True, blank = True, db_column='id_usuario')

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    class Meta:
        db_table = 'usuario'