
Documento de Requisitos de Sistema (DRS)
========================================

Sistema de Gestão de Processos Seletivos
----------------------------------------

1. Introdução
-------------

1.1. Objetivo
^^^^^^^^^^^^^
Este documento descreve os requisitos funcionais, não funcionais, regras de negócio e diretrizes arquiteturais para um sistema web de gestão de processos seletivos de colaboradores para órgão público.

O sistema permite:

* Autenticação via **gov.br**;
* Cadastro e administração de processos seletivos;
* Definição de fases e etapas sequenciais;
* Submissão de inscrição e documentação por candidatos;
* Configuração de formulários por fase;
* Distribuição de inscrições para avaliadores;
* Avaliação, pareceres, notas, checklist e recursos;
* Publicação de resultados parciais e finais;
* Exportação de informações e integração com sistemas externos.

1.2. Escopo
^^^^^^^^^^^
O sistema contempla todo o ciclo de um processo seletivo público, desde a inscrição até a publicação do resultado final, incluindo mecanismos de auditoria, recursos e integração com o SUAP.

1.3. Público-alvo do documento
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Equipe de análise de requisitos;
* Equipe de desenvolvimento;
* Equipe de testes;
* Gestores do órgão;
* Equipe de infraestrutura e segurança da informação.

2. Visão Geral do Sistema
-------------------------

2.1. Descrição Resumida
^^^^^^^^^^^^^^^^^^^^^^
O sistema é uma aplicação web responsiva, acessível mediante autenticação via gov.br para funcionalidades administrativas, de inscrição e acompanhamento. Permite que administradores, coordenadores, avaliadores e candidatos interajam com os processos seletivos conforme seus papéis e permissões.

2.2. Perfis de Usuário
^^^^^^^^^^^^^^^^^^^^^^

Candidato
~~~~~~~~~
Usuário externo que realiza inscrição pública em processo seletivo, envia documentos, preenche formulários, acompanha etapas, visualiza resultados parciais e finais e interpõe recursos.

Administrador
~~~~~~~~~~~~~
Usuário responsável por cadastrar coordenadores no sistema e administrar permissões globais.

Coordenador
~~~~~~~~~~~
Usuário responsável por cadastrar e configurar processos seletivos, fases, etapas, banca do processo, avaliadores e distribuição de inscrições para avaliação.

Avaliador
~~~~~~~~~
Usuário responsável por avaliar as inscrições distribuídas a ele em determinada etapa/fase do processo seletivo.

2.3. Regra de Compatibilidade de Papéis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Um mesmo usuário poderá possuir mais de um papel no sistema, exceto a combinação em um mesmo processo seletivo entre:

* Candidato;
* Avaliador;
* Coordenador;
* Administrador.

Ou seja, o mesmo usuário **não poderá atuar como candidato e como avaliador/coordenador/administrador no mesmo processo seletivo**.

2.4. Forma de Acesso e Páginas Públicas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
O acesso ao sistema será realizado **preferencialmente por autenticação gov.br**. Perfis administrativos e operacionais serão previamente cadastrados.

As funcionalidades públicas (listagem e detalhes de processos seletivos publicados) estarão disponíveis para acesso anônimo, sem necessidade de autenticação. Para garantir o correto funcionamento dessas páginas, o sistema utiliza um usuário anônimo customizado (``CustomAnonymousUser``), que define explicitamente os atributos ``is_coordenador``, ``is_avaliador`` e ``is_candidato`` como ``False``.

3. Requisitos de Negócio
-----------------------

3.1. Estrutura do Processo Seletivo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
O processo seletivo será composto por:

* Fase de inscrição;
* Fases intermediárias livres, definidas pelo coordenador;
* Fase final de resultado.

As fases serão compostas por uma ou mais etapas.

3.2. Regras sobre Fases e Etapas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. As etapas e fases serão sequenciais.
2. O avanço para uma fase seguinte dependerá da habilitação na fase anterior.
3. Somente os candidatos habilitados poderão prosseguir.
4. Uma vez não habilitado em uma fase, o candidato será eliminado do processo seletivo.
5. A quantidade de fases e etapas será variável, conforme o edital.
6. A fase de inscrição deve ser sempre a primeira.
7. A fase de resultado final deve ser sempre a última.
8. Não poderá haver fase anterior à inscrição nem fase posterior ao resultado final.

3.3. Regras sobre Inscrição
^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. A inscrição será sempre pública.
2. Cada candidato poderá manter apenas uma inscrição ativa por processo seletivo.
3. O candidato poderá cancelar a inscrição.
4. Após cancelamento, poderá realizar nova inscrição, observadas as regras e prazos vigentes.

