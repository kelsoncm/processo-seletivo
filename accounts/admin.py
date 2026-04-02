from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Papel, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('cpf', 'nome', 'email', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('cpf', 'nome', 'email')
    ordering = ('nome',)
    fieldsets = (
        (None, {'fields': ('cpf', 'password')}),
        ('Informações pessoais', {'fields': ('nome', 'email', 'govbr_sub')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'data_criacao', 'data_atualizacao')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('cpf', 'nome', 'email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('data_criacao', 'data_atualizacao', 'last_login')


@admin.register(Papel)
class PapelAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'processo_seletivo', 'data_criacao')
    list_filter = ('tipo',)
    search_fields = ('usuario__nome', 'usuario__cpf')
