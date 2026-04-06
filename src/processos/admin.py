from django.contrib import admin

from .models import Etapa, Fase, ProcessoSeletivo


class FaseInline(admin.TabularInline):
    model = Fase
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
