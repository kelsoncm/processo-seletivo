from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Recurso(models.Model):
    """
    Recurso interposto por candidato contra o resultado parcial de uma etapa.
    """

    PENDENTE = 'PENDENTE'
    DEFERIDO = 'DEFERIDO'
    INDEFERIDO = 'INDEFERIDO'

    STATUS_CHOICES = [
        (PENDENTE, 'Pendente'),
        (DEFERIDO, 'Deferido'),
        (INDEFERIDO, 'Indeferido'),
    ]

    inscricao = models.ForeignKey(
        'inscricoes.Inscricao',
        on_delete=models.CASCADE,
        related_name='recursos',
    )
    etapa = models.ForeignKey(
        'processos.Etapa',
        on_delete=models.PROTECT,
        related_name='recursos',
    )
    texto = models.TextField('Texto do recurso')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=PENDENTE)

    data_interposicao = models.DateTimeField('Data de interposição', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de atualização', auto_now=True)

    class Meta:
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
        unique_together = ('inscricao', 'etapa')
        ordering = ['-data_interposicao']

    def __str__(self):
        return f'Recurso de {self.inscricao} na {self.etapa}'

    def clean(self):
        resultado = self.etapa.resultados_etapa.filter(
            inscricao=self.inscricao,
            publicado=True,
        ).first()
        if not resultado:
            raise ValidationError(
                'Só é possível interpor recurso após a publicação do resultado parcial desta etapa.'
            )


class RespostaRecurso(models.Model):
    """
    Resposta ao recurso interposto por candidato.
    """

    recurso = models.OneToOneField(Recurso, on_delete=models.CASCADE, related_name='resposta')
    respondido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='respostas_recurso',
    )
    texto = models.TextField('Texto da resposta')
    data_resposta = models.DateTimeField('Data de resposta', auto_now_add=True)

    class Meta:
        verbose_name = 'Resposta ao Recurso'
        verbose_name_plural = 'Respostas aos Recursos'

    def __str__(self):
        return f'Resposta ao recurso {self.recurso}'
