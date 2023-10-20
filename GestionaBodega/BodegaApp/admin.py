from django.contrib import admin
from .models import *

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id_producto", "nombre_producto", "stock", "foto_prod", 'id_area', "rut")
    list_filter = ("stock",)

admin.site.register(Producto, ProductoAdmin)