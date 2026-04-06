# Acesso anônimo

Usuários não autenticados (anônimos) podem acessar as seguintes funcionalidades:

1. **Página inicial (front page):** listagem de processos seletivos publicados.
2. **Detalhes do processo seletivo:** visualizar informações completas de um processo seletivo publicado.

Funcionalidades administrativas e de inscrição continuam restritas a usuários autenticados.
# Documento de Requisitos de Sistema (DRS)

## Sistema de Gestão de Processos Seletivos

## 1. Introdução

### 1.1. Objetivo
Este documento descreve os requisitos funcionais, não funcionais, regras de negócio e diretrizes arquiteturais para um sistema web de gestão de processos seletivos de colaboradores para órgão público.

O sistema deverá permitir:
- autenticação via **gov.br**;
- cadastro e administração de processos seletivos;
- definição de fases e etapas sequenciais;
- submissão de inscrição e documentação por candidatos;
- configuração de formulários por fase;
- distribuição de inscrições para avaliadores;
- avaliação, pareceres, notas, checklist e recursos;
- publicação de resultados parciais e finais;
- exportação de informações e integração com sistemas externos.

### 1.2. Escopo
O sistema contemplará todo o ciclo de um processo seletivo público, desde a inscrição até a publicação do resultado final, incluindo mecanismos de auditoria, recursos e integração com o SUAP.

### 1.3. Público-alvo do documento
- equipe de análise de requisitos;
- equipe de desenvolvimento;
- equipe de testes;
- gestores do órgão;
- equipe de infraestrutura e segurança da informação.

---

## 2. Visão geral do sistema

### 2.1. Descrição resumida
O sistema será uma aplicação web responsiva, acessível mediante autenticação via gov.br para funcionalidades administrativas, de inscrição e acompanhamento. Permitirá que administradores, coordenadores, avaliadores e candidatos interajam com os processos seletivos conforme seus papéis e permissões.

**Acesso anônimo:**
Usuários não autenticados (anônimos) poderão acessar:
 - a página inicial (listagem dos processos seletivos publicados);
 - os detalhes de cada processo seletivo publicado.

Funcionalidades administrativas, de inscrição e acompanhamento continuam restritas a usuários autenticados.

### 2.2. Perfis de usuário

#### 2.2.1. Candidato
Usuário externo que realiza inscrição pública em processo seletivo, envia documentos, preenche formulários, acompanha etapas, visualiza resultados parciais e finais e interpoe recursos.

#### 2.2.2. Administrador
Usuário responsável por cadastrar coordenadores no sistema e administrar permissões globais.

#### 2.2.3. Coordenador
Usuário responsável por cadastrar e configurar processos seletivos, fases, etapas, banca do processo, avaliadores e distribuição de inscrições para avaliação.

#### 2.2.4. Avaliador
Usuário responsável por avaliar as inscrições distribuídas a ele em determinada etapa/fase do processo seletivo.

### 2.3. Regra de compatibilidade de papéis
Um mesmo usuário poderá possuir mais de um papel no sistema, exceto a combinação em um mesmo processo seletivo entre:
- candidato;
- avaliador;
- coordenador;
- administrador.

Ou seja, o mesmo usuário **não poderá atuar como candidato e como avaliador/coordenador/administrador no mesmo processo seletivo**.

### 2.4. Forma de acesso
O acesso ao sistema será realizado **preferencialmente por autenticação gov.br**. Perfis administrativos e operacionais serão previamente cadastrados:

**Exceção:**
As funcionalidades públicas (listagem e detalhes de processos seletivos publicados) estarão disponíveis para acesso anônimo, sem necessidade de autenticação.
- administrador: cadastrado previamente no sistema;
- coordenador e avaliador: cadastrados previamente para uso no processo seletivo ou para associação à fase.


## 3. Requisitos de negócio

### 3.1. Estrutura do processo seletivo
O processo seletivo será composto por:
- fase de inscrição;
- fases intermediárias livres, definidas pelo coordenador;
- fase final de resultado.

As fases serão compostas por uma ou mais etapas.

