from django.db import models

from equipo.models import Equipo
from operador.models import Operador


# Create your models here.

class Registro(models.Model):
    fecha_hora = models.DateField()
    numero_tiket = models.TextField(max_length=20)
    idEquipo = models.ForeignKey(Equipo, on_delete=models.DO_NOTHING)
    idOperador = models.ForeignKey(Operador, on_delete=models.DO_NOTHING)
    Litros = models.IntegerField(default=0)
    costolitro = models.FloatField(default=0)
    kilometraje = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f""