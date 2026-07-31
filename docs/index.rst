
Sistema de Gestão de Processos Seletivos
========================================

.. image:: https://img.shields.io/badge/python-3.12%20%7C%203.14-blue.svg
   :target: https://www.python.org/
   :alt: Python Versions

.. image:: https://img.shields.io/badge/django-5.0+-green.svg
   :target: https://www.djangoproject.com/
   :alt: Django Versions

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

.. image:: https://img.shields.io/badge/gov.br-OAuth2-blue.svg
   :target: https://www.gov.br/
   :alt: Gov.BR Auth

Sistema web para gestão completa de processos seletivos públicos de colaboradores, abrangendo inscrições online, formulários dinâmicos, envio de documentação em PDF, distribuição para banca avaliadora, interposição de recursos e publicação de resultados.

.. note::
   🌐 **Documentação do Projeto**: Esta documentação reúne o Guia de Início Rápido, Guia de Execução & Arquitetura, Guia de Contribuição e o Documento de Requisitos de Sistema (DRS).

📋 Conteúdo da Documentação
---------------------------

.. toctree::
   :maxdepth: 2
   :caption: Sumário:

   start-guide
   execution
   contribute
   drs

✨ Funcionalidades Principais
-----------------------------

* 🔐 **Autenticação Integrada**: Login unificado via **gov.br** (OAuth2) e integração com o **SUAP**.
* 📋 **Gestão de Processos Seletivos**: Cadastro de editais, fases sequenciais (Inscrição, Fases Intermediárias e Resultado Final) e etapas personalizadas.
* 📝 **Formulários Dinâmicos**: Criação de formulários customizáveis por fase com validações de dados e armazenamento estruturado.
* 📄 **Gestão de Documentos PDF**: Envio de comprovantes em formato PDF com controle de obrigatoriedade e limite de tamanho (padrão 2 MB).
* ⚖️ **Banca Avaliadora Flexível**: Avaliação por múltiplos avaliadores com garantia de número ímpar (1, 3, 5, 7...), notas, checklists e pareceres.
* 📣 **Resultados e Transparência**: Divulgação pública resumida (nº de inscrição) e visão detalhada para o candidato autenticado.
* 💬 **Módulo de Recursos**: Formulário específico para interposição e resposta a recursos sobre os resultados parciais.
* 🛡️ **Auditoria & Rastreabilidade**: Trilha de auditoria detalhada armazenando usuário, data/hora e valores alterados em todas as operações críticas.

🏗️ Módulos da Aplicação
-----------------------

A aplicação Django está dividida nos seguintes aplicativos principais dentro de ``src/``:

.. list-table::
   :header-rows: 1

   * - Módulo
     - Descrição
   * - ``accounts``
     - Gerenciamento de usuários, perfis (Candidato, Administrador, Coordenador, Avaliador) e ``CustomAnonymousUser``.
   * - ``processos``
     - Estruturação de processos seletivos, fases, etapas e controle de prazos.
   * - ``inscricoes``
     - Submissão de inscrições, cancelamento, reinscrição e upload de PDFs.
   * - ``formularios``
     - Motor de formulários configuráveis e armazenamento de respostas.
   * - ``avaliacoes``
     - Distribuição de inscrições para a banca, notas, pareceres e critérios.
   * - ``recursos``
     - Gestão de recursos interpostos por candidatos e publicação de respostas.
   * - ``resultados``
     - Consolidação e publicação de resultados parciais e finais.
   * - ``auditoria``
     - Log centralizado de ações e eventos auditáveis.
   * - ``tema``
     - Componentes visuais e integração com o Design System Gov.BR e AdminLTE.

🚀 Início Rápido (Comandos CLI ``prosel``)
------------------------------------------

Para iniciar rapidamente o ambiente de desenvolvimento via Docker:

.. code-block:: bash

   # 1. Clonar repositório e configurar ambiente
   git clone git@github.com:kelsoncm/processo-seletivo.git
   cd processo-seletivo
   cp .env.example .env

   # 2. Subir os serviços com o utilitário prosel
   ./prosel deploy

   # 3. Aplicar migrações e criar superusuário
   ./prosel migrate web
   ./prosel manage web createsuperuser

   # 4. Executar os testes automatizados
   ./prosel test web

Acesse a aplicação em `http://localhost:8000 <http://localhost:8000>`_.

📝 Licença
----------

Este projeto está licenciado sob a Licença MIT.

👥 Contato & Suporte
--------------------

**Kelson da Costa Medeiros**

* **Email**: kelsoncm@gmail.com
* **GitHub**: `@kelsoncm <https://github.com/kelsoncm>`_