### 3.2. Regras sobre fases e etapas
1. As etapas e fases serão sequenciais.
2. O avanço para uma fase seguinte dependerá da habilitação na fase anterior.
3. Somente os candidatos habilitados poderão prosseguir.
4. Uma vez não habilitado em uma fase, o candidato será eliminado do processo seletivo.
5. A quantidade de fases e etapas será variável, conforme o edital.
6. A fase de inscrição deve ser sempre a primeira.
7. A fase de resultado final deve ser sempre a última.
8. Não poderá haver fase anterior à inscrição nem fase posterior ao resultado final.

### 3.3. Regras sobre inscrição
1. A inscrição será sempre pública.
2. Cada candidato poderá manter apenas uma inscrição ativa por processo seletivo.
3. O candidato poderá cancelar a inscrição.
4. Após cancelamento, poderá realizar nova inscrição, observadas as regras e prazos vigentes.

### 3.4. Regras sobre documentos
1. Somente arquivos PDF serão aceitos.
2. Cada fase configurará:
   - lista de documentos aceitos/obrigatórios;
   - tamanho máximo por arquivo.
3. O tamanho padrão máximo será de 2 MB por arquivo, salvo configuração diferente pela coordenação.
4. Será permitido apenas 1 arquivo por tipo de documento.
5. O candidato deverá consolidar os documentos em um único PDF por tipo.
6. Alguns documentos poderão ser obrigatórios.
7. A ausência de documento obrigatório poderá implicar:
   - não habilitação na etapa; ou
   - eliminação do processo seletivo, conforme configuração da fase.
8. Quando o tipo de documento tiver pontuação associada, o candidato poderá informar a pontuação que acredita ser adequada, apenas como referência ao avaliador.
9. A pontuação informada pelo candidato terá caráter referencial e não vinculante.
10. O candidato poderá substituir o arquivo enquanto a fase de envio estiver aberta.
11. O sistema deverá manter histórico de envios para auditoria.

### 3.5. Regras sobre formulários
1. Os formulários serão configuráveis pelo coordenador.
2. Os formulários poderão conter campos do tipo:
   - texto;
   - número;
   - data;
   - seleção única;
   - múltipla seleção;
   - checkbox;
   - upload;
   - outros compatíveis com configuração interna.
3. Cada fase poderá ter:
   - envio de formulário;
   - envio de arquivos;
   - ambos;
   - ou nenhum dos dois.
4. As respostas dos formulários deverão ser estruturadas para consulta, análise e exportação.
5. O formulário deverá ser exibido também na interface de avaliação dos avaliadores.
6. O formulário poderá:
   - ser pontuado;
   - receber nota padronizada;
   - ser marcado como “não atendeu aos requisitos”;
   - receber observações para a banca/coordenadoria;
   - receber observações visíveis ao candidato quando aplicável.

### 3.6. Regras sobre avaliação
1. As avaliações serão, por padrão, por nota.
2. O sistema também deverá permitir:
   - parecer textual;
   - checklist;
   - critérios ponderados;
   - aprovação/reprovação.
3. Critérios não mensuráveis deverão ser acompanhados de:
   - ateste de aprovado/reprovado;
   - nota para fins de ranqueamento.
4. Uma candidatura poderá ser avaliada por múltiplos avaliadores.
5. O número de avaliadores por candidatura deverá ser ímpar: 1, 3, 5, 7 etc.
6. A nota final da candidatura em uma etapa seguirá critério configurado pelo coordenador:
   - média;
   - soma.
7. O avaliador visualizará apenas os dados da etapa corrente.
8. O avaliador poderá anexar 1 único PDF por avaliação.
9. A justificativa do avaliador será opcional.

### 3.7. Regras sobre resultados e recursos
1. O resultado parcial deverá ser publicado ao final de cada fase.
2. Para o público geral, o resultado parcial será divulgado apenas com o número de inscrição.
3. Para o candidato autenticado, o sistema deverá exibir:
   - notas de cada critério avaliado;
   - justificativas apresentadas pelo avaliador, quando houver.
4. O candidato poderá interpor recurso somente contra o resultado parcial da etapa corrente.
5. O recurso terá formulário próprio.
6. A resposta ao recurso deverá ser registrada no sistema.
7. O resultado final será consolidado automaticamente a partir da última etapa.

