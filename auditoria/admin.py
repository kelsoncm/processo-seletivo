from django.contrib import admin

from .models import EventoAuditoria


@admin.register(EventoAuditoria)
class EventoAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'tipo', 'usuario', 'acao', 'objeto_tipo', 'objeto_id')
    list_filter = ('tipo',)
    search_fields = ('acao', 'objeto_repr', 'usuario__nome')
    readonly_fields = ('data_hora', 'tipo', 'usuario', 'acao', 'objeto_tipo', 'objeto_id', 'objeto_repr',
                       'valor_anterior', 'valor_posterior', 'origem')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
