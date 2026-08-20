# Diretrizes gerais

- Foco na reprodutibilidade:
    - A criacao de todos os recursos deve estar presente nos notebooks/bundles finais.
    - Use metodos idempotentes para garantir a reprodutibilidade.
- Seja didatico:
    - Explique o fluxo geral e as funcionalidades usadas em celulas markdown.
    - Comentarios inline devem ser sucintos (interpretabilidade / instrucoes de preenchimento).
    - Nao descreva ou explique as alteracoes feitas.
- Seja pragmatico:
    - Para testes lentos em notebooks grandes, use um notebook one-off / DRAFT e depois atualize o final.
    - Para duvidas, faca pequenos testes one-off e depois consolide.
    - Use diretorios temporarios para execucoes one-off.
- Uso do Databricks:
    - Prefira Serverless nos jobs para minimizar startup e iterar mais rapido, salvo limitacao.
    - Use a Databricks CLI para importar/exportar codigos e operar bundles.
- Todos os artefatos produzidos devem estar em PT-BR.
