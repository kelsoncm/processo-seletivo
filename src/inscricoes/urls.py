from django.urls import path

from . import views

app_name = 'inscricoes'

urlpatterns = [
    path('', views.InscricaoListView.as_view(), name='list'),
    path('processo/<int:processo_pk>/nova/', views.InscricaoCreateView.as_view(), name='create'),
    path('<int:pk>/', views.InscricaoDetailView.as_view(), name='detail'),
    path('<int:pk>/cancelar/', views.CancelarInscricaoView.as_view(), name='cancelar'),
]
