from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, date
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db import DatabaseError
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from transbank.common.integration_type import IntegrationType
from transbank.webpay.webpay_plus.transaction import *
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db import DatabaseError
from .forms import *
from .models import *

# Importacion libreria oracle
import cx_Oracle

# HOST: https://webpay3gint.transbank.cl

# Create your views here.
def create_oracle_connection():
    dsn_str = cx_Oracle.makedsn(host="localhost", port="1521", sid="orcl")
    connection = cx_Oracle.connect(user="bodegon", password="bodegon", dsn = dsn_str)
    return connection

def login_view(request):
    error = False
    exito = False
    message = ""

    if request.method == 'POST':

        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            usu = Usuario.objects.get(correo = email, contrasena = password)

            request.session['rut'] = usu.pk
            exito = True
            message = "Bienvenido."
            return redirect('home')
            
        except Usuario.DoesNotExist:
            use = authenticate(request, username = email, password = password)
            if use is not None:
                login(request, use)
                exito = True
                message = "Bienvenido."
                return redirect('home')
            else:
                error = True
                message = "Usuario o Contraseña no válidos."
    return render(request, 'web/login.html', {'error': error, 'exito': exito, 'message': message})

def inicio(request):
    return render(request, 'web/home.html')

#Prueba integración
def realizar_transaccion(request):
    # Definir los datos de la transacción (reemplaza estos valores con los tuyos)
    buy_order = "Orden123"
    session_id = "Session123"
    amount = 10000  # Reemplaza con el monto correcto
    return_url = "http://127.0.0.1:8000/webpaysuccess/"

    if request.method == 'POST':
        #comercio = settings.COMERCIO_CODE
        #api = settings.API_KEY

        tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))

        resp = tx.create(buy_order, session_id, amount, return_url)

        url = resp["url"]
        token = resp["token"]

        print(resp)

        if token is not None:
            return redirect(url)
        else:
            return render(request, 'webpay/error.html', {'message': 'Error en la creación la transacción'})
    return render(request, 'webpay/crear_transaccion.html', {'buy_order': buy_order, 'session_id': session_id, 'amount': amount})

def webpay_success(request):
    # Obtiene el token de la respuesta de Transbank (debe extraerse de la respuesta de Transbank)
    token_ws = request.POST.get("token_ws")

    return render(request, 'webpay/success.html', {'token_ws': token_ws})

def logout_view(request):
    logout(request)
    return redirect('/')

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
            rut = request.POST.get('numRut')
            correo = request.POST.get('txtCorreo').strip()
            nacimiento = datetime.strptime(request.POST.get('dateFechaNacimiento'), '%Y-%m-%d').date()
            id_sucursal = request.POST.get('sucursal')
            contrasena = request.POST.get('txtContrasena').strip()
            rept_contrasena = request.POST.get('txtReptContrasena').strip()
            direccion = request.POST.get('txtDireccion').strip()
            id_bodega = 1
            id_usuario = 1

            hoy = date.today()

            edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))

            if contrasena != rept_contrasena:
                error = True
                message = "La contraseñas no coinciden."
            
            elif len(rut) < 9:
                error = True
                message = "El rut es corto."
            
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
                contrasena_encriptada = make_password(contrasena)

                oracle_connection = create_oracle_connection()

                with oracle_connection.cursor() as cursor:
                    cursor.callproc("sp_agregar_usuario_cliente", (rut, primer_nombre, segundo_nombre, apellido_paterno, apellido_materno, correo, contrasena_encriptada, direccion, nacimiento, id_sucursal, id_bodega, id_usuario))

                oracle_connection.commit()
                exito = True
                message = "Usuario registrado con éxito, favor de esperar para comprobar sus datos."
    except DatabaseError as e:
        error = True
        message = "Error al agregar usuario."
    return render(request, 'web/registrarse.html', {'empresas': empresa, 'sucursales': sucursal, 'error': error, 'exito': exito, 'message': message})


def cargar_sucursales(request):
    empresa_rut = request.GET.get('empresa_rut')
    sucursales = Sucursal.objects.filter(rut_empresa=empresa_rut).values('id_sucursal', 'nombre_sucursal')
    sucursal_data = list(sucursales)
    return JsonResponse(sucursal_data, safe=False)

def menuAdm(request):
    return render(request,'Admin/menuAdmin.html')

def admPerfiles(request):
    perfiles = TipoColaborador.objects.all()
    contexto = {"perfiles": perfiles}
    return render(request,'Admin/adminPerfile.html', contexto)

