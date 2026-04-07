from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/login/', RedirectView.as_view(url='/accounts/logout/', permanent=False)),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('processos/', include('processos.urls', namespace='processos')),
    path('inscricoes/', include('inscricoes.urls', namespace='inscricoes')),
    path('avaliacoes/', include('avaliacoes.urls', namespace='avaliacoes')),
    path('recursos/', include('recursos.urls', namespace='recursos')),
    path('resultados/', include('resultados.urls', namespace='resultados')),
    path('', RedirectView.as_view(url='/processos/', permanent=False), name='home'),
]
