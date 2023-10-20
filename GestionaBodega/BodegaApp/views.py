from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import *

# Importacion libreria oracle
import cx_Oracle

# Create your views here.

def login(request):
    return render(request, 'web/login.html')

def inicio(request):
    return render(request, 'web/home.html')

def registrarse(request):
    return render(request, 'web/registrarse.html')

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
    return render(request,'Admin/adminProducto.html', context)

def agregar_producto(request):
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

    return render(request, 'Admin/adminProducto.html') 

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
