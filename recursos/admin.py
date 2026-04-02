from django.contrib import admin

from .models import Recurso, RespostaRecurso


@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'etapa', 'status', 'data_interposicao')
    list_filter = ('status',)
    readonly_fields = ('data_interposicao',)


@admin.register(RespostaRecurso)
class RespostaRecursoAdmin(admin.ModelAdmin):
    list_display = ('recurso', 'respondido_por', 'data_resposta')
    readonly_fields = ('data_resposta',)
