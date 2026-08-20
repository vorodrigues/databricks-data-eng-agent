# Diretrizes de codigo

## 1. Pense antes de codar
- Explicite suposicoes. Se incerto, pergunte.
- Se ha multiplas interpretacoes, apresente-as — nao escolha em silencio.
- Se existe abordagem mais simples, diga. Questione quando cabivel.

## 2. Simplicidade primeiro
- Codigo minimo que resolve o problema. Nada especulativo.
- Sem abstracoes para uso unico, sem flexibilidade nao solicitada.

## 3. Mudancas cirurgicas
- Toque apenas no necessario. Siga o estilo existente.
- Nao refatore o que nao esta quebrado. Remova apenas orfaos criados por voce.

## 4. Determinismo primeiro
- Prefira o notebook parametrizado reutilizavel (CDC, SCD Tipo 1).
- Para excecoes, parta do template pre-construido e faca a alteracao minima.
- Toda ingestao e incremental e idempotente.

## 5. Execucao orientada a objetivo
- Transforme tarefas em criterios verificaveis e itere ate verificar.
- Atualize sempre o estado e o codigo locais e depois teste no workspace Databricks.
- Use as boas praticas de engenharia de dados da Databricks.
