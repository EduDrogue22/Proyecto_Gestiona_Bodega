from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, date
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db import DatabaseError
from django.contrib.auth import authenticate, login, logout
from .models import *

# Importacion libreria oracle
import cx_Oracle

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

        #form = EmailAuthenticationForm(request, request.POST)
        email = request.POST.get('username')
        password = request.POST.get('password')

        #autenticacion = authenticate(request, email = email, password = password)

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
    return render(request,'Admin/adminPerfile.html')

def admArea(request):
    return render(request,'Admin/adminArea.html')

def admBodega(request):
    return render(request,'Admin/adminBodega.html')

def admCliente(request):
    return render(request,'Admin/adminCliente.html')

def admColaborador(request):
    return render(request,'Admin/adminColaborador.html')

def admEmpresa(request):
    return render(request,'Admin/adminEmpresa.html')

def admPlan(request):
    return render(request,'Admin/adminPlan.html')

def admProducto(request):
    areas = AreaBodega.objects.all()
    clientes = Usuario.objects.all()
    context = {
        'areas': areas,
        'clientes': clientes,
    }
    print(request.POST)
    print(request.FILES)

    try:    
        if request.method == 'POST':
            nombre_producto = request.POST.get('nom_producto')
            stock = request.POST.get('stock')
            foto = request.FILES.get('imagen')
            id_area = request.POST.get('area')
            rut = request.POST.get('rut')
        

            if foto:
                fs = FileSystemStorage(location='static/media/')
                name = fs.save(foto.name, foto)
                url = fs.url(name)
            else:
                url = 'static/media/foto_pred.jpg'  # P.ej., '/media/defaults/default.jpg'

            dsn_str = cx_Oracle.makedsn(host="localhost", port="1521", sid="orcl")
            con = cx_Oracle.connect(user="bodegon", password="bodegon", dsn=dsn_str)
            cursor = con.cursor()
            cursor.callproc("SP_AGREGAR_PRODUCTO", [nombre_producto, stock, url, id_area, rut])
            cursor.close()
            con.close()
            

            return redirect('ADMPRODUCTO')
    except Exception as e:
            messages.error(request, f"Error al agregar producto: {e}")
    return render(request,'Admin/adminProducto.html', context)

def admSucursal(request):
    return render(request,'Admin/adminSucursal.html')

def agrePerfil(request):
    return render(request,'Admin/Agregar/agregarPerfil.html')

def agreProducto(request):
    return render(request,'Admin/Agregar/agregarProducto.html')

def agreEmpresa(request):
    return render(request,'Admin/Agregar/agregarEmpresa.html')

def agrePlan(request):
    return render(request,'Admin/Agregar/agregarPlan.html')

def agreSucursal(request):
    return render(request,'Admin/Agregar/agregarSucursal.html')

def agreCliente(request):
    return render(request,'Admin/Agregar/agregarCliente.html')

def agreBodega(request):
    return render(request,'Admin/Agregar/agregarBodega.html')

def agreAreaBodega(request):
    return render(request,'Admin/Agregar/agregarAreaBodega.html')

def agreEmpleado(request):
    return render(request,'Admin/Agregar/agregarEmpleado.html')

def modPerfil(request):
    return render(request,'Admin/Modificar/modificarPerfil.html')

def modEmpresa(request):
    return render(request,'Admin/Modificar/modificarEmpresa.html')

def modSucursal(request):
    return render(request,'Admin/Modificar/modificarSucursal.html')
