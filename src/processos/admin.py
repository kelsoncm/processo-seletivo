from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import Etapa, Fase, ProcessoSeletivo


class FaseInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        fases = []
        for form in self.forms:
            if not hasattr(form, 'cleaned_data') or not form.cleaned_data:
                continue
            if form.cleaned_data.get('DELETE'):
                continue

            tipo = form.cleaned_data.get('tipo')
            ordem = form.cleaned_data.get('ordem')
            if tipo and ordem is not None:
                fases.append((tipo, ordem))

        if not fases:
            return

        inscricoes = [ordem for tipo, ordem in fases if tipo == Fase.INSCRICAO]
        resultados = [ordem for tipo, ordem in fases if tipo == Fase.RESULTADO_FINAL]

        if len(inscricoes) > 1:
            raise ValidationError('Já existe uma fase de inscrição neste processo seletivo.')

        if len(resultados) > 1:
            raise ValidationError('Já existe uma fase de resultado final neste processo seletivo.')

        menor_ordem = min(ordem for _, ordem in fases)
        maior_ordem = max(ordem for _, ordem in fases)

        if inscricoes and inscricoes[0] != menor_ordem:
            raise ValidationError('A fase de inscrição deve ser sempre a primeira fase.')

        if resultados and resultados[0] != maior_ordem:
            raise ValidationError('A fase de resultado final deve ser sempre a última fase.')


class FaseInline(admin.TabularInline):
    model = Fase
    formset = FaseInlineFormSet
    extra = 0
    ordering = ['ordem']


class EtapaInline(admin.TabularInline):
    model = Etapa
    extra = 0
    ordering = ['ordem']


@admin.register(ProcessoSeletivo)
class ProcessoSeletivoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'edital', 'status', 'coordenador', 'data_criacao')
    list_filter = ('status',)
    search_fields = ('titulo', 'edital')
    inlines = [FaseInline]


@admin.register(Fase)
class FaseAdmin(admin.ModelAdmin):
    list_display = ('nome', 'processo_seletivo', 'tipo', 'ordem', 'data_inicio', 'data_fim')
    list_filter = ('tipo', 'processo_seletivo')
    ordering = ['processo_seletivo', 'ordem']
    inlines = [EtapaInline]


@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'fase', 'ordem', 'tipo_avaliacao', 'numero_avaliadores')
    list_filter = ('tipo_avaliacao',)
    ordering = ['fase', 'ordem']
