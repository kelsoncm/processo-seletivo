from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.test import TestCase

from accounts.models import Usuario
from .admin import FaseInlineFormSet

from .models import Etapa, Fase, ProcessoSeletivo


class ProcessoSeletivoTest(TestCase):
    def setUp(self):
        self.coord = Usuario.objects.create_user(
            cpf='12345678901',
            nome='Coordenador',
            email='coord@example.com',
        )
        self.processo = ProcessoSeletivo.objects.create(
            titulo='Processo Teste',
            coordenador=self.coord,
        )

    def test_publicar_processo(self):
        self.assertEqual(self.processo.status, ProcessoSeletivo.RASCUNHO)
        self.processo.publicar()
        self.assertEqual(self.processo.status, ProcessoSeletivo.PUBLICADO)

    def test_nao_pode_publicar_processo_ja_publicado(self):
        self.processo.publicar()
        with self.assertRaises(ValidationError):
            self.processo.publicar()

    def test_suspender_processo_publicado(self):
        self.processo.publicar()
        self.processo.suspender()
        self.assertEqual(self.processo.status, ProcessoSeletivo.SUSPENSO)

    def test_encerrar_processo(self):
        self.processo.publicar()
        self.processo.encerrar()
        self.assertEqual(self.processo.status, ProcessoSeletivo.ENCERRADO)


class FaseSequencialidadeTest(TestCase):
    def setUp(self):
        self.coord = Usuario.objects.create_user(
            cpf='12345678901',
            nome='Coordenador',
            email='coord@example.com',
        )
        self.processo = ProcessoSeletivo.objects.create(
            titulo='Processo Teste',
            coordenador=self.coord,
        )

    def test_apenas_uma_fase_inscricao(self):
        Fase.objects.create(
            processo_seletivo=self.processo,
            tipo=Fase.INSCRICAO,
            nome='Inscrições',
            ordem=1,
        )
        with self.assertRaises(ValidationError):
            Fase.objects.create(
                processo_seletivo=self.processo,
                tipo=Fase.INSCRICAO,
                nome='Inscrições 2',
                ordem=2,
            )

    def test_apenas_um_resultado_final(self):
        Fase.objects.create(
            processo_seletivo=self.processo,
            tipo=Fase.RESULTADO_FINAL,
            nome='Resultado',
            ordem=10,
        )
        with self.assertRaises(ValidationError):
            Fase.objects.create(
                processo_seletivo=self.processo,
                tipo=Fase.RESULTADO_FINAL,
                nome='Resultado 2',
                ordem=20,
            )

    def test_inscricao_deve_ser_primeira(self):
        Fase.objects.create(
            processo_seletivo=self.processo,
            tipo=Fase.INTERMEDIARIA,
            nome='Fase Intermediária',
            ordem=1,
        )
        with self.assertRaises(ValidationError):
            Fase.objects.create(
                processo_seletivo=self.processo,
                tipo=Fase.INSCRICAO,
                nome='Inscrições',
                ordem=2,
            )

    def test_resultado_final_deve_ser_ultimo(self):
        Fase.objects.create(
            processo_seletivo=self.processo,
            tipo=Fase.RESULTADO_FINAL,
            nome='Resultado',
            ordem=1,
        )
        with self.assertRaises(ValidationError):
            Fase.objects.create(
                processo_seletivo=self.processo,
                tipo=Fase.INTERMEDIARIA,
                nome='Fase Intermediária',
                ordem=2,
            )

    def test_ordem_fases_valida(self):
        f1 = Fase.objects.create(
            processo_seletivo=self.processo,
            tipo=Fase.INSCRICAO,
            nome='Inscrições',
            ordem=1,
        )
        f2 = Fase.objects.create(
            processo_seletivo=self.processo,
            tipo=Fase.INTERMEDIARIA,
            nome='Análise documental',
            ordem=2,
        )
        f3 = Fase.objects.create(
            processo_seletivo=self.processo,
            tipo=Fase.RESULTADO_FINAL,
            nome='Resultado Final',
            ordem=3,
        )
        self.assertEqual(Fase.objects.filter(processo_seletivo=self.processo).count(), 3)

    def test_clean_fase_com_processo_nao_salvo_nao_quebra(self):
        processo_novo = ProcessoSeletivo(
            titulo='Processo Novo',
            coordenador=self.coord,
        )
        fase = Fase(
            processo_seletivo=processo_novo,
            tipo=Fase.INSCRICAO,
            nome='Inscrições',
            ordem=1,
        )

        fase.clean()


