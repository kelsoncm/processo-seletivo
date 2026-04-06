from django.contrib import admin

from .models import ResultadoEtapa, ResultadoFase, ResultadoFinal


@admin.register(ResultadoEtapa)
class ResultadoEtapaAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'etapa', 'nota_final', 'habilitado', 'publicado')
    list_filter = ('habilitado', 'publicado', 'etapa')
    readonly_fields = ('data_publicacao',)


@admin.register(ResultadoFase)
class ResultadoFaseAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'fase', 'habilitado', 'publicado')
    list_filter = ('habilitado', 'publicado')


@admin.register(ResultadoFinal)
class ResultadoFinalAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'processo_seletivo', 'classificacao', 'nota_final', 'selecionado', 'publicado')
    list_filter = ('selecionado', 'publicado')
    readonly_fields = ('data_publicacao',)
