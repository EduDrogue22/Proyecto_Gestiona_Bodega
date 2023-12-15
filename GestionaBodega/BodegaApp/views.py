from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from datetime import datetime, date
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db import DatabaseError
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from transbank.common.integration_type import IntegrationType
from transbank.webpay.webpay_plus.transaction import *
from transbank.error.transaction_commit_error import TransactionCommitError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db import DatabaseError
from django.db import transaction
from django.shortcuts import get_object_or_404
from .forms import *
from .models import *
import random
import re
from xhtml2pdf import pisa
from django.http import FileResponse
from django.template.loader import get_template
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import user_passes_test

# Importacion libreria oracle
import cx_Oracle

# Create your views here.
def create_oracle_connection():
    dsn_str = cx_Oracle.makedsn(host="localhost", port="1521", sid="orcl")
    connection = cx_Oracle.connect(user="bodegon", password="bodegon", dsn = dsn_str)
    return connection

def login_view(request):
    message = ""
    exitoLogin = False
    error = False
    id_usuario = 0
    template = ''


    if request.method == 'POST':
        correo = request.POST.get('correo', '')
        password = request.POST.get('password', '')

        user = authenticate(request, username=correo, password=password)

        if user is not None:
            # Si 'authenticate' devuelve un usuario válido, puedes iniciar sesión
            login(request, user)
            id_usuario = user.id_usuario_id
            rut = user.rut
            usuario = Usuario.objects.filter(rut=rut).first()
            usu_colab = Colaborador.objects.filter(rut=rut).first()

            if id_usuario == 1:
                exitoLogin = True
                message = f"Bienvenido {usuario.primer_nombre} {usuario.apellido_paterno}"

            elif id_usuario == 2:
                if  usu_colab.id_tp_colab_id == 1:
                    exitoLogin = True
                    message = f"Bienvenido Jefe Bodega {usuario.primer_nombre} {usuario.apellido_paterno}"
                elif usu_colab.id_tp_colab_id == 2:
                    exitoLogin = True
                    message = f"Bienvenido Bodeguero {usuario.primer_nombre} {usuario.apellido_paterno}"
                elif usu_colab.id_tp_colab == 3:
                    exitoLogin = True
                    message = f"Bienvenido Repartidor {usuario.primer_nombre} {usuario.apellido_paterno}"
                    template = 'repartidor/baseRepar.html'
                else:
                    exitoLogin = True
                    message = f"Bienvenido Repartidor {usuario.primer_nombre} {usuario.apellido_paterno}"
            else:
                exitoLogin = True
                message = "Bienvenido Administrador"
        else:
            error = True
            message = "Error en usuario o contraseña"

    context = {'exitoLogin': exitoLogin, 'error': error, 'message': message, 'id_usuario': id_usuario, 'template': template}
    return render(request, 'web/login.html', context)

@login_required(login_url='/')
def inicio(request):
    return render(request, 'web/home.html')

#Prueba integración
@login_required(login_url='/')
def realizar_transaccion(request):
    # Definir los datos de la transacción (reemplaza estos valores con los tuyos)
    if request.method == 'POST':
        id_plan = request.POST.get('id_plan')
        rut = request.POST.get('rut')
        id_bodega = request.POST.get('id_bodega')
        buy_order = str(random.randint(1, 9999999))
        session_id = request.POST.get('nombre_plan')
        amount = request.POST.get('valor_plan')  # Reemplaza con el monto correcto
        return_url = 'http://127.0.0.1:8000/webpaycommit/'

        tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))

        resp = tx.create(buy_order, session_id, amount, return_url)

        url = resp["url"]
        token = resp["token"]

        request.session['webpay_token'] = token
        request.session['id_plan'] = id_plan
        request.session['id_bodega'] = id_bodega

        print(resp)

        return render(request, 'webpay/crear_transaccion.html', {'buy_order': buy_order, 'session_id': session_id, 'amount': amount, 'url': url, 'token': token, 'rut': rut, 'id_plan': id_plan})

@login_required(login_url='/')
def webpay_commit(request):
    # Obtiene el token de la respuesta de Transbank (debe extraerse de la respuesta de Transbank)
    try:
        rut_cliente = request.user.rut
        token = request.session.get('webpay_token')
        id_plan = request.session.get('id_plan')
        id_bodega = request.session.get('id_bodega')
        id_bodega_int = int(id_bodega)
        cliente = get_object_or_404(Cliente, rut = rut_cliente)
        plan_instance = get_object_or_404(Plan, pk = id_plan)
        bodega_instance = get_object_or_404(Bodega, pk = id_bodega_int)
        usuario = Usuario.objects.get(rut = request.user.rut)
        tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))
        resp = tx.commit(token)

        status = resp['status']
        amount = resp['amount']
        buy_order = resp['buy_order']
        session_id = resp['session_id']
        transa_date = resp['transaction_date']
        tipo_pago = resp['payment_type_code']
        insta_amount = resp.get('installments_amount', None)
        insta_number = resp['installments_number']
        
        print(resp)
        print(type(id_bodega))

        try:
            if status == 'AUTHORIZED':
                pago = Pago(valor_pago = amount, fecha_pago = transa_date, descripcion_pago = session_id, cant_cuotas = insta_number,
                            estado = status, id_plan = plan_instance, monto_cuotas = insta_amount, orden_compra = buy_order, rut = cliente, tipo_pago = tipo_pago)
                usuario.id_bodega = bodega_instance
                pago.save()
                usuario.save()
                message = "¡Felicidades!, Transbank a aceptado su transacción."
            else:
                message = "Lo sentimos, Transbank a rechazado su transacción."
        except IntegrityError as e:
            message = "Ha ocurrido un error."

        return render(request, 'webpay/commit.html', {'token': token, 'resp': resp, 'message': message})
    
    except TransactionCommitError as e:

        if "Transaction has an invalid finished state: aborted" in str(e):
            return render(request, 'webpay/anulacion.html')
        
    return render(request, 'webpay/commit.html', {'token': token, 'resp': resp})

@login_required(login_url='/')
def webpay_refund(request):

    return render(request, 'webpay/anulacion.html')

@login_required(login_url='/')
def logout_view(request):
    logout(request)
    return redirect('/')

def validar_rut(rut):
    # Formato de RUT: 12345678-9
    patron = re.compile(r'^(\d{7,8})-([\dkK])$')

    if not patron.match(rut):
        return False

    # Separar el número y el dígito verificador
    rut_numero, rut_verificador = rut.split('-')

    # Verificar que el dígito sea un número o la letra 'k' (mayúscula o minúscula)
    return rut_verificador.isdigit() or rut_verificador.lower() == 'k'

