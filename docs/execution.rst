
⚙️ Execução, Arquitetura e Deploy
=================================

Este documento detalha a arquitetura de infraestrutura, os serviços gerenciados pelo Docker Compose, as variáveis de ambiente e o funcionamento da ferramenta de linha de comando ``prosel``.

🏗️ Estrutura dos Serviços
-------------------------

O sistema é composto por 3 contêineres e serviços principais:

.. list-table::
   :header-rows: 1

   * - Serviço
     - Tecnologia
     - Função
   * - **web**
     - Django 5 + Celery Worker
     - Servidor de aplicação web, APIs REST, painel administrativo e processamento de filas de tarefas assíncronas.
   * - **db**
     - PostgreSQL 16+
     - Banco de dados relacional para persistência de dados de usuários, processos seletivos, inscrições e avaliações.
   * - **cache / redis**
     - Redis
     - Broker de mensagens para o Celery e camada de armazenamento de sessão/cache.

🔑 Variáveis de Ambiente
------------------------

As variáveis de ambiente customizam o comportamento da aplicação em dev e produção.

Configuração Geral e Banco de Dados
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``SECRET_KEY``: Chave secreta única do Django.
* ``DEBUG``: ``True`` para desenvolvimento ou ``False`` para produção.
* ``ALLOWED_HOSTS``: Lista de domínios ou IPs permitidos (ex: ``"localhost,127.0.0.1,seusistema.gov.br"``).
* ``DB_ENGINE``: Backend de banco de dados (ex: ``django.db.backends.postgresql``).
* ``DB_NAME``: Nome do banco de dados PostgreSQL.
* ``DB_USER``: Usuário do banco de dados.
* ``DB_PASSWORD``: Senha do banco de dados.
* ``DB_HOST``: Host do banco de dados (ex: ``db`` no Docker Compose).
* ``DB_PORT``: Porta do banco de dados (padrão: ``5432``).
* ``TIME_ZONE``: Fuso horário da aplicação (ex: ``America/Sao_Paulo``).

Celery & Redis
^^^^^^^^^^^^^^

* ``CELERY_BROKER_URL``: URL de conexão com Redis (ex: ``redis://cache:6379/0``).
* ``CELERY_RESULT_BACKEND``: Backend de resultados do Celery.

Autenticação Gov.BR (OAuth2)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``GOVBR_CLIENT_ID``: Client ID registrado na plataforma gov.br.
* ``GOVBR_CLIENT_SECRET``: Client Secret do gov.br.
* ``GOVBR_AUTHORIZATION_URL``: URL de autorização OAuth2.
* ``GOVBR_TOKEN_URL``: URL para obtenção de token de acesso.
* ``GOVBR_USERINFO_URL``: URL para consulta de dados do usuário autenticado.
* ``GOVBR_REDIRECT_URI``: URI de redirecionamento autorizada.

Integração SUAP
^^^^^^^^^^^^^^^

* ``SUAP_BASE_URL``: URL base da API do SUAP.
* ``SUAP_API_TOKEN``: Token de autenticação da API SUAP.
* ``SUAP_OAUTH_CLIENT_ID``: Client ID OAuth2 do SUAP.
* ``SUAP_OAUTH_CLIENT_SECRET``: Client Secret OAuth2 do SUAP.

Observabilidade e E-mail
^^^^^^^^^^^^^^^^^^^^^^^^

* ``SENTRY_DSN``: DSN para envio de relatórios de erros ao Sentry (opcional).
* ``EMAIL_BACKEND``: Backend de envio de e-mail do Django.
* ``EMAIL_HOST``: Host SMTP.
* ``EMAIL_PORT``: Porta SMTP.
* ``DEFAULT_FROM_EMAIL``: Endereço de e-mail do remetente do sistema.

🛠️ Utilitário de Linha de Comando (CLI ``prosel``)
--------------------------------------------------

O projeto fornece o script `./prosel` para facilitar a execução de comandos administrativos no ambiente Docker.

Comandos Frequentes:
^^^^^^^^^^^^^^^^^^^^

* **Iniciar ambiente em segundo plano:**

  .. code-block:: bash

     ./prosel deploy

* **Reiniciar serviços:**

  .. code-block:: bash

     ./prosel relaunch web

* **Acompanhar logs:**

  .. code-block:: bash

     ./prosel launch web

* **Executar migrações do banco:**

  .. code-block:: bash

     ./prosel migrate web

* **Criar novas migrações:**

  .. code-block:: bash

     ./prosel makemigrations web

* **Criar superusuário:**

  .. code-block:: bash

     ./prosel manage web createsuperuser

* **Executar testes e cobertura:**

  .. code-block:: bash

     ./prosel test web

* **Rodar linter de código:**

  .. code-block:: bash

     ./prosel lint web

* **Derrubar ambiente e limpar volumes:**

  .. code-block:: bash

     ./prosel undeploy
