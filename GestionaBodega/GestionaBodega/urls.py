"""
URL configuration for GestionaBodega project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from BodegaApp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login, name='login'),
    path('inicio/', inicio, name='home'),
    path('registrarse/', registrarse, name='registrarse'),
    path('menuAdmin/',menuAdm,name='MENUADMIN'),
    path('adminPerfiles/',admPerfiles,name='ADMPERFILES'),
    path('adminArea/',admArea,name='ADMAREA'),
    path('adminBodega/',admBodega,name='ADMBODEGA'),
    path('adminCliente/',admCliente,name='ADMCLIENTE'),
    path('adminColaborador/',admColaborador,name='ADMCOLABORADOR'),
    path('adminEmpresa/',admEmpresa,name='ADMEMPRESA'),
    path('adminPlan/',admPlan,name='ADMPLAN'),
    path('adminProducto/',admProducto,name='ADMPRODUCTO'),
    path('adminSucursal/',admSucursal,name='ADMSUCRUSAL'),
    path('agregarPerfil/',agrePerfil,name='AGREPERFIL'),
    path('agregarEmpresa/',agreEmpresa,name='AGREEMPRESA'),
    path('agregarProducto/',agreProducto,name='AGREPRODUCTO'),
    path('agregarPlan/',agrePlan,name='AGREPLAN'),
    path('agregarSucursal/',agreSucursal,name='AGRESUCU'),
    path('agregarCliente/',agreCliente,name='AGRECLIENTE'),
    path('agregarBodega/',agreBodega,name='AGREBODEGA'),
    path('agregarAreaBodega/',agreAreaBodega,name='AGREAREABODEGA'),
    path('agregarEmpleado/',agreEmpleado,name='AGREEMP'),
    path('modificarPerfil/',modPerfil,name='MODPERFIL'),
    path('modificarEmpresa/',modEmpresa,name='MODEMPRESA'),
    path('modificarSucursal/',modSucursal,name='MODSUCRUSAL'),
    path('agregar_producto/',agregar_producto,name='AGRPROD'),
]