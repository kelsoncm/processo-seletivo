from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from auditoria.models import EventoAuditoria
from processos.models import Etapa, Fase, ProcessoSeletivo

from .models import ResultadoEtapa, ResultadoFinal


class ResultadoPublicoView(ListView):
    """Visão pública de resultados parciais — exibe apenas número de inscrição (RF26)."""

    template_name = 'resultados/resultado_publico.html'
    context_object_name = 'resultados'

    def get_queryset(self):
        self.etapa = get_object_or_404(Etapa, pk=self.kwargs['etapa_pk'])
        return ResultadoEtapa.objects.filter(
            etapa=self.etapa,
            publicado=True,
            habilitado=True,
        ).order_by('-nota_final').only('inscricao__numero', 'nota_final', 'habilitado')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['etapa'] = self.etapa
        return ctx


class ResultadoCandidatoView(LoginRequiredMixin, ListView):
    """Visão do candidato autenticado: notas detalhadas e justificativas (RF27)."""

    template_name = 'resultados/resultado_candidato.html'
    context_object_name = 'resultados'

    def get_queryset(self):
        return ResultadoEtapa.objects.filter(
            inscricao__candidato=self.request.user,
            publicado=True,
        ).select_related('etapa', 'inscricao').order_by('etapa__fase__ordem', 'etapa__ordem')


class PublicarResultadoEtapaView(LoginRequiredMixin, View):
    def post(self, request, etapa_pk):
        if not (request.user.is_staff or request.user.is_administrador or request.user.is_coordenador):
            raise PermissionDenied
        etapa = get_object_or_404(Etapa, pk=etapa_pk)
        ResultadoEtapa.objects.filter(etapa=etapa, publicado=False).update(
            publicado=True,
            data_publicacao=timezone.now(),
        )
        EventoAuditoria.registrar(
            tipo=EventoAuditoria.PUBLICACAO,
            acao=f'Publicação dos resultados da etapa {etapa}',
            usuario=request.user,
            objeto=etapa,
            origem=request.META.get('REMOTE_ADDR', ''),
        )
        return redirect(f'/processos/{etapa.fase.processo_seletivo_id}/')


class ResultadoFinalPublicoView(ListView):
    """Visão pública do resultado final do processo seletivo."""

    template_name = 'resultados/resultado_final.html'
    context_object_name = 'resultados'

    def get_queryset(self):
        self.processo = get_object_or_404(ProcessoSeletivo, pk=self.kwargs['processo_pk'])
        return ResultadoFinal.objects.filter(
            processo_seletivo=self.processo,
            publicado=True,
        ).order_by('classificacao')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['processo'] = self.processo
        return ctx
