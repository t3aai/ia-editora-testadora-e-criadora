# GUIA COMPLETO: ESTRUTURAÇÃO DE BASES DE DADOS PARA AGENTES DE ATENDIMENTO

**Versão:** 2.0 (com integração T3A Analyser)  
**Data de Criação:** 22/01/2026  
**Última Atualização:** 22/01/2026  
**Responsável:** T3A Intelligence  

---

## O QUE É UMA BASE DE DADOS

Uma **Base de Dados** é um documento técnico estruturado que centraliza todas as informações essenciais de uma empresa para orientar agentes (humanos ou virtuais) no atendimento ao cliente. Funciona como um manual de referência completo que permite respostas precisas, consistentes e alinhadas com a identidade da marca.

### Objetivo Principal

Garantir que qualquer agente, ao consultar a base, consiga:

- ✅ Responder perguntas com informações corretas e atualizadas
- ✅ Manter tom de voz e posicionamento da marca
- ✅ Oferecer soluções adequadas para cada situação
- ✅ Evitar erros, contradições ou informações desatualizadas

---

## COMPONENTES ESSENCIAIS DE UMA BASE DE DADOS

### 1. INFORMAÇÕES DA EMPRESA

#### O que incluir:

- **Identificação:** Nome completo, segmento, razão social (se aplicável)
- **Localização:** Endereço completo, pontos de referência, instruções de acesso
- **Contatos:** Telefone, WhatsApp, email, redes sociais (com @usuário)
- **Horário de Funcionamento:** Dias da semana, horários especiais, feriados
- **Público-Alvo:** Descrição detalhada de quem a empresa atende
- **Diferenciais Competitivos:** O que torna a empresa única no mercado
- **Missão/Valores:** Posicionamento, propósito, promessas ao cliente

#### Exemplo de estruturação:

```markdown
### IDENTIFICAÇÃO
- Nome: [Nome da Empresa]
- Segmento: [Área de atuação]
- Público-Alvo: [Descrição detalhada]

### LOCALIZAÇÃO
- Endereço: [Endereço completo com CEP]
- Ponto de referência: [Se aplicável]
- Instruções de acesso: [Como chegar, onde fica]

### CONTATOS
- WhatsApp: (XX) XXXXX-XXXX
- Instagram: @usuario
- Email: contato@empresa.com

### HORÁRIO DE FUNCIONAMENTO
- Segunda a Sexta: 9h às 18h
- Sábado: 9h às 13h
- Domingo: Fechado

### DIFERENCIAIS
- Diferencial 1: [Descrição]
- Diferencial 2: [Descrição]
- Diferencial 3: [Descrição]
```

---

### 2. PRODUTOS E SERVIÇOS

#### Estrutura recomendada para cada produto:

##### A) ORGANIZAÇÃO POR CATEGORIAS

Agrupe produtos/serviços similares para facilitar navegação:

```markdown
### CATEGORIA: [NOME DA CATEGORIA]

#### Produto 1
#### Produto 2
#### Produto 3
```

##### B) INFORMAÇÕES DE CADA PRODUTO

Para cada item, inclua:

1. **Identificação:**
   - Nome oficial do produto
   - Marca/fabricante
   - Modelo/versão
   - Apelidos/nomes populares (se houver)

2. **Especificações Técnicas:**
   - Tamanho/peso/dimensões
   - Variações (sabores, cores, capacidades)
   - Composição/ingredientes/materiais
   - Características técnicas relevantes

3. **Precificação:**
   - Valor à vista
   - Valores parcelados (se aplicável)
   - Promoções ativas
   - Condições especiais

4. **Disponibilidade:**
   - Status de estoque (disponível/limitado/esgotado)
   - Quantidade em estoque (se relevante)
   - Previsão de reposição (se esgotado)

5. **Descrição Comercial:**
   - Para que serve
   - Principais benefícios
   - Diferencial do produto
   - Para quem é indicado

