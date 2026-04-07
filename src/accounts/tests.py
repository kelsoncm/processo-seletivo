from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from auditoria.models import EventoAuditoria
from processos.models import ProcessoSeletivo

from .models import ConfiguracaoAutenticacao, Papel, Usuario


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

    def test_name_compatibility_properties(self):
        self.assertEqual(self.user.first_name, 'João')
        self.assertEqual(self.user.last_name, 'Silva')
        self.assertEqual(self.user.get_short_name(), 'João')
        self.assertEqual(self.user.get_full_name(), 'João Silva')

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


class ConfiguracaoAutenticacaoTest(TestCase):
    def test_get_instance_cria_se_nao_existir(self):
        ConfiguracaoAutenticacao.objects.all().delete()
        config = ConfiguracaoAutenticacao.get_instance()
        self.assertIsNotNone(config.pk)
        self.assertTrue(config.govbr_habilitado)
        self.assertTrue(config.suap_habilitado)
        self.assertTrue(config.django_habilitado)

    def test_get_instance_retorna_existente(self):
        ConfiguracaoAutenticacao.objects.all().delete()
        c1 = ConfiguracaoAutenticacao.get_instance()
        c2 = ConfiguracaoAutenticacao.get_instance()
        self.assertEqual(c1.pk, c2.pk)
        self.assertEqual(ConfiguracaoAutenticacao.objects.count(), 1)

    def test_singleton_forca_pk_1(self):
        ConfiguracaoAutenticacao.objects.all().delete()
        config = ConfiguracaoAutenticacao(govbr_habilitado=False, suap_habilitado=True)
        config.save()
        self.assertEqual(config.pk, 1)
        self.assertEqual(ConfiguracaoAutenticacao.objects.count(), 1)


class LoginViewTest(TestCase):
    def _set_config(self, govbr=True, suap=False, django=False):
        config = ConfiguracaoAutenticacao.get_instance()
        config.govbr_habilitado = govbr
        config.suap_habilitado = suap
        config.django_habilitado = django
        config.save()

    def test_apenas_govbr_habilitado(self):
        self._set_config(govbr=True, suap=False, django=False)
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('govbr_auth_url', response.context)
        self.assertIsNotNone(response.context['govbr_auth_url'])
        self.assertIsNone(response.context['suap_auth_url'])
        self.assertFalse(response.context['django_habilitado'])

    def test_apenas_suap_habilitado(self):
        self._set_config(govbr=False, suap=True, django=False)
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['govbr_auth_url'])
        self.assertIsNotNone(response.context['suap_auth_url'])
        self.assertFalse(response.context['django_habilitado'])

    def test_apenas_django_habilitado(self):
        self._set_config(govbr=False, suap=False, django=True)
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['govbr_auth_url'])
        self.assertIsNone(response.context['suap_auth_url'])
        self.assertTrue(response.context['django_habilitado'])

    def test_nenhum_habilitado_exibe_mensagem(self):
        self._set_config(govbr=False, suap=False, django=False)
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhum meio de autenticação')

    def test_todos_habilitados(self):
        self._set_config(govbr=True, suap=True, django=True)
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['govbr_auth_url'])
        self.assertIsNotNone(response.context['suap_auth_url'])
        self.assertTrue(response.context['django_habilitado'])


class SuapCallbackViewTest(TestCase):
    def test_state_invalido_redireciona_login(self):
        session = self.client.session
        session['suap_state'] = 'correct_state'
        session.save()
        response = self.client.get(
            reverse('accounts:suap_callback'),
            {'code': 'abc', 'state': 'wrong_state'},
        )
        self.assertRedirects(response, reverse('accounts:login'))

    def test_sem_code_redireciona_login(self):
        session = self.client.session
        session['suap_state'] = 'mystate'
        session.save()
        response = self.client.get(
            reverse('accounts:suap_callback'),
            {'state': 'mystate'},
        )
        self.assertRedirects(response, reverse('accounts:login'))

    def test_callback_sucesso_cria_usuario(self):
        session = self.client.session
        session['suap_state'] = 'valid_state'
        session.save()

        token_response = {'access_token': 'tok123', 'token_type': 'Bearer'}
        user_info = {
            'identificacao': '12345',
            'cpf': '123.456.789-09',
            'nome_usual': 'Maria Souza',
            'email': 'maria@example.com',
        }

        with patch('accounts.views.requests.post') as mock_post, \
             patch('accounts.views.requests.get') as mock_get:
            mock_post.return_value.json.return_value = token_response
            mock_post.return_value.raise_for_status = lambda: None
            mock_get.return_value.json.return_value = user_info
            mock_get.return_value.raise_for_status = lambda: None

            response = self.client.get(
                reverse('accounts:suap_callback'),
                {'code': 'mycode', 'state': 'valid_state'},
            )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Usuario.objects.filter(suap_id='12345').exists())
        self.assertTrue(
            EventoAuditoria.objects.filter(
                tipo=EventoAuditoria.CRIACAO,
                acao='Criação de usuário via SUAP',
            ).exists()
        )
        self.assertTrue(
            EventoAuditoria.objects.filter(
                tipo=EventoAuditoria.LOGIN,
                acao='Login via SUAP',
            ).exists()
        )

    def test_callback_sucesso_atualiza_usuario_registra_alteracao(self):
        Usuario.objects.create_user(
            cpf='12345678909',
            nome='Nome Antigo',
            email='antigo@example.com',
            suap_id='12345',
        )

        session = self.client.session
        session['suap_state'] = 'valid_state'
        session.save()

        token_response = {'access_token': 'tok123', 'token_type': 'Bearer'}
        user_info = {
            'identificacao': '12345',
            'cpf': '123.456.789-09',
            'nome_usual': 'Nome Novo',
            'email': 'novo@example.com',
        }

        with patch('accounts.views.requests.post') as mock_post, \
             patch('accounts.views.requests.get') as mock_get:
            mock_post.return_value.json.return_value = token_response
            mock_post.return_value.raise_for_status = lambda: None
            mock_get.return_value.json.return_value = user_info
            mock_get.return_value.raise_for_status = lambda: None

            response = self.client.get(
                reverse('accounts:suap_callback'),
                {'code': 'mycode', 'state': 'valid_state'},
            )

        self.assertEqual(response.status_code, 302)
        usuario = Usuario.objects.get(suap_id='12345')
        self.assertEqual(usuario.nome, 'Nome Novo')
        self.assertEqual(usuario.email, 'novo@example.com')
        self.assertTrue(
            EventoAuditoria.objects.filter(
                tipo=EventoAuditoria.ALTERACAO,
                acao='Atualização de usuário via SUAP',
            ).exists()
        )


