from django.urls import path

from . import views

app_name = 'resultados'

urlpatterns = [
    path('etapa/<int:etapa_pk>/publico/', views.ResultadoPublicoView.as_view(), name='publico'),
    path('etapa/<int:etapa_pk>/publicar/', views.PublicarResultadoEtapaView.as_view(), name='publicar'),
    path('meus/', views.ResultadoCandidatoView.as_view(), name='meus'),
    path('processo/<int:processo_pk>/final/', views.ResultadoFinalPublicoView.as_view(), name='final'),
]