### 3.8. Regras sobre prazos
1. Todos os períodos deverão ser configurados com data e hora.
2. O sistema deverá bloquear ações fora do período permitido.
3. Será necessário considerar o fuso horário do órgão.
4. O sistema deverá permitir prorrogação de prazo após publicação, mediante ação autorizada.

### 3.9. Regras sobre comunicação e transparência
1. O sistema deverá enviar avisos aos candidatos por e-mail sobre andamento das etapas.
2. Após autenticação, o usuário deverá visualizar de forma clara:
   - fase atual;
   - situação de cada etapa;
   - status de habilitação.
3. O sistema deverá manter trilha de auditoria completa.
4. Os resultados deverão ser publicados em área pública do sistema.
5. O sistema deverá permitir exportação de dados em:
   - PDF;
   - CSV;
   - planilha;
   - HTML.
6. O sistema deverá gerar relatórios gerenciais.

### 3.10. Regras sobre integração
1. O sistema deverá integrar-se ao SUAP para:
   - publicação de documentos;
   - cadastro dos selecionados;
   - assinatura eletrônica;
   - outras necessidades definidas pelo órgão.


## 4. Requisitos funcionais

### RF01 — Autenticação via gov.br
O sistema deve permitir autenticação exclusiva por meio da plataforma gov.br.

### RF02 — Cadastro de administradores
O sistema deve permitir ao administrador cadastrar coordenadores com definição de seus papéis e permissões.

### RF03 — Cadastro de coordenadores
O sistema deve permitir o cadastramento prévio de coordenadores autorizados a operar processos seletivos.

### RF04 — Cadastro de avaliadores
O sistema deve permitir o cadastramento prévio de avaliadores e sua vinculação a processos seletivos e/ou fases.

### RF05 — Cadastro de processos seletivos
O sistema deve permitir ao coordenador cadastrar, editar, visualizar, publicar, suspender, prorrogar e encerrar processos seletivos.

### RF06 — Estruturação de fases
O sistema deve permitir ao coordenador definir fases do processo seletivo, respeitando a obrigatoriedade da fase de inscrição como primeira fase e da fase de resultado final como última fase.

### RF07 — Estruturação de etapas
O sistema deve permitir ao coordenador configurar etapas dentro de cada fase.

### RF08 — Sequenciamento de fases e etapas
O sistema deve controlar o fluxo sequencial entre fases e etapas, bloqueando o avanço de candidatos não habilitados.

### RF09 — Inscrição pública
O sistema deve permitir inscrições públicas em processo seletivo.

### RF10 — Cancelamento de inscrição
O sistema deve permitir ao candidato cancelar sua inscrição ativa.

### RF11 — Reinscrição após cancelamento
O sistema deve permitir nova inscrição após cancelamento, desde que dentro do período válido.

### RF12 — Upload de arquivos PDF
O sistema deve permitir ao candidato enviar arquivos exclusivamente no formato PDF.

### RF13 — Controle de obrigatoriedade documental
O sistema deve permitir definir documentos obrigatórios e impedir a habilitação quando ausentes, conforme regra de negócio configurada.

### RF14 — Controle de tamanho de arquivo
O sistema deve permitir configurar o tamanho máximo de arquivo por fase, com padrão de 2 MB.

### RF15 — Substituição de arquivos
O sistema deve permitir substituição de arquivos enquanto o período de envio estiver aberto.

### RF16 — Histórico de envios
O sistema deve manter histórico completo de arquivos enviados e substituídos.

### RF17 — Formulários configuráveis
O sistema deve permitir ao coordenador criar e configurar formulários por fase.

### RF18 — Estrutura de campos de formulário
O sistema deve suportar os tipos de campos definidos nas regras de negócio.

### RF19 — Respostas estruturadas
O sistema deve armazenar respostas de formulários em formato estruturado para consulta e exportação.

### RF20 — Avaliação de candidaturas
O sistema deve permitir o registro de avaliações por múltiplos avaliadores, com nota, parecer, checklist ou critérios ponderados.

### RF21 — Número ímpar de avaliadores
O sistema deve garantir que cada candidatura possua número ímpar de avaliadores quando configurado para múltiplas avaliações.

