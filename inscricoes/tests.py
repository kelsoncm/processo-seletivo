from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Usuario
from processos.models import Etapa, Fase, ProcessoSeletivo

from .models import Documento, Inscricao, TipoDocumento


class InscricaoTest(TestCase):
    def setUp(self):
        self.coord = Usuario.objects.create_user(
            cpf='12345678901',
            nome='Coordenador',
            email='coord@example.com',
        )
        self.candidato = Usuario.objects.create_user(
            cpf='98765432100',
            nome='Candidato Teste',
            email='candidato@example.com',
        )
        self.processo = ProcessoSeletivo.objects.create(
            titulo='Processo Teste',
            status=ProcessoSeletivo.PUBLICADO,
            coordenador=self.coord,
        )
        self.fase_inscricao = Fase.objects.create(
            processo_seletivo=self.processo,
            tipo=Fase.INSCRICAO,
            nome='Inscrições',
            ordem=1,
        )

    def test_inscricao_cria_numero(self):
        inscricao = Inscricao.objects.create(
            candidato=self.candidato,
            processo_seletivo=self.processo,
        )
        self.assertIsNotNone(inscricao.numero)
        self.assertNotEqual(inscricao.numero, '')

    def test_apenas_uma_inscricao_ativa_por_candidato(self):
        Inscricao.objects.create(
            candidato=self.candidato,
            processo_seletivo=self.processo,
        )
        with self.assertRaises(ValidationError):
            Inscricao.objects.create(
                candidato=self.candidato,
                processo_seletivo=self.processo,
            )

    def test_cancelar_inscricao(self):
        inscricao = Inscricao.objects.create(
            candidato=self.candidato,
            processo_seletivo=self.processo,
        )
        inscricao.cancelar()
        self.assertEqual(inscricao.status, Inscricao.CANCELADA)
        self.assertIsNotNone(inscricao.data_cancelamento)

    def test_nova_inscricao_apos_cancelamento(self):
        inscricao1 = Inscricao.objects.create(
            candidato=self.candidato,
            processo_seletivo=self.processo,
        )
        inscricao1.cancelar()
        inscricao2 = Inscricao.objects.create(
            candidato=self.candidato,
            processo_seletivo=self.processo,
        )
        self.assertEqual(inscricao2.status, Inscricao.ATIVA)

    def test_nao_pode_cancelar_inscricao_ja_cancelada(self):
        inscricao = Inscricao.objects.create(
            candidato=self.candidato,
            processo_seletivo=self.processo,
        )
        inscricao.cancelar()
        with self.assertRaises(ValidationError):
            inscricao.cancelar()