6. **Modo de Uso/Aplicação:**
   - Como usar corretamente
   - Dosagem/frequência recomendada
   - Melhores práticas
   - Tempo de uso para ver resultados

7. **Avisos e Contraindicações:**
   - Quem não deve usar
   - Cuidados especiais
   - Efeitos colaterais possíveis
   - Recomendações de segurança

8. **Recursos Visuais:**
   - Links para imagens (frente/verso/detalhes)
   - Vídeos demonstrativos (se aplicável)
   - Tabelas nutricionais/técnicas

---

### 3. OBJEÇÕES

**Objeções** são as resistências, dúvidas ou barreiras que impedem o cliente de finalizar a compra. Esta seção deve antecipar essas situações e fornecer respostas estratégicas.

#### Categorias comuns de objeções:

- 💰 Preço/Investimento
- ⏰ Necessidade/Urgência
- 🔒 Confiança/Credibilidade
- 📅 Timing/Momento
- 🔄 Comparação com concorrentes
- ⚙️ Funcionalidade/Adequação
- 🛒 Processo de compra

#### Formato de cada objeção:

```markdown
**Objeção:** [Frase típica do cliente]

**Contexto:** [Situação em que aparece]

**Estratégia de resposta:**
1. [Passo 1]
2. [Passo 2]
3. [Passo 3]

**Respostas sugeridas:**
- \"[Exemplo de resposta 1]\"
- \"[Exemplo de resposta 2]\"

**❌ Não fazer:**
- [O que evitar]
```

---

### 4. DÚVIDAS FREQUENTES (FAQ)

Esta seção antecipa e responde perguntas recorrentes, reduzindo tempo de atendimento e aumentando autonomia do cliente.

#### Organização por temas:

```markdown
### DÚVIDAS SOBRE PRODUTOS
[Perguntas técnicas sobre produtos/serviços]

### DÚVIDAS SOBRE COMPRA
[Processo de pedido, pagamento, entrega]

### DÚVIDAS SOBRE PÓS-VENDA
[Garantia, troca, suporte]

### DÚVIDAS SOBRE POLÍTICAS
[Privacidade, termos de uso, regras]
```

#### Formato de cada pergunta:

```markdown
**Pergunta:** [Pergunta exata como cliente faria]

**Resposta curta:** [Resposta direta em 1-2 linhas]

**Resposta completa:** [Explicação detalhada se necessário]

**Informações adicionais:** [Links, referências, próximos passos]
```

---

### 5. POLÍTICAS E CONDIÇÕES

#### A) FORMAS DE PAGAMENTO

```markdown
### PAGAMENTOS ACEITOS
- ✅ PIX (à vista) - Chave: [chave]
- ✅ Cartão de crédito (até Xx)
- ✅ Cartão de débito
- ✅ Boleto bancário
- ✅ Transferência bancária
- ❌ Cheque (não aceitamos)

### CONDIÇÕES ESPECIAIS
- Desconto de X% para pagamento à vista
- Parcelamento sem juros até Xx
- Primeira compra: desconto de X%
```

#### B) ENTREGA E RETIRADA

```markdown
### ENTREGA
- Prazo: X a X dias úteis
- Áreas atendidas: [regiões]
- Valor do frete: R$ XX,XX ou grátis acima de R$ XXX
- Rastreamento: enviado por WhatsApp/email

### RETIRADA NA LOJA
- Disponível em [endereço]
- Horário: [horário]
- Produto fica reservado por X horas
- Trazer documento com foto
```

#### C) TROCAS E DEVOLUÇÕES

```markdown
### POLÍTICA DE TROCA
- Prazo: até X dias após recebimento
- Produto sem uso, na embalagem original
- Nota fiscal obrigatória
- Não aceitamos: [exceções]

### COMO SOLICITAR
1. Entrar em contato pelo WhatsApp
2. Informar motivo da troca
3. Enviar fotos do produto
4. Aguardar autorização
5. Enviar/levar produto
```

---

## ESTRUTURA COMPLETA SUGERIDA

