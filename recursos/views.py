from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from auditoria.models import EventoAuditoria
from inscricoes.models import Inscricao
from processos.models import Etapa

from .models import Recurso, RespostaRecurso


class RecursoCreateView(LoginRequiredMixin, CreateView):
    model = Recurso
    template_name = 'recursos/recurso_form.html'
    fields = ['texto']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.inscricao = get_object_or_404(Inscricao, pk=kwargs['inscricao_pk'])
        self.etapa = get_object_or_404(Etapa, pk=kwargs['etapa_pk'])
        if self.inscricao.candidato != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.inscricao = self.inscricao
        form.instance.etapa = self.etapa
        response = super().form_valid(form)
        EventoAuditoria.registrar(
            tipo=EventoAuditoria.RECURSO,
            acao=f'Recurso da inscrição {self.inscricao.numero} na etapa {self.etapa}',
            usuario=self.request.user,
            objeto=self.object,
            origem=self.request.META.get('REMOTE_ADDR', ''),
        )
        return response

    def get_success_url(self):
        return reverse('recursos:detail', kwargs={'pk': self.object.pk})


class RecursoDetailView(LoginRequiredMixin, DetailView):
    model = Recurso
    template_name = 'recursos/recurso_detail.html'
    context_object_name = 'recurso'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if obj.inscricao.candidato != user and not (
            user.is_staff or user.is_administrador or user.is_coordenador
        ):
            raise PermissionDenied
        return obj


class RespostaRecursoCreateView(LoginRequiredMixin, CreateView):
    model = RespostaRecurso
    template_name = 'recursos/resposta_form.html'
    fields = ['texto']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_staff or request.user.is_administrador or request.user.is_coordenador):
            raise PermissionDenied
        self.recurso = get_object_or_404(Recurso, pk=kwargs['recurso_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.recurso = self.recurso
        form.instance.respondido_por = self.request.user
        self.recurso.status = Recurso.DEFERIDO if self.request.POST.get('deferido') else Recurso.INDEFERIDO
        self.recurso.save()
        response = super().form_valid(form)
        EventoAuditoria.registrar(
            tipo=EventoAuditoria.RESPOSTA_RECURSO,
            acao=f'Resposta ao recurso {self.recurso.pk}',
            usuario=self.request.user,
            objeto=self.object,
            origem=self.request.META.get('REMOTE_ADDR', ''),
        )
        return response

    def get_success_url(self):
        return reverse('recursos:detail', kwargs={'pk': self.recurso.pk})
