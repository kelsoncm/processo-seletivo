import hashlib
import os
import urllib.parse

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.views import View

from auditoria.models import EventoAuditoria

from .models import ConfiguracaoAutenticacao, Usuario


def _get_govbr_auth_url(request, state):
    params = {
        'response_type': 'code',
        'client_id': settings.GOVBR_CLIENT_ID,
        'redirect_uri': settings.GOVBR_REDIRECT_URI,
        'scope': 'openid email profile',
        'state': state,
        'nonce': hashlib.sha256(os.urandom(16)).hexdigest(),
    }
    return f"{settings.GOVBR_AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"


def _get_suap_auth_url(request, state):
    params = {
        'response_type': 'code',
        'client_id': settings.SUAP_OAUTH_CLIENT_ID,
        'redirect_uri': settings.SUAP_OAUTH_REDIRECT_URI,
        'scope': 'identificacao email',
        'state': state,
    }
    return f"{settings.SUAP_OAUTH_AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"


class LoginView(View):
    """Exibe os meios de autenticação habilitados para o usuário escolher."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        config = ConfiguracaoAutenticacao.get_instance()

        govbr_auth_url = None
        if config.govbr_habilitado:
            state = hashlib.sha256(os.urandom(16)).hexdigest()
            request.session['govbr_state'] = state
            govbr_auth_url = _get_govbr_auth_url(request, state)

        suap_auth_url = None
        if config.suap_habilitado:
            state = hashlib.sha256(os.urandom(16)).hexdigest()
            request.session['suap_state'] = state
            suap_auth_url = _get_suap_auth_url(request, state)

        return render(request, 'accounts/login.html', {
            'govbr_auth_url': govbr_auth_url,
            'suap_auth_url': suap_auth_url,
            'django_habilitado': config.django_habilitado,
        })


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            EventoAuditoria.registrar(
                tipo=EventoAuditoria.ACESSO,
                acao='Logout',
                usuario=request.user,
                origem=request.META.get('REMOTE_ADDR', ''),
            )
        logout(request)
        return redirect('accounts:login')


class CallbackView(View):
    """Processa o callback do gov.br após autenticação."""

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        stored_state = request.session.pop('govbr_state', None)

        if not code or state != stored_state:
            messages.error(request, 'Falha na autenticação. Tente novamente.')
            return redirect('accounts:login')

        try:
            token_data = self._exchange_code(code)
            access_token = token_data.get('access_token')
            user_info = self._get_user_info(access_token)

            usuario = self._get_or_create_user(user_info)
            login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')

            EventoAuditoria.registrar(
                tipo=EventoAuditoria.ACESSO,
                acao='Login via gov.br',
                usuario=usuario,
                origem=request.META.get('REMOTE_ADDR', ''),
            )

            return redirect(settings.LOGIN_REDIRECT_URL)

        except Exception as exc:
            messages.error(request, f'Erro na autenticação: {exc}')
            return redirect('accounts:login')

    def _exchange_code(self, code):
        response = requests.post(
            settings.GOVBR_TOKEN_URL,
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': settings.GOVBR_REDIRECT_URI,
                'client_id': settings.GOVBR_CLIENT_ID,
                'client_secret': settings.GOVBR_CLIENT_SECRET,
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def _get_user_info(self, access_token):
        response = requests.get(
            settings.GOVBR_USERINFO_URL,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def _get_or_create_user(self, user_info):
        sub = user_info.get('sub')
        cpf = user_info.get('cpf', '').replace('.', '').replace('-', '')
        nome = user_info.get('name', '')
        email = user_info.get('email', '')

        usuario, created = Usuario.objects.get_or_create(
            govbr_sub=sub,
            defaults={'cpf': cpf, 'nome': nome, 'email': email},
        )

        if not created:
            updated = False
            if nome and usuario.nome != nome:
                usuario.nome = nome
                updated = True
            if email and usuario.email != email:
                usuario.email = email
                updated = True
            if updated:
                usuario.save()

        return usuario


class SuapCallbackView(View):
    """Processa o callback do SUAP OAuth2 após autenticação."""

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        stored_state = request.session.pop('suap_state', None)

        if not code or state != stored_state:
            messages.error(request, 'Falha na autenticação via SUAP. Tente novamente.')
            return redirect('accounts:login')

        try:
            token_data = self._exchange_code(code)
            access_token = token_data.get('access_token')
            user_info = self._get_user_info(access_token)

            usuario = self._get_or_create_user(user_info)
            login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')

            EventoAuditoria.registrar(
                tipo=EventoAuditoria.ACESSO,
                acao='Login via SUAP',
                usuario=usuario,
                origem=request.META.get('REMOTE_ADDR', ''),
            )

            return redirect(settings.LOGIN_REDIRECT_URL)

        except Exception as exc:
            messages.error(request, f'Erro na autenticação via SUAP: {exc}')
            return redirect('accounts:login')

    def _exchange_code(self, code):
        response = requests.post(
            settings.SUAP_OAUTH_TOKEN_URL,
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': settings.SUAP_OAUTH_REDIRECT_URI,
                'client_id': settings.SUAP_OAUTH_CLIENT_ID,
                'client_secret': settings.SUAP_OAUTH_CLIENT_SECRET,
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def _get_user_info(self, access_token):
        response = requests.get(
            settings.SUAP_OAUTH_USERINFO_URL,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def _get_or_create_user(self, user_info):
        raw_id = user_info.get('identificacao')
        if not raw_id:
            raise ValueError('SUAP não retornou identificação do usuário.')
        suap_id = str(raw_id)
        cpf = user_info.get('cpf', '').replace('.', '').replace('-', '')
        nome = user_info.get('nome_usual') or user_info.get('nome', '')
        email = user_info.get('email', '') or user_info.get('email_secundario', '')

        usuario, created = Usuario.objects.get_or_create(
            suap_id=suap_id,
            defaults={'cpf': cpf, 'nome': nome, 'email': email},
        )

        if not created:
            updated = False
            if nome and usuario.nome != nome:
                usuario.nome = nome
                updated = True
            if email and usuario.email != email:
                usuario.email = email
                updated = True
            if updated:
                usuario.save()

        return usuario


class DjangoLoginView(View):
    """Login nativo Django com CPF e senha."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        form = AuthenticationForm(request=request)
        return render(request, 'accounts/login_django.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
            EventoAuditoria.registrar(
                tipo=EventoAuditoria.ACESSO,
                acao='Login nativo (Django)',
                usuario=usuario,
                origem=request.META.get('REMOTE_ADDR', ''),
            )
            return redirect(settings.LOGIN_REDIRECT_URL)
        return render(request, 'accounts/login_django.html', {'form': form})
