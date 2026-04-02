from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from auditoria.models import EventoAuditoria
from processos.models import ProcessoSeletivo

from .models import Inscricao


class InscricaoCreateView(LoginRequiredMixin, CreateView):
    model = Inscricao
    template_name = 'inscricoes/inscricao_form.html'
    fields = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.processo = get_object_or_404(ProcessoSeletivo, pk=kwargs['processo_pk'])
        if self.processo.status != ProcessoSeletivo.PUBLICADO:
            raise PermissionDenied('Este processo seletivo não está aberto para inscrições.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.candidato = self.request.user
        form.instance.processo_seletivo = self.processo
        form.instance.fase_atual = self.processo.get_fase_inscricao()
        response = super().form_valid(form)
        EventoAuditoria.registrar(
            tipo=EventoAuditoria.INSCRICAO,
            acao=f'Inscrição {self.object.numero} no processo {self.processo}',
            usuario=self.request.user,
            objeto=self.object,
            origem=self.request.META.get('REMOTE_ADDR', ''),
        )
        return response

    def get_success_url(self):
        return reverse('inscricoes:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['processo'] = self.processo
        return ctx


class InscricaoDetailView(LoginRequiredMixin, DetailView):
    model = Inscricao
    template_name = 'inscricoes/inscricao_detail.html'
    context_object_name = 'inscricao'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if obj.candidato != user and not (user.is_staff or user.is_administrador or user.is_coordenador):
            raise PermissionDenied
        return obj


class InscricaoListView(LoginRequiredMixin, ListView):
    model = Inscricao
    template_name = 'inscricoes/inscricao_list.html'
    context_object_name = 'inscricoes'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_administrador or user.is_coordenador:
            processo_pk = self.request.GET.get('processo')
            if processo_pk:
                return Inscricao.objects.filter(processo_seletivo_id=processo_pk)
            return Inscricao.objects.all()
        return Inscricao.objects.filter(candidato=user)


class CancelarInscricaoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        inscricao = get_object_or_404(Inscricao, pk=pk)
        if inscricao.candidato != request.user and not (request.user.is_staff or request.user.is_administrador):
            raise PermissionDenied
        inscricao.cancelar()
        EventoAuditoria.registrar(
            tipo=EventoAuditoria.CANCELAMENTO,
            acao=f'Cancelamento da inscrição {inscricao.numero}',
            usuario=request.user,
            objeto=inscricao,
            origem=request.META.get('REMOTE_ADDR', ''),
        )
        return redirect('inscricoes:detail', pk=pk)
