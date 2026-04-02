from django.core.exceptions import ValidationError
from django.test import TestCase

from processos.models import ProcessoSeletivo

from .models import Papel, Usuario


class UsuarioModelTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            cpf='12345678901',
            nome='João Silva',
            email='joao@example.com',
        )

    def test_criar_usuario(self):
        self.assertEqual(self.user.cpf, '12345678901')
        self.assertEqual(self.user.nome, 'João Silva')
        self.assertTrue(self.user.is_active)

    def test_str(self):
        self.assertIn('João Silva', str(self.user))
        self.assertIn('12345678901', str(self.user))

    def test_is_administrador_false_sem_papel(self):
        self.assertFalse(self.user.is_administrador)

    def test_is_administrador_true_com_papel(self):
        Papel.objects.create(usuario=self.user, tipo=Papel.ADMINISTRADOR)
        self.assertTrue(self.user.is_administrador)


class PapelCompatibilidadeTest(TestCase):
    def setUp(self):
        self.coordenador = Usuario.objects.create_user(
            cpf='99999999901',
            nome='Coordenador Teste',
            email='coord@example.com',
        )
        self.processo = ProcessoSeletivo.objects.create(
            titulo='Processo Teste',
            coordenador=self.coordenador,
        )
        self.user = Usuario.objects.create_user(
            cpf='11111111101',
            nome='Usuário Teste',
            email='usuario@example.com',
        )

    def test_candidato_e_avaliador_no_mesmo_processo_e_invalido(self):
        Papel.objects.create(
            usuario=self.user,
            tipo=Papel.CANDIDATO,
            processo_seletivo=self.processo,
        )
        with self.assertRaises(ValidationError):
            Papel.objects.create(
                usuario=self.user,
                tipo=Papel.AVALIADOR,
                processo_seletivo=self.processo,
            )

    def test_candidato_e_coordenador_no_mesmo_processo_e_invalido(self):
        Papel.objects.create(
            usuario=self.user,
            tipo=Papel.CANDIDATO,
            processo_seletivo=self.processo,
        )
        with self.assertRaises(ValidationError):
            Papel.objects.create(
                usuario=self.user,
                tipo=Papel.COORDENADOR,
                processo_seletivo=self.processo,
            )

    def test_usuario_pode_ter_multiplos_papeis_em_processos_diferentes(self):
        outro_coordenador = Usuario.objects.create_user(
            cpf='88888888801',
            nome='Outro Coord',
            email='outrocoord@example.com',
        )
        outro_processo = ProcessoSeletivo.objects.create(
            titulo='Outro Processo',
            coordenador=outro_coordenador,
        )
        Papel.objects.create(
            usuario=self.user,
            tipo=Papel.CANDIDATO,
            processo_seletivo=self.processo,
        )
        papel2 = Papel.objects.create(
            usuario=self.user,
            tipo=Papel.AVALIADOR,
            processo_seletivo=outro_processo,
        )
        self.assertIsNotNone(papel2.pk)

    def test_papel_global_administrador_sem_processo(self):
        papel = Papel.objects.create(
            usuario=self.user,
            tipo=Papel.ADMINISTRADOR,
        )
        self.assertIsNone(papel.processo_seletivo)

