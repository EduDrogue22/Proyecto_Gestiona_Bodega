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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('inicio/', inicio, name='home'),
    path('logout/', logout_view, name='logout'),
    path('crear_transaccion/', realizar_transaccion, name='crear_transaccion'),
    path('webpaycommit/', webpay_commit, name='webpay_commit'),
    path('webpayanulacion/', webpay_refund, name='webpay_refund'),
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
    path('registrarProducto/',registrarProducto,name='REGSPRO'),
    path('producto/',producto,name='PROD'),
    path('buscar_producto/',buscar_producto,name='BUSCPRO'),
    path('despacho/',despacho,name='DESPCHO'),
    path('despachar/',despachar,name='DESPA'),
    path('buscar_despacho/',buscar_despacho,name='BUSDESP'),
    path('plan/',plan,name='PLAN'),

    path('agregarPerfil/',agrePerfil,name='AGREPERFIL'),
    path('agregarEmpresa/',agreEmpresa,name='AGREEMPRESA'),
    path('agregarProducto/',agreProducto,name='AGREPRODUCTO'),
    path('agregarPlan/',agrePlan,name='AGREPLAN'),
    path('agregarSucursal/',agreSucursal,name='AGRESUCU'),
    path('agregarCliente/',agreCliente,name='AGRECLIENTE'),
    path('agregarBodega/',agreBodega,name='AGREBODEGA'),
    path('agregarAreaBodega/',agreAreaBodega,name='AGREAREABODEGA'),
    path('agregarEmpleado/',agreEmpleado,name='AGREEMP'),
    path('modificarPerfil/<int:id_tp_colab>/',modPerfil,name='MODPERFIL'),
    path('modificar_perfil/<int:id_tp_colab>/', modifPerfil, name='MODIFPERFIL'),
    path('modificarEmpresa/<str:rut_empresa>/',modEmpresa,name='MODEMPRESA'),
    path('modificar_empresa/<str:rut_empresa>/',modifEmpresa, name='MODIFEMPRESA'),
    path('modificarSucursal/<int:id_sucursal>/',modSucursal,name='MODSUCRUSAL'),
    path('modificar_Sucursal/<int:id_sucursal>/',modifSucursal,name='MODFSUCURSAL'),
    path('modificarBodega/<int:id_bodega>/',modBodega,name='MODBODEGA'),
    path('modificar_bodega/<int:id_bodega>/', modifBodega, name='MODFBODEGA'),
    path('modificarAreaBodega/<int:id_area>/',modAreaBodega,name='MODAREABODEGA'),
    path('modificar_areaBodega/<int:id_area>/',modifArea,name='MODFAREABODEGA'),
    path('modificarCliente/',modCliente,name='MODCLIENTE'),
    path('modificarEmpleado/',modEmpleado,name='MODEMP'),
    path('modificarProducto/',modProducto,name='MODPRODUCTO'),
    path('modificarPlan/<int:id_plan>/',modPlan,name='MODPLAN'),
    path('modificar_plan/<int:plan_id>/',modifPlan, name='MODIFPLAN'),
    path('entregas/',entregasRepa,name='ENTREGAREPA'),
    path('eliminar_perfil/<int:id_tp_colab>/', eliminarPerfil, name='eliminar_perfil'),
    path('eliminar_bodega/<int:id_bodega>/', eliminarBodega, name='eliminar_bodega'),
    path('eliminar_area/<int:id_area>/', eliminarArea, name='eliminar_area'),
    path('eliminar_plan/<int:id_plan>/', eliminarPlan, name='eliminar_plan'),
    path('eliminar_empresa/<str:rut_empresa>/', eliminarEmpresa, name='eliminar_empresa'),
    path('eliminar_sucursal/<int:id_sucursal>/', eliminarSucursal, name='eliminar_sucursal'),
    path('eliminar_colaborador/<str:rut>/', eliminarEmpleado, name='eliminar_colaborador'),
    path('eliminar_cliente/<str:rut>/', eliminarCliente, name='eliminar_cliente'),
    path('error/',errorMod,name='ERRORMOD'),
    path('imprimirHojaDespachoRepa/',imprimirRepa,name='IMPRIMIRREPA'),
    #Este path para las sucursales.
    path('ajax/cargar_sucursales/', cargar_sucursales, name='cargar_sucursales'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)