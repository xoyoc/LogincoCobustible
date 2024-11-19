from django.contrib import admin

from operador.models import Operador

# Register your models here.

class OperationAdmin(admin.ModelAdmin):
    model = Operador
    list_display = ['nombre', 'email','movil']
    search_fields = ['nombre', 'email']

admin.site.register(Operador, OperationAdmin)