### RF22 — Consolidação de notas
O sistema deve calcular a nota final por candidatura em cada etapa conforme critério de média ou soma definido pelo coordenador.

### RF23 — Visão restrita do avaliador
O sistema deve apresentar ao avaliador apenas os dados da etapa corrente e os materiais permitidos daquela etapa.

### RF24 — Anexo na avaliação
O sistema deve permitir ao avaliador anexar 1 PDF por avaliação.

### RF25 — Publicação de resultado parcial
O sistema deve permitir a publicação de resultados parciais por fase.

### RF26 — Divulgação pública resumida
O sistema deve disponibilizar publicamente o resultado parcial contendo apenas o número de inscrição.

### RF27 — Visualização completa pelo candidato
O sistema deve permitir ao candidato autenticado visualizar as notas detalhadas e justificativas de sua própria avaliação.

### RF28 — Recurso
O sistema deve permitir ao candidato interpor recurso contra o resultado parcial da etapa corrente por meio de formulário próprio.

### RF29 — Resposta ao recurso
O sistema deve permitir registrar e publicar a resposta ao recurso no próprio sistema.

### RF30 — Resultado final consolidado
O sistema deve consolidar automaticamente o resultado final a partir da última etapa.

### RF31 — Controle de prazos
O sistema deve bloquear ações fora dos períodos configurados.

### RF32 — Notificação por e-mail
O sistema deve enviar notificações por e-mail sobre eventos relevantes do processo seletivo.

### RF33 — Painel de acompanhamento
O sistema deve exibir ao usuário autenticado a fase atual, status das etapas e situação de habilitação.

### RF34 — Auditoria
O sistema deve registrar eventos de acesso, alteração, avaliação e publicação, com data, hora e usuário responsável.

### RF35 — Exportação de dados
O sistema deve permitir exportação de informações em PDF, CSV, planilha e HTML.

### RF36 — Relatórios gerenciais
O sistema deve disponibilizar relatórios gerenciais para coordenação e administração.

### RF37 — Integração com SUAP
O sistema deve integrar-se ao SUAP para as operações definidas pelo órgão.

### RF38 — Máscara de dados pessoais
O sistema deve mascarar dados pessoais em visões públicas e em visões acessadas por candidatos, conforme política de privacidade.

### RF39 — Controle por perfis
O sistema deve aplicar regras de acesso distintas para administrador, coordenador, avaliador e candidato.


## 5. Requisitos não funcionais

### RNF01 — Segurança
O sistema deve utilizar autenticação via gov.br e adotar mecanismos de segurança compatíveis com aplicações governamentais.

### RNF02 — Conformidade legal
O sistema deve atender à LGPD, ao Marco Civil da Internet, à Lei Carolina Dieckmann e às normas de acessibilidade eMAG/WCAG.

### RNF03 — Controle de acesso
O sistema deve implementar controle de acesso baseado em perfis e permissões.

### RNF04 — Auditoria
O sistema deve manter logs auditáveis de todas as ações relevantes.

### RNF05 — Desempenho
O sistema deve responder adequadamente sob carga compatível com processos seletivos públicos, mantendo usabilidade mesmo em períodos de pico.

### RNF06 — Disponibilidade
O sistema deve estar disponível durante os períodos críticos de inscrição e avaliação, conforme infraestrutura contratada.

### RNF07 — Usabilidade
A interface deve ser clara, intuitiva e adequada ao uso por candidatos e servidores públicos.

### RNF08 — Acessibilidade
A interface deve seguir boas práticas de acessibilidade, incluindo compatibilidade com leitores de tela e navegação por teclado.

### RNF09 — Responsividade
O sistema deve ser responsivo e funcional em diferentes tamanhos de tela.

### RNF10 — Compatibilidade
O sistema deve funcionar nos principais navegadores modernos.

### RNF11 — Fuso horário
O sistema deve respeitar o fuso horário oficial do órgão para controle de datas e prazos.

### RNF12 — Portabilidade e implantação
O sistema deverá ser implantado em infraestrutura própria do órgão.


## 6. Arquitetura do software