```markdown
# BASE DE DADOS - [NOME DA EMPRESA]

## 1. INFORMAÇÕES GERAIS
### 1.1 Identificação da Empresa
### 1.2 Localização e Contatos
### 1.3 Horário de Funcionamento
### 1.4 Diferenciais Competitivos
### 1.5 Público-Alvo

## 2. PRODUTOS E SERVIÇOS
### 2.1 Categoria 1
#### Produto A
#### Produto B
### 2.2 Categoria 2
#### Produto C
### 2.3 Tabelas Resumo
### 2.4 Kits e Combos

## 3. OBJEÇÕES
### 3.1 Objeções de Preço
### 3.2 Objeções de Necessidade
### 3.3 Objeções de Confiança
### 3.4 Objeções de Timing
### 3.5 Outras Objeções

## 4. DÚVIDAS FREQUENTES (FAQ)
### 4.1 Sobre Produtos
### 4.2 Sobre Compra e Pagamento
### 4.3 Sobre Entrega
### 4.4 Sobre Trocas e Garantia
### 4.5 Sobre a Empresa

## 5. POLÍTICAS E CONDIÇÕES
### 5.1 Formas de Pagamento
### 5.2 Entrega e Retirada
### 5.3 Trocas e Devoluções
### 5.4 Garantias
### 5.5 Privacidade e Dados

## 6. PROCESSOS INTERNOS
### 6.1 Fluxo de Atendimento
### 6.2 Escalação de Problemas
### 6.3 Situações Especiais
### 6.4 Scripts de Mensagens

## 7. AVISOS LEGAIS E IMPORTANTES
### 7.1 Compliance e Regulamentações
### 7.2 Contraindicações
### 7.3 Termos de Uso

## 8. INFORMAÇÕES DE CONTROLE
### 8.1 Histórico de Atualizações
### 8.2 Responsáveis
### 8.3 Próxima Revisão
```

---

## MAPEAMENTO PARA GAP ANALYSIS

### Campos Obrigatórios para Validação:

#### 1. INFORMAÇÕES DA EMPRESA (Obrigatório)
- [ ] Nome da empresa
- [ ] Segmento/área de atuação
- [ ] Pelo menos 1 forma de contato
- [ ] Horário de funcionamento OU indicação de atendimento 24h

#### 2. PRODUTOS/SERVIÇOS (Obrigatório - mínimo 1)
Para cada produto:
- [ ] Nome do produto/serviço
- [ ] Descrição básica (mínimo 20 caracteres)
- [ ] Preço OU indicação de \"sob consulta\"
- [ ] Disponibilidade (em estoque/sob encomenda/esgotado)

#### 3. OBJEÇÕES (Recomendado - mínimo 2)
- [ ] Pelo menos 1 objeção de preço
- [ ] Pelo menos 1 objeção de confiança/timing/necessidade
- [ ] Estratégia de resposta para cada objeção

#### 4. FAQ (Recomendado - mínimo 3)
- [ ] Perguntas sobre produtos
- [ ] Perguntas sobre compra/pagamento
- [ ] Perguntas sobre entrega/garantia

#### 5. POLÍTICAS (Obrigatório)
- [ ] Formas de pagamento aceitas
- [ ] Política de entrega OU retirada
- [ ] Política de troca/devolução

### Gaps Críticos que Bloqueiam Geração:

🔴 **CRÍTICO** - Sistema não pode gerar prompt sem:
- Nome da empresa
- Pelo menos 1 produto/serviço com preço
- Pelo menos 1 forma de contato
- Política de pagamento

🟡 **IMPORTANTE** - Sistema gera com avisos:
- Sem objeções mapeadas
- Sem FAQ estruturado
- Sem política de trocas

🟢 **OPCIONAL** - Melhora qualidade mas não bloqueia:
- Imagens de produtos
- Vídeos demonstrativos
- Depoimentos de clientes
- Certificações

---

**Última Atualização:** 22/01/2026  
**Versão:** 2.0 (com integração T3A Analyser)
