# Generated by Django 4.2.6 on 2023-10-27 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BodegaApp', '0002_producto_rut'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='contrasena',
            field=models.CharField(max_length=128),
        ),
    ]