3.4. Regras sobre Documentos
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. Somente arquivos PDF serão aceitos.
2. Cada fase configurará: lista de documentos aceitos/obrigatórios e tamanho máximo por arquivo.
3. O tamanho padrão máximo será de 2 MB por arquivo, salvo configuração diferente pela coordenação.
4. Será permitido apenas 1 arquivo por tipo de documento.
5. O candidato deverá consolidar os documentos em um único PDF por tipo.
6. A ausência de documento obrigatório poderá implicar não habilitação ou eliminação do processo seletivo.
7. Quando o tipo de documento tiver pontuação associada, o candidato poderá informar a pontuação estimada (caráter referencial e não vinculante).
8. O candidato poderá substituir o arquivo enquanto a fase de envio estiver aberta.
9. O sistema deverá manter histórico de envios para auditoria.

3.5. Regras sobre Formulários
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. Os formulários serão configuráveis pelo coordenador.
2. Suporte a campos do tipo: texto, número, data, seleção única, múltipla seleção, checkbox e upload.
3. Cada fase poderá ter envio de formulário, envio de arquivos, ambos ou nenhum.
4. Respostas estruturadas para consulta, análise e exportação.
5. Formulário exibido também na interface de avaliação dos avaliadores.

3.6. Regras sobre Avaliação
^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. As avaliações serão, por padrão, por nota.
2. Permitido parecer textual, checklist, critérios ponderados e aprovação/reprovação.
3. Critérios não mensuráveis deverão ser acompanhados de ateste de aprovado/reprovado e nota para ranqueamento.
4. Uma candidatura poderá ser avaliada por múltiplos avaliadores.
5. O número de avaliadores por candidatura deverá ser **ímpar**: 1, 3, 5, 7 etc.
6. A nota final da candidatura em uma etapa seguirá critério configurado pelo coordenador (média ou soma).
7. O avaliador visualizará apenas os dados da etapa corrente.
8. O avaliador poderá anexar 1 único PDF por avaliação.

3.7. Regras sobre Resultados e Recursos
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. O resultado parcial deverá ser publicado ao final de cada fase.
2. Para o público geral, o resultado parcial será divulgado apenas com o número de inscrição.
3. Para o candidato autenticado, o sistema exibirá notas detalhadas de cada critério e justificativas.
4. O candidato poderá interpor recurso somente contra o resultado parcial da etapa corrente.
5. O resultado final será consolidado automaticamente a partir da última etapa.

3.8. Regras sobre Prazos
^^^^^^^^^^^^^^^^^^^^^^^^
1. Todos os períodos deverão ser configurados com data e hora.
2. O sistema deverá bloquear ações fora do período permitido.
3. Fuso horário oficial do órgão será respeitado.
4. Permitida prorrogação de prazo após publicação, mediante ação autorizada.

3.9. Comunicação e Transparência
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. Envio de avisos aos candidatos por e-mail sobre andamento das etapas.
2. Painel claro de acompanhamento da fase atual, situação de etapas e status de habilitação.
3. Trilha de auditoria completa.
4. Exportação de dados em PDF, CSV, planilha e HTML.

3.10. Integração com SUAP
^^^^^^^^^^^^^^^^^^^^^^^^^
1. Integração ao SUAP para publicação de documentos, cadastro dos selecionados e assinatura eletrônica.

4. Requisitos Funcionais (RF)
-----------------------------

