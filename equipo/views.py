from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views import generic
from django.http import HttpResponse
from django.shortcuts import render

from equipo.forms import TeamForm


# Create your views here.
def my_view(request):
    team_list = [
        {},
        {}
    ]
    context ={
        "team_list": team_list
    }
    return render(request, "equipo/team_list.html", context)

class TeamListView(TemplateView):
    template_name = "equipo/team_list.html"

    def get_context_data(self):
        team_list = [
            {},
            {}
        ]
        return {
            "team_list": team_list
        }

class TeamFormView(generic.FormView):
    template_name = "equipo/add_equipo.html"
    form_class = TeamForm
    success_url = reverse_lazy('add_team')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    

def my_test_view(request):
    return HttpResponse("Prueba vista de equipo")

def my_view_detalle(request, *args, **kwargs):
    print(args)
    print(kwargs)
    return HttpResponse("Prueba vista de equipo detallado")
