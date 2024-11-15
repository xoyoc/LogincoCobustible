from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import render


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

def my_test_view(request):
    return HttpResponse("Prueba vista de equipo")

def my_view_detalle(request, *args, **kwargs):
    print(args)
    print(kwargs)
    return HttpResponse("Prueba vista de equipo detallado")
