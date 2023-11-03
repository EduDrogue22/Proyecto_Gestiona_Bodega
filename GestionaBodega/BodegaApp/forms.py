from django import forms
from .models import Producto, Despacho

class ProductoForm(forms.ModelForm):
    foto_prod = forms.ImageField(required=False)
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'stock', 'foto_prod', 'id_area', 'rut']

class LoginForm(forms.Form):
    correo = forms.CharField()
    contrasena = forms.CharField()


