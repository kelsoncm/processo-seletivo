from django.urls import path

from . import views

app_name = 'recursos'

urlpatterns = [
    path('inscricao/<int:inscricao_pk>/etapa/<int:etapa_pk>/recurso/',
         views.RecursoCreateView.as_view(), name='create'),
    path('<int:pk>/', views.RecursoDetailView.as_view(), name='detail'),
    path('<int:recurso_pk>/responder/', views.RespostaRecursoCreateView.as_view(), name='responder'),
]
