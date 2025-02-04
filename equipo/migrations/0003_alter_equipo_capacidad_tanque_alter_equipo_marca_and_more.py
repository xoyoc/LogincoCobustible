# Generated by Django 5.1.2 on 2024-11-15 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipo', '0002_alter_equipo_capacidad_tanque_alter_equipo_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipo',
            name='capacidad_tanque',
            field=models.IntegerField(default=10, verbose_name='Capacidad del taque'),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='marca',
            field=models.TextField(max_length=100, verbose_name='Marca'),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='modelo',
            field=models.TextField(max_length=100, verbose_name='Modelo'),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='placa',
            field=models.TextField(max_length=50, verbose_name='Placa'),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='year',
            field=models.IntegerField(default=2023, verbose_name='Año'),
        ),
    ]
