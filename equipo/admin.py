from django.contrib import admin

from equipo.models import Equipo

# Register your models here.

class TeamAdmin(admin.ModelAdmin):
    model = Equipo
    list_display = [
        'placa',
        'modelo',
        'marca',
        'year',
        'capacidad_tanque'
    ]

admin.site.register(Equipo, TeamAdmin)
    