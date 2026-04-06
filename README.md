# Processo Seletivo

Sistema web para gestão de processos seletivos, inscrições, avaliações, recursos e resultados. Desenvolvido em Django, Celery e REST Framework, com suporte a autenticação via gov.br e integração com SUAP.

## Funcionalidades
- Cadastro e gerenciamento de processos seletivos
- Inscrições online
- Avaliações e recursos
- Publicação de resultados
- Auditoria de ações
- Integração gov.br OAuth2
- Integração SUAP

## Requisitos
- Docker
- Docker Compose

## Subindo o projeto

1. Clone o repositório:

```bash
git clone git@github.com:kelsoncm/processo-seletivo.git ~/projetos/PESSOAL/processo-seletivo
cd ~/projetos/PESSOAL/processo-seletivo
```

2. Copie o arquivo de variáveis de ambiente e ajuste conforme necessário:

```bash
cp .env.example .env
```

3. Suba os serviços com Docker Compose:

```bash
docker compose up --build
```

4. Acesse o sistema em [http://localhost:8000](http://localhost:8000)

## Estrutura dos Serviços
- **web**: Django + Celery
- **db**: PostgreSQL
- **redis**: Broker para Celery

## Variáveis de Ambiente Disponíveis

As seguintes variáveis de ambiente podem ser informadas ao subir a imagem para customizar o comportamento do sistema:

- `SECRET_KEY`: Chave secreta do Django.
- `DEBUG`: Ativa/desativa modo debug (True/False).
- `ALLOWED_HOSTS`: Hosts permitidos, separados por vírgula (ex: "localhost,127.0.0.1").
- `DB_ENGINE`: Backend do banco de dados (ex: django.db.backends.postgresql, django.db.backends.sqlite3).
- `DB_NAME`: Nome do banco de dados ou caminho do arquivo SQLite.
- `DB_USER`: Usuário do banco de dados.
- `DB_PASSWORD`: Senha do banco de dados.
- `DB_HOST`: Host do banco de dados.
- `DB_PORT`: Porta do banco de dados.
- `TIME_ZONE`: Fuso horário (ex: America/Sao_Paulo).
- `CELERY_BROKER_URL`: URL do broker do Celery (ex: redis://cache:6379/0).
- `CELERY_RESULT_BACKEND`: Backend de resultados do Celery.
- `SENTRY_DSN`: DSN do Sentry para monitoramento de erros (opcional).
- `GOVBR_CLIENT_ID`: Client ID do gov.br OAuth2.
- `GOVBR_CLIENT_SECRET`: Client Secret do gov.br OAuth2.
- `GOVBR_AUTHORIZATION_URL`: URL de autorização do gov.br.
- `GOVBR_TOKEN_URL`: URL de token do gov.br.
- `GOVBR_USERINFO_URL`: URL de userinfo do gov.br.
- `GOVBR_REDIRECT_URI`: Redirect URI do gov.br.
- `EMAIL_BACKEND`: Backend de e-mail do Django.
- `EMAIL_HOST`: Host SMTP.
- `EMAIL_PORT`: Porta SMTP.
- `EMAIL_USE_TLS`: Usar TLS (True/False).
- `EMAIL_HOST_USER`: Usuário SMTP.
- `EMAIL_HOST_PASSWORD`: Senha SMTP.
- `DEFAULT_FROM_EMAIL`: E-mail padrão do remetente.
- `SUAP_BASE_URL`: URL base da API SUAP.
- `SUAP_API_TOKEN`: Token de API do SUAP.
- `SUAP_OAUTH_CLIENT_ID`: Client ID do SUAP OAuth2.
- `SUAP_OAUTH_CLIENT_SECRET`: Client Secret do SUAP OAuth2.
- `SUAP_OAUTH_AUTHORIZATION_URL`: URL de autorização do SUAP OAuth2.
- `SUAP_OAUTH_TOKEN_URL`: URL de token do SUAP OAuth2.
- `SUAP_OAUTH_USERINFO_URL`: URL de userinfo do SUAP OAuth2.
- `SUAP_OAUTH_REDIRECT_URI`: Redirect URI do SUAP OAuth2.

### Exemplo de bloco environment no docker-compose.yml

```yaml
    environment:
      - SECRET_KEY=uma-chave-secreta
      - DEBUG=True
      - ALLOWED_HOSTS=localhost,127.0.0.1
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=postgres
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_HOST=db
      - DB_PORT=5432
      - TIME_ZONE=America/Sao_Paulo
      - CELERY_BROKER_URL=redis://cache:6379/0
      - CELERY_RESULT_BACKEND=redis://cache:6379/0
      - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
      - EMAIL_HOST=mail
      - EMAIL_PORT=1025
      - EMAIL_USE_TLS=False
      - EMAIL_HOST_USER=''
      - EMAIL_HOST_PASSWORD=''
      - DEFAULT_FROM_EMAIL='noreply@example.gov.br'
      # Adicione outras variáveis conforme necessário
```

## Rodando migrações e criando superusuário

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Testes

```bash
docker compose exec web python manage.py test
```

## Atualizando o uv

Para atualizar o uv (gerenciador de dependências Python ultrarrápido) no ambiente Docker, execute:

```bash
docker compose run --rm web uv pip install --upgrade uv
```

Se desejar atualizar o uv.lock após atualizar o uv ou requirements.txt:

```bash
docker compose run --rm web uv pip compile -o uv.lock requirements.txt
```

E para o ambiente de desenvolvimento:

```bash
docker compose run --rm web uv pip compile -o uv-dev.lock requirements-dev.txt
```

## Licença
MIT