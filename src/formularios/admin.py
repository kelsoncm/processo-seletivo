from django.contrib import admin

from .models import Campo, Formulario, RespostaCampo, RespostaFormulario


class CampoInline(admin.TabularInline):
    model = Campo
    extra = 0
    ordering = ['ordem']


@admin.register(Formulario)
class FormularioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'etapa', 'pontuado')
    inlines = [CampoInline]


@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    list_display = ('rotulo', 'formulario', 'tipo', 'ordem', 'obrigatorio')
    list_filter = ('tipo', 'obrigatorio')


@admin.register(RespostaFormulario)
class RespostaFormularioAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'formulario', 'respondido_por', 'data_resposta')
    readonly_fields = ('data_resposta',)