### 6.1. Visão geral arquitetural
A solução deverá adotar uma arquitetura web baseada em camadas, com separação clara entre:
- interface web;
- camada de aplicação;
- camada de domínio;
- camada de persistência;
- serviços assíncronos;
- monitoramento e observabilidade;
- integrações externas.

### 6.2. Stack tecnológica
A arquitetura deverá adotar obrigatoriamente:

- **Banco de dados:** PostgreSQL  
- **Linguagem:** Python 3.14  
- **Framework web:** Django 5  
- **Arquitetura operacional:** Web / Celery / Sentry

### 6.3. Componentes da arquitetura

#### 6.3.1. Camada Web
Responsável por:
- autenticação;
- navegação;
- formulários;
- telas de administração;
- telas de avaliação;
- área pública de resultados.

#### 6.3.2. Camada de aplicação
Responsável pela implementação das regras do processo seletivo:
- fases;
- etapas;
- validações;
- publicação;
- recursos;
- cálculo de notas;
- controle de habilitação.

#### 6.3.3. Camada de domínio
Responsável por concentrar as entidades principais do sistema:
- usuário;
- papel;
- processo seletivo;
- fase;
- etapa;
- inscrição;
- documento;
- formulário;
- resposta;
- avaliação;
- recurso;
- resultado;
- auditoria.

#### 6.3.4. Camada de persistência
Responsável pelo armazenamento de dados em PostgreSQL.

#### 6.3.5. Processamento assíncrono
O sistema deverá utilizar **Celery** para tarefas assíncronas, como:
- envio de e-mails;
- geração de exportações;
- integração com SUAP;
- processamento de notificações;
- tarefas de auditoria e consolidação.

#### 6.3.6. Observabilidade
O sistema deverá utilizar **Sentry** para:
- captura de exceções;
- monitoramento de erros;
- rastreamento de falhas;
- apoio à manutenção e estabilidade.

### 6.4. Integração com gov.br
A autenticação deverá ser feita por integração com gov.br, utilizando os mecanismos oficiais definidos pelo provedor de identidade.

### 6.5. Integração com SUAP
A integração com SUAP deverá ser tratada como serviço externo, com responsabilidades como:
- envio de dados dos selecionados;
- publicação de documentos;
- apoio à assinatura eletrônica;
- sincronizações necessárias.

### 6.6. Segurança arquitetural
A arquitetura deverá prever:
- proteção contra acesso indevido;
- segregação por perfil;
- mascaramento de dados sensíveis;
- trilha de auditoria;
- proteção de arquivos enviados;
- controle de sessão.

### 6.7. Escalabilidade
A solução deverá ser preparada para aumento de carga em períodos de inscrição e publicação de resultados, especialmente em:
- acesso simultâneo de candidatos;
- envio de documentos;
- consultas públicas a resultados;
- processamento assíncrono de integrações.

### 6.8. Manutenibilidade
A arquitetura deverá favorecer:
- modularidade;
- reutilização;
- testes automatizados;
- facilidade de evolução do fluxo de fases e etapas;
- separação entre regra de negócio e interface.



## 7. Regras de auditoria e rastreabilidade

### 7.1. Eventos auditáveis
Devem ser auditados, no mínimo:
- acesso ao sistema;
- criação/alteração/exclusão de processos;
- cadastro de fases e etapas;
- submissão e substituição de arquivos;
- preenchimento de formulários;
- avaliação;
- envio e resposta a recursos;
- publicação de resultados;
- integrações externas;
- alterações de prazo;
- cancelamento de inscrição.

### 7.2. Dados mínimos de auditoria
Cada evento auditável deverá registrar:
- usuário;
- data e hora;
- ação executada;
- objeto afetado;
- valor anterior e posterior, quando aplicável;
- origem da ação, quando aplicável.



## 8. Considerações finais

Este DRS estabelece uma base inicial para especificação, implementação e validação do sistema. Como próximos passos, recomenda-se elaborar:

1. **casos de uso detalhados**;
2. **modelo de dados conceitual**;
3. **matriz de permissões por perfil**;
4. **regras de negócio formalizadas por fase/etapa**;
5. **critério de aprovação por etapa e por fase**;
6. **especificação da integração com gov.br e SUAP**;
7. **protótipos de interface**.
