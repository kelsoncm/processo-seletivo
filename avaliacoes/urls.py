from django.urls import path

from . import views

app_name = 'avaliacoes'

urlpatterns = [
    path('', views.AvaliacaoListView.as_view(), name='list'),
    path('inscricao/<int:inscricao_pk>/etapa/<int:etapa_pk>/avaliar/',
         views.AvaliacaoCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AvaliacaoDetailView.as_view(), name='detail'),
]
