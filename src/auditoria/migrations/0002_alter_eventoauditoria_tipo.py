from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auditoria', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventoauditoria',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('ACESSO', 'Acesso ao sistema'),
                    ('LOGIN', 'Login'),
                    ('LOGOUT', 'Logout'),
                    ('CRIACAO', 'Criação'),
                    ('ALTERACAO', 'Alteração'),
                    ('EXCLUSAO', 'Exclusão'),
                    ('PUBLICACAO', 'Publicação de resultado'),
                    ('INSCRICAO', 'Inscrição'),
                    ('CANCELAMENTO', 'Cancelamento de inscrição'),
                    ('ENVIO_DOCUMENTO', 'Envio/substituição de documento'),
                    ('AVALIACAO', 'Avaliação'),
                    ('RECURSO', 'Interposição de recurso'),
                    ('RESPOSTA_RECURSO', 'Resposta a recurso'),
                    ('INTEGRACAO', 'Integração externa'),
                    ('PRORROGACAO', 'Prorrogação de prazo'),
                    ('FORMULARIO', 'Preenchimento de formulário'),
                ],
                max_length=30,
                verbose_name='Tipo de evento',
            ),
        ),
    ]
