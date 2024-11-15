from django.db import models

# Create your models here.
class Equipo(models.Model):
    placa = models.TextField(max_length=50, verbose_name="Placa")
    modelo = models.TextField(max_length=100, verbose_name="Modelo")
    marca = models.TextField(max_length=100, verbose_name="Marca")
    year = models.IntegerField(default=2023, verbose_name="Año")
    capacidad_tanque = models.IntegerField(default=10, verbose_name="Capacidad del taque")

    def __str__(self) -> str:
        return f"Placa:{self.placa} Modelo:{self.modelo} Marca:{self.marca} Año:{self.year} Tanque:{self.capacidad_tanque}"