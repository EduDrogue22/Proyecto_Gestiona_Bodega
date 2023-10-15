from django.shortcuts import render, redirect


# Create your views here.

def login(request):
    return render(request, 'web/login.html')

def inicio(request):
    return render(request, 'web/home.html')

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
    return render(request,'Admin/adminProducto.html')

def admSucursal(request):
    return render(request,'Admin/adminSucursal.html')