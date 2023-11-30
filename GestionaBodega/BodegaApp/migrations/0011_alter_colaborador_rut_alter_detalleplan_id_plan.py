# Generated by Django 4.2.6 on 2023-11-15 23:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BodegaApp', '0010_alter_cliente_rut'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colaborador',
            name='rut',
            field=models.OneToOneField(db_column='rut', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='detalleplan',
            name='id_plan',
            field=models.ForeignKey(db_column='id_plan', on_delete=django.db.models.deletion.CASCADE, to='BodegaApp.plan'),
        ),
    ]