from django.db import models

# Create your models here.
class Operador(models.Model):
    nombre = models.TextField(max_length=150)
    email = models.EmailField()
    movil = models.TextField(max_length=10)