def registrarse(request):
    empresa = Empresa.objects.all()
    sucursal = Sucursal.objects.all()
    error = False
    exito = False
    message = ""

    try:
        if request.method == 'POST':
            primer_nombre = request.POST.get('txtPrimerNombre').strip()
            segundo_nombre = request.POST.get('txtSegundoNombre')
            apellido_paterno = request.POST.get('txtApellidoPaterno').strip()
            apellido_materno = request.POST.get('txtApellidoMaterno').strip()
            rut = request.POST.get('txtRut').strip()
            correo = request.POST.get('txtCorreo').strip().lower()
            contrasena = request.POST.get('txtContrasena').strip()
            nacimiento = datetime.strptime(request.POST.get('dateFechaNacimiento'), '%Y-%m-%d').date()
            id_sucursal = request.POST.get('sucursal')
            rept_contrasena = request.POST.get('txtReptContrasena').strip()
            direccion = request.POST.get('txtDireccion').strip()
            id_bodega = 1
            id_usuario = 1
            
            hoy = date.today()

            edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))

            if contrasena != rept_contrasena:
                error = True
                message = "La contraseñas no coinciden."
            
            elif not validar_rut(rut):
                error = True
                message = "El RUT no es válido."
                print(validar_rut(rut))
            
            elif edad < 18:
                error = True
                message = "Debe tener al menos 18 años para registrarse."
            
            elif not primer_nombre:
                error = True
                message = "El campo Primer Nombre no puede estar en blanco."

            elif not apellido_paterno:
                error = True
                message = "El campo Apellido Paterno no puede estar en blanco."
            
            elif not apellido_materno:
                error = True
                message = "El campo Apellido Materno no puede estar en blanco."

            elif not correo:
                error = True
                message = "El campo Correo no puede estar en blanco."
            
            elif not contrasena:
                error = True
                message = "El campo Contraseña no puede estar en blanco."
            
            elif not rept_contrasena:
                error = True
                message = "El campo Repetir Contraseña no puede estar en blanco."

            elif not direccion:
                error = True
                message = "El campo Direccion no puede estar en blanco."

            else:
                usuario = Usuario()
                usuario.set_password(contrasena)
         
                oracle_connection = create_oracle_connection()
                with oracle_connection.cursor() as cursor:
                    cursor.callproc("sp_agregar_usuario_cliente", (usuario.password, rut, primer_nombre, segundo_nombre, apellido_paterno, apellido_materno, correo, direccion, nacimiento, int(edad), id_sucursal, id_bodega, id_usuario))
                oracle_connection.commit()
                exito = True
                message = "Usuario registrado con éxito, favor de esperar para comprobar sus datos."
                
    except DatabaseError as e:
        error = True
        message = "Error al agregar usuario."
    return render(request, 'web/registrarse.html', {'empresas': empresa, 'sucursales': sucursal, 'error': error, 'exito': exito, 'message': message})

