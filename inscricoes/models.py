import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


def documento_upload_path(instance, filename):
    return f'inscricoes/{instance.inscricao.numero}/{instance.tipo_documento.nome}/{filename}'


class Inscricao(models.Model):
    """
    Inscrição de um candidato em um processo seletivo.
    Cada candidato pode ter apenas uma inscrição ativa por processo.
    """

    ATIVA = 'ATIVA'
    CANCELADA = 'CANCELADA'
    HABILITADA = 'HABILITADA'
    ELIMINADA = 'ELIMINADA'

    STATUS_CHOICES = [
        (ATIVA, 'Ativa'),
        (CANCELADA, 'Cancelada'),
        (HABILITADA, 'Habilitada'),
        (ELIMINADA, 'Eliminada'),
    ]

    numero = models.CharField('Número de inscrição', max_length=50, unique=True, blank=True)
    candidato = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='inscricoes',
        verbose_name='Candidato',
    )
    processo_seletivo = models.ForeignKey(
        'processos.ProcessoSeletivo',
        on_delete=models.PROTECT,
        related_name='inscricoes',
        verbose_name='Processo Seletivo',
    )
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=ATIVA)
    fase_atual = models.ForeignKey(
        'processos.Fase',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inscricoes_na_fase',
    )

    data_inscricao = models.DateTimeField('Data de inscrição', auto_now_add=True)
    data_cancelamento = models.DateTimeField('Data de cancelamento', null=True, blank=True)
    data_atualizacao = models.DateTimeField('Data de atualização', auto_now=True)

    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        ordering = ['-data_inscricao']

    def __str__(self):
        return f'Inscrição {self.numero} — {self.candidato} em {self.processo_seletivo}'

    def clean(self):
        inscricoes_ativas = Inscricao.objects.filter(
            candidato=self.candidato,
            processo_seletivo=self.processo_seletivo,
            status=self.ATIVA,
        ).exclude(pk=self.pk)
        if inscricoes_ativas.exists():
            raise ValidationError('Já existe uma inscrição ativa deste candidato neste processo seletivo.')

    def save(self, *args, **kwargs):
        if not self.numero:
            last = Inscricao.objects.filter(
                processo_seletivo=self.processo_seletivo
            ).order_by('numero').last()
            if last and last.numero:
                try:
                    seq = int(last.numero.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.numero = f'{self.processo_seletivo_id:04d}-{seq:06d}'
        if self.status != self.ATIVA:
            pass
        else:
            self.full_clean()
        super().save(*args, **kwargs)

    def cancelar(self):
        if self.status != self.ATIVA:
            raise ValidationError('Apenas inscrições ativas podem ser canceladas.')
        self.status = self.CANCELADA
        self.data_cancelamento = timezone.now()
        self.save()

    def habilitar(self):
        self.status = self.HABILITADA
        self.save()

    def eliminar(self):
        self.status = self.ELIMINADA
        self.save()


class TipoDocumento(models.Model):
    """
    Tipo de documento aceito em uma fase do processo seletivo.
    """

    etapa = models.ForeignKey(
        'processos.Etapa',
        on_delete=models.CASCADE,
        related_name='tipos_documento',
    )
    nome = models.CharField('Nome', max_length=255)
    descricao = models.TextField('Descrição', blank=True)
    obrigatorio = models.BooleanField('Obrigatório', default=False)
    tamanho_maximo_mb = models.PositiveIntegerField(
        'Tamanho máximo (MB)',
        default=2,
        help_text='Tamanho máximo do arquivo em megabytes.',
    )
    tem_pontuacao = models.BooleanField(
        'Possui pontuação',
        default=False,
        help_text='Indica se o candidato pode informar pontuação referencial para este documento.',
    )
    pontuacao_maxima = models.DecimalField(
        'Pontuação máxima',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'
        ordering = ['etapa', 'nome']

    def __str__(self):
        return f'{self.etapa} — {self.nome}'


class Documento(models.Model):
    """
    Documento enviado por um candidato para uma fase/etapa.
    Um candidato pode substituir o arquivo enquanto a fase estiver aberta.
    O sistema mantém histórico para auditoria.
    """

    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT, related_name='documentos')
    arquivo = models.FileField(
        'Arquivo',
        upload_to=documento_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    pontuacao_informada = models.DecimalField(
        'Pontuação informada pelo candidato',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Caráter referencial. Não vinculante.',
    )
    ativo = models.BooleanField('Arquivo atual', default=True)

    data_envio = models.DateTimeField('Data de envio', auto_now_add=True)
    enviado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='documentos_enviados',
    )

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-data_envio']

    def __str__(self):
        return f'{self.inscricao} — {self.tipo_documento.nome}'

    def clean(self):
        if self.arquivo:
            tamanho_max = self.tipo_documento.tamanho_maximo_mb * 1024 * 1024
            if self.arquivo.size > tamanho_max:
                raise ValidationError(
                    f'O arquivo excede o tamanho máximo permitido de '
                    f'{self.tipo_documento.tamanho_maximo_mb} MB.'
                )

        etapa = self.tipo_documento.etapa
        if not etapa.esta_aberta:
            raise ValidationError('O período de envio de documentos desta etapa está encerrado.')

    def save(self, *args, **kwargs):
        if self.ativo and self.pk is None:
            Documento.objects.filter(
                inscricao=self.inscricao,
                tipo_documento=self.tipo_documento,
                ativo=True,
            ).update(ativo=False)
        super().save(*args, **kwargs)
