from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Formulario(models.Model):
    """
    Formulário configurável para uma etapa do processo seletivo.
    """

    etapa = models.OneToOneField(
        'processos.Etapa',
        on_delete=models.CASCADE,
        related_name='formulario',
    )
    titulo = models.CharField('Título', max_length=255)
    descricao = models.TextField('Descrição', blank=True)
    pontuado = models.BooleanField('Formulário pontuado', default=False)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Formulário'
        verbose_name_plural = 'Formulários'

    def __str__(self):
        return f'Formulário: {self.titulo} ({self.etapa})'


class Campo(models.Model):
    """
    Campo de um formulário configurável.
    """

    TEXTO = 'TEXTO'
    NUMERO = 'NUMERO'
    DATA = 'DATA'
    SELECAO_UNICA = 'SELECAO_UNICA'
    MULTIPLA_SELECAO = 'MULTIPLA_SELECAO'
    CHECKBOX = 'CHECKBOX'
    UPLOAD = 'UPLOAD'

    TIPO_CHOICES = [
        (TEXTO, 'Texto'),
        (NUMERO, 'Número'),
        (DATA, 'Data'),
        (SELECAO_UNICA, 'Seleção única'),
        (MULTIPLA_SELECAO, 'Múltipla seleção'),
        (CHECKBOX, 'Checkbox'),
        (UPLOAD, 'Upload'),
    ]

    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, related_name='campos')
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    rotulo = models.CharField('Rótulo', max_length=255)
    descricao = models.TextField('Descrição/ajuda', blank=True)
    ordem = models.PositiveIntegerField('Ordem')
    obrigatorio = models.BooleanField('Obrigatório', default=False)
    opcoes = models.JSONField(
        'Opções',
        default=list,
        blank=True,
        help_text='Lista de opções para campos de seleção.',
    )
    pontuacao = models.DecimalField(
        'Pontuação máxima',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Campo'
        verbose_name_plural = 'Campos'
        ordering = ['formulario', 'ordem']
        unique_together = ('formulario', 'ordem')

    def __str__(self):
        return f'{self.formulario} — {self.rotulo}'


class RespostaFormulario(models.Model):
    """
    Resposta de um candidato a um formulário.
    """

    inscricao = models.ForeignKey(
        'inscricoes.Inscricao',
        on_delete=models.CASCADE,
        related_name='respostas_formulario',
    )
    formulario = models.ForeignKey(Formulario, on_delete=models.PROTECT, related_name='respostas')
    respondido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='respostas_formulario',
    )
    data_resposta = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Resposta de Formulário'
        verbose_name_plural = 'Respostas de Formulários'
        unique_together = ('inscricao', 'formulario')

    def __str__(self):
        return f'Resposta de {self.inscricao} ao {self.formulario}'


class RespostaCampo(models.Model):
    """
    Resposta estruturada a um campo específico do formulário.
    """

    resposta_formulario = models.ForeignKey(
        RespostaFormulario,
        on_delete=models.CASCADE,
        related_name='respostas_campo',
    )
    campo = models.ForeignKey(Campo, on_delete=models.PROTECT, related_name='respostas')
    valor = models.JSONField('Valor', null=True, blank=True)

    class Meta:
        verbose_name = 'Resposta de Campo'
        verbose_name_plural = 'Respostas de Campos'
        unique_together = ('resposta_formulario', 'campo')

    def __str__(self):
        return f'{self.resposta_formulario} — {self.campo.rotulo}: {self.valor}'
