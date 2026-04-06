from django.contrib import admin

from .models import Documento, Inscricao, TipoDocumento


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    readonly_fields = ('data_envio', 'enviado_por')


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'candidato', 'processo_seletivo', 'status', 'data_inscricao')
    list_filter = ('status', 'processo_seletivo')
    search_fields = ('numero', 'candidato__nome', 'candidato__cpf')
    readonly_fields = ('numero', 'data_inscricao', 'data_cancelamento')
    inlines = [DocumentoInline]


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'etapa', 'obrigatorio', 'tamanho_maximo_mb', 'tem_pontuacao')
    list_filter = ('obrigatorio', 'tem_pontuacao')


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'tipo_documento', 'ativo', 'data_envio')
    list_filter = ('ativo',)
    readonly_fields = ('data_envio',)
