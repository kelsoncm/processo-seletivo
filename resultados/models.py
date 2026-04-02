from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class ResultadoEtapa(models.Model):
    """
    Resultado parcial de uma inscrição ao final de uma etapa.
    """

    inscricao = models.ForeignKey(
        'inscricoes.Inscricao',
        on_delete=models.CASCADE,
        related_name='resultados_etapa',
    )
    etapa = models.ForeignKey(
        'processos.Etapa',
        on_delete=models.PROTECT,
        related_name='resultados_etapa',
    )
    nota_final = models.DecimalField('Nota final', max_digits=10, decimal_places=2, null=True, blank=True)
    habilitado = models.BooleanField('Habilitado', default=False)
    publicado = models.BooleanField('Publicado', default=False)

    data_publicacao = models.DateTimeField('Data de publicação', null=True, blank=True)
    data_atualizacao = models.DateTimeField('Data de atualização', auto_now=True)

    class Meta:
        verbose_name = 'Resultado de Etapa'
        verbose_name_plural = 'Resultados de Etapa'
        unique_together = ('inscricao', 'etapa')
        ordering = ['-nota_final']

    def __str__(self):
        return f'Resultado de {self.inscricao} na {self.etapa}: {self.nota_final}'

    def calcular_nota_final(self):
        """
        Calcula a nota final com base nas avaliações e critério de consolidação da etapa.
        """
        from django.utils import timezone

        avaliacoes = self.inscricao.avaliacoes.filter(etapa=self.etapa)
        if not avaliacoes.exists():
            return

        notas = [a.nota for a in avaliacoes if a.nota is not None]
        if not notas:
            return

        criterio = self.etapa.criterio_consolidacao
        from processos.models import Etapa
        if criterio == Etapa.MEDIA:
            self.nota_final = sum(notas) / len(notas)
        elif criterio == Etapa.SOMA:
            self.nota_final = sum(notas)

        self.save()

    def publicar(self):
        from django.utils import timezone

        self.publicado = True
        self.data_publicacao = timezone.now()
        self.save()


class ResultadoFase(models.Model):
    """
    Resultado de uma inscrição ao final de uma fase.
    """

    inscricao = models.ForeignKey(
        'inscricoes.Inscricao',
        on_delete=models.CASCADE,
        related_name='resultados_fase',
    )
    fase = models.ForeignKey(
        'processos.Fase',
        on_delete=models.PROTECT,
        related_name='resultados',
    )
    habilitado = models.BooleanField('Habilitado', default=False)
    publicado = models.BooleanField('Publicado', default=False)

    data_publicacao = models.DateTimeField('Data de publicação', null=True, blank=True)

    class Meta:
        verbose_name = 'Resultado de Fase'
        verbose_name_plural = 'Resultados de Fase'
        unique_together = ('inscricao', 'fase')

    def __str__(self):
        return f'Resultado de fase de {self.inscricao} na {self.fase}'


class ResultadoFinal(models.Model):
    """
    Resultado final consolidado do processo seletivo.
    Gerado automaticamente a partir da última etapa.
    """

    processo_seletivo = models.ForeignKey(
        'processos.ProcessoSeletivo',
        on_delete=models.CASCADE,
        related_name='resultados_finais',
    )
    inscricao = models.OneToOneField(
        'inscricoes.Inscricao',
        on_delete=models.CASCADE,
        related_name='resultado_final',
    )
    classificacao = models.PositiveIntegerField('Classificação', null=True, blank=True)
    nota_final = models.DecimalField('Nota final', max_digits=10, decimal_places=2, null=True, blank=True)
    selecionado = models.BooleanField('Selecionado', default=False)
    publicado = models.BooleanField('Publicado', default=False)

    data_publicacao = models.DateTimeField('Data de publicação', null=True, blank=True)
    data_atualizacao = models.DateTimeField('Data de atualização', auto_now=True)

    class Meta:
        verbose_name = 'Resultado Final'
        verbose_name_plural = 'Resultados Finais'
        ordering = ['classificacao']

    def __str__(self):
        return f'Resultado final de {self.inscricao}: {self.classificacao}º'