# Verificar en las páginas del admin sea el administrador que entre
def admin_required(view_func):
    """
    Decorador que requiere que el usuario sea un administrador.
    """
    actual_decorator = user_passes_test(
        lambda u: u.rut == '1111111-1',
        login_url='login'
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

@login_required(login_url='/')
@admin_required
def menuAdm(request):
    return render(request,'Admin/menuAdmin.html')

@login_required(login_url='/')
@admin_required
def admPerfiles(request):
    perfiles = TipoColaborador.objects.all()
    contexto = {"perfiles": perfiles}
    return render(request,'Admin/Menu/adminPerfile.html', contexto)

@login_required(login_url='/')
@admin_required
def admArea(request):
    areas = AreaBodega.objects.all()
    contexto = {"areas": areas}
    return render(request,'Admin/Menu/adminArea.html', contexto)

@login_required(login_url='/')
@admin_required
def admBodega(request):
    bodegas = Bodega.objects.all()
    contexto = {"bodegas": bodegas}
    return render(request,'Admin/Menu/adminBodega.html', contexto)

@login_required(login_url='/')
@admin_required
def admCliente(request):
    regis = Usuario.objects.filter(id_usuario=1) 
    empl = Colaborador.objects.all()
    bodega = Bodega.objects.all()
    sucursal = Sucursal.objects.all
    contexto =  {'user': regis, 'empl': empl, 'bodega': bodega, 'sucursal': sucursal}
    return render(request,'Admin/Menu/adminCliente.html', contexto)

@login_required(login_url='/')
@admin_required
def admColaborador(request):
    regis = Usuario.objects.filter(id_usuario=2) 
    empl = Colaborador.objects.all()
    bodega = Bodega.objects.all()
    tpColab = TipoColaborador.objects.all()
    contexto = {'user': regis, 'empl': empl, 'bodega': bodega, 'tpColab': tpColab}
    return render(request,'Admin/Menu/adminColaborador.html', contexto)

@login_required(login_url='/')
@admin_required
def admEmpresa(request):
    empresas = Empresa.objects.all()
    contexto = {"empresas": empresas}
    return render(request,'Admin/Menu/adminEmpresa.html', contexto)

@login_required(login_url='/')
@admin_required
def admPlan(request):
    planes = Plan.objects.all()
    contexto = {"planes": planes}
    return render(request,'Admin/Menu/adminPlan.html', contexto)

@login_required(login_url='/')
@admin_required
def admProducto(request):
    productos = Producto.objects.all()
    contexto = {'productos': productos}
    return render(request,'Admin/Menu/adminProducto.html', contexto)

@login_required(login_url='/')
@admin_required
def admSucursal(request):
    sucursales = Sucursal.objects.all()
    contexto = {"sucursales": sucursales}
    return render(request,'Admin/Menu/adminSucursal.html', contexto)

@login_required(login_url='/')
def plan(request):
    planes = DetallePlan.objects.select_related('id_plan','id_bodega').all()
    usuario = request.user
    rut = usuario.rut

    plan_contratado = Pago.objects.filter(rut=rut).values_list('id_plan', flat=True).order_by('-fecha_pago').first() #flat=True
    detalle_planes_contratados = DetallePlan.objects.filter(id_plan=plan_contratado, id_bodega=usuario.id_bodega).values_list('id_plan', flat=True)
    detalle_planes_contratados_bodega = DetallePlan.objects.filter(id_plan=plan_contratado, id_bodega=usuario.id_bodega).values_list('id_bodega', flat=True)

    #plan.id_plan.id_plan in detalle_planes_contratados and plan.id_bodega.id_bodega in detalle_planes_contratados_bodega

    #'detalle_planes_contratados': detalle_planes_contratados, 'detalle_planes_contratados_bodega': detalle_planes_contratados_bodega

    context = {'planes':planes, 'detalle_planes_contratados': detalle_planes_contratados, 'detalle_planes_contratados_bodega': detalle_planes_contratados_bodega}
    return render(request,'web/plan.html',context)

@login_required(login_url='/')
def despacho(request,):
    user = request.user
    rut = user.rut
    bodega = user.id_bodega_id

    tipo_usuario = user.id_usuario_id
    despachos = Despacho.objects.select_related('rut__id_sucursal','id_producto__id_area__id_bodega').filter(Q(rut=rut) & Q(id_producto__id_area__id_bodega=bodega))
    despachos_colab = Despacho.objects.select_related('rut__id_sucursal','id_producto__id_area__id_bodega').filter(id_producto__id_area__id_bodega=bodega)

    if tipo_usuario == 1:
        template_name = 'web/base.html'
    else:
        template_name = 'jefe_bodega/base_jefe.html'
    context = {'despachos': despachos,'template_name':template_name,'despachos_colab':despachos_colab}

    return render(request,'web/despacho.html',context)

@login_required(login_url='/')
def producto(request):
    user = request.user
    rut = user.rut
    id_bodega = user.id_bodega_id
    tipo_usuario = user.id_usuario_id

    productos = Producto.objects.select_related('rut__rut','id_area').filter(id_area__id_bodega=id_bodega,rut=rut)
    productos_colab = Producto.objects.select_related('rut__rut','id_area').filter(id_area__id_bodega=id_bodega)

    if tipo_usuario == 1:
        template_name = 'web/base.html'
    else:
        template_name = 'jefe_bodega/base_jefe.html'
    
    print(productos)

    contexto = {'productos': productos,'productos_colab':productos_colab,'template_name':template_name}
    return render(request, 'web/producto.html', contexto)

@login_required(login_url='/')
def perfil(request):
    user = request.user
    tipo_usuario = user.id_usuario_id
    rut = user.rut
    id_bodega = user.id_bodega_id

    perfiles = Usuario.objects.select_related('perfil').filter(rut=rut)
    plan_contratado = Pago.objects.filter(rut=rut).order_by('-fecha_pago').first()
    bodega = Bodega.objects.filter(id_bodega=id_bodega)

    notificacion = Perfil.objects.filter(rut=rut)

    if tipo_usuario == 1:
        template_name = 'web/base.html'
    else:
        template_name = 'jefe_bodega/base_jefe.html'
    context = {'template_name':template_name, 'perfiles':perfiles,'plan_contratado':plan_contratado, 'bodega':bodega,'notificacion':notificacion}
    return render(request,'web/perfil.html',context)

@login_required(login_url='/')
def registrarProducto(request):
    errorProd = False
    exitoProd = False
    error_message = ""
    exito_message = ""
    title = ""

    user = request.user
    rut_colab = user.rut
    tipo_usuario = user.id_usuario_id
    id_bodega = user.id_bodega_id

    if request.method == 'POST':
        nombre_producto = request.POST.get("nombre_producto").lower()
        stock = int(request.POST.get("stock"))
        rut_cliente = request.POST.get("rut")
        id_area = request.POST.get("id_area")
        foto = request.FILES.get("foto_prod")

        producto_existente = Producto.objects.filter(Q(nombre_producto=nombre_producto) & Q(rut=rut_cliente))

        try:
            if nombre_producto == "":
                errorProd = True
                error_message = "Debe ingresar un nombre al producto" 
            
            elif stock == "":
                errorProd = True
                error_message = "Debe ingresar el stock" 

            elif rut_cliente == "":
                errorProd = True
                error_message = "Debe seleccionar un cliente" 
            
            elif id_area == "":
                errorProd = True
                error_message = "Debe seleccionar el area" 
            
            elif producto_existente:
                errorProd = True
                error_message = "El producto ya existe para este usuario." 

            elif stock == 0:
                errorProd = True
                error_message = "El stock no puede ser igual a 0"

            elif stock < 0:
                errorProd = True
                error_message = "El stock no puede contener números negativos" 

            else:
                if not foto:
                    foto = 'producto/foto_pred.jpg'

                area_bodega = AreaBodega.objects.get(id_area=id_area)
                cliente = Cliente.objects.get(rut=rut_cliente)
            
                producto = Producto(nombre_producto=nombre_producto, stock=stock, foto_prod=foto, id_area=area_bodega, rut=cliente)
                producto.save()
                exitoProd = True
                title = "Agregado"
                exito_message = 'Producto agregado correctamente'
        except:
            errorProd = True
            error_message = "Error al agregar Producto"

    areas = Usuario.objects.filter(Q(rut=rut_colab) & Q(id_usuario=tipo_usuario) & Q(id_bodega__areabodega__disponible='S')).values('id_bodega__areabodega__id_area','id_bodega__areabodega__sector')
    clientes = Usuario.objects.filter(Q(id_bodega=id_bodega) & Q(id_usuario=1))
     
    context = {
        'areas': areas,
        'clientes': clientes,
        'errorProd': errorProd, 
        'error_message': error_message,
        'exitoProd': exitoProd,
        'exito_message': exito_message,
        'title':title
    }

    return render(request, 'jefe_bodega/registrarProducto.html', context)

@login_required(login_url='/')
def modificar_prod(request, id_producto):
    errorProd = False
    exitoProd = False
    error_message = ""
    exito_message = ""
    title = ""

    user = request.user
    rut_colab = user.rut
    tipo_usuario = user.id_usuario_id
    id_bodega = user.id_bodega_id

    producto = Producto.objects.get(id_producto=id_producto)

    if request.method == "POST":
        nombre_prod = request.POST.get("nombre_producto")
        stock = int(request.POST.get("stock"))
        area = request.POST.get("id_area")
        rut = request.POST.get("rut")
        foto = request.FILES.get("foto_prod")

        
        producto_existente = Producto.objects.filter(Q(nombre_producto=nombre_prod) & Q(rut=nombre_prod))

        try:
            if nombre_prod == "":
                errorProd = True
                error_message = "Debe ingresar un nombre al producto" 
            
            elif stock == "":
                errorProd = True
                error_message = "Debe ingresar el stock" 
            
            elif rut == "":
                errorProd = True
                error_message = "Debe seleccionar un cliente" 
            
            elif area == "":
                errorProd = True
                error_message = "Debe seleccionar el area" 
            
            elif producto_existente:
                errorProd = True
                error_message = "El producto ya existe para este usuario." 

            elif stock == 0:
                errorProd = True
                error_message = "El stock no puede ser igual a 0"

            elif stock < 0:
                errorProd = True
                error_message = "El stock no puede contener números negativos" 

            else:
                if not foto:
                    foto = producto.foto_prod
                else:
                    default_storage.delete(producto.foto_prod.name)
                    producto.foto_prod = foto
                
                area_bodega = AreaBodega.objects.get(id_area=area)
                cliente = Cliente.objects.get(rut=rut)
                
                producto.nombre_producto = nombre_prod
                producto.stock = stock
                producto.id_area = area_bodega
                producto.rut = cliente
                
                producto.save()
                exitoProd = True
                title = 'Actualizado'
                exito_message = 'Producto Actualizado correctamente'

        except Producto.DoesNotExist:
            errorProd = True
            error_message = "Error al actualizar Producto:"

    areas = Usuario.objects.filter(Q(rut=rut_colab) & Q(id_usuario=tipo_usuario) & Q(id_bodega__areabodega__disponible='S')).values('id_bodega__areabodega__id_area','id_bodega__areabodega__sector')
    clientes = Usuario.objects.filter(Q(id_bodega=id_bodega) & Q(id_usuario=1))

    context = {
        'areas': areas,
        'clientes': clientes,
        'errorProd': errorProd, 
        'error_message': error_message,
        'errorProd': errorProd,
        'exitoProd':exitoProd,
        'exito_message': exito_message,
        'title':title,
        'producto': producto,
        'id_producto': id_producto
        
    }
    return render(request, 'jefe_bodega/modificarProd.html', context)

@login_required(login_url='/')
def eliminarProducto(request, id_producto):
    eliminarProd = False
    exito_message = ''
    error_message = ''

    try:
        productoDelete = Producto.objects.get(id_producto=id_producto)
        if productoDelete.foto_prod != 'producto/foto_pred.jpg':
            default_storage.delete(productoDelete.foto_prod.name)

        productoDelete.delete()
        eliminarProd =  True
        exito_message = 'Producto Eliminado con exito'
    except ObjectDoesNotExist:
        error_message = 'Producto no eliminado'

    if eliminarProd:
        return JsonResponse({'status': 'success', 'exito_message': exito_message})
    else:
        return JsonResponse({'status': 'error', 'error_message': error_message})

# Buscar Producto
@login_required(login_url='/')
def buscar_producto(request):
    user = request.user
    rut = user.rut
    tipo_usuario = user.id_usuario_id
    id_bodega = user.id_bodega_id

    if request.method == 'GET' and 'txtNombreProd' in request.GET:
        nombre_producto = request.GET.get("txtNombreProd")

        productos = Producto.objects.filter(nombre_producto__icontains=nombre_producto,rut=rut)
        productos_colab = Producto.objects.select_related('rut__rut','id_area').filter(nombre_producto__icontains=nombre_producto,id_area__id_bodega=id_bodega)

        if(tipo_usuario == 1):
            template_name = 'web/base.html'
        else:
            template_name = 'jefe_bodega/base_jefe.html'
    contexto = {"productos":productos,"productos_colab":productos_colab,"template_name":template_name}
    return render(request,"web/producto.html",contexto)

login_required(login_url='/')
def despachar(request):
    exitoDespacho = False
    error_message = ""
    exito_message = ""

    if request.method == "POST":
        cantidad_despachar = int(request.POST.get('cantidad_despachar'))
        id_producto = request.POST.get('id_producto')
        rut_cliente = request.POST.get('rut')
        

        producto = Producto.objects.get(id_producto=id_producto)
        despacho = Despacho.objects.filter(id_producto=id_producto).first()
        cliente = Cliente.objects.get(rut=rut_cliente)

        estado = 'S'
        tiempo_entrega = 60  

        if producto.stock == 0:
            error_message = "El producto sin stock"

        elif cantidad_despachar > producto.stock:
            error_message = "La cantidad a despachar supera el stock disponible"

        elif cantidad_despachar == 0:
            error_message = "La cantidad a despachar no puede ser 0"
            
        elif cantidad_despachar < 0:
            error_message = "La cantidad a despachar debe ser mayor que 0" 

        else:
            despacho = Despacho(estado=estado, tiempo_entrega=tiempo_entrega, id_producto=producto, cant_despachada=cantidad_despachar, rut=cliente)
            exitoDespacho = True
            exito_message = "Producto Despachado"
            cantidad_despachar = int(cantidad_despachar)
            producto.stock = producto.stock - cantidad_despachar
            despacho.save()
            producto.save()
    else:
        error_message = "A ocurrido un error inesperado"

    if exitoDespacho:
        return JsonResponse({'status': 'success', 'exito_message': exito_message})
    else:
        return JsonResponse({'status': 'error', 'error_message': error_message})

@login_required(login_url='/')
def buscar_despacho(request):
    user = request.user
    rut = user.rut

    id_bodega = user.id_bodega_id

    tipo_usuario = user.id_usuario_id

    if request.method == 'GET' and 'txtNombreProd' in request.GET:
        nombre_producto = request.GET.get("txtNombreProd")
        despachos = Despacho.objects.filter(id_producto__nombre_producto__icontains=nombre_producto).select_related('rut__id_sucursal', 'id_producto__id_area__id_bodega').filter(rut=rut)
        despachos_colab = Despacho.objects.select_related('rut__id_sucursal','id_producto__id_area__id_bodega').filter(id_producto__nombre_producto__icontains=nombre_producto,id_producto__id_area__id_bodega=id_bodega)

        #productos_colab = Producto.objects.select_related('rutrut','id_area').filter(nombre_productoicontains=nombre_producto,id_area__id_bodega=id_bodega)
    if tipo_usuario == 1:
        template_name = 'web/base.html'
    else:
        template_name = 'jefe_bodega/base_jefe.html'
    contexto = {"despachos":despachos,'template_name':template_name,'despachos_colab':despachos_colab}

    return render(request,"web/despacho.html",contexto)

def cargar_sucursales(request):
    empresa_rut = request.GET.get('empresa_rut')
    sucursales = Sucursal.objects.filter(rut_empresa=empresa_rut).values('id_sucursal', 'nombre_sucursal')
    sucursal_data = list(sucursales)
    return JsonResponse(sucursal_data, safe=False)

@login_required(login_url='/')
@admin_required
def agrePerfil(request):
    regis = TipoColaborador.objects.all()
    contexto = {"categorias": regis}

    if request.POST:
        nombre_colab = request.POST.get("nombre_perfil")

        try:
            # Intenta crear y guardar una instancia de TipoColaborador
            tipo_colaborador = TipoColaborador(nombre_colab=nombre_colab)
            tipo_colaborador.save()
            return redirect('ADMPERFILES')
        except IntegrityError as e:
            # Si se produce una excepción de IntegrityError, puedes manejarla aquí
            contexto["mensaje"] = "Error al guardar."

    return render(request, 'Admin/Agregar/agregarPerfil.html', contexto)

@login_required(login_url='/')
@admin_required
def modifPerfil(request, id_tp_colab):
    try:
        perfil = TipoColaborador.objects.get(pk=id_tp_colab)

        if request.method == "POST":
            nombre_colab = request.POST.get("nombre_perfil")

            # Actualiza el nombre del perfil
            perfil.nombre_colab = nombre_colab
            perfil.save()  # Guarda la instancia modificada en la base de datos

            # Puedes mostrar una alerta de éxito aquí si lo deseas
            return redirect('ADMPERFILES')

        else:
            contexto = {"perfil": perfil}
            return render(request, 'Admin/Modificar/modificarPerfil.html', contexto)

    except TipoColaborador.DoesNotExist:
        # Maneja el caso en el que no se encuentre el perfil con el ID proporcionado
        return render(request, 'Admin/error.html', {"mensaje": "El perfil no existe"})

@login_required(login_url='/')
@admin_required
def eliminarPerfil(request, id_tp_colab):
    try:
        perfilDelete = TipoColaborador.objects.get(id_tp_colab=id_tp_colab)
        perfilDelete.delete()
        messages.success(request, 'Perfil eliminado exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar el perfil.')

    return redirect('ADMPERFILES')

@login_required(login_url='/')
@admin_required
def agreProducto(request):
    regis = Producto.objects.all()
    clientes = Usuario.objects.filter(id_usuario=1)
    areas = AreaBodega.objects.all()
    contexto = {"productos": regis, "clientes": clientes, "areas":areas}

    if request.method == 'POST':
        nombre_producto = request.POST.get("nombre_pro")
        stock = request.POST.get("stock")
        rut_cliente = request.POST.get("selectCliente")
        id_area = request.POST.get("selectSector")
        foto = request.FILES.get("foto_prod")

        if not foto:
                default_photo_path = 'producto/foto_pred.jpg'
                foto = default_photo_path


        area_bodega = AreaBodega.objects.get(id_area=id_area)
        cliente = Cliente.objects.get(rut=rut_cliente)

        producto = Producto(nombre_producto=nombre_producto, stock=stock, foto_prod=foto, id_area=area_bodega, rut=cliente)
        producto.save()
        return redirect('ADMPRODUCTO')

    return render(request, 'Admin/Agregar/agregarProducto.html',contexto)

@login_required(login_url='/')
@admin_required
def agreEmpresa(request):
    regis = Empresa.objects.all()
    contexto = {"categorias": regis}

    if request.POST:
        rut_empresa = request.POST.get("rut_emp")
        nombre_empresa = request.POST.get("nombre_empresa")
        descripcion = request.POST.get("descrip_emp")

        # Verificar si el RUT ya existe
        if Empresa.objects.filter(rut_empresa=rut_empresa).exists():
            contexto["mensaje"] = "El RUT ya existe."
        else:
            try:
                empresa = Empresa(
                    rut_empresa=rut_empresa, nombre_empresa=nombre_empresa, descripcion=descripcion)
                empresa.save()
                return redirect('ADMEMPRESA')
            except IntegrityError as e:
                contexto["mensaje"] = "Error al guardar la empresa."

    return render(request, 'Admin/Agregar/agregarEmpresa.html', contexto)

@login_required(login_url='/')
@admin_required
def eliminarEmpresa(request, rut_empresa):
    try:
        empresaDelete = Empresa.objects.get(rut_empresa=rut_empresa)
        empresaDelete.delete()
        messages.success(request, 'Empresa eliminada exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar esta empresa.')

    return redirect('ADMEMPRESA')

@login_required(login_url='/')
@admin_required
def agrePlan(request):
    regis = Plan.objects.all()
    bodegas = Bodega.objects.all()
    contexto = {"categorias": regis, "bodega": bodegas}

    if request.POST:
        nombre_plan = request.POST.get("nombre_plan")
        valor_plan = request.POST.get("costo")
        cant_anaquel_plan = request.POST.get("cant_anaqueles")
        capacidad_anaquel = request.POST.get("capacidad")
        id_bodega = request.POST.get("selectBodega")
        plan = Plan(
            nombre_plan=nombre_plan,
            valor_plan=valor_plan,
            cant_anaquel_plan=cant_anaquel_plan,
            capacidad_anaquel=capacidad_anaquel
        )
        plan.save()

            # Obtener la instancia de Bodega
        bodega = Bodega.objects.get(id_bodega=id_bodega)

            # Guardar el detalle del plan
        dtPlan = DetallePlan(id_bodega=bodega, id_plan=plan)  # Usar la instancia de Plan, no el id
        dtPlan.save()

        return redirect('ADMPLAN')

    return render(request, 'Admin/Agregar/agregarPlan.html', contexto)

@login_required(login_url='/')
@admin_required
def modifPlan(request, plan_id):
    try:
        plan = Plan.objects.get(pk=plan_id)

        if request.method == "POST":
            nombre_plan = request.POST.get("nombre_plan")
            valor_plan = request.POST.get("costo")
            cant_anaquel_plan = request.POST.get("cant_anaqueles")
            capacidad_anaquel = request.POST.get("capacidad")

            # Actualiza los campos del plan con los nuevos valores
            plan.nombre_plan = nombre_plan
            plan.valor_plan = valor_plan
            plan.cant_anaquel_plan = cant_anaquel_plan
            plan.capacidad_anaquel = capacidad_anaquel

            plan.save()  # Guarda la instancia modificada en la base de datos

            return redirect('ADMPLAN')
        else:
            contexto = {"plan": plan}
            return render(request, 'Admin/Modificar/modificarPlan.html', contexto)

    except Plan.DoesNotExist:
        # Maneja el caso en el que no se encuentre el plan con el ID proporcionado
        return render(request, 'Admin/error.html', {"mensaje": "El plan no existe"})

@login_required(login_url='/')
@admin_required
def eliminarPlan(request, id_plan):
    try:
        planDelete = Plan.objects.get(id_plan=id_plan)
        dtPlan = DetallePlan.objects.get(id_plan=planDelete)
        planDelete.delete()
        dtPlan.delete()
        messages.success(request, 'Plan eliminado exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar el plan seleccionado.')

    return redirect('ADMPLAN')

@login_required(login_url='/')
@admin_required
def agreSucursal(request):
    regis = Sucursal.objects.all()
    empresas = Empresa.objects.all()
    contexto = {'sucursales': regis, 'empresas': empresas}

    if request.POST:
        nombre_sucursal = request.POST.get("nombre_sus")
        direccion = request.POST.get("direccion_sus")
        rut_empresa = request.POST.get("selectEmpresa")

        if rut_empresa:
                empresa = Empresa.objects.get(rut_empresa=rut_empresa)
                sucursal = Sucursal(
                    nombre_sucursal=nombre_sucursal, direccion=direccion, rut_empresa=empresa)
                sucursal.save()
                return redirect('ADMSUCRUSAL')
        else:
            contexto["mensaje"] = "Por favor, selecciona una empresa antes de registrar la sucursal."

    return render(request, 'Admin/Agregar/agregarSucursal.html', contexto)

@login_required(login_url='/')
@admin_required
def eliminarSucursal(request, id_sucursal):
    try:
        sucursalDelete = Sucursal.objects.get(id_sucursal=id_sucursal)
        sucursalDelete.delete()
        messages.success(request, 'Sucursal eliminada exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar la sucursal seleccionada.')

    return redirect('ADMSUCRUSAL')

@login_required(login_url='/')
@admin_required
def agreCliente(request):
    regis = Usuario.objects.all()
    cli = Cliente.objects.all()
    bodega = Bodega.objects.all()
    sucursal = Sucursal.objects.all()
    contexto = {'regis': regis, 'cli': cli,
                'bodega': bodega, 'sucursal': sucursal}

    if request.POST:
        rut = request.POST.get("rut_cli")

        # Verificar si el rut ya existe en la base de datos
        if Usuario.objects.filter(rut=rut).exists():
            error_message = "El rut ya está registrado. Por favor, elija otro rut."
            contexto["error_message"] = error_message
            return render(request, 'Admin/Agregar/agregarCliente.html', contexto)

        primer_nombre = request.POST.get("p_nombre_cli")
        segundo_nombre = request.POST.get("s_nombre_cli")
        apellido_paterno = request.POST.get("ap_apellido_cli")
        apellido_materno = request.POST.get("am_apellido_cli")
        correo = request.POST.get("mail_cli")
        hoy = date.today()

        # Verificar si el correo ya existe en la base de datos
        if Usuario.objects.filter(correo=correo).exists():
            error_message = "El correo ya está registrado. Por favor, elija otro correo."
            contexto["error_message"] = error_message
            return render(request, 'Admin/Agregar/agregarCliente.html', contexto)

        contrasena = request.POST.get("pass_cli")

        fecha_nac_str = request.POST.get('fecha_nac')

        # Verifica que la fecha no esté vacía
        if fecha_nac_str:
            fecha = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
        else:
            # Handle the case where fecha_nac is empty or None
            error_message = "La fecha de nacimiento es obligatoria."
            contexto["error_message"] = error_message
            return render(request, 'Admin/Agregar/agregarCliente.html', contexto)

        direccion = request.POST.get("direccion_cli")
        id_sucursal = request.POST.get("selectSucursal")
        id_bodega = request.POST.get("selectBodega")
        id_usuario = request.POST.get("txtId")

        edad_cli = hoy.year - fecha.year

        # Validación y procesamiento de los datos, similar al código anterior

        try:

            nuevo_usuario = Usuario(
                rut=rut,
                primer_nombre=primer_nombre,
                segundo_nombre=segundo_nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                password = contrasena,
                correo=correo,
                id_bodega=Bodega.objects.get(id_bodega=id_bodega),
                id_usuario_id=id_usuario
            )
            nuevo_usuario.set_password(contrasena)
            nuevo_usuario.save()

            nuevo_cliente = Cliente(
                rut=nuevo_usuario,
                direccion=direccion,
                fecha_nac=fecha,
                id_sucursal=Sucursal.objects.get(id_sucursal=id_sucursal),
            )
            nuevo_cliente.save()

            nuevo_perfil = Perfil(
                edad = edad_cli,
                rut = nuevo_usuario
            )

            nuevo_perfil.save()

            return redirect('ADMCLIENTE')

        except DatabaseError as e:
            contexto["mensaje"] = "Error al guardar."

    return render(request, 'Admin/Agregar/agregarCliente.html', contexto)

@login_required(login_url='/')
@admin_required
def eliminarCliente(request,rut):
    try:
        usuario = Usuario.objects.get(rut=rut)
        cliente = Cliente.objects.get(rut=usuario.rut)
        usuario.delete()
        cliente.delete()
        messages.success(request, 'Cliente eliminada exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar cliente.')

    return redirect('ADMCLIENTE')

@login_required(login_url='/')
@admin_required
def modifCliente(request, rut):
    try:
        usuario_existente = Usuario.objects.get(pk=rut)
        cliente_existente = Cliente.objects.get(rut=usuario_existente)

        if request.method == "POST":
            rut = request.POST.get("rut_cli")
            correo = request.POST.get("mail_cli")
            primer_nombre = request.POST.get("p_nombre_cli")
            segundo_nombre = request.POST.get("s_nombre_cli")
            apellido_paterno = request.POST.get("ap_apellido_cli")
            apellido_materno = request.POST.get("am_apellido_cli")
            id_sucursal = request.POST.get("selectSucursal")
            id_bodega = request.POST.get("selectBodega")
            id_usuario = request.POST.get("txtId")

            # Actualiza los campos del usuario con los nuevos valores
            usuario_existente.rut = rut
            usuario_existente.primer_nombre = primer_nombre
            usuario_existente.segundo_nombre = segundo_nombre
            usuario_existente.apellido_paterno = apellido_paterno
            usuario_existente.apellido_materno = apellido_materno
            usuario_existente.correo = correo
            usuario_existente.id_bodega = Bodega.objects.get(id_bodega=id_bodega)
            usuario_existente.id_usuario_id = id_usuario

            usuario_existente.save()

            # Actualiza el cliente asociado
            cliente_existente.rut = usuario_existente
            cliente_existente.direccion = request.POST.get("direccion_cli")
            cliente_existente.fecha_nac = datetime.strptime(request.POST.get('fecha_nac'), '%Y-%m-%d').date()
            cliente_existente.id_sucursal = Sucursal.objects.get(id_sucursal=id_sucursal)

            cliente_existente.save()

            return redirect('ADMCLIENTE')
        else:
            contexto = {"usuario_existente": usuario_existente, "cliente_existente": cliente_existente}
            return render(request, 'Admin/Modificar/modificarCliente.html', contexto)
    except Usuario.DoesNotExist:
        # Maneja el caso en el que no se encuentre el usuario con el ID proporcionado
        return render(request, 'Admin/error.html', {"mensaje": "El cliente no existe"})

@login_required(login_url='/')
@admin_required
def agreBodega(request):
    regis = Bodega.objects.all()
    tipoBodegas = TipoBodega.objects.all()
    contexto = {'bodega': regis, 'tipoBodega': tipoBodegas}

    if request.POST:
        nombre_bodega = request.POST.get("nombre_bod")
        direccion = request.POST.get("direccion_bod")
        id_tp_bodega = request.POST.get("selectTpBodega")

        if id_tp_bodega:
            tipoBodega = TipoBodega.objects.get(id_tp_bodega=id_tp_bodega)
            bodega = Bodega(nombre_bodega=nombre_bodega,
                                direccion=direccion, id_tp_bodega=tipoBodega)
            bodega.save()
            return redirect('ADMBODEGA')
        else:
            contexto["mensaje"] = "Por favor, selecciona un tipo de bodega antes de registrar."

    return render(request, 'Admin/Agregar/agregarBodega.html', contexto)

@login_required(login_url='/')
@admin_required
@transaction.atomic
def eliminarBodega(request, id_bodega):
    try:
        bodegaDelete = Bodega.objects.get(id_bodega=id_bodega)

        # Intenta obtener el área de bodega asociada, si existe
        try:
            areaBodega = AreaBodega.objects.get(id_bodega=id_bodega)
            areaBodega.delete()
        except ObjectDoesNotExist:
            pass  # No hay área de bodega asociada, continuar con la eliminación de la bodega

        # Eliminar la bodega en una transacción
        bodegaDelete.delete()

        messages.success(request, 'Bodega eliminada exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar la bodega.')

    return redirect('ADMBODEGA')

@login_required(login_url='/')
@admin_required
def agreAreaBodega(request):
    regis = AreaBodega.objects.all()
    bodegas = Bodega.objects.all()
    contexto = {'areaBodega': regis, 'bodegas': bodegas}

    if request.POST:
        sector = request.POST.get("sector_area")
        cant_anaq_area = request.POST.get("anaqueles_area")
        id_bodega = request.POST.get("selectBodega")
        disponible = request.POST.get("disponible")

        if id_bodega:
            bodega = Bodega.objects.get(id_bodega=id_bodega)
            areaBodega = AreaBodega(
                sector=sector, cant_anaq_area=cant_anaq_area, disponible=disponible, id_bodega=bodega)
            areaBodega.save()
            return redirect('ADMAREA')
        else:
            contexto["mensaje"] = "Por favor, selecciona una bodega antes de registrar."

    return render(request, 'Admin/Agregar/agregarAreaBodega.html', contexto)

@login_required(login_url='/')
@admin_required
def eliminarArea(request, id_area):
    try:
        bodegaDelete = AreaBodega.objects.get(id_area=id_area)
        bodegaDelete.delete()
        messages.success(request, 'Área bodega eliminada exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar área bodega.')

    return redirect('ADMAREA')

@login_required(login_url='/')
@admin_required
def agreEmpleado(request):
    regis = Usuario.objects.all()
    empl = Colaborador.objects.all()
    bodega = Bodega.objects.all()
    tpColab = TipoColaborador.objects.all()
    contexto = {'regis': regis, 'empl': empl,
                'bodega': bodega, 'tpColab': tpColab}

    if request.POST:
        rut = request.POST.get("rut_emp")

        # Verificar si el rut ya existe en la base de datos
        if Usuario.objects.filter(rut=rut).exists():
            error_message = "El rut ya está registrado. Por favor, elija otro rut."
            contexto["error_message"] = error_message
        else:
            correo = request.POST.get("mail_emp")

            # Verificar si el correo ya existe en la base de datos
            if Usuario.objects.filter(correo=correo).exists():
                error_message = "El correo ya está registrado. Por favor, elija otro correo."
                contexto["error_message"] = error_message
            else:
                primer_nombre = request.POST.get("p_nombre_emp")
                segundo_nombre = request.POST.get("s_nombre_emp")
                apellido_paterno = request.POST.get("ap_apellido_emp")
                apellido_materno = request.POST.get("am_apellido_emp")
                PASSWORD = request.POST.get("pass_emp")
                id_tp_colab = request.POST.get("selectPerfil")
                id_bodega = request.POST.get("selectBodega")
                id_usuario = request.POST.get("txtId")

                try:
                    nuevo_usuario = Usuario(
                        rut=rut,
                        primer_nombre=primer_nombre,
                        segundo_nombre=segundo_nombre,
                        apellido_paterno=apellido_paterno,
                        apellido_materno=apellido_materno,
                        correo=correo,
                        id_bodega=Bodega.objects.get(id_bodega=id_bodega),
                        id_usuario_id=id_usuario,
                    )
                    nuevo_usuario.set_password(PASSWORD)
                    nuevo_usuario.save()

                    nuevo_colaborador = Colaborador(
                        rut=nuevo_usuario,  # Asociar al usuario que acabamos de crear
                        id_tp_colab=TipoColaborador.objects.get(
                            id_tp_colab=id_tp_colab),
                    )
                    nuevo_colaborador.save()
                    return redirect('ADMCOLABORADOR')

                except DatabaseError as e:
                    contexto["mensaje"] = "Error al guardar."

    return render(request, 'Admin/Agregar/agregarEmpleado.html', contexto)

@login_required(login_url='/')
@admin_required
def eliminarEmpleado(request,rut):
    try:
        usuario = Usuario.objects.get(rut=rut)
        colaborador = Colaborador.objects.get(rut=usuario.rut)
        usuario.delete()
        colaborador.delete()
        messages.success(request, 'Empleado eliminado exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar colaborador.')

    return redirect('ADMCOLABORADOR')

@login_required(login_url='/')
@admin_required
def modPerfil(request, id_tp_colab):
    modPerfil = TipoColaborador.objects.get(id_tp_colab=id_tp_colab)
    contexto = {"perfiles": modPerfil}

    return render(request,'Admin/Modificar/modificarPerfil.html', contexto)

@login_required(login_url='/')
@admin_required
def modEmpresa(request, rut_empresa):
    modEmpresa = Empresa.objects.get(rut_empresa=rut_empresa)
    contexto = {"empresas": modEmpresa}
    return render(request,'Admin/Modificar/modificarEmpresa.html', contexto)

@login_required(login_url='/')
@admin_required
def modifEmpresa(request, rut_empresa):
    try:
        empresa = Empresa.objects.get(pk= rut_empresa)

        if request.method == "POST":
            nombre_empresa = request.POST.get("nombre_empresa")
            rut_empresa = request.POST.get("rut_emp")
            descripcion = request.POST.get("descrip_emp")

            empresa.nombre_empresa = nombre_empresa
            empresa.rut_empresa = rut_empresa
            empresa.descripcion = descripcion
           
            empresa.save()  # Guarda la instancia modificada en la base de datos

            return redirect('ADMEMPRESA')
        else:
            contexto = {"empresa": empresa}
            return render(request, 'Admin/Modificar/modificarEmpresa.html', contexto)

    except Empresa.DoesNotExist:
        return render(request, 'Admin/error.html', {"mensaje": "La empresa no existe"})

@login_required(login_url='/')
@admin_required
def modBodega(request, id_bodega):
    modBodega = Bodega.objects.get( id_bodega= id_bodega)
    modTPBodega = TipoBodega.objects.all()
    contexto = {"bodega":modBodega,"tipoBodega":modTPBodega}
    return render(request,'Admin/Modificar/modificarBodega.html', contexto)

@login_required(login_url='/')
@admin_required
def modifBodega(request, id_bodega):
    try:
        bodega = Bodega.objects.get(pk=id_bodega)

        if request.method == "POST":
            nombre_bodega = request.POST.get("nombre_bod")
            direccion = request.POST.get("direccion_bod")
            tp_bodega = request.POST.get("selectTpBodega")
            objTPBodega = TipoBodega.objects.get(id_tp_bodega=tp_bodega)

            bodega.nombre_bodega = nombre_bodega
            bodega.id_tp_bodega = objTPBodega
            bodega.direccion = direccion

            bodega.save()  # Guarda la instancia modificada en la base de datos

            return redirect('ADMBODEGA')
        else:
            contexto = {"bodega": bodega}
            return render(request, 'Admin/Modificar/modificarBodega.html', contexto)

    except Bodega.DoesNotExist:
        return render(request, 'Admin/error.html', {"mensaje": "La bodega no existe"})

@login_required(login_url='/')
@admin_required
def modAreaBodega(request, id_area):
    modArea = AreaBodega.objects.get(id_area=id_area)
    modBodega = Bodega.objects.all()
    contexto = {"areaBodega": modArea, "bodega":modBodega}
    return render(request,'Admin/Modificar/modificarAreaBodega.html', contexto)

@login_required(login_url='/')
@admin_required
def modifArea(request, id_area):
    try:
        area = AreaBodega.objects.get(pk=id_area)

        if request.method == "POST":
            sector = request.POST.get("sector_area")
            cant_anaq_area = request.POST.get("anaqueles_area")
            id_bodega = request.POST.get("selectBodega")
            objBodega = Bodega.objects.get(id_bodega=id_bodega)
            disponible = request.POST.get("disponible")

            area.sector = sector
            area.id_bodega = objBodega
            area.cant_anaq_area = cant_anaq_area
            area.disponible = disponible

            area.save()  # Guarda la instancia modificada en la base de datos

            return redirect('ADMAREA')
        else:
            contexto = {"area": area}
            return render(request, 'Admin/Modificar/modificarAreaBodega.html', contexto)
    except AreaBodega.DoesNotExist:
        return render(request, 'Admin/error.html', {"mensaje": "El área bodega no existe"})

@login_required(login_url='/')
@admin_required
def modCliente(request, rut):
    usuarioCli = Usuario.objects.filter(rut=rut).first()
    cli = Cliente.objects.all()
    bodega = Bodega.objects.all()
    sucursal = Sucursal.objects.all
    contexto = {"usuarioCli": usuarioCli, "cli": cli, "bodega": bodega, "sucursal": sucursal}
    return render(request,'Admin/Modificar/modificarCliente.html', contexto)

@login_required(login_url='/')
@admin_required
def modEmpleado(request, rut):
    modEmpl = Usuario.objects.filter(rut=rut).first()
    empl = Colaborador.objects.all()
    bodega = Bodega.objects.all()
    tpColab = TipoColaborador.objects.all()
    contexto = {"usuarioEmp": modEmpl, "empl": empl,"bodega": bodega, "tpColab": tpColab}
    return render(request,'Admin/Modificar/modificarEmpleado.html', contexto)

@login_required(login_url='/')
@admin_required
def modifEmpleado(request, rut):
    try:
        usuario_existente = Usuario.objects.get(pk=rut)
        colaborador_existente = Colaborador.objects.get(rut=usuario_existente)

        if request.method == "POST":
            rut = request.POST.get("rut_emp")
            correo = request.POST.get("mail_emp")
            primer_nombre = request.POST.get("p_nombre_emp")
            segundo_nombre = request.POST.get("s_nombre_emp")
            apellido_paterno = request.POST.get("ap_apellido_emp")
            apellido_materno = request.POST.get("am_apellido_emp")
            id_tp_colab = request.POST.get("selectPerfil")
            id_bodega = request.POST.get("selectBodega")
            id_usuario = request.POST.get("txtId")

            # Actualiza los campos del usuario con los nuevos valores
            usuario_existente.rut = rut
            usuario_existente.primer_nombre = primer_nombre
            usuario_existente.segundo_nombre = segundo_nombre
            usuario_existente.apellido_paterno = apellido_paterno
            usuario_existente.apellido_materno = apellido_materno
            usuario_existente.correo = correo
            usuario_existente.id_bodega = Bodega.objects.get(id_bodega=id_bodega)
            usuario_existente.id_usuario_id = id_usuario

            usuario_existente.save()

            # Actualiza el colaborador asociado
            colaborador_existente.rut = usuario_existente
            colaborador_existente.id_tp_colab = TipoColaborador.objects.get(id_tp_colab=id_tp_colab)
            colaborador_existente.save()

            return redirect('ADMCOLABORADOR')
        else:
            contexto = {"usuario_existente": usuario_existente, "colaborador_existente": colaborador_existente}
            return render(request, 'Admin/Modificar/modificarEmpleado.html', contexto)
    except Usuario.DoesNotExist:
        # Maneja el caso en el que no se encuentre el usuario con el ID proporcionado
        return render(request, 'Admin/error.html', {"mensaje": "El empleado no existe"})

@login_required(login_url='/')
@admin_required
def modSucursal(request, id_sucursal):
    modSucursal = Sucursal.objects.get(id_sucursal=id_sucursal)
    modEmpresa = Empresa.objects.all()
    contexto = {"sucursal": modSucursal, "empresas": modEmpresa}
    return render(request,'Admin/Modificar/modificarSucursal.html', contexto)

@login_required(login_url='/')
@admin_required
def modifSucursal(request, id_sucursal):
    try:
        sucursal = Sucursal.objects.get(pk= id_sucursal)

        if request.method == "POST":
            nombre_sucursal = request.POST.get("nombre_sus")
            direccion = request.POST.get("direccion_sus")
            rut_empresa = request.POST.get("selectEmpresa")
            objRutEmp =Empresa.objects.get(rut_empresa=rut_empresa)

            sucursal.nombre_sucursal = nombre_sucursal
            sucursal.rut_empresa = objRutEmp
            sucursal.direccion = direccion
           
            sucursal.save()  # Guarda la instancia modificada en la base de datos

            return redirect('ADMSUCRUSAL')
        else:
            contexto = {"sucursal": sucursal}
            return render(request, 'Admin/Modificar/modificarSucursal.html', contexto)

    except Sucursal.DoesNotExist:
        return render(request, 'Admin/error.html', {"mensaje": "La sucursal no existe"})

@login_required(login_url='/')
@admin_required
def modPlan(request, id_plan):
    modPlan = Plan.objects.get(id_plan=id_plan)
    bodegas = Bodega.objects.all()
    dtPlan = DetallePlan.objects.get(id_plan=id_plan)
    contexto = {"planes": modPlan,"bodega": bodegas, "dtPlan": dtPlan}
    return render(request, "Admin/Modificar/modificarPlan.html", contexto)

@login_required(login_url='/')
@admin_required
def modProductoAdmin(request, id_producto):
    modProducto = Producto.objects.get(id_producto=id_producto)
    clientes = Usuario.objects.filter(id_usuario=1)
    areas = AreaBodega.objects.all()
    contexto = {"producto": modProducto,"clientes": clientes, "areas":areas}
    return render(request, 'Admin/Modificar/modificarProducto.html',contexto)

@login_required(login_url='/')
@admin_required
def modifProductoAdmin(request,id_producto):
    try:
        producto = Producto.objects.get(pk=id_producto)

        if request.method == "POST": 
            nombre_producto = request.POST.get("nombre_pro")
            stock = request.POST.get("stock")
            rut_cliente = request.POST.get("selectCliente")
            id_area = request.POST.get("selectSector")
            foto_nueva = request.FILES.get("foto_prod")
            foto_actual = request.POST.get("foto_prod_actual")


            area_bodega = AreaBodega.objects.get(id_area=id_area)
            cliente = Cliente.objects.get(rut=rut_cliente)
       
            producto.nombre_producto = nombre_producto
            producto.stock = stock
            producto.rut = cliente
            producto.id_area = area_bodega
            if foto_nueva:
                producto.foto_prod = foto_nueva
            else:
                # Mantener la imagen actual si no se proporciona una nueva
                producto.foto_prod.name = foto_actual

            producto.save()  # Guarda la instancia modificada en la base de datos

            return redirect('ADMPRODUCTO')

        else:
            contexto = {"producto": producto}
            return render(request, 'Admin/Modificar/modificarProducto.html', contexto)

    except Producto.DoesNotExist:
        return render(request, 'Admin/error.html', {"mensaje": "El perfil no existe"})

@login_required(login_url='/')
@admin_required
@transaction.atomic
def eliminarProductoAdmin(request, id_producto):
    try:
        with transaction.atomic():
            productoDelete = Producto.objects.get(id_producto=id_producto)

            try:
                despachoDelete = Despacho.objects.get(id_producto=id_producto)
                productoDelete.delete()
                despachoDelete.delete()
                messages.success(request, 'Producto y despacho eliminados exitosamente')
            except Despacho.DoesNotExist:
                # No se encontró despacho, eliminar solo el producto
                productoDelete.delete()
                messages.success(request, 'Producto eliminado exitosamente')

    except Producto.DoesNotExist:
        messages.error(request, 'No se puede eliminar el producto seleccionado. Producto no encontrado.')

    return redirect('ADMPRODUCTO')

@login_required(login_url='/')
def entregasRepa(request):
    despacho = Despacho.objects.all()
    contexto = {"despacho": despacho}
    print(despacho)
    return render(request, 'repartidor/entregas.html',contexto)

@login_required(login_url='/')
def plantillaRepaCambio(request, id_despacho):
    despacho = Despacho.objects.get(id_despacho=id_despacho)
    opciones_estado = Despacho.ESTADO_CHOICES
    contexto = {"despacho": despacho, 'opEst': opciones_estado}
    return render(request, 'repartidor/plantillaCambioEstado.html', contexto)

@login_required(login_url='/')
def imprimirRepa(request):
    return render(request,'repartidor/imprimir.html')

@login_required(login_url='/')
@admin_required
def modifPerfil(request, id_tp_colab):
    try:
        perfil = TipoColaborador.objects.get(pk=id_tp_colab)

        if request.method == "POST":
            nombre_colab = request.POST.get("nombre_perfil")

            # Actualiza el nombre del perfil
            perfil.nombre_colab = nombre_colab
            perfil.save()  # Guarda la instancia modificada en la base de datos

            # Puedes mostrar una alerta de éxito aquí si lo deseas
            return redirect('ADMPERFILES')

        else:
            contexto = {"perfil": perfil}
            return render(request, 'Admin/Modificar/modificarPerfil.html', contexto)

    except TipoColaborador.DoesNotExist:
        # Maneja el caso en el que no se encuentre el perfil con el ID proporcionado
        return render(request, 'Admin/error.html', {"mensaje": "El perfil no existe"})

@login_required(login_url='/')
@admin_required
def modifPlan(request, plan_id):
    try:
        plan = Plan.objects.get(pk=plan_id)
        dtPlan, created = DetallePlan.objects.get_or_create(id_plan=plan)

        if request.method == "POST":
            nombre_plan = request.POST.get("nombre_plan")
            valor_plan = request.POST.get("costo")
            cant_anaquel_plan = request.POST.get("cant_anaqueles")
            capacidad_anaquel = request.POST.get("capacidad")
            id_bodega = request.POST.get("selectBodega")

            # Convertir id_bodega a una instancia de Bodega
            bodega = get_object_or_404(Bodega, pk=id_bodega)

            # Actualiza los campos del plan con los nuevos valores
            plan.nombre_plan = nombre_plan
            plan.valor_plan = valor_plan
            plan.cant_anaquel_plan = cant_anaquel_plan
            plan.capacidad_anaquel = capacidad_anaquel
            plan.save()

            # Actualiza los campos del detalle del plan con los nuevos valores
            dtPlan.id_bodega = bodega
            dtPlan.save()

            return redirect('ADMPLAN')
        else:
            contexto = {"plan": plan, "dtPlan": dtPlan}
            return render(request, 'Admin/Modificar/modificarPlan.html', contexto)

    except Plan.DoesNotExist:
        # Maneja el caso en el que no se encuentre el plan con el ID proporcionado
        return render(request, 'Admin/error.html', {"mensaje": "El plan no existe"})

@login_required(login_url='/')
@admin_required
def errorMod(request):
    return render(request,'Admin/error.html')

@login_required(login_url='/')
def modifDespacho(request, id_despacho):
    try:
        despacho = Despacho.objects.get(pk=id_despacho)

        if request.method == "POST":
            tiempoEntrega = request.POST.get("TEntrega")
            estado = request.POST.get("estado")

            despacho.tiempo_entrega = tiempoEntrega
            despacho.estado = estado
            despacho.save()  

            # Puedes mostrar una alerta de éxito aquí si lo deseas
            return redirect('ENTREGAREPA')

        else:
            contexto = {"despacho": despacho}
            return render(request, 'repartidor/plantillaCambioEstado.html', contexto)

    except Despacho.DoesNotExist:
        # Maneja el caso en el que no se encuentre el perfil con el ID proporcionado
        return render(request, 'Admin/error.html', {"mensaje": "El despacho no existe"})

@login_required(login_url='/') 
def plantillaPdf_ent(request):
    user = request.user
    rut = user.rut
    id_bodega = user.id_bodega_id

    productos = Producto.objects.select_related('rut__rut', 'id_area').filter(Q(rut=rut) | Q(id_area__id_bodega__id_bodega=id_bodega))

    # Carga la plantilla HTML
    template_path = 'jefe_bodega/plantilla_pdf.html'
    template = get_template(template_path)

    # Rellena la plantilla con los datos
    context = {'productos': productos}
    html = template.render(context)
    
    # Convierte la plantilla HTML a PDF
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    if not pisa_status.err:
        # Vuelve al comienzo del buffer para que el PDF se genere correctamente
        buffer.seek(0)
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="reporte.pdf"' 
        
        return response
    else:
        return HttpResponse('Error al generar el PDF', status=500)

@login_required(login_url='/')    
def plantillaPdf_Desp(request, id_sucursal):
    user = request.user
    bodega = user.id_bodega_id


    sucursal =  Sucursal.objects.get(id_sucursal=id_sucursal)
    despachos = Despacho.objects.select_related('rut__id_sucursal','id_producto__id_area__id_bodega','rut__rut__id_bodega').filter(Q(rut__id_sucursal=sucursal) & Q(id_producto__id_area__id_bodega=bodega))

    # Carga la plantilla HTML
    template_path = 'jefe_bodega/plantillaDesp_pdf.html'
    template = get_template(template_path)

    # Rellena la plantilla con los datos
    context = {'despachos': despachos}
    html = template.render(context)

    #Convierte la plantilla HTML a PDF
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    if not pisa_status.err:
        # Vuelve al comienzo del buffer para que el PDF se genere correctamente
        buffer.seek(0)
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="reporte.pdf"' 
        print(sucursal)
        return response

    else:
        return HttpResponse('Error al generar el PDF', status=500)

@login_required(login_url='/')
def reporte_desp(request):
    user = request.user
    rut = user.rut
    bodega = user.id_bodega_id

    #sucursales = Despacho.objects.select_related('rut__id_sucursal','id_producto__id_area__id_bodega').filter(id_producto__id_area__id_bodega=bodega)
    clientes = Cliente.objects.select_related('id_sucursal').filter(rut__id_bodega=bodega)

    sucursales = Sucursal.objects.filter(id_sucursal__in=[suc.id_sucursal_id for suc in clientes]).distinct()

    usu_colab = Colaborador.objects.filter(rut=rut).first()
    if usu_colab.id_tp_colab_id == 1 or usu_colab.id_tp_colab_id == 2:
        template_name = 'jefe_bodega/base_jefe.html'
    else:
        template_name = 'repartidor/baseRepar.html'
    
    contexto = {'sucursales':sucursales, 'template_name':template_name}
    return render(request, 'jefe_bodega/reportesDespacho.html',contexto)

@login_required(login_url='/')
def reportes_pdf(request):
    user = request.user
    rut = user.rut
    usu_colab = Colaborador.objects.filter(rut=rut).first()
    if usu_colab.id_tp_colab_id == 1 or usu_colab.id_tp_colab_id == 2:
        template_name = 'jefe_bodega/base_jefe.html'
    else:
        template_name = 'repartidor/baseRepar.html'
    return render(request, 'jefe_bodega/reporte_pdf.html', {'template_name':template_name})

@login_required(login_url='/')
def entregas(request):
    return render(request, 'repartidor/entregas.html')

@login_required(login_url='/')
def incioColab(request):
    user = request.user
    rut = user.rut
    usu_colab = Colaborador.objects.filter(rut=rut).first()

    if usu_colab.id_tp_colab_id == 1 or usu_colab.id_tp_colab_id == 2:
        template_name = 'jefe_bodega/base_jefe.html'
    else:
        template_name = 'repartidor/baseRepar.html'
    return render(request,'web/home_colab.html',{'template_name':template_name})