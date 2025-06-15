from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from registros.models import Registro

# Create your views here.

class RegisterListView(generic.ListView):
    model = Registro
    template_name = "registros/list_register.html"
    ordering = '-fecha_hora'
    context_object_name = 'registros'

class RegisterDetailView(generic.DetailView):
    model = Registro
    template_name = 'registros/detail_register.html'

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

class RegisterDeleteView(generic.DeleteView):
    model = Registro
    success_url = reverse_lazy('registro_list')
