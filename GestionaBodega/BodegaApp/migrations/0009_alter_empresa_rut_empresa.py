# Generated by Django 4.2.6 on 2023-11-15 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BodegaApp', '0008_alter_pago_fecha_pago'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresa',
            name='rut_empresa',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]
