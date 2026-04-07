import os

from django.db import migrations, models


def _get_env_bool(name, default):
    raw = os.getenv(name)
    if raw is None:
        return default

    value = raw.strip().lower()
    if value in {'1', 'true', 't', 'yes', 'y', 'on'}:
        return True
    if value in {'0', 'false', 'f', 'no', 'n', 'off'}:
        return False
    return default


def sync_auth_methods_from_env(apps, schema_editor):
    ConfiguracaoAutenticacao = apps.get_model('accounts', 'ConfiguracaoAutenticacao')
    config, _ = ConfiguracaoAutenticacao.objects.get_or_create(pk=1)

    config.govbr_habilitado = _get_env_bool('AUTH_GOVBR_HABILITADO', True)
    config.suap_habilitado = _get_env_bool('AUTH_SUAP_HABILITADO', True)
    config.django_habilitado = _get_env_bool('AUTH_DJANGO_HABILITADO', True)
    config.save(update_fields=['govbr_habilitado', 'suap_habilitado', 'django_habilitado'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_configuracaoautenticacao_usuario_suap_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuracaoautenticacao',
            name='suap_habilitado',
            field=models.BooleanField(default=True, verbose_name='SUAP habilitado'),
        ),
        migrations.AlterField(
            model_name='configuracaoautenticacao',
            name='django_habilitado',
            field=models.BooleanField(default=True, verbose_name='Login nativo (Django) habilitado'),
        ),
        migrations.RunPython(sync_auth_methods_from_env, migrations.RunPython.noop),
    ]