def admArea(request):
    areas = AreaBodega.objects.all()
    contexto = {"areas": areas}
    return render(request,'Admin/adminArea.html', contexto)

def admBodega(request):
    bodegas = Bodega.objects.all()
    contexto = {"bodegas": bodegas}
    return render(request,'Admin/adminBodega.html', contexto)

def admCliente(request):
    return render(request,'Admin/adminCliente.html')

def admColaborador(request):
    return render(request,'Admin/adminColaborador.html')

def admEmpresa(request):
    empresas = Empresa.objects.all()
    contexto = {"empresas": empresas}
    return render(request,'Admin/adminEmpresa.html', contexto)

def admPlan(request):
    planes = Plan.objects.all()
    contexto = {"planes": planes}
    return render(request,'Admin/adminPlan.html', contexto)

def admProducto(request):
    """rut = request.session['rut']"""
    productos = Producto.objects.all()
    contexto = {'productos': productos}
    return render(request,'Admin/adminProducto.html', contexto)

def admSucursal(request):
    sucursales = Sucursal.objects.all()
    contexto = {"sucursales": sucursales}
    return render(request,'Admin/adminSucursal.html', contexto)

def plan(request):
    planes = DetallePlan.objects.select_related('id_plan','id_bodega').all()
    context = {'planes':planes}
    return render(request,'web/plan.html',context)

def despacho(request):
    despachos = Despacho.objects.select_related('rut__id_sucursal','id_producto__id_area__id_bodega').all()
    context = {'despachos': despachos}
    return render(request,'web/despacho.html',context)

def producto(request):
    """rut = request.session['rut']"""
    productos = Producto.objects.all()
    contexto = {'productos': productos}
    return render(request, 'web/producto.html', contexto)

def registrarProducto(request):
    errorAgregar = False
    prodCreado = False
    error_message = ""
    agregado_message = ""
 
    # Cracion producto
    form = ProductoForm()

    if request.method == 'POST':

        form = ProductoForm(request.POST, request.FILES)
        nombre_producto = request.POST.get("nombre_producto")
        rut_cliente = request.POST.get("rut")

        producto_existente = Producto.objects.filter(Q(nombre_producto=nombre_producto) & Q(rut=rut_cliente))
    
        if producto_existente:
            errorAgregar = True
            error_message = "El producto ya existe para este usuario." 
        
        elif form.is_valid():
            producto = form.save(commit=False)
            if not producto.foto_prod:
                producto.foto_prod = 'producto/foto_pred.jpg'
            producto.save()
            prodCreado = True
            agregado_message = 'Producto agregado correctamente'

            
        else:
            form = ProductoForm()


    areas = AreaBodega.objects.all()
    clientes = Cliente.objects.all()
     
    context = {
        'areas': areas,
        'clientes': clientes,
        'form': form, 
        'errorAgregar': errorAgregar, 
        'error_message': error_message,
        'prodCreado': prodCreado,
        'agregado_message': agregado_message,
    }

    return render(request, 'web/registrarProducto.html', context)

def buscar_producto(request):
    productos = Producto.objects.all()
    if request.method == 'GET' and 'txtNombreProd' in request.GET:
        nombre_producto = request.GET.get("txtNombreProd")
        productos = Producto.objects.filter(nombre_producto__icontains=nombre_producto)
    contexto = {"productos":productos}
    return render(request,"web/producto.html",contexto)

def despachar(request):
    if request.method == "POST":
        id_producto = request.POST['id_prod']
        rut_cliente = request.POST['rut_cli']

        producto = Producto.objects.get(id_producto=id_producto)
        cliente = Cliente.objects.get(rut=rut_cliente)

        estado = 'S'
        tiempo_entrega = 60  

        despacho = Despacho(estado=estado, tiempo_entrega=tiempo_entrega, id_producto=producto, rut=cliente)
        despacho.save()
        return redirect('DESPCHO')

def buscar_despacho(request):
    despachos = Despacho.objects.select_related('rut__id_sucursal','id_producto__id_area__id_bodega').all()
    if request.method == 'GET' and 'txtNombreProd' in request.GET:
        nombre_producto = request.GET.get("txtNombreProd")
        despachos = Despacho.objects.filter(id_producto__nombre_producto__icontains=nombre_producto).select_related('rut__id_sucursal', 'id_producto__id_area__id_bodega')
    contexto = {"despachos":despachos}
    return render(request,"web/despacho.html",contexto)

def cargar_sucursales(request):
    empresa_rut = request.GET.get('empresa_rut')
    sucursales = Sucursal.objects.filter(rut_empresa=empresa_rut).values('id_sucursal', 'nombre_sucursal')
    sucursal_data = list(sucursales)
    return JsonResponse(sucursal_data, safe=False)

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

    return render(request,'Admin/Agregar/agregarPerfil.html')