class GovbrCallbackViewTest(TestCase):
    def test_callback_sucesso_cria_usuario(self):
        session = self.client.session
        session['govbr_state'] = 'valid_state'
        session.save()

        token_response = {'access_token': 'tok123', 'token_type': 'Bearer'}
        user_info = {
            'sub': 'govbr-12345',
            'cpf': '123.456.789-09',
            'name': 'Maria Souza',
            'email': 'maria@example.com',
        }

        with patch('accounts.views.requests.post') as mock_post, \
             patch('accounts.views.requests.get') as mock_get:
            mock_post.return_value.json.return_value = token_response
            mock_post.return_value.raise_for_status = lambda: None
            mock_get.return_value.json.return_value = user_info
            mock_get.return_value.raise_for_status = lambda: None

            response = self.client.get(
                reverse('accounts:govbr_callback'),
                {'code': 'mycode', 'state': 'valid_state'},
            )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Usuario.objects.filter(govbr_sub='govbr-12345').exists())
        self.assertTrue(
            EventoAuditoria.objects.filter(
                tipo=EventoAuditoria.CRIACAO,
                acao='Criação de usuário via gov.br',
            ).exists()
        )
        self.assertTrue(
            EventoAuditoria.objects.filter(
                tipo=EventoAuditoria.LOGIN,
                acao='Login via gov.br',
            ).exists()
        )

    def test_callback_sucesso_atualiza_usuario_registra_alteracao(self):
        Usuario.objects.create_user(
            cpf='12345678909',
            nome='Nome Antigo',
            email='antigo@example.com',
            govbr_sub='govbr-12345',
        )

        session = self.client.session
        session['govbr_state'] = 'valid_state'
        session.save()

        token_response = {'access_token': 'tok123', 'token_type': 'Bearer'}
        user_info = {
            'sub': 'govbr-12345',
            'cpf': '123.456.789-09',
            'name': 'Nome Novo',
            'email': 'novo@example.com',
        }

        with patch('accounts.views.requests.post') as mock_post, \
             patch('accounts.views.requests.get') as mock_get:
            mock_post.return_value.json.return_value = token_response
            mock_post.return_value.raise_for_status = lambda: None
            mock_get.return_value.json.return_value = user_info
            mock_get.return_value.raise_for_status = lambda: None

            response = self.client.get(
                reverse('accounts:govbr_callback'),
                {'code': 'mycode', 'state': 'valid_state'},
            )

        self.assertEqual(response.status_code, 302)
        usuario = Usuario.objects.get(govbr_sub='govbr-12345')
        self.assertEqual(usuario.nome, 'Nome Novo')
        self.assertEqual(usuario.email, 'novo@example.com')
        self.assertTrue(
            EventoAuditoria.objects.filter(
                tipo=EventoAuditoria.ALTERACAO,
                acao='Atualização de usuário via gov.br',
            ).exists()
        )


class DjangoLoginViewTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            cpf='12345678901',
            nome='Test User',
            email='test@example.com',
            password='secret123',
        )

    def test_get_renderiza_formulario(self):
        response = self.client.get(reverse('accounts:django_login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_post_credenciais_invalidas(self):
        response = self.client.post(reverse('accounts:django_login'), {
            'username': '12345678901',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_post_credenciais_validas(self):
        response = self.client.post(reverse('accounts:django_login'), {
            'username': '12345678901',
            'password': 'secret123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

