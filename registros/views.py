from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from registros.forms import RegisterForm
from registros.models import Registro

# Create your views here.

class RegisterListView(generic.ListView):
    model = Registro
    template_name="registros/list_register.html"
    context_object_name = 'registros'

class RegisterFormView(generic.CreateView):
    model = Registro
    fields = [
            'numero_tiket',
            'idEquipo', 
            'idOperador',
            'Litros',
            'Litros',
            'costolitro',
            'kilometraje',
            'photo_tiket'
            ]
    template_name="registros/add_register.html"
    success_url = reverse_lazy('registro_list')

"""     def form_valid(self, form):
        form.save()
        return super().form_valid(form) """