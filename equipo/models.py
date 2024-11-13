from django.db import models

# Create your models here.
class Equipo(models.Model):
    placa = models.TextField(max_length=50)
    modelo = models.TextField(max_length=100)
    marca = models.TextField(max_length=100)
    year = models.IntegerField(default=2023)
    capacidad_tanque = models.IntegerField(default=10)

    def __str__(self) -> str:
        return f"Placa:{self.placa} Modelo:{self.modelo} Marca:{self.marca} Año:{self.year} Tanque:{self.capacidad_tanque}"