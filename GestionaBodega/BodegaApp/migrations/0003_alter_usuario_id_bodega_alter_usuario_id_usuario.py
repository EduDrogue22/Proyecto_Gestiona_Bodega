# Generated by Django 4.2.6 on 2023-11-11 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BodegaApp', '0002_alter_usuario_id_bodega_alter_usuario_id_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='id_bodega',
            field=models.ForeignKey(blank=True, db_column='id_bodega', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.bodega'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='id_usuario',
            field=models.ForeignKey(blank=True, db_column='id_usuario', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.tipousuario'),
        ),
    ]
