from django.urls import path

from . import views

app_name = 'processos'

urlpatterns = [
    path('', views.ProcessoSeletivoListView.as_view(), name='list'),
    path('novo/', views.ProcessoSeletivoCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProcessoSeletivoDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.ProcessoSeletivoUpdateView.as_view(), name='update'),
    path('<int:pk>/publicar/', views.PublicarProcessoView.as_view(), name='publicar'),
    path('<int:pk>/suspender/', views.SuspenderProcessoView.as_view(), name='suspender'),
    path('<int:pk>/encerrar/', views.EncerrarProcessoView.as_view(), name='encerrar'),
]
