from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.http import JsonResponse
from datetime import date
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db import DatabaseError
from .models import *
import time

# Importacion libreria oracle
import cx_Oracle

# Create your views here.
def create_oracle_connection():
    dsn_str = cx_Oracle.makedsn(host="localhost", port="1521", sid="orcl")
    connection = cx_Oracle.connect(user="bodegon", password="bodegon", dsn = dsn_str)
    return connection

def login(request):
    return render(request, 'web/login.html')

def inicio(request):
    return render(request, 'web/home.html')

def registrarse(request):
    empresa = Empresa.objects.all()
    sucursal = Sucursal.objects.all()
    error = False
    exito = False
    exito_message = ""
    error_message = ""

    try:
        if request.method == 'POST':
            primer_nombre = request.POST.get('txtPrimerNombre')
            segundo_nombre = request.POST.get('txtSegundoNombre')
            apellido_paterno = request.POST.get('txtApellidoPaterno')
            apellido_materno = request.POST.get('txtApellidoMaterno')
            rut = request.POST.get('numRut')
            correo = request.POST.get('txtCorreo')
            nacimiento = request.POST.get('dateFechaNacimiento')
            id_sucursal = request.POST.get('sucursal')
            contrasena = request.POST.get('txtContrasena')
            rept_contrasena = request.POST.get('txtReptContrasena')
            direccion = request.POST.get('txtDireccion')
            id_bodega = 1
            id_usuario = 1

            if contrasena != rept_contrasena:
                error = True
                error_message = "La contraseñas no coinciden."
            
            if len(rut) < 9:
                error = True
                error_message = "El rut es corto."
            
            else:
                            
                contrasena_encriptada = make_password(contrasena)

                oracle_connection = create_oracle_connection()

                with oracle_connection.cursor() as cursor:
                    cursor.callproc("sp_agregar_usuario_cliente", (rut, primer_nombre, segundo_nombre, apellido_paterno, apellido_materno, correo, contrasena_encriptada, direccion, nacimiento, id_sucursal, id_bodega, id_usuario))

                oracle_connection.commit()
                exito = True
                exito_message = "Usuario registrado con éxito, favor de esperar para comprobar sus datos."
    except DatabaseError as e:
        error = True
        error_message = "Error al agregar usuario."
    return render(request, 'web/registrarse.html', {'empresas': empresa, 'sucursales': sucursal, 'error': error, 'error_mensaje': error_message, 'exito': exito, 'exito_message': exito_message})


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