.. list-table::
   :header-rows: 1

   * - Código
     - Descrição
   * - **RF01**
     - Permite autenticação via plataforma gov.br.
   * - **RF02**
     - Permite ao administrador cadastrar coordenadores e permissões globais.
   * - **RF03**
     - Permite o cadastramento prévio de coordenadores autorizados.
   * - **RF04**
     - Permite cadastramento prévio e vinculação de avaliadores a processos/fases.
   * - **RF05**
     - Permite cadastrar, editar, publicar, suspender, prorrogar e encerrar processos seletivos.
   * - **RF06**
     - Permite estruturar fases (fase de inscrição como 1ª e resultado final como última).
   * - **RF07**
     - Permite configurar etapas dentro de cada fase.
   * - **RF08**
     - Controla o fluxo sequencial entre fases/etapas, bloqueando candidatos não habilitados.
   * - **RF09**
     - Permite inscrições públicas em processos seletivos.
   * - **RF10**
     - Permite ao candidato cancelar sua inscrição ativa.
   * - **RF11**
     - Permite nova inscrição após cancelamento dentro do prazo.
   * - **RF12**
     - Permite ao candidato enviar arquivos exclusivamente em formato PDF.
   * - **RF13**
     - Controla obrigatoriedade documental e impede habilitação se ausentes.
   * - **RF14**
     - Permite configurar tamanho máximo de arquivo por fase (padrão 2 MB).
   * - **RF15**
     - Permite substituição de arquivos enquanto o período estiver aberto.
   * - **RF16**
     - Mantém histórico completo de arquivos enviados e substituídos.
   * - **RF17**
     - Permite ao coordenador criar e configurar formulários por fase.
   * - **RF18**
     - Suporta diversos tipos de campos de formulário.
   * - **RF19**
     - Armazena respostas de formulários de forma estruturada.
   * - **RF20**
     - Registra avaliações por múltiplos avaliadores (nota, parecer, checklist, critérios).
   * - **RF21**
     - Garante número ímpar de avaliadores por candidatura.
   * - **RF22**
     - Calcula nota final da etapa por média ou soma.
   * - **RF23**
     - Restringe a visão do avaliador apenas aos dados da etapa corrente.
   * - **RF24**
     - Permite ao avaliador anexar 1 PDF por avaliação.
   * - **RF25**
     - Permite publicação de resultados parciais por fase.
   * - **RF26**
     - Divulga resultado parcial público apenas com o número de inscrição.
   * - **RF27**
     - Exibe ao candidato autenticado suas notas detalhadas e justificativas.
   * - **RF28**
     - Permite interposição de recurso contra resultado parcial da etapa corrente.
   * - **RF29**
     - Permite registrar e publicar respostas a recursos.
   * - **RF30**
     - Consolida automaticamente o resultado final a partir da última etapa.
   * - **RF31**
     - Bloqueia ações fora dos prazos configurados.
   * - **RF32**
     - Envia notificações por e-mail aos candidatos.
   * - **RF33**
     - Exibe painel de acompanhamento de status e habilitação ao candidato.
   * - **RF34**
     - Registra trilha de auditoria completa de acessos, alterações e avaliações.
   * - **RF35**
     - Permite exportação de dados em PDF, CSV, planilha e HTML.
   * - **RF36**
     - Disponibiliza relatórios gerenciais para coordenação e administração.
   * - **RF37**
     - Integração com SUAP para publicação de documentos e cadastro de selecionados.
   * - **RF38**
     - Mascara dados pessoais em visões públicas.
   * - **RF39**
     - Aplica controle de acesso estrito baseado em perfis.

5. Requisitos Não Funcionais (RNF)
----------------------------------

* **RNF01 — Segurança:** Autenticação via gov.br e padrões de segurança governamentais.
* **RNF02 — Conformidade Legal:** Atendimento à LGPD, Marco Civil da Internet e acessibilidade (eMAG/WCAG).
* **RNF03 — Controle de Acesso:** Baseado em perfis e permissões granulares.
* **RNF04 — Auditoria:** Registros auditáveis imutáveis de ações relevantes.
* **RNF05 — Desempenho:** Suporte a alta carga durante picos de inscrição e publicação de resultados.
* **RNF06 — Disponibilidade:** Alta disponibilidade nos períodos críticos do edital.
* **RNF07 — Usabilidade:** Interface intuitiva e acessível.
* **RNF08 — Acessibilidade:** Conformidade WCAG 2.1 nível AA.
* **RNF09 — Responsividade:** Interface adaptável para dispositivos móveis e desktop.
* **RNF10 — Compatibilidade:** Suporte aos navegadores modernos.
* **RNF11 — Fuso Horário:** Respeita fuso horário oficial configurado.
* **RNF12 — Portabilidade:** Implantação via containers Docker em infraestrutura própria.

6. Arquitetura do Software
--------------------------

* **Banco de dados:** PostgreSQL 16+
* **Linguagem:** Python 3.14 / 3.12
* **Framework web:** Django 5
* **Processamento Assíncrono:** Celery + Redis
* **Observabilidade:** Sentry

7. Auditoria e Rastreabilidade
------------------------------

Eventos auditados incluem: login/acesso, alteração de processos seletivos, envio e substituição de arquivos, submissão de formulários, avaliações, recursos, respostas e publicações de resultados. Cada registro de auditoria armazena usuário, data/hora, ação, objeto afetado, valor anterior e posterior.

8. Considerações Finais
-----------------------

O presente DRS norteia todo o desenvolvimento, homologação e implantação do Sistema de Gestão de Processos Seletivos.
