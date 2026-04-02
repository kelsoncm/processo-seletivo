from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from auditoria.models import EventoAuditoria
from inscricoes.models import Inscricao
from processos.models import Etapa

from .models import Avaliacao


class AvaliadorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_avaliador or request.user.is_coordenador or
                request.user.is_administrador or request.user.is_staff):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AvaliacaoListView(AvaliadorRequiredMixin, ListView):
    model = Avaliacao
    template_name = 'avaliacoes/avaliacao_list.html'
    context_object_name = 'avaliacoes'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_administrador or user.is_coordenador:
            return Avaliacao.objects.all()
        return Avaliacao.objects.filter(avaliador=user)


class AvaliacaoCreateView(AvaliadorRequiredMixin, CreateView):
    model = Avaliacao
    template_name = 'avaliacoes/avaliacao_form.html'
    fields = ['nota', 'parecer', 'aprovado', 'atende_requisitos',
              'observacoes_banca', 'observacoes_candidato', 'justificativa', 'anexo']

    def dispatch(self, request, *args, **kwargs):
        self.inscricao = get_object_or_404(Inscricao, pk=kwargs['inscricao_pk'])
        self.etapa = get_object_or_404(Etapa, pk=kwargs['etapa_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.inscricao = self.inscricao
        form.instance.etapa = self.etapa
        form.instance.avaliador = self.request.user
        response = super().form_valid(form)
        EventoAuditoria.registrar(
            tipo=EventoAuditoria.AVALIACAO,
            acao=f'Avaliação da inscrição {self.inscricao.numero} na etapa {self.etapa}',
            usuario=self.request.user,
            objeto=self.object,
            origem=self.request.META.get('REMOTE_ADDR', ''),
        )
        return response

    def get_success_url(self):
        return f'/avaliacoes/{self.object.pk}/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['inscricao'] = self.inscricao
        ctx['etapa'] = self.etapa
        # Show only current step data (RF23)
        ctx['documentos'] = self.inscricao.documentos.filter(
            tipo_documento__etapa=self.etapa, ativo=True
        )
        if hasattr(self.etapa, 'formulario'):
            ctx['formulario'] = self.etapa.formulario
            ctx['respostas'] = self.inscricao.respostas_formulario.filter(
                formulario=self.etapa.formulario
            ).first()
        return ctx


class AvaliacaoDetailView(AvaliadorRequiredMixin, DetailView):
    model = Avaliacao
    template_name = 'avaliacoes/avaliacao_detail.html'
    context_object_name = 'avaliacao'
