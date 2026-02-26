# Design de Conciliação de Transações de Renda Fixa

Este documento detalha o plano para implementar o fluxo de trabalho de conciliação diária, garantindo que 1 milhão de registros sejam processados em menos de 20 minutos.

## 1. Arquitetura do Fluxo de Trabalho (Workflow)

O fluxo será dividido em etapas sequenciais com monitoramento em tempo real:

### Etapa 1: Ingestão e Validação do Arquivo

- **Ação**: Recebimento do CSV via SFTP ou Cloud Storage.
- **Validação**: Verificar layout do arquivo (colunas: `external_id`, `order_id`, etc.) e integridade básica (ex: tipos de dados, campos obrigatórios).
- **Tratamento de Erros**: Se o arquivo for inválido ou não chegar no prazo, disparar notificação imediata.

### Etapa 2: Processamento Paralelo de Dados

- **Ferramenta Sugerida**: Processamento em memória (foco em performance para atingir o SLA de 20min).
- **Ação**: Carregar movimentações do dia (arquivo CSV) e movimentações internas do dia anterior (banco de dados).

### Etapa 3: Motor de Conciliação (Diff Engine)

- **Lógica**: Comparar registros baseando-se em chaves únicas (`order_id` ou combinação de `external_id` + `asset_id`).
- **Verificação de Atributos**: Comparar `quantity`, `unit_price`, e `transaction_type`.
- **Categorização**:
  - **Match**: Registros idênticos em ambos os lados.
  - **Divergência**: Registros com valores diferentes em campos-chave.
  - **Faltante (Orfandade)**: Registro presente em apenas uma das bases.

### Etapa 4: Geração de Relatório e Publicação

- **Saída**: Relatório em formato tabular/dashboard para a área responsável.
- **Ação**: Publicar o relatório em um portal interno ou área de BI.

### Etapa 5: Notificação e Finalização

- **Sucesso**: Notificar equipe sobre a conclusão e disponibilidade do relatório.
- **Falha**: Enviar detalhes técnicos para a equipe de suporte.

---

## Proposta de Implementação Técnica

### Componentes [NEW]

- `ConciliatorService`: Motor principal de comparação.
- `ValidationLayer`: Validação de esquema de arquivo.
- `ReportingEngine`: Gerador de relatórios de divergência.

## Plano de Verificação

### Testes Automatizados

- Simulação com arquivo CSV de 1 milhão de linhas para validar o SLA de 20 minutos.
- Testes unitários para casos de divergência de preço e quantidade.

### Verificação Manual

- Verificação visual do relatório gerado comparando com uma amostra de dados controlada.

---

Este documento foi validado e assinado por David Wallace Marques Ferreira - Engenheiro Sênior
