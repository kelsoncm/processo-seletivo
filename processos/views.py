from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from auditoria.models import EventoAuditoria

from .models import Etapa, Fase, ProcessoSeletivo


class CoordenadorRequiredMixin(LoginRequiredMixin):
    """Mixin que restringe acesso a coordenadores ou administradores."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_coordenador or request.user.is_administrador or request.user.is_staff):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ProcessoSeletivoListView(LoginRequiredMixin, ListView):
    model = ProcessoSeletivo
    template_name = 'processos/processo_list.html'
    context_object_name = 'processos'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_administrador:
            return ProcessoSeletivo.objects.all()
        if user.is_coordenador:
            return ProcessoSeletivo.objects.filter(coordenador=user)
        return ProcessoSeletivo.objects.filter(status=ProcessoSeletivo.PUBLICADO)


class ProcessoSeletivoDetailView(LoginRequiredMixin, DetailView):
    model = ProcessoSeletivo
    template_name = 'processos/processo_detail.html'
    context_object_name = 'processo'


class ProcessoSeletivoCreateView(CoordenadorRequiredMixin, CreateView):
    model = ProcessoSeletivo
    template_name = 'processos/processo_form.html'
    fields = ['titulo', 'descricao', 'edital']

    def form_valid(self, form):
        form.instance.coordenador = self.request.user
        response = super().form_valid(form)
        EventoAuditoria.registrar(
            tipo=EventoAuditoria.CRIACAO,
            acao=f'Criação do processo seletivo: {self.object}',
            usuario=self.request.user,
            objeto=self.object,
            origem=self.request.META.get('REMOTE_ADDR', ''),
        )
        return response

    def get_success_url(self):
        return f'/processos/{self.object.pk}/'


class ProcessoSeletivoUpdateView(CoordenadorRequiredMixin, UpdateView):
    model = ProcessoSeletivo
    template_name = 'processos/processo_form.html'
    fields = ['titulo', 'descricao', 'edital']

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if not (user.is_staff or user.is_administrador or obj.coordenador == user):
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        valor_anterior = {
            'titulo': self.object.titulo,
            'descricao': self.object.descricao,
        }
        response = super().form_valid(form)
        EventoAuditoria.registrar(
            tipo=EventoAuditoria.ALTERACAO,
            acao=f'Alteração do processo seletivo: {self.object}',
            usuario=self.request.user,
            objeto=self.object,
            valor_anterior=valor_anterior,
            valor_posterior={'titulo': self.object.titulo, 'descricao': self.object.descricao},
            origem=self.request.META.get('REMOTE_ADDR', ''),
        )
        return response

    def get_success_url(self):
        return f'/processos/{self.object.pk}/'


class PublicarProcessoView(CoordenadorRequiredMixin, View):
    def post(self, request, pk):
        processo = get_object_or_404(ProcessoSeletivo, pk=pk)
        processo.publicar()
        EventoAuditoria.registrar(
            tipo=EventoAuditoria.PUBLICACAO,
            acao=f'Publicação do processo seletivo: {processo}',
            usuario=request.user,
            objeto=processo,
            origem=request.META.get('REMOTE_ADDR', ''),
        )
        return redirect(f'/processos/{pk}/')


class SuspenderProcessoView(CoordenadorRequiredMixin, View):
    def post(self, request, pk):
        processo = get_object_or_404(ProcessoSeletivo, pk=pk)
        processo.suspender()
        return redirect(f'/processos/{pk}/')


class EncerrarProcessoView(CoordenadorRequiredMixin, View):
    def post(self, request, pk):
        processo = get_object_or_404(ProcessoSeletivo, pk=pk)
        processo.encerrar()
        return redirect(f'/processos/{pk}/')
