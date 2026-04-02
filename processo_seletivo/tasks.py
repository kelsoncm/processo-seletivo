from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(bind=True, max_retries=3)
def enviar_email_notificacao(self, destinatario, assunto, mensagem):
    """
    Tarefa assíncrona para envio de e-mail de notificação aos candidatos (RF32).
    """
    try:
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task
def notificar_candidatos_fase(fase_id):
    """
    Notifica todos os candidatos com inscrição ativa sobre abertura/fechamento de fase.
    """
    from inscricoes.models import Inscricao
    from processos.models import Fase

    fase = Fase.objects.get(pk=fase_id)
    inscricoes_ativas = Inscricao.objects.filter(
        processo_seletivo=fase.processo_seletivo,
        status=Inscricao.ATIVA,
    ).select_related('candidato')

    for inscricao in inscricoes_ativas:
        enviar_email_notificacao.delay(
            destinatario=inscricao.candidato.email,
            assunto=f'[{fase.processo_seletivo}] Atualização da fase: {fase.nome}',
            mensagem=(
                f'Prezado(a) {inscricao.candidato.nome},\n\n'
                f'Informamos que a fase "{fase.nome}" do processo seletivo '
                f'"{fase.processo_seletivo}" foi atualizada.\n\n'
                f'Acesse o sistema para mais informações.\n\n'
                f'Atenciosamente,\nSistema de Processos Seletivos'
            ),
        )


@shared_task
def consolidar_resultado_final(processo_seletivo_id):
    """
    Consolida o resultado final do processo seletivo a partir da última etapa (RF30).
    """
    from processos.models import ProcessoSeletivo
    from resultados.models import ResultadoEtapa, ResultadoFinal

    processo = ProcessoSeletivo.objects.get(pk=processo_seletivo_id)
    ultima_fase = processo.fases.order_by('-ordem').first()
    if not ultima_fase:
        return

    ultima_etapa = ultima_fase.etapas.order_by('-ordem').first()
    if not ultima_etapa:
        return

    resultados_etapa = ResultadoEtapa.objects.filter(
        etapa=ultima_etapa,
        habilitado=True,
    ).select_related('inscricao').order_by('-nota_final')

    for pos, resultado in enumerate(resultados_etapa, start=1):
        ResultadoFinal.objects.update_or_create(
            processo_seletivo=processo,
            inscricao=resultado.inscricao,
            defaults={
                'classificacao': pos,
                'nota_final': resultado.nota_final,
                'selecionado': True,
            },
        )


@shared_task
def calcular_resultados_etapa(etapa_id):
    """
    Calcula a nota final de todas as inscrições em uma etapa.
    """
    from inscricoes.models import Inscricao
    from processos.models import Etapa
    from resultados.models import ResultadoEtapa

    etapa = Etapa.objects.get(pk=etapa_id)
    inscricoes = Inscricao.objects.filter(
        processo_seletivo=etapa.fase.processo_seletivo,
        status__in=[Inscricao.ATIVA, Inscricao.HABILITADA],
    )

    for inscricao in inscricoes:
        resultado, _ = ResultadoEtapa.objects.get_or_create(
            inscricao=inscricao,
            etapa=etapa,
        )
        resultado.calcular_nota_final()
