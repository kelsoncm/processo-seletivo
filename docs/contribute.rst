
🔧 Guia de Desenvolvimento e Contribuição
=========================================

Agradecemos o interesse em contribuir com o **Sistema de Gestão de Processos Seletivos**! Este documento orienta o ambiente de desenvolvimento, padrões de código e fluxo de contribuição.

💻 Setup de Desenvolvimento Local
----------------------------------

1. Ambiente Virtual Python
^^^^^^^^^^^^^^^^^^^^^^^^^^

Para desenvolvimento local fora do container (autocompletar na IDE, linting local, etc.):

.. code-block:: bash

   # Criar o ambiente virtual
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou: .venv\Scripts\activate  # Windows

   # Instalar dependências de desenvolvimento
   pip install -r src/requirements.txt
   pip install -r src/requirements-dev.txt

2. Hooks de Pre-commit
^^^^^^^^^^^^^^^^^^^^^^

Configure o pre-commit para formatar e verificar o código automaticamente antes dos commits:

.. code-block:: bash

   pre-commit install --hook-type pre-push --hook-type pre-commit

🎨 Padrões de Código e Formatação
---------------------------------

O projeto adota ferramentas automatizadas para manter a qualidade e padronização do código:

* **Black**: Formatador de código Python padrão (linha máx: 120 caracteres).
* **Ruff**: Linter ultrarrápido para checagem de erros e conformidade PEP 8.
* **doc8**: Linter para validação dos arquivos de documentação em reStructuredText (``.rst``).

Para formatar o código manualmente via CLI ``prosel``:

.. code-block:: bash

   ./prosel lint web

🧪 Testes Automatizados
-----------------------

Toda nova funcionalidade ou correção de bug deve ser acompanhada de testes unitários ou de integração.

.. code-block:: bash

   # Rodar os testes via prosel CLI
   ./prosel test web

   # Ou rodar pytest localmente no ambiente virtual
   pytest src/

👥 Fluxo de Contribuição Git
----------------------------

1. Faça um **Fork** do repositório.
2. Crie uma branch para sua modificação:

   .. code-block:: bash

      git checkout -b feature/MinhaNovaFuncionalidade

3. Garanta que os testes e linters estejam passando.
4. Escreva commits claros e objetivos:

   .. code-block:: bash

      git commit -m "feat(inscricoes): adiciona restricao de tamanho maximo de PDF"

5. Envie a branch para o seu repositório remoto:

   .. code-block:: bash

      git push origin feature/MinhaNovaFuncionalidade

6. Abra um **Pull Request (PR)** detalhando as alterações efetuadas.
