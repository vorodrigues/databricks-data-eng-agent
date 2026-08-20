# Indice da base de conhecimento SAP

Uma linha por tabela: `nome | camada | comentario`. Use para descobrir se uma
tabela/data product ja existe na KB **sem** carregar as definicoes no contexto.
Consulte via `python3 scripts/kb.py find <nome>`.

| Tabela | Camada | Comentario |
|--------|--------|------------|
| `accounting_documents_header` | gold | Metadados do cabeçalho de documentos contábeis do SAP BKPF (ex.: datas de lançamento e entrada, dados de usuário, status do documento e chave de moeda), enriquecidos com dimensões de datas do calendário para relatórios financeiros. |
| `accounting_documents_item` | gold | Itens de linha de documentos contábeis SAP BSEG (valores, impostos, contas e ordens) com ajuste dinâmico de casas decimais monetárias, enriquecido com dimensões de calendário. |
| `accounts_payable` | gold | Visão unificada de contas a pagar do livro contábil universal do SAP S/4HANA (ACDOCA, BKPF, BSEG), filtrada pelo tipo de conta Fornecedor, para suporte a análises de fluxo de caixa e rastreamento de passivos. |
| `accounts_receivable` | gold | Visão unificada de contas a receber proveniente do livro razão universal SAP S/4HANA (ACDOCA, BKPF, BSEG), filtrada pelo tipo de conta Cliente, para suporte a análise de DSO (Days Sales Outstanding), relatórios de envelhecimento e modelagem de risco de crédito. |
| `acdoca` | bronze | Itens de linha do diário universal (Universal Journal Entry Line Items) |
| `acdocu` | bronze | Lancamentos contabeis do grupo (Group Journal Entries) |
| `addresses` | gold | Visão consolidada e globalmente consistente de endereços geográficos e de comunicação de parceiros de negócio, clientes, fornecedores e unidades organizacionais (ADRC, ADR6, ADRCT), para suporte a análises geoespaciais e roteamento de cadeia de suprimentos. |
| `adr6` | bronze | Enderecos de e-mail (Business Address Services) — comunicacao por e-mail de enderecos SAP. |
| `adrc` | bronze | Enderecos (Business Address Services) |
| `adrct` | bronze | Textos de endereco do servico de endereco corporativo (Business Address Services) |
| `afko` | bronze | Dados do cabeçalho de ordens de produção PP (AFKO) |
| `afpo` | bronze | Item de ordem de producao/processo |
| `afru` | bronze | Confirmacoes de ordens de producao |
| `afvc` | bronze | Operação dentro de uma ordem (PP/PM/PS) |
| `afvv` | bronze | Estrutura de BD das quantidades, datas e valores da operação |
| `agency_settlement_document_headers` | gold | Metadados de cabeçalho de documentos de acerto de agência e liquidação (WBRK), incluindo parceiros, status de lançamento e chaves de moeda, para suporte à rastreabilidade de rebates e analytics de liquidação de comissões. |
| `agency_settlement_document_items` | gold | Detalhes de itens de documentos de acerto de agência e liquidação (WBRP), incluindo números de material, quantidades, condições de preço e valores líquidos, para suporte à reconciliação financeira e relatórios de fluxo de compra/venda de terceiros. |
| `ankt` | bronze | Descrições de classes de ativo |
| `anla` | bronze | Segmento do cadastro de ativo imobilizado |
| `anlb` | bronze | Parâmetros de depreciação do ativo fixo |
| `anlh` | bronze | Número principal de ativo imobilizado |
| `anlz` | bronze | Alocacoes de ativo com dependencia temporal (ANLZ) |
| `aufk` | bronze | Dados mestre de ordens internas |
| `ausp` | bronze | Valores de características de classificação (SAP AUSP). |
| `billing_blocking_reasons` | gold | Captura descrições e códigos de motivos de bloqueio de faturamento por idioma (SAP TVFST) para auditoria do fluxo order-to-cash. |
| `billing_document_headers` | gold | Metadados transacionais do cabeçalho de documentos de faturamento SAP (VBRK), enriquecidos com dimensões de data para suporte a reconhecimento de receita e análise de margem. |
| `billing_document_items` | gold | Itens de documentos de faturamento SAP (VBRP): quantidades faturadas, valores líquidos, custos e referências a documentos anteriores, para suporte a análise de rentabilidade e margem de clientes. |
| `bkpf` | bronze | Cabeçalho de documento contábil (Accounting Document Header) |
| `bseg` | bronze | Segmento de documento contábil (FI) |
| `business_partner_addresses` | gold | Endereços físicos, e-mails de contato (ADR6) e observações de endereço (ADRCT) de parceiros de negócio SAP a partir de BUT020 e ADRC, para suporte à verificação de dados mestre geográficos e de comunicação. |
| `business_partner_bank_details` | gold | Dados bancários de parceiros de negócios SAP (BUT0BK), incluindo IBAN, contas bancárias e períodos de validade, para suporte a roteamento de pagamentos e validação de segurança financeira. |
| `business_partners` | gold | Perfil mestre central dos parceiros de negócio SAP (pessoas físicas, organizações ou grupos), oriundo de BUT000, incluindo categorias, papéis e detalhes de status para suporte a auditorias. |
| `but000` | bronze | Parceiro de negócio: dados gerais I |
| `but020` | bronze | Endereços de parceiro de negócios (BP) |
| `but0bk` | bronze | Detalhes bancários do parceiro de negócios (BP) |
| `ce1c001` | bronze | Itens de resultado por setor de negócio C001 — tabela de linhas CO-PA (Operating Concern CE1C001) |
| `ce3c001` | bronze | Dados reais de rentabilidade por segmento (CO-PA) - objeto de rentabilidade C001 (CE3C001) |
| `ce4c001` | bronze | Concern operacional CO-PA (ce4c001) - dados periodicos de lucratividade |
| `ce4c001_acct` | bronze | Concern operacional CO-PA baseado em conta (ce4c001_acct) |
| `ce4c001_flag` | bronze | Área de resultados (CO-PA): tabela de flags do objeto de lucratividade para o objeto de controlling C001. |
| `cepc` | bronze | Dados mestre do centro de lucro |
| `cepct` | bronze | Textos do mestre de centro de lucro |
| `ckmi1` | bronze | Índice de documentos contábeis por material |
| `coep` | bronze | Itens de linha de objeto CO por período |
| `company_codes` | gold | Estruturas corporativas centrais a partir de T001, detalhando localidades, moedas base, planos de contas e variantes de exercício fiscal ativas. |
| `condition_contract_settlement_detailed_statement` | gold | Demonstrativo detalhado de liquidação (WB2_D_BVDETAIL) com volume de negócios e valores liquidados para auditoria de bonificações comerciais. |
| `condition_contracts_header` | gold | Definições de contratos de condição SAP (CCS) em nível de cabeçalho, incluindo números de parceiros, tipos de contrato e datas de validade, para rastrear contratos comerciais de rebate. |
| `condition_contracts_item` | gold | Regras de liquidação por item dos contratos de condição SAP (WCOCOI), incluindo critérios de elegibilidade, materiais e parâmetros de liquidação. |
| `controlling_area_assignment` | gold | Mapeia empresas e areas de negocio para seus respectivos areas de controlling (TKA02), suportando consolidacao fiscal entre empresas. |
| `controlling_areas` | gold | Dados mestre das áreas de controladoria configuradas no SAP a partir de TKA01, incluindo hierarquias padrão, configurações de moeda, plano de contas e variante de exercício, para suporte a alocações de overhead corporativo. |
| `cosp` | bronze | Objeto de CO: totais de custos por lançamentos externos (partidas individuais agregadas por período) |
| `coss` | bronze | Objeto CO: totais de custo para lançamentos internos (COSS) |
| `cost_centers` | gold | Definições mestre de centros de custo oriundas de CSKS e CSKT, incluindo intervalos de validade, códigos de empresa, departamentos, responsáveis, indicadores de bloqueio e descrições multilíngues para suporte ao controle de gastos corporativos. |
| `cost_elements` | gold | Definições mestre de elementos de custo (CSKB/CSKU) com intervalos de validade, categorias, indicadores de planejamento e descrições multilíngues para suporte ao controle de custos e análise de lucratividade. |
| `countries` | gold | Registros mestre de países a partir das tabelas SAP T005 e T005T, com nomes localizados, padrões de formatação, configurações regionais e mapeamentos de códigos internacionais para suporte a análises de comércio internacional. |
| `country_dialing_codes` | gold | Códigos de discagem internacional e nacional para telefone e fax a partir de T005K, permitindo consultas de metadados de telecomunicação. |
| `country_tax_regions` | gold | Detalhes de estados, províncias e regiões a partir de T005S e T005U com descrições por idioma, para consulta de chaves de imposto regional. |
| `crhd` | bronze | Cabecalho do centro de trabalho |
| `cskb` | bronze | Elementos de custo (dados dependentes da área de controle) |
| `csks` | bronze | Registro mestre de centro de custo |
| `cskt` | bronze | Textos de centro de custo |
| `csku` | bronze | Textos de elementos de custo por idioma e plano de contas (CSKU). |
| `currency_codes` | gold | Dicionário global padronizado de códigos de moeda ativos a partir de TCURC, TCURT e TCURX, com referências ISO-4217, configuração de decimais e nomes multilíngues. |
| `customer_cleared_items` | gold | Visão detalhada dos itens de transação de clientes compensados do SAP ECC (BSAD) para suporte à reconciliação histórica e auditoria de pagamentos de clientes. |
| `customer_open_items` | gold | Visão detalhada de itens de linha de transações abertas de clientes do SAP ECC (BSID) para rastreamento operacional e análise de faturas em aberto. |
| `customers` | gold | Visão unificada e consolidada dos registros mestre de clientes, integrando dados cadastrais centrais (KNA1) com dados de endereço padronizados (ADRC). Suporta CRM, auditoria de dados mestre, execução de vendas e geoanalytics. |
| `dd01l` | bronze | Domínios do dicionário ABAP (SAP DD01L). Tabela independente de mandante. |
| `dd02t` | bronze | Textos descritivos de tabelas do dicionario de dados SAP (DD), independente de mandante |
| `dd03l` | bronze | Campos de tabelas do dicionário ABAP (SAP DD03L). Tabela independente de mandante. |
| `dd03t` | bronze | Textos descritivos de campos do dicionario de dados SAP (DD), dependentes de idioma, independente de mandante |
| `dd04l` | bronze | Elementos de dados ABAP (DD04L) |
| `dd04t` | bronze | Textos de elementos de dado ABAP (DD) |
| `dd07l` | bronze | Valores de dominio do dicionario ABAP |
| `dd07t` | bronze | Textos dos valores fixos de domínio ABAP (dependente de idioma) |
| `dd08l` | bronze | Definições de relacionamento (chaves estrangeiras do ABAP DD) |
| `delivery_blocking_reasons` | gold | Nomes descritivos (dependentes de idioma) para os motivos de bloqueio de entrega SAP (TVLST), para identificação das causas de bloqueios no processo de remessa. |
| `delivery_document_headers` | gold | Cabeçalhos de documentos de entrega SAP (LIKP): registro central de entregas de saída ou entrada, com detalhes logísticos e de expedição incluindo datas, pontos de expedição, tipos de entrega, pesos, rotas e status de liberação de crédito. |
| `delivery_document_items` | gold | Itens de linha de remessas SAP (LIPS), com quantidades entregues, materiais, unidades de medida, centros, valores líquidos e referências de ordens predecessoras para atendimento e faturamento |
| `depreciation_terms` | gold | Captura parâmetros de depreciação e configurações de vida útil de ANLB, T093B e tabelas SAP relacionadas para modelar tendências de avaliação de ativos fixos. |
| `distribution_channels` | gold | Dicionario mestre de canais de distribuicao do SAP TVTW, enriquecido com nomes multilinguagem de TVTWT. |
| `divisions` | gold | Dados mestre de divisoes do SAP TSPA, enriquecidos com descricoes multilinguagem de TSPAT. |
| `ekbe` | bronze | Histórico por documento de compra |
| `ekes` | bronze | Confirmações do fornecedor (SAP EKES). |
| `eket` | bronze | Linhas de programação do acordo de fornecimento |
| `ekkn` | bronze | Imputação contábil em documentos de compras (EKKN) |
| `ekko` | bronze | Cabecalho do documento de compras |
| `ekpo` | bronze | Item do documento de compra (EKPO) |
| `exchange_rates` | gold | Taxas de câmbio diárias expandidas entre pares de moedas a partir de TCURR e TCURF, para conversões financeiras em transações internacionais e auditoria consolidada. |
| `fagl_011pc` | bronze | Versão de demonstrações financeiras: itens da estrutura |
| `fagl_011qt` | bronze | Estrutura de demonstracao financeira: textos dos itens de demonstracao financeira |
| `fagl_011zc` | bronze | Versão de demonstrações financeiras: atribuição de itens a contas contábeis |
| `faglflexa` | bronze | Razão geral novo (New GL): itens reais de linha |
| `faglflext` | bronze | Razão geral: totais por período e dimensão contábil (General Ledger Totals) |
| `financial_statement_structure_items` | gold | Nós hierárquicos e estrutura de layouts para versões de demonstrações financeiras a partir de FAGL_011PC, para geração de hierarquias de balanço e DRE. |
| `financial_statement_structure_texts` | gold | Descrições textuais dependentes de idioma para itens de demonstrações financeiras a partir de FAGL_011QT, para suporte a hierarquias de relatórios financeiros. |
| `financial_statement_version_assignments` | gold | Mapeamento e atribuição de itens de demonstrações financeiras a contas contábeis a partir de FAGL_011ZC, verificando atribuições de plano de contas e estruturas de nós de reporte. |
| `fincs_ref_vers_r` | bronze | Relacao de versoes de referencia para consolidacao financeira (FIN-CS) |
| `finsc_ledger` | bronze | Razão para lançamentos do diário universal (S/4HANA) |
| `finsc_ledger_t` | bronze | Textos de razao contabil do journal universal (dependente de idioma) |
| `fiscal_year_variant_periods` | gold | Definições de períodos a partir de T009B, mapeando meses e dias do calendário para períodos fiscais de lançamento e deslocamentos de período. |
| `fiscal_year_variants` | gold | Definições mestres das variantes de exercício fiscal SAP a partir de T009, incluindo indicadores de ano civil, dependência do ano e quantidade de períodos de lançamento e especiais. |
| `fixed_assets_master` | gold | Consolida dados mestre de ativos imobilizados do SAP a partir de ANLA, ANLH e ANKT, combinando detalhes do ativo, número principal e descrições da classe para relatórios de ciclo de vida e propriedade. |
| `general_ledger_accounts` | gold | Visão unificada de contas contábeis (G/L) ao nível do plano de contas SAP (SKA1/SKAT), com categorias, grupos, indicadores de exclusão/bloqueio e descrições multilíngues para suporte a relatórios financeiros e auditoria de conformidade. |
| `group_journal_entries` | gold | Registra lançamentos contábeis de consolidação em nível de grupo a partir da tabela ACDOCU do S/4HANA, suportando relatórios de consolidação financeira corporativa. |
| `jest` | bronze | Status individual de objeto (status de sistema e usuario por objeto) |
| `kako` | bronze | Segmento de cabeçalho de capacidade produtiva |
| `klah` | bronze | Dados do cabeçalho de classe (classificação de objetos) |
| `kna1` | bronze | Dados gerais do mestre de clientes |
| `knb1` | bronze | Mestre de clientes por empresa (dados contábeis) |
| `knc1` | bronze | Dados mestre de cliente - movimentos por periodo (transaction figures) |
| `knkk` | bronze | Gestão de crédito do cliente: dados da área de crédito |
| `knvk` | bronze | Contatos do mestre de clientes (pessoas de contato) |
| `knvp` | bronze | Funções de parceiro do mestre de clientes |
| `knvv` | bronze | Dados de vendas do mestre de clientes |
| `konv` | bronze | Condições de precificação - dados de transação (KONV) |
| `kssk` | bronze | Tabela de alocação: objeto para classe |
| `languages` | gold | Dicionario de idiomas do SAP T002/T002T, mapeando chaves de idioma a nomes padronizados para suporte a relatorios multilinguagem. |
| `lfa1` | bronze | Mestre de fornecedores (secao geral) |
| `lfb1` | bronze | Mestre de fornecedores por empresa (dados contábeis) |
| `likp` | bronze | Cabeçalho da entrega (documento SD) |
| `lips` | bronze | Documento SD: Entrega: Dados de item |
| `makt` | bronze | Descrições de material (textos curtos por idioma) |
| `mara` | bronze | Dados gerais do material (General Material Data) |
| `marc` | bronze | Dados de material por centro (Plant Data for Material) |
| `mard` | bronze | Dados de estoque por depósito para o material |
| `marm` | bronze | Unidades de medida alternativas do material (SAP MARM). |
| `mast` | bronze | Vínculo de material com lista de materiais (LM) |
| `material_batch_stocks` | gold | Rastreia quantidades fisicas de estoque por lote, planta e deposito a partir da MCHB do SAP, incluindo estoque livre, bloqueado, em transferencia, com uso restrito e devolucoes. |
| `material_cross_plant_batches` | gold | Registro central entre centros de lotes de material SAP da MCH1, rastreando detalhes universais do lote como datas de fabricação e validade, propriedades de prazo de validade, referências de fornecedor e status do lote. |
| `material_documents` | gold | Captura movimentações operacionais de mercadorias do SAP, rastreando recebimentos, saídas, transferências entre centros e ajustes de inventário dos logs transacionais MSEG e MATDOC. |
| `material_groups` | gold | Catálogo de classificações de grupos de materiais a partir de T023 e T023T, agrupando materiais para avaliação de estoque, controles de compras e análise estruturada de vendas. |
| `material_movement_types` | gold | Dicionario de tipos de movimento de materiais SAP (T156) enriquecido com textos de descricao multilinguais da T156T. |
| `material_plant_batches` | gold | Fornece definições de lote por centro e configurações de avaliação do SAP MCHA, rastreando atribuições de lote por centro, chaves de status e parâmetros de fabricação. |
| `material_plants` | gold | Dados de material específicos por planta a partir de MARC, incluindo indicadores de exclusão, gestão de lotes, status específico da planta e níveis de estoque de segurança. |
| `material_types` | gold | Mapeia códigos de tipo de material para descrições localizadas (SAP T134/T134T), definindo parâmetros de controle como controle de preço e tipos de suprimento. |
| `materials` | gold | Dados mestre gerais de materiais do SAP (MARA) combinados com descrições multilíngues (MAKT), incluindo códigos, descrições e especificações físicas e dimensionais do produto. |
| `materials_by_storage_location` | gold | Níveis de estoque de materiais por depósito (SAP MARD/MAKT/T001W/T001L), com descrições multilíngues de materiais, nomes de centros produtivos e locais de armazenamento. |
| `mbew` | bronze | Valoração de material (saldos de estoque e preços por área/tipo de avaliação) |
| `mbewh` | bronze | Histórico de valoração de material (saldos e preços por período) |
| `mch1` | bronze | Lotes (gestao de lotes entre plantas) |
| `mcha` | bronze | Lotes por centro (dados do lote em nível de centro) |
| `mchb` | bronze | Estoques de lote |
| `mkol` | bronze | Estoques especiais de fornecedor (consignacao) |
| `mkpf` | bronze | Cabeçalho do documento de material (SAP MKPF). |
| `mseg` | bronze | Segmento do documento: material (movimentacoes de estoque) |
| `msfd` | bronze | Estoque especial de pedido de cliente com fornecedor (SAP MSFD). |
| `mska` | bronze | Estoque de pedido de vendas |
| `msku` | bronze | Estoques especiais com cliente (SAP MSKU). |
| `mslb` | bronze | Estoques especiais com fornecedor (SAP MSLB). |
| `mssa` | bronze | Total de pedidos de cliente em carteira |
| `mvke` | bronze | Dados de vendas por material (MVKE) |
| `nast` | bronze | Status de mensagens de saída (Message Status) |
| `plants` | gold | Dados mestre de centros produtivos (SAP T001W): mapeamento de unidades de produção com endereços, atribuições organizacionais e parâmetros operacionais. |
| `profit_centers` | gold | Expõe definições mestre de centros de lucro de CEPC e CEPCT, incluindo intervalos de vigência, empresas, segmentos, responsáveis, indicadores de bloqueio e nomes/descrições multilíngues, para avaliação de desempenho e relatório por segmento. |
| `proj` | bronze | Definição de projeto (SAP PROJ). |
| `project_info_database` | gold | Expõe valores reais, orçados, comprometidos e planejados por período e exercício fiscal para projetos SAP e elementos EAP da Base de Dados de Informações de Projeto (RPSCO). |
| `project_structure` | gold | Combina definições de projeto, elementos WBS e dados de programação das tabelas SAP PROJ, PRPS, PRTE e PRHI para fornecer uma visão consolidada de estruturas de projeto, hierarquias e cronogramas. |
| `prps` | bronze | Dados mestre do elemento WBS (Work Breakdown Structure, SAP PRPS). |
| `prte` | bronze | Dados de programação do item de projeto |
| `purchasing_document_headers` | gold | Termos administrativos e comerciais de ordens de compra, contratos e programações de entrega SAP (EKKO), com datas de transação, fornecedores, moedas e condições de pagamento. |
| `purchasing_document_items` | gold | Itens de documentos de compras SAP (EKPO): materiais, quantidades, componentes de preço, centros e atribuições de conta, para análise de compras. |
| `purchasing_document_schedule_lines` | gold | Captura cronogramas logísticos de entrega do SAP EKET, especificando datas de entrega, quantidades programadas e quantidades recebidas/emitidas por linha de item. |
| `purchasing_groups` | gold | Dados mestre de grupos de compras do SAP T024, mapeando cada grupo ao seu nome, telefone e e-mail. |
| `purchasing_organizations` | gold | Dados mestre da hierarquia de organizacoes de compras do SAP T024E, mapeando cada unidade organizacional a sua descricao e empresa associada (BUKRS). |
| `rbco` | bronze | Item de documento de entrada de fatura com atribuição de conta |
| `rbkp` | bronze | Cabeçalho do documento de entrada de fatura (verificação de faturas de fornecedor) |
| `rebates_settlement_calendar` | gold | Registra as datas do calendario de liquidacao e referencias de documentos de liquidacao do WB2_D_SETTL_CAL para monitorar o status de pagamento e as frequencias de avaliacao. |
| `resb` | bronze | Reservas e necessidades dependentes |
| `rseg` | bronze | Item do documento de fatura de entrada (invoice verification) |
| `s066` | bronze | Pedidos abertos: gestão de crédito |
| `s067` | bronze | Entregas e documentos de faturamento abertos (gestão de crédito KM) |
| `sales_document_flow` | gold | Fluxo de documentos de venda a partir de VBFA, mapeando pedidos de venda para entregas e faturas subsequentes. |
| `sales_document_header_statuses` | gold | Captura os status de processamento, entrega e faturamento do cabeçalho do documento de venda do SAP VBUK (ECC) ou VBAK (S4). |
| `sales_document_headers` | gold | Detalhes do cabeçalho de documentos de vendas do SAP VBAK, incluindo contas de clientes, valor líquido, categorias de documento e datas. |
| `sales_document_item_statuses` | gold | Captura os status de separacao, entrega e faturamento dos itens de documentos de vendas a partir da VBUP do SAP (ECC) ou VBAP/LIPS (S4). |
| `sales_document_items` | gold | Itens de documentos de vendas SAP (VBAP): materiais, quantidades pedidas, precos liquidos e locais de producao. |
| `sales_document_partners` | gold | Dados de parceiros de documentos de vendas (cabeçalho e itens) do SAP VBPA, incluindo funções como Parceiro Pagador e Parceiro Destinatário da Mercadoria. |
| `sales_document_schedule_lines` | gold | Dados de linhas de programação de itens de documentos de vendas SAP (VBEP), detalhando quantidades confirmadas, solicitadas e entregues. |
| `sales_organizations` | gold | Detalhes e configurações das organizações de vendas SAP (TVKO), enriquecidos com textos descritivos multilíngues de TVKOT para análise da estrutura territorial de vendas. |
| `setheader` | bronze | Cabecalho e diretorio de conjunto SAP (set) |
| `setheadert` | bronze | Descricao resumida de conjuntos (sets) do SAP |
| `setleaf` | bronze | Valores em conjuntos (folhas) |
| `setnode` | bronze | Subconjuntos em conjuntos (nós internos) |
| `ska1` | bronze | Mestre de contas contábeis (plano de contas) |
| `skat` | bronze | Registro mestre de conta contábil por plano de contas e idioma (G/L Account Master Record) |
| `skb1` | bronze | Mestre de conta contabil por empresa (SKB1) |
| `stas` | bronze | Seleção de itens de lista de materiais (LM) |
| `stko` | bronze | Cabeçalho da lista de materiais (BOM Header, SAP STKO). |
| `storage_locations` | gold | Dados mestre de depositos/locais de estocagem do SAP T001L, mapeando locais a seus centros e divisoes. |
| `stpo` | bronze | Item da lista de materiais (BOM) |
| `system_status_texts` | gold | Textos de status de sistema dependentes de idioma do SAP TJ02T, permitindo mapeamento localizado de status. |
| `t000` | bronze | Mandantes |
| `t001` | bronze | Empresas (Company Codes) |
| `t001k` | bronze | Área de avaliação (valuation area) |
| `t001l` | bronze | Depósitos (locais de armazenamento por centro) |
| `t001t` | bronze | Textos dependentes de empresa (company code) |
| `t001w` | bronze | Centros e filiais (T001W) |
| `t002` | bronze | Chaves de idioma do SAP (componente BC-I18), independente de mandante |
| `t002t` | bronze | Textos das chaves de idioma do SAP (independente de mandante) |
| `t005` | bronze | Tabela de configuração de países (T005) |
| `t005k` | bronze | Código de discagem internacional por país (tabela de comunicação SAP T005K). |
| `t005s` | bronze | Chaves de regiao/provincia para calculo de impostos |
| `t005t` | bronze | Nomes de países por idioma |
| `t005u` | bronze | Textos das chaves de regiao para impostos (dependente de idioma) |
| `t006` | bronze | Unidades de medida |
| `t006a` | bronze | Atribuição de unidade de medida interna à unidade dependente de idioma (T006A) |
| `t006t` | bronze | Textos de dimensoes de unidades de medida (dependente de idioma) |
| `t009` | bronze | Variantes de exercício fiscal |
| `t009b` | bronze | Períodos da variante de exercício fiscal |
| `t023` | bronze | Grupos de materiais |
| `t023t` | bronze | Descricoes de grupos de materiais (dependente de idioma) |
| `t024` | bronze | Grupos de compras |
| `t024e` | bronze | Organizações de compras |
| `t090nat` | bronze | Textos de chaves de depreciacao do ativo imobilizado (dependente de idioma) |
| `t093b` | bronze | Parâmetros de empresa para área de depreciação |
| `t093c` | bronze | Configurações de código de empresa para contabilidade de ativos (SAP T093C). |
| `t093t` | bronze | Textos de areas de depreciacao do ativo imobilizado |
| `t095t` | bronze | Nomes dos determinantes de conta do ativo imobilizado (dependente de idioma) |
| `t098t` | bronze | Descricao dos motivos de avaliacao manual do ativo imobilizado (dependente de idioma) |
| `t134` | bronze | Tipos de material |
| `t134t` | bronze | Descricoes dos tipos de material (dependente de idioma) |
| `t148t` | bronze | Descricoes de estoques especiais (dependente de idioma) |
| `t156` | bronze | Tipo de movimento de materiais |
| `t156c` | bronze | Tipos de estoque e seus valores (tabela de customizing independente de mandante) |
| `t156t` | bronze | Texto do tipo de movimento de mercadoria |
| `t157e` | bronze | Tabela de textos para motivos de movimento de material (dependente de idioma) |
| `t157t` | bronze | Descricao dos campos do bloco de disponibilidade (verificacao de disponibilidade) |
| `t161` | bronze | Tipos de documento de compras (T161) |
| `t161t` | bronze | Textos dos tipos de documento de compras (dependente de idioma) |
| `t179` | bronze | Hierarquias de produtos de materiais do SAP |
| `t179t` | bronze | Textos das hierarquias de produtos de materiais (dependente de idioma) |
| `t881` | bronze | Mestre do razao contabil (T881) |
| `t881t` | bronze | Textos de razao contabil do FI-SL (dependente de idioma) |
| `tbdls` | bronze | Sistema logico de distribuicao de dados (ALE/IDOC), independente de mandante |
| `tcurc` | bronze | Codigos de moeda do SAP |
| `tcurf` | bronze | Fatores de conversão de moeda |
| `tcurr` | bronze | Taxas de câmbio (TCURR) |
| `tcurt` | bronze | Nomes de codigos de moeda do SAP (dependente de idioma) |
| `tcurv` | bronze | Tipos de taxa de câmbio para conversão de moeda |
| `tcurx` | bronze | Casas decimais das moedas no SAP (independente de mandante) |
| `tf200` | bronze | Versoes de consolidacao |
| `tfacd` | bronze | Definição de calendário de fábrica |
| `tfacs` | bronze | Calendário de fábrica (exibição) |
| `tfact` | bronze | Textos do calendario de fabrica (independente de mandante) |
| `time_dependent_asset_allocations` | gold | Rastreia as alocacoes organizacionais com dependencia temporal de ativos fixos (centro de custo, centro de lucro, planta, etc.) a partir da ANLZ do SAP. |
| `tj02t` | bronze | Textos de status de sistema SAP (independente de mandante, dependente de idioma) |
| `tj20t` | bronze | Textos dos perfis de status de usuario (dependente de idioma) |
| `tka01` | bronze | Áreas de controladoria |
| `tka02` | bronze | Atribuicao de empresas e areas de negocio a areas de controlling |
| `tspa` | bronze | Divisoes de vendas (unidade organizacional de vendas) |
| `tspat` | bronze | Textos das divisoes organizacionais de vendas (dependente de idioma) |
| `tstc` | bronze | Codigos de transacao SAP (tabela independente de mandante) |
| `tvarvc` | bronze | Tabela de variáveis de variante de seleção (dependente de mandante) |
| `tvfs` | bronze | Motivos de bloqueio de faturamento |
| `tvfst` | bronze | Textos dos motivos de bloqueio de faturamento (dependente de idioma) |
| `tvko` | bronze | Unidade organizacional: organizações de vendas (SAP TVKO). |
| `tvkot` | bronze | Textos das organizacoes de vendas (dependente de idioma) |
| `tvls` | bronze | Motivos e critérios de bloqueio de entrega |
| `tvlst` | bronze | Textos dos motivos de bloqueio de entrega (dependente de idioma) |
| `tvst` | bronze | Unidade organizacional: pontos de expedição (SAP TVST). |
| `tvstt` | bronze | Textos dos pontos de expedicao/recebimento (dependente de idioma) |
| `tvstz` | bronze | Unidade organizacional: pontos de expedição por planta |
| `tvtw` | bronze | Canais de distribuicao (unidade organizacional de vendas) |
| `tvtwt` | bronze | Textos dos canais de distribuicao (dependente de idioma) |
| `units_of_measurement` | gold | Visão padronizada das unidades de medida SAP (T006/T006A/T006T), incluindo pesos, volumes, dimensões e temperaturas, com mapeamento para códigos ISO. |
| `universal_journal_entry_ledgers` | gold | Lista mestre de razões definidos no S/4HANA a partir de FINSC_LEDGER, enriquecida com descrições multilíngues de FINSC_LEDGER_T. |
| `universal_journal_entry_line_items` | gold | Itens de lançamento contábil do razão unificado do S/4HANA (ACDOCA), suportando análises de balanço, DRE e variações. |
| `usr01` | bronze | Registro mestre de usuário (dados de runtime) |
| `usr02` | bronze | Dados de logon do usuário SAP (uso interno do kernel) |
| `vbak` | bronze | Cabeçalho do documento de vendas (SD) |
| `vbap` | bronze | Documento de venda: dados do item (VBAP) |
| `vbep` | bronze | Dados de linha de programa de remessa do documento de vendas (VBEP) |
| `vbfa` | bronze | Fluxo do documento de vendas |
| `vbkd` | bronze | Dados comerciais do documento de vendas |
| `vbpa` | bronze | Parceiros do documento de vendas |
| `vbrk` | bronze | Documento de faturamento: dados do cabeçalho (Billing Document Header Data) |
| `vbrp` | bronze | Documento de faturamento: dados de item (VBRP) |
| `vbuk` | bronze | Documento de vendas: status do cabeçalho e dados administrativos |
| `vbup` | bronze | Documento de vendas: status do item |
| `vendor_cleared_items` | gold | Visão detalhada dos itens de transação de fornecedores compensados do SAP ECC (BSAK) para suporte à conciliação automatizada e auditoria de pagamentos históricos. |
| `vendor_invoice_account_assignments` | gold | Detalha as imputações contábeis dos itens de linha de notas fiscais de fornecedores do SAP RBCO, mapeando transações para centros de custo, centros de lucro, contas de razão geral e elementos WBS. |
| `vendor_invoice_headers` | gold | Visão unificada em nível de cabeçalho das faturas de fornecedores a partir do SAP RBKP, permitindo auditoria de valores brutos, detalhes de impostos e descontos de caixa. |
| `vendor_invoice_items` | gold | Itens de faturas de fornecedores recebidas, com quantidades faturadas, materiais e referencias ao pedido de compra (origem: SAP RSEG) |
| `vendor_open_items` | gold | Visão detalhada dos itens de transação de fornecedores em aberto do SAP ECC (BSIK) para acompanhamento operacional e análise de passivos pendentes. |
| `vendors` | gold | Visão consolidada do cadastro de fornecedores — combina informações base do fornecedor (LFA1) com detalhes de endereço físico (ADRC). |
| `wb2_d_bvdetail` | bronze | CCS: demonstrativo detalhado de volume de negócios para liquidação (SAP WB2_D_BVDETAIL). |
| `wb2_d_settl_cal` | bronze | Calendário de liquidação de bonificações (rebates) |
| `wbrk` | bronze | Cabeçalho do documento de liquidação de agência |
| `wbrp` | bronze | Documento de liquidacao de agencia: item |
| `wcocoh` | bronze | Cabeçalho do contrato de condição |
| `wcocoi` | bronze | Contrato de condição: item |
