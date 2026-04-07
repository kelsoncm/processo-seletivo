from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ProcessoSeletivo(models.Model):
    """
    Processo seletivo público.
    """

    RASCUNHO = 'RASCUNHO'
    PUBLICADO = 'PUBLICADO'
    SUSPENSO = 'SUSPENSO'
    ENCERRADO = 'ENCERRADO'

    STATUS_CHOICES = [
        (RASCUNHO, 'Rascunho'),
        (PUBLICADO, 'Publicado'),
        (SUSPENSO, 'Suspenso'),
        (ENCERRADO, 'Encerrado'),
    ]

    titulo = models.CharField('Título', max_length=255)
    descricao = models.TextField('Descrição', blank=True)
    edital = models.CharField('Número do edital', max_length=100, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=RASCUNHO)

    coordenador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='processos_coordenados',
        verbose_name='Coordenador',
    )

    data_criacao = models.DateTimeField('Data de criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de atualização', auto_now=True)

    class Meta:
        verbose_name = 'Processo Seletivo'
        verbose_name_plural = 'Processos Seletivos'
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo

    def publicar(self):
        if self.status != self.RASCUNHO:
            raise ValidationError('Apenas processos em rascunho podem ser publicados.')
        self.status = self.PUBLICADO
        self.save()

    def suspender(self):
        if self.status != self.PUBLICADO:
            raise ValidationError('Apenas processos publicados podem ser suspensos.')
        self.status = self.SUSPENSO
        self.save()

    def encerrar(self):
        if self.status not in [self.PUBLICADO, self.SUSPENSO]:
            raise ValidationError('Apenas processos publicados ou suspensos podem ser encerrados.')
        self.status = self.ENCERRADO
        self.save()

    def get_fase_inscricao(self):
        return self.fases.filter(tipo=Fase.INSCRICAO).first()

    def get_fase_resultado_final(self):
        return self.fases.filter(tipo=Fase.RESULTADO_FINAL).first()