def eliminarPerfil(request, id_tp_colab):
    try:
        perfilDelete = TipoColaborador.objects.get(id_tp_colab=id_tp_colab)
        perfilDelete.delete()
        messages.success(request, 'Perfil eliminado exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar el perfil.')

    return redirect('ADMPERFILES')


def agreProducto(request):
    errorAgregar = False
    prodCreado = False
    error_message = ""
    agregado_message = ""
 
    # Cracion producto
    form = ProductoForm()

    if request.method == 'POST':

        form = ProductoForm(request.POST, request.FILES)
        nombre_producto = request.POST.get("nombre_producto")
        rut_cliente = request.POST.get("rut")

        producto_existente = Producto.objects.filter(Q(nombre_producto=nombre_producto) & Q(rut=rut_cliente))
    
        if producto_existente:
            errorAgregar = True
            error_message = "El producto ya existe para este usuario." 
        
        elif form.is_valid():
            producto = form.save(commit=False)
            if not producto.foto_prod:
                producto.foto_prod = 'producto/foto_pred.jpg'
            producto.save()
            prodCreado = True
            agregado_message = 'Producto agregado correctamente'

            
        else:
            error_message = "A ocurrido un error"
            errorAgregar = False
            form = ProductoForm()


    areas = AreaBodega.objects.all()
    clientes = Cliente.objects.all()
    bodegas = Bodega.objects.all()
     
    context = {
        'areas': areas,
        'clientes': clientes,
        'form': form, 
        'errorAgregar': errorAgregar, 
        'error_message': error_message,
        'prodCreado': prodCreado,
        'agregado_message': agregado_message,
        'bodegas': bodegas,
    }

    return render(request,'Admin/Agregar/agregarProducto.html', context)

def agreEmpresa(request):
    regis = Empresa.objects.all()
    contexto = {"categorias": regis}

    if request.POST:
        rut_empresa = request.POST.get("rut_emp")
        nombre_empresa = request.POST.get("nombre_empresa")
        descripcion = request.POST.get("descrip_emp")

        try:
            empresa = Empresa(rut_empresa=rut_empresa,nombre_empresa=nombre_empresa,descripcion=descripcion)
            empresa.save()
            return redirect('ADMEMPRESA') 
        except IntegrityError as e:
            # Si se produce una excepción de IntegrityError, puedes manejarla aquí
            contexto["mensaje"] = "Error al guardar."

    return render(request,'Admin/Agregar/agregarEmpresa.html')

def eliminarEmpresa(request, rut_empresa):
    try:
        empresaDelete = Empresa.objects.get(rut_empresa=rut_empresa)
        empresaDelete.delete()
        messages.success(request, 'Empresa eliminada exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar esta empresa.')

    return redirect('ADMEMPRESA')


def agrePlan(request):
    regis = Plan.objects.all()
    contexto = {"categorias": regis}

    if request.POST:
        nombre_plan = request.POST.get("nombre_plan")
        valor_plan = request.POST.get("costo")
        cant_anaquel_plan = request.POST.get("cant_anaqueles")
        capacidad_anaquel = request.POST.get("capacidad")

        try:
            plan = Plan(nombre_plan=nombre_plan, valor_plan=valor_plan,
                        cant_anaquel_plan=cant_anaquel_plan, capacidad_anaquel=capacidad_anaquel)
            plan.save()
            return redirect('ADMPLAN')
        except IntegrityError as e:
            # Si se produce una excepción de IntegrityError, puedes manejarla aquí
            contexto["mensaje"] = "Error al guardar."

    return render(request,'Admin/Agregar/agregarPlan.html')

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

def eliminarPlan(request, id_plan):
    try:
        planDelete = Plan.objects.get(id_plan=id_plan)
        planDelete.delete()
        messages.success(request, 'Plan eliminado exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar el plan seleccionado.')

    return redirect('ADMPLAN')

def agreSucursal(request):
    regis = Sucursal.objects.all()
    empresas = Empresa.objects.all()
    contexto = {'sucursales': regis, 'empresas': empresas}

    if request.POST:
        nombre_sucursal = request.POST.get("nombre_sus")
        direccion = request.POST.get("direccion_sus")
        rut_empresa = request.POST.get("selectEmpresa")

        if rut_empresa:
            try:
                empresa = Empresa.objects.get(rut_empresa=rut_empresa)
                sucursal = Sucursal(
                    nombre_sucursal=nombre_sucursal, direccion=direccion, rut_empresa=empresa)
                sucursal.save()
                return redirect('ADMSUCRUSAL')
            except IntegrityError as e:
                # Si se produce una excepción de IntegrityError, puedes manejarla aquí
                contexto["mensaje"] = "Error al guardar."
        else:
            contexto["mensaje"] = "Por favor, selecciona una empresa antes de registrar la sucursal."

    return render(request,'Admin/Agregar/agregarSucursal.html')

