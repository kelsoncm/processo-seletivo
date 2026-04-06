from django.contrib import admin

from .models import Avaliacao, CriterioAvaliacao, ItemChecklist, NotaCriterio, RespostaChecklist


class NotaCriterioInline(admin.TabularInline):
    model = NotaCriterio
    extra = 0


class RespostaChecklistInline(admin.TabularInline):
    model = RespostaChecklist
    extra = 0


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'etapa', 'avaliador', 'nota', 'aprovado', 'data_avaliacao')
    list_filter = ('etapa', 'aprovado')
    readonly_fields = ('data_avaliacao',)
    inlines = [NotaCriterioInline, RespostaChecklistInline]


@admin.register(CriterioAvaliacao)
class CriterioAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'etapa', 'peso', 'mensuravel', 'nota_maxima')
    list_filter = ('mensuravel',)


@admin.register(ItemChecklist)
class ItemChecklistAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'etapa', 'obrigatorio', 'ordem')
    list_filter = ('obrigatorio',)
