from django.db import models

# Create your models here.
class Operador(models.Model):
    nombre = models.TextField(max_length=150)
    email = models.EmailField()
    movil = models.TextField(max_length=10)

    def __str__(self) -> str:
        return f"Nombre:{self.nombre} Email:{self.email} Celular:{self.movil}"
