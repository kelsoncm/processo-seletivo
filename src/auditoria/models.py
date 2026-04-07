from django.conf import settings
from django.db import models


class EventoAuditoria(models.Model):
    """
    Trilha de auditoria completa de todos os eventos relevantes do sistema.
    Registra: usuário, data/hora, ação, objeto afetado, valores anterior e posterior.
    """

    ACESSO = 'ACESSO'
    LOGIN = 'LOGIN'
    LOGOUT = 'LOGOUT'
    CRIACAO = 'CRIACAO'
    ALTERACAO = 'ALTERACAO'
    EXCLUSAO = 'EXCLUSAO'
    PUBLICACAO = 'PUBLICACAO'
    INSCRICAO = 'INSCRICAO'
    CANCELAMENTO = 'CANCELAMENTO'
    ENVIO_DOCUMENTO = 'ENVIO_DOCUMENTO'
    AVALIACAO = 'AVALIACAO'
    RECURSO = 'RECURSO'
    RESPOSTA_RECURSO = 'RESPOSTA_RECURSO'
    INTEGRACAO = 'INTEGRACAO'
    PRORROGACAO = 'PRORROGACAO'
    FORMULARIO = 'FORMULARIO'

    TIPO_CHOICES = [
        (ACESSO, 'Acesso ao sistema'),
        (LOGIN, 'Login'),
        (LOGOUT, 'Logout'),
        (CRIACAO, 'Criação'),
        (ALTERACAO, 'Alteração'),
        (EXCLUSAO, 'Exclusão'),
        (PUBLICACAO, 'Publicação de resultado'),
        (INSCRICAO, 'Inscrição'),
        (CANCELAMENTO, 'Cancelamento de inscrição'),
        (ENVIO_DOCUMENTO, 'Envio/substituição de documento'),
        (AVALIACAO, 'Avaliação'),
        (RECURSO, 'Interposição de recurso'),
        (RESPOSTA_RECURSO, 'Resposta a recurso'),
        (INTEGRACAO, 'Integração externa'),
        (PRORROGACAO, 'Prorrogação de prazo'),
        (FORMULARIO, 'Preenchimento de formulário'),
    ]

    tipo = models.CharField('Tipo de evento', max_length=30, choices=TIPO_CHOICES)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_auditoria',
    )
    acao = models.CharField('Ação executada', max_length=500)
    objeto_tipo = models.CharField('Tipo do objeto afetado', max_length=100, blank=True)
    objeto_id = models.CharField('ID do objeto afetado', max_length=100, blank=True)
    objeto_repr = models.CharField('Representação do objeto', max_length=500, blank=True)
    valor_anterior = models.JSONField('Valor anterior', null=True, blank=True)
    valor_posterior = models.JSONField('Valor posterior', null=True, blank=True)
    origem = models.CharField('Origem da ação (IP/endpoint)', max_length=255, blank=True)

    data_hora = models.DateTimeField('Data e hora', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Evento de Auditoria'
        verbose_name_plural = 'Eventos de Auditoria'
        ordering = ['-data_hora']

    def __str__(self):
        return f'[{self.data_hora}] {self.get_tipo_display()} por {self.usuario}: {self.acao}'

    @classmethod
    def registrar(
        cls,
        tipo,
        acao,
        usuario=None,
        objeto=None,
        valor_anterior=None,
        valor_posterior=None,
        origem='',
    ):
        kwargs = {
            'tipo': tipo,
            'acao': acao,
            'usuario': usuario,
            'valor_anterior': valor_anterior,
            'valor_posterior': valor_posterior,
            'origem': origem,
        }
        if objeto is not None:
            kwargs['objeto_tipo'] = type(objeto).__name__
            kwargs['objeto_id'] = str(getattr(objeto, 'pk', ''))
            kwargs['objeto_repr'] = str(objeto)
        return cls.objects.create(**kwargs)
