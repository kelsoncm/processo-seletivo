
Guia de Início Rápido
=====================

Este guia apresenta os passos necessários para configurar e executar o **Sistema de Gestão de Processos Seletivos** em seu ambiente de desenvolvimento ou produção local.

📋 Requisitos Prévios
---------------------

Antes de iniciar, certifique-se de ter instalado em sua máquina:

* **Docker** (versão 20.10 ou superior)
* **Docker Compose** (versão 2.0 ou superior)
* **Python** (3.12+ / 3.14+)
* **Git**

🚀 Passos para Instalação e Execução
-------------------------------------

1. Clonar o Repositório
^^^^^^^^^^^^^^^^^^^^^^^

Execute o comando abaixo para clonar o repositório em seu ambiente local:

.. code-block:: bash

   git clone git@github.com:kelsoncm/processo-seletivo.git ~/projetos/PESSOAL/processo-seletivo
   cd ~/projetos/PESSOAL/processo-seletivo

2. Configurar Arquivo de Ambiente (.env)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Copie o arquivo de exemplo e ajuste as variáveis de ambiente conforme necessário:

.. code-block:: bash

   cp .env.example .env

3. Subir os Serviços com Docker Compose ou CLI ``prosel``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Utilizando Docker Compose:

.. code-block:: bash

   docker compose up --build -d

Ou utilizando a CLI inclusa no projeto (``prosel``):

.. code-block:: bash

   ./prosel deploy

4. Executar Migrações do Banco de Dados
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Para aplicar as migrações no banco PostgreSQL:

.. code-block:: bash

   ./prosel migrate web

5. Criar Usuário Administrador
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Para criar um superusuário no Django:

.. code-block:: bash

   ./prosel manage web createsuperuser

6. Coletar Arquivos Estáticos (Opcional em Dev)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   ./prosel collectstatic web

7. Acessar o Sistema
^^^^^^^^^^^^^^^^^^^^

Após subir os serviços, acesse o sistema no navegador:

* **Aplicação Principal:** `http://localhost:8000 <http://localhost:8000>`_
* **Painel Administrativo:** `http://localhost:8000/admin <http://localhost:8000/admin>`_

🧪 Executando Testes Unitários
------------------------------

Para rodar a suíte de testes com cobertura de código:

.. code-block:: bash

   ./prosel test web

Isso executará o ``coverage`` e gerará relatórios em terminal e em HTML.
