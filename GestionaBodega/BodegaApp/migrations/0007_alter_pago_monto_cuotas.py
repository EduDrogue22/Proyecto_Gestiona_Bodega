# Generated by Django 4.2.6 on 2023-11-13 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BodegaApp', '0006_alter_perfil_notificaciones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pago',
            name='monto_cuotas',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