class Fase(models.Model):
    """
    Fase do processo seletivo. Sempre sequencial.
    A primeira deve ser INSCRICAO e a última deve ser RESULTADO_FINAL.
    """

    INSCRICAO = 'INSCRICAO'
    INTERMEDIARIA = 'INTERMEDIARIA'
    RESULTADO_FINAL = 'RESULTADO_FINAL'

    TIPO_CHOICES = [
        (INSCRICAO, 'Inscrição'),
        (INTERMEDIARIA, 'Intermediária'),
        (RESULTADO_FINAL, 'Resultado Final'),
    ]

    processo_seletivo = models.ForeignKey(
        ProcessoSeletivo,
        on_delete=models.CASCADE,
        related_name='fases',
    )
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, default=INTERMEDIARIA)
    nome = models.CharField('Nome', max_length=255)
    descricao = models.TextField('Descrição', blank=True)
    ordem = models.PositiveIntegerField('Ordem')

    data_inicio = models.DateTimeField('Data de início', null=True, blank=True)
    data_fim = models.DateTimeField('Data de fim', null=True, blank=True)

    habilitacao_obrigatoria = models.BooleanField(
        'Eliminação por não habilitação',
        default=True,
        help_text='Se marcado, candidatos não habilitados serão eliminados do processo.',
    )

    class Meta:
        verbose_name = 'Fase'
        verbose_name_plural = 'Fases'
        ordering = ['processo_seletivo', 'ordem']
        unique_together = ('processo_seletivo', 'ordem')

    def __str__(self):
        return f'{self.processo_seletivo} — Fase {self.ordem}: {self.nome}'

    def clean(self):
        # During inline creation in admin, parent object may still be unsaved.
        # In this case, DB-based cross-record validations must be skipped.
        if not self.processo_seletivo_id:
            return

        qs = Fase.objects.filter(processo_seletivo_id=self.processo_seletivo_id).exclude(pk=self.pk)

        if self.tipo == self.INSCRICAO:
            if qs.filter(tipo=self.INSCRICAO).exists():
                raise ValidationError('Já existe uma fase de inscrição neste processo seletivo.')
            if qs.filter(ordem__lt=self.ordem).exists():
                raise ValidationError('A fase de inscrição deve ser sempre a primeira fase.')

        if self.tipo == self.RESULTADO_FINAL:
            if qs.filter(tipo=self.RESULTADO_FINAL).exists():
                raise ValidationError('Já existe uma fase de resultado final neste processo seletivo.')
            if qs.filter(ordem__gt=self.ordem).exists():
                raise ValidationError('A fase de resultado final deve ser sempre a última fase.')

        if self.tipo == self.INTERMEDIARIA:
            inscricao = qs.filter(tipo=self.INSCRICAO).first()
            resultado = qs.filter(tipo=self.RESULTADO_FINAL).first()
            if inscricao and self.ordem <= inscricao.ordem:
                raise ValidationError('Fases intermediárias devem vir após a fase de inscrição.')
            if resultado and self.ordem >= resultado.ordem:
                raise ValidationError('Fases intermediárias devem vir antes da fase de resultado final.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def esta_aberta(self):
        now = timezone.now()
        if self.data_inicio and now < self.data_inicio:
            return False
        if self.data_fim and now > self.data_fim:
            return False
        return True

    def prorrogar(self, nova_data_fim):
        self.data_fim = nova_data_fim
        self.save()


class Etapa(models.Model):
    """
    Etapa dentro de uma fase. Sequencial dentro da fase.
    """

    NOTA = 'NOTA'
    PARECER = 'PARECER'
    CHECKLIST = 'CHECKLIST'
    CRITERIOS = 'CRITERIOS'
    APROVACAO = 'APROVACAO'

    TIPO_AVALIACAO_CHOICES = [
        (NOTA, 'Nota'),
        (PARECER, 'Parecer textual'),
        (CHECKLIST, 'Checklist'),
        (CRITERIOS, 'Critérios ponderados'),
        (APROVACAO, 'Aprovação/Reprovação'),
    ]

    MEDIA = 'MEDIA'
    SOMA = 'SOMA'

    CONSOLIDACAO_CHOICES = [
        (MEDIA, 'Média'),
        (SOMA, 'Soma'),
    ]

    fase = models.ForeignKey(Fase, on_delete=models.CASCADE, related_name='etapas')
    nome = models.CharField('Nome', max_length=255)
    descricao = models.TextField('Descrição', blank=True)
    ordem = models.PositiveIntegerField('Ordem')

    tipo_avaliacao = models.CharField(
        'Tipo de avaliação',
        max_length=20,
        choices=TIPO_AVALIACAO_CHOICES,
        default=NOTA,
    )
    criterio_consolidacao = models.CharField(
        'Critério de consolidação de notas',
        max_length=10,
        choices=CONSOLIDACAO_CHOICES,
        default=MEDIA,
    )
    numero_avaliadores = models.PositiveIntegerField(
        'Número de avaliadores',
        default=1,
        help_text='Deve ser ímpar: 1, 3, 5, 7...',
    )

    exige_formulario = models.BooleanField('Exige preenchimento de formulário', default=False)
    exige_documentos = models.BooleanField('Exige envio de documentos', default=False)

    data_inicio = models.DateTimeField('Data de início', null=True, blank=True)
    data_fim = models.DateTimeField('Data de fim', null=True, blank=True)

    class Meta:
        verbose_name = 'Etapa'
        verbose_name_plural = 'Etapas'
        ordering = ['fase', 'ordem']
        unique_together = ('fase', 'ordem')

    def __str__(self):
        return f'{self.fase} — Etapa {self.ordem}: {self.nome}'

    def clean(self):
        if self.numero_avaliadores % 2 == 0:
            raise ValidationError('O número de avaliadores deve ser ímpar (1, 3, 5, 7...).')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def esta_aberta(self):
        now = timezone.now()
        if self.data_inicio and now < self.data_inicio:
            return False
        if self.data_fim and now > self.data_fim:
            return False
        return True