def eliminarSucursal(request, id_sucursal):
    try:
        sucursalDelete = Sucursal.objects.get(id_sucursal=id_sucursal)
        sucursalDelete.delete()
        messages.success(request, 'Sucursal eliminada exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar la sucursal seleccionada.')

    return redirect('ADMSUCRUSAL')

def agreCliente(request):
    return render(request,'Admin/Agregar/agregarCliente.html')

def agreBodega(request):
    regis = Bodega.objects.all()
    tipoBodegas = TipoBodega.objects.all()
    contexto = {'bodega': regis, 'tipoBodega': tipoBodegas}

    if request.POST:
        nombre_bodega = request.POST.get("nombre_bod")
        direccion = request.POST.get("direccion_bod")
        id_tp_bodega = request.POST.get("selectTpBodega")

        if id_tp_bodega:
            try:
                tipoBodega = TipoBodega.objects.get(id_tp_bodega=id_tp_bodega)
                bodega = Bodega(nombre_bodega=nombre_bodega,
                                direccion=direccion, id_tp_bodega=tipoBodega)
                bodega.save()
                return redirect('ADMBODEGA')
            except IntegrityError as e:
                # Si se produce una excepción de IntegrityError, puedes manejarla aquí
                contexto["mensaje"] = "Error al guardar."
        else:
            contexto["mensaje"] = "Por favor, selecciona un tipo de bodega antes de registrar."

    return render(request,'Admin/Agregar/agregarBodega.html')

def eliminarBodega(request, id_bodega):
    try:
        bodegaDelete = Bodega.objects.get(id_bodega=id_bodega)
        bodegaDelete.delete()
        messages.success(request, 'Bodega eliminado exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar la bodega.')

    return redirect('ADMBODEGA')

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
            try:
                bodega = Bodega.objects.get(id_bodega=id_bodega)
                areaBodega = AreaBodega(
                    sector=sector, cant_anaq_area=cant_anaq_area, disponible=disponible, id_bodega=bodega)
                areaBodega.save()
                return redirect('ADMAREA')
            except IntegrityError as e:
                # Si se produce una excepción de IntegrityError, puedes manejarla aquí
                contexto["mensaje"] = "Error al guardar."

        else:
            contexto["mensaje"] = "Por favor, selecciona una bodega antes de registrar."

    return render(request,'Admin/Agregar/agregarAreaBodega.html')

def eliminarArea(request, id_area):
    try:
        bodegaDelete = AreaBodega.objects.get(id_area=id_area)
        bodegaDelete.delete()
        messages.success(request, 'Área bodega eliminada exitosamente')
    except ObjectDoesNotExist:
        messages.error(request, 'No se puede eliminar área bodega.')

    return redirect('ADMAREA')

def agreEmpleado(request):
    return render(request,'Admin/Agregar/agregarEmpleado.html')

def modPerfil(request):
    modPerfil = TipoColaborador.objects.get(id_tp_colab=id_tp_colab)
    contexto = {"perfiles": modPerfil}

    return render(request,'Admin/Modificar/modificarPerfil.html', contexto)

def modEmpresa(request):
    return render(request,'Admin/Modificar/modificarEmpresa.html')

def modBodega(request):
    return render(request,'Admin/Modificar/modificarBodega.html')

def modAreaBodega(request):
    return render(request,'Admin/Modificar/modificarAreaBodega.html')

def modCliente(request):
    return render(request,'Admin/Modificar/modificarCliente.html')

def modEmpleado(request):
    return render(request,'Admin/Modificar/modificarEmpleado.html')

def modSucursal(request):
    return render(request,'Admin/Modificar/modificarSucursal.html')

def modPlan(request, id_plan):
    modPlan = Plan.objects.get(id_plan=id_plan)
    contexto = {"planes": modPlan}
    return render(request, "Admin/Modificar/modificarPlan.html", contexto)

def modProducto(request):
    return render(request,'Admin/Modificar/modificarProducto.html')

def entregasRepa(request):
    return render(request,'repartidor/entregas.html')

def imprimirRepa(request):
    return render(request,'repartidor/imprimir.html')

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