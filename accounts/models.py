from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class ConfiguracaoAutenticacao(models.Model):
    """
    Configuração singleton dos meios de autenticação habilitados no sistema.
    Apenas uma instância é permitida (pk=1).
    """

    govbr_habilitado = models.BooleanField('gov.br habilitado', default=True)
    suap_habilitado = models.BooleanField('SUAP habilitado', default=False)
    django_habilitado = models.BooleanField('Login nativo (Django) habilitado', default=False)

    class Meta:
        verbose_name = 'Configuração de Autenticação'
        verbose_name_plural = 'Configuração de Autenticação'

    def __str__(self):
        return 'Configuração de Autenticação'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance


class UsuarioManager(BaseUserManager):
    def create_user(self, cpf, nome, email, password=None, **extra_fields):
        if not cpf:
            raise ValueError('O CPF é obrigatório')
        email = self.normalize_email(email)
        user = self.model(cpf=cpf, nome=nome, email=email, **extra_fields)
        user.set_unusable_password()
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, nome, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(cpf, nome, email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Usuário do sistema. Suporta autenticação via gov.br, SUAP OAuth2 ou login nativo Django.
    Pode ter múltiplos papéis (Administrador, Coordenador, Avaliador, Candidato).
    """

    cpf = models.CharField('CPF', max_length=11, unique=True)
    nome = models.CharField('Nome completo', max_length=255)
    email = models.EmailField('E-mail', unique=True)
    govbr_sub = models.CharField('ID gov.br', max_length=255, blank=True, null=True, unique=True)
    suap_id = models.CharField('ID SUAP', max_length=255, blank=True, null=True, unique=True)

    is_active = models.BooleanField('Ativo', default=True)
    is_staff = models.BooleanField('Equipe', default=False)

    data_criacao = models.DateTimeField('Data de criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de atualização', auto_now=True)

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['nome', 'email']

    objects = UsuarioManager()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} ({self.cpf})'

    @property
    def is_administrador(self):
        return self.papeis.filter(tipo=Papel.ADMINISTRADOR).exists()

    @property
    def is_coordenador(self):
        return self.papeis.filter(tipo=Papel.COORDENADOR).exists()

    @property
    def is_avaliador(self):
        return self.papeis.filter(tipo=Papel.AVALIADOR).exists()

    @property
    def is_candidato(self):
        return self.papeis.filter(tipo=Papel.CANDIDATO).exists()


class Papel(models.Model):
    """
    Papel de um usuário no sistema. Um usuário pode ter múltiplos papéis.
    Restrição: no mesmo processo seletivo, um usuário não pode ser
    candidato e avaliador/coordenador/administrador simultaneamente.
    """

    ADMINISTRADOR = 'ADMINISTRADOR'
    COORDENADOR = 'COORDENADOR'
    AVALIADOR = 'AVALIADOR'
    CANDIDATO = 'CANDIDATO'

    TIPO_CHOICES = [
        (ADMINISTRADOR, 'Administrador'),
        (COORDENADOR, 'Coordenador'),
        (AVALIADOR, 'Avaliador'),
        (CANDIDATO, 'Candidato'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='papeis')
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    processo_seletivo = models.ForeignKey(
        'processos.ProcessoSeletivo',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='papeis',
        help_text='Se nulo, o papel é global (Administrador). Se definido, é específico do processo.',
    )

    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Papel'
        verbose_name_plural = 'Papéis'
        unique_together = ('usuario', 'tipo', 'processo_seletivo')

    def __str__(self):
        if self.processo_seletivo:
            return f'{self.usuario} — {self.get_tipo_display()} em {self.processo_seletivo}'
        return f'{self.usuario} — {self.get_tipo_display()}'

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.processo_seletivo:
            return

        papeis_incompativeis = [self.ADMINISTRADOR, self.COORDENADOR, self.AVALIADOR, self.CANDIDATO]
        if self.tipo not in papeis_incompativeis:
            return

        papeis_existentes = Papel.objects.filter(
            usuario=self.usuario,
            processo_seletivo=self.processo_seletivo,
        ).exclude(pk=self.pk)

        if self.tipo == self.CANDIDATO:
            conflito = papeis_existentes.filter(tipo__in=[self.ADMINISTRADOR, self.COORDENADOR, self.AVALIADOR])
        else:
            conflito = papeis_existentes.filter(tipo=self.CANDIDATO)

        if conflito.exists():
            raise ValidationError(
                'Um usuário não pode ser candidato e avaliador/coordenador/administrador '
                'no mesmo processo seletivo.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
