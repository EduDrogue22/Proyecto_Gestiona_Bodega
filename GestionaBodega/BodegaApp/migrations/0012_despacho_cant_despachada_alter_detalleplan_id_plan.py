# Generated by Django 4.2.6 on 2023-12-11 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BodegaApp', '0011_alter_colaborador_rut_alter_detalleplan_id_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='despacho',
            name='cant_despachada',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='detalleplan',
            name='id_plan',
            field=models.ForeignKey(blank=True, db_column='id_plan', null=True, on_delete=django.db.models.deletion.SET_NULL, to='BodegaApp.plan'),
        ),
    ]