class FaseInlineFormSetTest(TestCase):
    def setUp(self):
        self.coord = Usuario.objects.create_user(
            cpf='12345678901',
            nome='Coordenador',
            email='coord@example.com',
        )

    def _build_formset_data(self, instance, forms_payload):
        formset_class = inlineformset_factory(
            ProcessoSeletivo,
            Fase,
            formset=FaseInlineFormSet,
            fields=('tipo', 'nome', 'ordem'),
            extra=0,
            can_delete=True,
        )
        prefix = formset_class(instance=instance).prefix

        data = {
            f'{prefix}-TOTAL_FORMS': str(len(forms_payload)),
            f'{prefix}-INITIAL_FORMS': '0',
            f'{prefix}-MIN_NUM_FORMS': '0',
            f'{prefix}-MAX_NUM_FORMS': '1000',
        }

        for i, form_data in enumerate(forms_payload):
            data[f'{prefix}-{i}-tipo'] = form_data['tipo']
            data[f'{prefix}-{i}-nome'] = form_data['nome']
            data[f'{prefix}-{i}-ordem'] = str(form_data['ordem'])

        return formset_class(data=data, instance=instance)

    def test_inline_nao_permita_duas_fases_inscricao_no_mesmo_submit(self):
        processo_novo = ProcessoSeletivo(
            titulo='Processo Inline',
            coordenador=self.coord,
        )
        formset = self._build_formset_data(
            processo_novo,
            [
                {'tipo': Fase.INSCRICAO, 'nome': 'Inscrição 1', 'ordem': 1},
                {'tipo': Fase.INSCRICAO, 'nome': 'Inscrição 2', 'ordem': 2},
            ],
        )

        self.assertFalse(formset.is_valid())
        self.assertIn(
            'Já existe uma fase de inscrição neste processo seletivo.',
            formset.non_form_errors(),
        )

    def test_inline_exige_inscricao_com_menor_ordem(self):
        processo_novo = ProcessoSeletivo(
            titulo='Processo Inline',
            coordenador=self.coord,
        )
        formset = self._build_formset_data(
            processo_novo,
            [
                {'tipo': Fase.INTERMEDIARIA, 'nome': 'Análise', 'ordem': 1},
                {'tipo': Fase.INSCRICAO, 'nome': 'Inscrição', 'ordem': 2},
            ],
        )

        self.assertFalse(formset.is_valid())
        self.assertIn(
            'A fase de inscrição deve ser sempre a primeira fase.',
            formset.non_form_errors(),
        )


class EtapaTest(TestCase):
    def setUp(self):
        self.coord = Usuario.objects.create_user(
            cpf='12345678901',
            nome='Coordenador',
            email='coord@example.com',
        )
        self.processo = ProcessoSeletivo.objects.create(
            titulo='Processo Teste',
            coordenador=self.coord,
        )
        self.fase = Fase.objects.create(
            processo_seletivo=self.processo,
            tipo=Fase.INTERMEDIARIA,
            nome='Avaliação',
            ordem=1,
        )

    def test_numero_avaliadores_impar(self):
        etapa = Etapa.objects.create(
            fase=self.fase,
            nome='Análise',
            ordem=1,
            numero_avaliadores=3,
        )
        self.assertEqual(etapa.numero_avaliadores, 3)

    def test_numero_avaliadores_par_invalido(self):
        with self.assertRaises(ValidationError):
            Etapa.objects.create(
                fase=self.fase,
                nome='Análise',
                ordem=1,
                numero_avaliadores=2,
            )
