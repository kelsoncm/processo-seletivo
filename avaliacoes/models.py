from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


def avaliacao_upload_path(instance, filename):
    return f'avaliacoes/{instance.inscricao.numero}/{instance.etapa_id}/{filename}'


class Avaliacao(models.Model):
    """
    Avaliação de uma inscrição em uma etapa, feita por um avaliador.
    """

    inscricao = models.ForeignKey(
        'inscricoes.Inscricao',
        on_delete=models.CASCADE,
        related_name='avaliacoes',
    )
    etapa = models.ForeignKey(
        'processos.Etapa',
        on_delete=models.PROTECT,
        related_name='avaliacoes',
    )
    avaliador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='avaliacoes',
    )
    nota = models.DecimalField(
        'Nota',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    parecer = models.TextField('Parecer', blank=True)
    aprovado = models.BooleanField('Aprovado', null=True, blank=True)
    atende_requisitos = models.BooleanField('Atende aos requisitos', null=True, blank=True)
    observacoes_banca = models.TextField('Observações para banca/coordenadoria', blank=True)
    observacoes_candidato = models.TextField('Observações para o candidato', blank=True)
    justificativa = models.TextField('Justificativa', blank=True)
    anexo = models.FileField(
        'Anexo',
        upload_to=avaliacao_upload_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )

    data_avaliacao = models.DateTimeField('Data de avaliação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de atualização', auto_now=True)

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        unique_together = ('inscricao', 'etapa', 'avaliador')
        ordering = ['-data_avaliacao']

    def __str__(self):
        return f'Avaliação de {self.inscricao} na {self.etapa} por {self.avaliador}'

    def clean(self):
        num_avaliacoes = Avaliacao.objects.filter(
            inscricao=self.inscricao,
            etapa=self.etapa,
        ).exclude(pk=self.pk).count() + 1

        if num_avaliacoes > self.etapa.numero_avaliadores:
            raise ValidationError(
                f'Esta candidatura já atingiu o número máximo de avaliadores '
                f'({self.etapa.numero_avaliadores}) nesta etapa.'
            )


class CriterioAvaliacao(models.Model):
    """
    Critério de avaliação ponderado de uma etapa.
    """

    etapa = models.ForeignKey(
        'processos.Etapa',
        on_delete=models.CASCADE,
        related_name='criterios',
    )
    nome = models.CharField('Nome', max_length=255)
    descricao = models.TextField('Descrição', blank=True)
    peso = models.DecimalField('Peso', max_digits=5, decimal_places=2, default=1)
    mensuravel = models.BooleanField(
        'Mensurável',
        default=True,
        help_text='Critérios não mensuráveis exigem ateste de aprovado/reprovado além de nota.',
    )
    nota_maxima = models.DecimalField('Nota máxima', max_digits=10, decimal_places=2, default=10)

    class Meta:
        verbose_name = 'Critério de Avaliação'
        verbose_name_plural = 'Critérios de Avaliação'
        ordering = ['etapa', 'nome']

    def __str__(self):
        return f'{self.etapa} — {self.nome}'


class NotaCriterio(models.Model):
    """
    Nota atribuída a um critério de avaliação por um avaliador.
    """

    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name='notas_criterio')
    criterio = models.ForeignKey(CriterioAvaliacao, on_delete=models.PROTECT, related_name='notas')
    nota = models.DecimalField('Nota', max_digits=10, decimal_places=2)
    aprovado = models.BooleanField('Aprovado no critério', null=True, blank=True)
    observacao = models.TextField('Observação', blank=True)

    class Meta:
        verbose_name = 'Nota por Critério'
        verbose_name_plural = 'Notas por Critério'
        unique_together = ('avaliacao', 'criterio')

    def __str__(self):
        return f'{self.avaliacao} — {self.criterio.nome}: {self.nota}'

    def clean(self):
        if not self.criterio.mensuravel and self.aprovado is None:
            raise ValidationError(
                'Critérios não mensuráveis requerem ateste de aprovado/reprovado.'
            )


class ItemChecklist(models.Model):
    """
    Item de um checklist de avaliação associado a uma etapa.
    """

    etapa = models.ForeignKey(
        'processos.Etapa',
        on_delete=models.CASCADE,
        related_name='itens_checklist',
    )
    descricao = models.CharField('Descrição', max_length=500)
    obrigatorio = models.BooleanField('Obrigatório', default=True)
    ordem = models.PositiveIntegerField('Ordem', default=0)

    class Meta:
        verbose_name = 'Item de Checklist'
        verbose_name_plural = 'Itens de Checklist'
        ordering = ['etapa', 'ordem']

    def __str__(self):
        return f'{self.etapa} — {self.descricao}'


class RespostaChecklist(models.Model):
    """
    Resposta de um avaliador a um item de checklist.
    """

    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name='respostas_checklist')
    item = models.ForeignKey(ItemChecklist, on_delete=models.PROTECT, related_name='respostas')
    marcado = models.BooleanField('Marcado', default=False)
    observacao = models.TextField('Observação', blank=True)

    class Meta:
        verbose_name = 'Resposta de Checklist'
        verbose_name_plural = 'Respostas de Checklist'
        unique_together = ('avaliacao', 'item')

    def __str__(self):
        return f'{self.avaliacao} — {self.item.descricao}: {self.marcado}'
