from django.contrib import admin

from registros.models import Registro

# Register your models here.

class RecordAdmin(admin.ModelAdmin):
    model=Registro

admin.site.register(Registro, RecordAdmin)