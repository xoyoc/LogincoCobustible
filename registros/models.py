from django.db import models

from equipo.models import Equipo
from operador.models import Operador


# Create your models here.


class Registro(models.Model):
    fecha_hora = models.DateField(verbose_name="Fecha y hora")
    numero_tiket = models.TextField(max_length=20, verbose_name="Numero ticket")
    idEquipo = models.ForeignKey(Equipo, on_delete=models.DO_NOTHING)
    idOperador = models.ForeignKey(Operador, on_delete=models.DO_NOTHING)
    Litros = models.DecimalField(max_digits=4,decimal_places=2, verbose_name="Cantidad de litros")
    costolitro = models.DecimalField(max_digits=4,decimal_places=2, verbose_name="Costo por litro")
    kilometraje = models.IntegerField(default=0, verbose_name="Kilometraje de Vehiculo")
    photo_tiket = models.ImageField(upload_to="ticket", null=True, blank=True, verbose_name="Foto del ticket")

    def __str__(self) -> str:
        return f"{self.numero_tiket}"
