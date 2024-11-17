from django.urls import path

from operador.views import OperationFormView, OperationListView

def my_view(request):
    return "Prueba vista de operadores"

urlpatterns = [
    path('', OperationListView.as_view(), name="list_operation"),
    path("agregar/", OperationFormView.as_view(), name="add_operation"),
    path("listado/", my_view)
]