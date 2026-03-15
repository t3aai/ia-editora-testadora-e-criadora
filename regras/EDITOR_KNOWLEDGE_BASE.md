# EDITOR KNOWLEDGE BASE — PADROES UNIVERSAIS DE EDICAO

**Versao:** 3.0
**Ultima atualizacao:** 11/03/2026
**Base de dados:** 22 clientes reais, 50.000+ linhas de conversa analisadas
**Clientes analisados (v2.0):** Gnomo Suplementos, Cafe Virtual, Rodrigo Vancini, Placas & Brindes, Star Protecao Veicular, Star V2, Nuvtech, King Manutencoes, Imagem Soccer, Elishop
**Clientes adicionados (v3.0):** Lameds, Hudson (Instituto Gourmet), BR Sollar, Eduardo (Rei do Pod), Plastbox, Cleef, Titancell, Arck1pro, Curta (Gratta), Kohll Beauty, Odonto Referencia, Traiano Advogados

---

## COMO USAR ESTE DOCUMENTO

Este documento contem regras GENERICAS extraidas de dados reais. A IA Editora deve:
1. Consultar este documento ANTES de cada edicao
2. Verificar quais padroes de deteccao (D-XX) se aplicam ao problema reportado
3. Aplicar as regras de correcao (R-XX) correspondentes
4. Seguir as meta-regras (M-XX) durante o processo de edicao
5. Nunca aplicar regras especificas de um segmento a outro — usar apenas os padroes universais

---

## SECAO 1: PADROES DE DETECCAO

O que o analisador deve buscar no prompt e base de dados do cliente.

### D-01 — DADO INCORRETO NA BASE
**Severidade:** CRITICO
**Frequencia:** 8/10 clientes (Cafe, Placas, Vancini, King, Imagem, Elishop, Star, StarV2)
**O que buscar:**
- Precos, prazos, tamanhos, formas de pagamento que nao tem tabela explicita
- Valores hardcoded no prompt em vez de na base de dados
- Dados que dependem de variacao (tamanho, modelo, regiao) sem tabela de variantes
**Indicador:** Cliente reclamou "preco errado", "valor incorreto", "informacao desatualizada"

### D-02 — SERVICO/PRODUTO INEXISTENTE SENDO OFERECIDO
**Severidade:** CRITICO
**Frequencia:** 5/10 clientes (Cafe, Placas, Imagem, Elishop, Star)
**O que buscar:**
- Ausencia de secao "O QUE NAO FAZEMOS" quando ha 5+ produtos/servicos
- IA mencionando produtos genericos sem restricao (ex: "trofeus" quando so faz placas)
- Descricoes de produto com features que nao existem
**Indicador:** Cliente disse "nao fazemos isso", "isso nao existe", "inventou produto"

### D-03 — TOM ROBOTICO / MENSAGENS LONGAS
**Severidade:** ALTA
**Frequencia:** 9/10 clientes (todos exceto StarV2 que era muito curto para avaliar)
**O que buscar:**
- Mensagens de exemplo no prompt com mais de 3 linhas
- Frases corporativas: "estou a disposicao", "como posso ajudar hoje", "fico a disposicao"
- IA repetindo nome do lead em cada mensagem
- Fechamentos formais em cada resposta
**Indicador:** Cliente pediu "mais curto", "mais humano", "menos robotico", "menos formal"
**Regra comprovada:** Nome do lead: usar APENAS na saudacao inicial. Depois, nunca mais.

### D-04 — SEQUENCIA DE PERGUNTAS FORA DE ORDEM
**Severidade:** ALTA
**Frequencia:** 6/10 clientes (Cafe, King, Gnomo, Star, Imagem, Placas)
**O que buscar:**
- Fluxo sem numeracao explicita de etapas
- Perguntas que dependem de resposta anterior mas nao tem condicional
- IA pedindo preco antes de qualificar, ou arte antes de pagamento
**Indicador:** Cliente disse "perguntou fora de hora", "nao faz sentido essa ordem"

### D-05 — REGRAS DE PAGAMENTO INCOMPLETAS
**Severidade:** ALTA
**Frequencia:** 6/10 clientes (Cafe, Placas, Vancini, Gnomo, King, Imagem)
**O que buscar:**
- Ausencia de checklist: metodo (PIX/cartao/boleto), parcelas, desconto, sinal, momento
- Pagamento cobrado no momento errado do fluxo (ex: antes de aprovar arte)
- Formas de pagamento mencionadas parcialmente
**Indicador:** Cliente corrigiu forma de pagamento, momento de cobranca, ou desconto

### D-06 — MIDIA SEM MAPEAMENTO PRODUTO→IMAGEM
**Severidade:** MEDIA
**Frequencia:** 5/10 clientes (Cafe, Placas, Imagem, Star, Elishop)
**O que buscar:**
- IA promete enviar foto/video mas nao envia
- Imagem enviada nao corresponde ao produto discutido
- Ausencia de tabela produto→asset(imagem/video/PDF)
**Indicador:** Cliente disse "imagem errada", "mandou foto de outro produto", "nao enviou foto"

### D-07 — TRANSFERENCIA PARA HUMANO GENERICA
**Severidade:** MEDIA
**Frequencia:** 7/10 clientes (Placas, Cafe, Vancini, Star, Nuvtech, Imagem, King)
**O que buscar:**
- Frase de transferencia sem identidade da marca
- Lead confuso se estava falando com IA ou humano
- Ausencia de instrucao sobre o que acontece DEPOIS da transferencia
**Indicador:** Cliente disse "lead ficou confuso", "pensou que era eu", "nao sabia que era IA"

### D-08 — IA CONTINUA APOS OBJETIVO ATINGIDO
**Severidade:** ALTA
**Frequencia:** 8/10 clientes (Vancini, Star, Nuvtech, King, Cafe, Elishop, Placas, Imagem)
**O que buscar:**
- Ausencia de regra de encerramento apos agendamento/venda/transferencia
- IA oferecendo mais ajuda depois que lead ja confirmou
- Follow-up disparado para lead que ja converteu
**Indicador:** Cliente disse "continua falando", "nao para", "lead desmarcou por causa disso"
**Dado real:** Em Vancini, lead DESMARCOU reuniao porque IA continuou mandando mensagens apos confirmacao.

### D-09 — IA RE-PERGUNTA DADOS JA FORNECIDOS
**Severidade:** ALTA
**Frequencia:** 7/10 clientes (Placas, Star, King, Cafe, Elishop, Vancini, Nuvtech)
**O que buscar:**
- IA pedindo nome quando ja foi dito
- IA pedindo informacao que o lead deu na primeira mensagem
- Ausencia de instrucao "extrair dados da mensagem inicial antes de perguntar"
**Indicador:** Cliente disse "ja falei isso", "perguntou de novo", "nao le o que o lead manda"

### D-10 — IA FABRICA/INVENTA INFORMACAO (ALUCINACAO)
**Severidade:** CRITICO
**Frequencia:** 7/10 clientes (Cafe, Imagem, Elishop, Star, Placas, Vancini, Nuvtech)
**O que buscar:**
- IA mencionando descontos que nao existem
- IA gerando links de pagamento falsos
- IA dando informacoes tecnicas sobre produto que nao confere
- IA prometendo coisas que nao pode cumprir (enviar proposta, materiais)
**Indicador:** Cliente disse "inventou", "isso nao existe", "nunca falamos isso"
**PERIGO REAL:** Imagem Soccer — IA gerou link de pagamento FALSO e chave PIX inventada. Elishop — IA inventou composicao de produto e politica de reembolso inexistente. Risco juridico.

### D-11 — COMANDO DE PAUSA/HUMANO NAO FUNCIONA
**Severidade:** CRITICO
**Frequencia:** 8/10 clientes (Cafe, Placas, Vancini, Star, King, Imagem, Elishop, Nuvtech)
**O que buscar:**
- Comando de pausa mencionado no prompt sem teste
- Multiplos formatos de comando (hashtag, frase, emoji) sem padronizacao
- IA continuando a falar quando humano intervem
**Indicador:** Cliente disse "nao para", "#oi nao funciona", "mandei 6 comandos"
**Regra comprovada (Star):** A melhor solucao e pausa AUTOMATICA: qualquer mensagem do atendente humano pausa a IA por 45min naquela conversa. Nao depende de comando.

### D-12 — CLIENTE EXISTENTE TRATADO COMO LEAD NOVO
**Severidade:** ALTA
**Frequencia:** 4/10 clientes (Star, StarV2, Nuvtech, Vancini)
**O que buscar:**
- Ausencia de roteamento inicial: "voce ja e cliente?" vs lead novo
- IA pedindo dados que ja tem de interacoes anteriores
- Cliente enviando comprovante/boleto e IA iniciando fluxo de venda
**Indicador:** Cliente disse "ja e cliente nosso", "mandou comprovante e a IA pediu dados"

### D-13 — HORARIO DE ATENDIMENTO ERRADO
**Severidade:** MEDIA
**Frequencia:** 5/10 clientes (Cafe, King, Elishop, Vancini, Star)
**O que buscar:**
- IA sugerindo horarios fora do expediente
- Ausencia de regra de horario comercial no prompt
- Follow-up disparando fora de horario
**Indicador:** Cliente disse "sugeriu reuniao no sabado", "agendou as 22h", "fora do horario"
**Regra comprovada (Elishop):** Fora do horario: "Voce sera contatado amanha a partir das 8h" (dia util). Sexta noite/sabado/domingo: "segunda a partir das 8h". NUNCA agendar horario especifico fora do expediente.

### D-14 — EDICAO NAO PERSISTE / REVERTE APOS OUTRA MUDANCA
**Severidade:** ALTA
**Frequencia:** 4/10 clientes (Imagem, Elishop, Star, StarV2)
**O que buscar:**
- Regra que ja foi corrigida mas voltou a falhar
- Edicao de uma secao quebrando regra de outra secao
- Historico de conversa cacheado sobrescrevendo edicao nova
**Indicador:** Cliente disse "voltou o problema", "ja corrigimos isso", "os ajustes nao foram feitos"
**Regra comprovada (Imagem):** Apos editar prompt, LIMPAR historico de conversas de teste. Contexto antigo sobrescreve instrucoes novas.

### D-15 — IA ENVIA DADOS SENSIVEIS POR FORMATO ERRADO
**Severidade:** CRITICO
**Frequencia:** 3/10 clientes (Star, Imagem, Cafe)
**O que buscar:**
- Links, telefones, CNPJ, PIX sendo enviados por audio em vez de texto
- Dados financeiros (PIX, boleto) sem verificacao
**Indicador:** Cliente disse "mandou PIX por audio", "link no audio nao funciona"
**Regra:** Numeros, links, chaves PIX, CNPJ = SEMPRE texto escrito. NUNCA audio.

### D-16 — DELAY DE RESPOSTA INADEQUADO
**Severidade:** MEDIA
**Frequencia:** 4/10 clientes (Vancini, Elishop, Star, Nuvtech)
**O que buscar:**
- IA respondendo cada mensagem individual em vez de esperar bloco completo
- Ausencia de delay configurado (recomendado: 30-60 segundos)
**Indicador:** Cliente disse "responde antes de eu terminar", "resposta em cima de resposta"
**Regra comprovada (Vancini):** Aumentar delay para 40s resolveu parcialmente. Elishop: 30-60s e o ideal.

### D-17 — SALTO DE ETAPA NO FUNIL DE VENDAS
**Severidade:** ALTA
**Frequencia:** 6/22 clientes (Hudson, BR Sollar, Arck1pro, Curta, Odonto, Traiano)
**O que buscar:**
- IA pula qualificacao e vai direto para fechamento/agendamento
- Sondagem incompleta — IA nao entende contexto do lead antes de ofertar
- Oferta enviada antes de aquecer o lead
**Indicador:** Cliente disse "pulou etapa", "nao qualificou", "ja mandou a oferta direto"
**Regra:** Definir fluxo sequencial obrigatorio. IA so avanca quando etapa anterior cumprida.

### D-18 — FOLLOW-UP SEM CONTEXTO
**Severidade:** ALTA
**Frequencia:** 7/22 clientes (Hudson, Eduardo, Cleef, Arck1pro, Traiano, Curta, Kohll)
**O que buscar:**
- Mensagens de reengajamento genericas sem referencia a conversa anterior
- Follow-up disparado apos objetivo ja alcancado (agendamento feito, venda fechada)
- Follow-up em horario inadequado (madrugada, 23h, 00h)
- Follow-up para lead que explicitamente disse que nao quer
**Indicador:** Cliente disse "follow-up generico", "mandou msg de madrugada", "ja agendou e mandou follow"
**Regra comprovada (Traiano):** Janela horaria 8h-20h obrigatoria. Verificar status do lead ANTES de disparar.

### D-19 — OVER-INFORMATION (DADOS NAO SOLICITADOS)
**Severidade:** MEDIA
**Frequencia:** 5/22 clientes (Titancell, Plastbox, Arck1pro, Curta, Kohll)
**O que buscar:**
- IA envia todas as parcelas quando lead pediu so uma
- IA descreve todos os modelos quando lead perguntou sobre um
- IA antecipa informacoes que nao foram perguntadas
**Indicador:** Cliente disse "informacao demais", "so queria saber X", "mandou tudo junto"
**Regra:** Responder SOMENTE o que foi perguntado. Nao antecipar informacoes nao solicitadas.

### D-20 — CONFUSAO ENTRE ENTIDADES SIMILARES
**Severidade:** CRITICO
**Frequencia:** 6/22 clientes (Lameds, Hudson, Plastbox, Titancell, Curta, Kohll)
**O que buscar:**
- IA confunde medicos, unidades, cidades, produtos de negocios diferentes
- Cor do vidro confundida com cor do acabamento (Plastbox)
- Foto do modelo 12 enviada no lugar do 12 Pro (Titancell)
- Produto de um expert confundido com outro (Curta)
**Indicador:** Cliente disse "misturou", "confundiu", "esse e de outro"
**Regra:** Cada entidade deve ter bloco estruturado unico na base com TODOS os atributos. Nomenclatura clara e nao-ambigua.

### D-21 — ERRO DE CALCULO NUMERICO
**Severidade:** CRITICO
**Frequencia:** 4/22 clientes (Lameds, Titancell, Arck1pro, Plastbox)
**O que buscar:**
- IA somando valores de produtos/exames incorretamente
- Calculo de parcelas errado
- Desconto aplicado onde nao deveria
- Percentuais de rendimento/juros incorretos
**Indicador:** Cliente disse "conta errada", "valor nao bate", "parcela errada"
**Regra:** IA NUNCA deve calcular valores. Tabela pre-calculada ou transferir para humano.

### D-22 — INVASAO DE ATENDIMENTO HUMANO ATIVO
**Severidade:** CRITICO
**Frequencia:** 7/22 clientes (Titancell, Kohll, Traiano, Curta, Plastbox, BR Sollar, Arck1pro)
**O que buscar:**
- IA responde em conversas onde atendente humano ja esta atuando
- Etiqueta "Em Atendimento" nao respeitada
- IA reativa automaticamente durante conversa humana
- Diferente de D-11 (que e sobre o comando tecnico): este e sobre IA nao detectar presenca humana
**Indicador:** Cliente disse "IA respondeu por cima", "atendente tava respondendo e IA entrou", "nao respeitou a etiqueta"
**Regra comprovada (Kohll):** Pausa INDEFINIDA apos transferencia. Humano reativa manualmente. NUNCA reativacao por timeout.

### D-23 — REGRESSAO DE FLUXO
**Severidade:** ALTA
**Frequencia:** 5/22 clientes (Cleef, Plastbox, Lameds, Hudson, Traiano)
**O que buscar:**
- IA volta a etapas anteriores do fluxo que lead ja completou
- Pede documentos ja enviados
- Pergunta interesse quando lead ja agendou
- Mesma correcao solicitada pelo cliente 3+ vezes sem persistir
**Indicador:** Cliente disse "ja mandei isso", "voltou a perguntar", "ja corrigimos isso antes"
**Regra:** Registrar no contexto quais etapas ja concluidas. NUNCA retornar a etapa concluida.

### D-24 — VAZAMENTO DE INFORMACAO RESTRITA
**Severidade:** CRITICO
**Frequencia:** 4/22 clientes (Plastbox, Titancell, Curta, BR Sollar)
**O que buscar:**
- IA revela precos internos que nao deveria
- IA menciona margens, valores comparativos ("2x o valor")
- IA usa palavras proibidas por razoes juridicas (ex: "cura" em saude)
- IA expoe processos internos ("analise de arquivo", "sistema detectou")
**Indicador:** Cliente disse "nao pode falar preco", "nao pode usar essa palavra", "informacao interna"
**Regra:** Lista explicita de "informacoes proibidas" no prompt. Se dado pode prejudicar venda ou gerar problema juridico, NAO mencionar.

### D-25 — MENSAGENS MULTIPLAS SEM RESPOSTA (METRALHADORA)
**Severidade:** ALTA
**Frequencia:** 5/22 clientes (Traiano, Curta, Arck1pro, Plastbox, Titancell)
**O que buscar:**
- IA dispara 3+ mensagens seguidas sem lead responder
- Varias perguntas na mesma mensagem
- IA "continua atendimento sozinha" sem interacao do lead
- Fragmentacao de mensagem de abertura em partes separadas
**Indicador:** Cliente disse "mandou tudo de uma vez", "nao esperou eu responder", "3 mensagens seguidas"
**Regra:** Maximo 1 pergunta por mensagem. Aguardar resposta antes de enviar proxima. Mensagem de abertura como bloco unico.

### D-26 — ADAPTACAO INSUFICIENTE AO PUBLICO-ALVO
**Severidade:** MEDIA
**Frequencia:** 3/22 clientes (Odonto, Traiano, Arck1pro)
**O que buscar:**
- Publico idoso e IA pede email (nao tem)
- Lead analfabeto/dificuldade de leitura e IA so manda texto
- Contexto formal (investimento, advocacia) e IA usa emojis
- IA nao adapta complexidade da linguagem ao perfil do lead
**Indicador:** Cliente disse "publico nao sabe usar", "nao tem email", "precisa ser mais simples"
**Regra:** Tom e canal devem ser calibrados ao publico-alvo no onboarding. Idosos = simples + audio. Formal = zero emojis. Jovens = informal ok.

---

## SECAO 2: REGRAS DE CORRECAO

Como o editor deve corrigir cada tipo de problema detectado.

### R-01 — CORRIGIR DADO NA BASE
**Quando:** D-01 detectado
**Acao:**
1. Criar tabela markdown com TODOS os valores por produto/variacao
2. Formato: | Produto | Tamanho | Preco | Observacao |
3. Se valor depende de consulta, escrever "sob consulta — encaminhar para humano"
4. NUNCA deixar valor calculado pela IA (ex: frete) — sempre valor fixo ou "sob consulta"
**Exemplo real (Placas):** "PIX R$250 + frete | Cartao R$300 + frete, parcela com taxas"

### R-02 — ADICIONAR SECAO NEGATIVA
**Quando:** D-02 detectado
**Acao:**
1. Adicionar secao `## O QUE NAO FAZEMOS / NAO VENDEMOS`
2. Listar explicitamente servicos/produtos que NAO oferece
3. Para cada item, dar alternativa se possivel: "Nao fazemos X, mas oferecemos Y"
**Exemplo real (Placas):** "Nao fazemos trofeus, somente placas"

### R-03 — CORRIGIR TOM E COMPRIMENTO
**Quando:** D-03 detectado
**Acao:**
1. Toda mensagem de exemplo: max 3 linhas
2. Remover: "estou a disposicao", "como posso te ajudar hoje", "sigo disponivel"
3. Substituir por versao curta e informal: "Pode falar!", "To aqui!", "Manda ai!"
4. Nome do lead: SOMENTE na saudacao. Depois, zero.
5. Remover emojis excessivos (max 1 por mensagem, e so se a marca usa)
6. Remover jargao corporativo do segmento em toda frase de encerramento
**Exemplo real (Vancini):** "Estou a disposicao para esclarecer" → "Pode falar, to aqui!"

### R-04 — NUMERAR FLUXO E ADICIONAR DEPENDENCIAS
**Quando:** D-04 detectado
**Acao:**
1. Numerar TODAS as etapas do fluxo: Etapa 1, Etapa 2, etc.
2. Adicionar prerequisito: "Etapa 3 requer resposta da Etapa 2"
3. Adicionar condicional quando fluxo ramifica: "Se X → Etapa 4A. Se Y → Etapa 4B"
4. Proibir pular etapa
**Exemplo real (Cafe):** "1.Tipo → 2.Quantidade → 3.Arte → 4.Preco → 5.Pagamento → 6.Producao"

### R-05 — COMPLETAR REGRAS DE PAGAMENTO
**Quando:** D-05 detectado
**Acao:** Adicionar checklist obrigatoria:
- [ ] Metodos aceitos (PIX, cartao, boleto, dinheiro)
- [ ] Parcelas (se cartao: quantas vezes, se tem taxa)
- [ ] Desconto PIX (se aplicavel: valor exato)
- [ ] Sinal/entrada (se aplicavel: percentual e momento)
- [ ] Quando cobrar (antes ou depois de aprovar arte/servico)
**Exemplo real (Placas):** "PIX: R$250 + frete (desconto) | Cartao: R$300 + frete, parcela com taxas da maquininha"

### R-06 — MAPEAR MIDIA POR PRODUTO
**Quando:** D-06 detectado
**Acao:**
1. Criar tabela: | Produto/Fluxo | Asset | Quando enviar |
2. Para cada produto que tem imagem: mapear qual imagem vai
3. Se IA promete enviar mas nao pode: remover a promessa do fluxo
4. Se imagem nao existe: marcar [VERIFICAR COM CLIENTE — imagem necessaria]
**Exemplo real (Imagem Soccer):** Evento simples → video de festa | Campo → video de futebol

### R-07 — PERSONALIZAR TRANSFERENCIA
**Quando:** D-07 detectado
**Acao:**
1. Substituir frase generica por: "Sou [FUNCAO] da [EMPRESA]. Vou acionar [CARGO/NOME] que ja te retorna com as informacoes."
2. Se IA deve se identificar como IA: "Sou assistente virtual da [EMPRESA]"
3. Se IA NAO deve se identificar: usar nome do persona sem mencionar "virtual" ou "IA"
4. Informar o que acontece depois: "Voce recebera retorno em ate [TEMPO]"
**Exemplo real (Placas):** "Sou assistente virtual da Placas e Brindes. Vou acionar nosso atendimento humano responsavel."

### R-08 — ADICIONAR REGRA DE ENCERRAMENTO
**Quando:** D-08 detectado
**Acao:**
1. Definir CONDICAO DE PARADA: "Apos [OBJETIVO], enviar mensagem de encerramento"
2. Mensagem de encerramento curta: "Perfeito, tudo certo! Qualquer coisa, so chamar"
3. Regra: NAO oferecer mais nada apos encerramento
4. Regra: NAO enviar follow-up para lead que ja converteu
5. Se lead respondeu "ok"/"obrigado" apos objetivo: encerrar, nao re-engajar
**Exemplo real (Vancini):** Lead agendou reuniao → IA continuou → lead DESMARCOU. Regra: apos agendamento = silencio total.

### R-09 — ADICIONAR EXTRACAO DE CONTEXTO INICIAL
**Quando:** D-09 detectado
**Acao:**
1. Adicionar regra: "ANTES de fazer qualquer pergunta, extrair dados que o lead ja forneceu na mensagem"
2. Se lead disse "quero placa de diploma 30x20": NAO perguntar tipo, NAO perguntar tamanho
3. Se lead mandou audio: mesma regra — extrair tudo antes de perguntar
4. Adicionar: "Pular etapas cujas respostas ja foram fornecidas"
**Exemplo real (King):** Lead disse modelo e defeito na 1a mensagem. IA perguntou modelo e defeito de novo.

### R-10 — RESTRINGIR ALUCINACAO
**Quando:** D-10 detectado
**Acao:**
1. Adicionar regra EXPLICITA: "NUNCA inventar valores, links, composicoes, ou politicas"
2. Se nao sabe: "Vou verificar com a equipe e te retorno" → transferir humano
3. Para pagamento: NUNCA gerar link. NUNCA informar chave PIX de memoria. Usar EXATAMENTE o que esta na base
4. Para precos: se valor nao esta na tabela da base, dizer "vou consultar"
5. Para descontos/garantias: NUNCA prometer se nao esta EXPLICITAMENTE na base
**Exemplo CRITICO (Imagem):** IA gerou "https://pag.ae/seu-link-cartao" — link FALSO. IA inventou chave PIX inexistente.

### R-11 — CONFIGURAR PAUSA AUTOMATICA
**Quando:** D-11 detectado
**Acao:**
1. IDEAL: Pausa automatica — qualquer mensagem do atendente na conversa = pausa de 45min
2. ALTERNATIVA: Comando curto, case-insensitive, tolerante a variacoes
3. Comando de retomada tambem definido (ex: #ia)
4. Documentar: comando DEVE ser enviado como mensagem separada, NAO junto com texto
**Regra comprovada (Star):** Pausa automatica por 45min na interacao do atendente. Melhor que qualquer comando.

### R-12 — ADICIONAR ROTEAMENTO INICIAL
**Quando:** D-12 detectado
**Acao:**
1. Adicionar no INICIO do fluxo: detectar intencao do contato
2. Se menciona boleto/pagamento/2a via/suporte → rota CLIENTE EXISTENTE (transferir ou numero especifico)
3. Se menciona compra/cotacao/duvida → rota LEAD NOVO (fluxo de vendas)
4. Se ambiguo: perguntar "Voce ja e nosso cliente ou esta conhecendo nossos servicos?"
**Exemplo real (Nuvtech):** Adicionou: "Este numero e para novos clientes. Se voce ja e cliente, entre em contato pelo [numero de suporte]."

### R-13 — CONFIGURAR HORARIO COMERCIAL
**Quando:** D-13 detectado
**Acao:**
1. Adicionar regra de horario no prompt com DIAS e HORAS exatos
2. Fora do horario: "Voce sera contatado [proximo dia util] a partir das [HORA]"
3. NUNCA sugerir horario especifico fora do expediente
4. Follow-ups tambem respeitam horario comercial
5. Dia-aware: "amanha" em dia util / "segunda" em sexta noite e fins de semana
**Regra comprovada (Elishop):** Mensagem noturna: "amanha a partir das 8h" (seg-qui) / "segunda a partir das 8h" (sex-dom)

### R-14 — ISOLAR REGRAS PARA EVITAR REGRESSAO
**Quando:** D-14 detectado
**Acao:**
1. Cada regra critica deve ser uma SECAO INDEPENDENTE no prompt
2. Ao editar uma secao, verificar se outras secoes nao foram afetadas
3. Apos edicao: testar o cenario da edicao E cenarios de regras adjacentes
4. Se possivel, limpar historico de conversa de teste apos edicao
**Regra comprovada (Imagem):** Contexto antigo de conversa sobrescreve instrucao nova. Limpar cache apos edicao.

### R-15 — SEPARAR FORMATO DE DADOS SENSIVEIS
**Quando:** D-15 detectado
**Acao:**
1. Adicionar regra: "Links, telefones, CNPJ, PIX, emails = SEMPRE texto escrito, NUNCA audio"
2. Se IA usa audio: marcar explicitamente quais conteudos sao "somente texto"
**Regra comprovada (Star):** Pedido feito 3x antes de resolver. Regra precisa ser MUITO explicita.

### R-16 — AJUSTAR DELAY DE RESPOSTA
**Quando:** D-16 detectado
**Acao:**
1. Configurar delay de 30-60 segundos entre ultima mensagem do lead e resposta da IA
2. IA espera bloco completo antes de responder
3. Se lead manda 3 mensagens seguidas: responder ao conjunto, nao a cada uma
**Regra comprovada (Vancini):** Delay de 40s resolveu parcialmente. 30-60s e ideal.

### R-17 — DEFINIR FLUXO SEQUENCIAL OBRIGATORIO
**Quando:** D-17 detectado
**Acao:**
1. Numerar etapas do funil: 1.Qualificar → 2.Sondar → 3.Enviar material → 4.Oferta → 5.Fechar
2. Regra: IA so avanca para etapa N+1 quando etapa N foi cumprida
3. Cada etapa tem condicao de entrada e condicao de saida
4. Se lead pula direto para "quero comprar": atender, mas preencher dados de qualificacao depois
**Exemplo real (Hudson):** IA ia direto para prova de bolsas sem sondar interesse. Correcao: etapa de sondagem obrigatoria antes.

### R-18 — CONFIGURAR FOLLOW-UP CONTEXTUAL
**Quando:** D-18 detectado
**Acao:**
1. Follow-up DEVE referenciar ultimo assunto discutido: "Ola [NOME], sobre [ASSUNTO]..."
2. Janela horaria: 8h-20h OBRIGATORIA. Nunca madrugada.
3. Verificar status do lead antes: se ja converteu → NAO enviar. Se desqualificou → NAO enviar.
4. Max 3 follow-ups. Apos 3 sem resposta: desqualificar silenciosamente.
5. Regra: follow-up para lead que disse "nao quero" = SPAM. Marcar como desqualificado.
**Exemplo real (Traiano):** Follow-ups as 23h e 00h. Correcao: janela 8h-20h + contexto da conversa anterior.

### R-19 — RESPONDER SOMENTE O SOLICITADO
**Quando:** D-19 detectado
**Acao:**
1. Regra no prompt: "Responda APENAS o que o lead perguntou. Nao antecipe informacoes."
2. Se lead pediu preco de 1 produto: enviar so esse, nao toda a tabela
3. Se lead pediu 1 parcela: enviar so essa, nao todas as opcoes
4. Oferecer "Quer saber mais detalhes?" como follow-up, em vez de enviar tudo de uma vez
**Exemplo real (Titancell):** Lead perguntou preco do iPhone 12, IA mandou tabela completa com todos os modelos.

### R-20 — ESTRUTURAR ENTIDADES COM BLOCOS UNICOS
**Quando:** D-20 detectado
**Acao:**
1. Na base de dados: cada entidade (medico, produto, unidade) em bloco independente
2. Formato: `## [ENTIDADE]: [Nome]` com TODOS os atributos dentro do bloco
3. Atributos que diferenciam entidades similares: destacar em NEGRITO
4. Se multiplos negocios/produtos: separar fluxos com gatilhos de entrada claros
5. NUNCA misturar atributos de entidades diferentes na mesma secao
**Exemplo real (Lameds):** Dr Ribamar misturado com outros medicos. Correcao: bloco individual com cidade, horarios, especialidade.

### R-21 — PROIBIR CALCULOS PELA IA
**Quando:** D-21 detectado
**Acao:**
1. Regra explicita: "NUNCA calcule valores. Use SOMENTE valores pre-calculados da tabela."
2. Para parcelas: tabela fixa | Valor | 2x | 3x | 4x | com valores exatos
3. Para somas de produtos: instruir "some manualmente e confira" ou transferir para humano
4. Para descontos: valor final ja calculado na tabela, nao percentual para IA calcular
**Exemplo real (Lameds):** IA somou exames errado (HIV 10 + hemograma 20 = respondeu errado). Titancell: parcelas calculadas errado.

### R-22 — CONFIGURAR PAUSA POR PRESENCA HUMANA
**Quando:** D-22 detectado
**Acao:**
1. IDEAL: Qualquer mensagem de atendente na conversa = pausa INDEFINIDA
2. Reativacao: SOMENTE manual pelo atendente (nunca timeout automatico)
3. Detectar presenca humana por: etiqueta, numero do atendente, ou qualquer mensagem nao-lead
4. Diferente de R-11 (comando): esta regra e sobre DETECCAO automatica de presenca humana
**Regra comprovada (Kohll):** Pausa indefinida apos transferencia. Zero conflitos humano-IA.

### R-23 — RASTREAR PROGRESSO NO FLUXO
**Quando:** D-23 detectado
**Acao:**
1. Registrar no contexto: quais etapas o lead ja completou
2. Regra: NUNCA retornar a etapa concluida
3. Se feedback do cliente foi dado: aplicar E verificar que persiste entre versoes
4. Ao editar prompt: re-testar cenarios ja corrigidos anteriormente
**Exemplo real (Hudson):** Mesmo feedback dado 3+ vezes sem correcao persistir. Cleef: IA voltava a pedir documentos ja enviados.

### R-24 — CRIAR LISTA DE INFORMACOES PROIBIDAS
**Quando:** D-24 detectado
**Acao:**
1. Secao no prompt: `## INFORMACOES PROIBIDAS (NUNCA MENCIONAR)`
2. Listar: precos restritos, termos juridicos proibidos, processos internos, margens
3. Para cada item: alternativa segura ("Em vez de preco, dizer: cada caso tem orcamento personalizado")
4. Regra HARD: se possivel, REMOVER dado da base (M-12) em vez de pedir "nao mencione"
**Exemplo real (Curta):** Palavra "cura" proibida por razoes juridicas. Plastbox: IA revelou "2x o valor" como comparacao interna.

### R-25 — LIMITAR MENSAGENS SEM RESPOSTA
**Quando:** D-25 detectado
**Acao:**
1. Regra: maximo 1 pergunta por mensagem
2. Aguardar resposta do lead antes de enviar proxima mensagem
3. Se lead envia mensagens em sequencia rapida: aguardar 30-60s para processar bloco completo
4. Mensagem de abertura: bloco unico, nunca fragmentada
5. Se lead nao responde apos 1 mensagem: aguardar, nao enviar outra pergunta
**Exemplo real (Traiano):** IA disparou varias mensagens seguidas sem lead responder. Arck1pro: 2 perguntas na mesma mensagem.

### R-26 — CALIBRAR CANAL E TOM AO PUBLICO
**Quando:** D-26 detectado
**Acao:**
1. No onboarding: perguntar perfil do publico-alvo (idade, escolaridade, formalidade)
2. Publico idoso: linguagem simples, oferecer audio, nao pedir email, nao exigir app
3. Contexto formal (juridico, financeiro): zero emojis, linguagem profissional
4. Contexto informal (e-commerce jovem): emojis ok, linguagem casual
5. Lead sinaliza dificuldade de leitura: responder em audio quando possivel
**Exemplo real (Odonto):** Publico idoso nao tem email. Correcao: oferecer preencher qualquer email. Traiano: lead nao sabia ler, IA mandava so texto.

---

## SECAO 3: META-REGRAS DE EDICAO

Regras sobre o PROCESSO de editar, nao sobre o conteudo.

### M-01 — NUNCA INVENTAR DADOS
Se informacao nao existe na base, marcar `[VERIFICAR COM CLIENTE]`. Nunca preencher com suposicao.

### M-02 — PRESERVAR LOGICA DE NEGOCIO
Editar FORMA (tom, ordem, formato), nunca SUBSTANCIA (regras do negocio, precos, politicas) sem confirmacao.

### M-03 — COMPLETAR, NUNCA REMOVER
Se algo esta incompleto, ADICIONAR o que falta. Nunca deletar informacao existente sem motivo explicito.

### M-04 — TABELA > TEXTO CORRIDO
Para precos, produtos, horarios, midias: SEMPRE usar tabela markdown. Nunca paragrafo.

### M-05 — TESTAR APOS EDICAO
Cada edicao deve ser testada com cenario especifico. Verificar: (1) o problema corrigido, (2) nada mais quebrou.

### M-06 — SECOES INDEPENDENTES
Cada regra critica em secao propria. Edicao de uma nao pode quebrar outra.

### M-07 — VERSIONAMENTO
Ao salvar edicao, incrementar versao. Nunca sobrescrever sem historico.

### M-08 — ESCALACAO
Se mesma edicao pedida 3x (detectar por similaridade): escalar para modelo avancado (Opus) e injetar tentativas anteriores como contexto.

### M-09 — MIRROR DO LEAD
Instruir IA a espelhar formato do lead: se lead manda texto curto → resposta curta. Se lead manda audio → responder em audio (se disponivel). Se lead e formal → ser formal. Se informal → ser informal.

### M-10 — AUDITAR APOS MIGRACAO
Quando prompt muda de versao, modelo, ou plataforma: verificar TODAS as regras, nao apenas a nova. Regressao e o problema #1 em edicoes (4/10 clientes afetados).

### M-11 — SCRIPT COMO GUIA, NAO COMO TEXTO LITERAL
Nunca forcar IA a falar script palavra por palavra. Usar conteudo do script como CONHECIMENTO e deixar IA adaptar ao contexto. Script rigido = tom robotico comprovado (King).

### M-12 — REGRA HARD > REGRA SOFT
Para restricoes criticas (precos, links, dados financeiros): REMOVER a informacao da base em vez de pedir "nao mencione". "Tente nao" falha; remocao total funciona (Imagem).

### M-13 — NEGACAO EXPLICITA > AFIRMACAO
Dizer "NAO fazemos X" funciona melhor que listar apenas o que faz. A IA precisa de listas de exclusao. Quando IA nao tem a informacao, ela INVENTA — a solucao e sempre "se nao sabe, pergunte ou transfira". (Lameds, Plastbox, Titancell)

### M-14 — TOM E LINGUAGEM EXIGEM EXEMPLOS, NAO DESCRICOES
Dizer "seja humanizado" nao funciona. O que funciona e dar 3-5 exemplos de mensagens no tom desejado. Descricoes de tom sao ignoradas pela IA; exemplos concretos sao seguidos. (Hudson, Arck1pro)

### M-15 — PRIMEIRO FEEDBACK RARAMENTE E COMPLETO
O cliente reclama de um sintoma (ex: "preco errado"), mas a causa raiz e mais profunda (ex: tabela de precos faltando na base). Ao receber feedback, investigar causa raiz, nao apenas tratar sintoma. (Lameds, Plastbox)

### M-16 — URGENCIA CRESCE EXPONENCIALMENTE
Padrao: feedback educado → feedback firme → pedido urgente → "PARAR A IA". Feedbacks devem ser resolvidos no primeiro ciclo, nao no terceiro. A recorrencia da mesma reclamacao 2+ vezes indica falha ESTRUTURAL no prompt, nao pontual. (Plastbox, Titancell)

### M-17 — COMPLEXIDADE DO NEGOCIO ∝ FLUXOS CONDICIONAIS
Negocios com multiplas unidades (Lameds), multiplos produtos (Hudson, Curta), ou processos tecnicos (BR Sollar) precisam de fluxos if/then EXPLICITOS. Quanto mais produtos/variantes, mais erros de confusao de atributos. (Lameds, Plastbox, Titancell)

### M-18 — FOLLOW-UP E A FUNCIONALIDADE MAIS COMPLEXA
Em 70%+ dos clientes, follow-up gerou problemas: horario errado, conteudo errado, persistencia indevida, duplicacao, follow-up para desqualificado. Follow-up deve SEMPRE verificar: horario ok? status ok? contexto ok? Sem esses 3 checks, nao enviar. (Traiano, Curta, Cleef, Kohll)

### M-19 — "O QUE A IA NAO DEVE FAZER" > "O QUE DEVE FAZER"
As restricoes (nao mencionar preco, nao usar "cura", nao reagendar apos confirmacao) sao mais criticas que as instrucoes positivas. O prompt deve ter secao dedicada "PROIBIDO" antes das instrucoes de fluxo. (Curta, Plastbox, Kohll)

---

## SECAO 4: TABELA DE FREQUENCIA CROSS-CLIENT

Quantos dos 22 clientes apresentaram cada padrao. Usado para priorizar deteccao.

| Padrao | Clientes afetados | % | Peso |
|--------|-------------------|---|------|
| D-01 Dado incorreto na base | 20/22 | 91% | SEMPRE verificar |
| D-08 IA continua apos objetivo | 19/22 | 86% | SEMPRE verificar |
| D-03 Tom robotico/longo | 17/22 | 77% | SEMPRE verificar |
| D-11 Comando pausa nao funciona | 16/22 | 73% | SEMPRE verificar |
| D-22 Invasao atendimento humano | 7/22 | 32% | SEMPRE verificar |
| D-18 Follow-up sem contexto | 7/22 | 32% | SEMPRE verificar |
| D-10 Alucinacao/invencao | 14/22 | 64% | SEMPRE verificar |
| D-09 Re-pergunta dados fornecidos | 12/22 | 55% | SEMPRE verificar |
| D-07 Transferencia generica | 9/22 | 41% | Verificar se transfere |
| D-04 Sequencia fora de ordem | 8/22 | 36% | Verificar se ha fluxo |
| D-20 Confusao entre entidades | 6/22 | 27% | Verificar se multiplas entidades |
| D-17 Salto de etapa no funil | 6/22 | 27% | Verificar se ha funil de vendas |
| D-05 Pagamento incompleto | 6/22 | 27% | Verificar se vende |
| D-06 Midia sem mapeamento | 8/22 | 36% | Verificar se envia midia |
| D-23 Regressao de fluxo | 5/22 | 23% | Verificar no re-teste |
| D-25 Metralhadora (msgs sem resposta) | 5/22 | 23% | Verificar se multi-msg |
| D-19 Over-information | 5/22 | 23% | Verificar se catalogo grande |
| D-13 Horario errado | 8/22 | 36% | Verificar se agenda |
| D-02 Servico inexistente | 7/22 | 32% | Verificar se 5+ produtos |
| D-21 Erro de calculo numerico | 4/22 | 18% | Verificar se IA calcula |
| D-24 Vazamento info restrita | 4/22 | 18% | Verificar se tem dados sensiveis |
| D-12 Cliente existente = lead | 4/22 | 18% | Verificar se tem base clientes |
| D-14 Edicao nao persiste | 4/22 | 18% | Verificar no re-teste |
| D-16 Delay inadequado | 6/22 | 27% | Verificar se multi-mensagem |
| D-15 Dados sensiveis formato errado | 3/22 | 14% | Verificar se usa audio |
| D-26 Adaptacao publico-alvo | 3/22 | 14% | Verificar perfil do publico |

---

## SECAO 5: EXEMPLOS REAIS DE EDICOES QUE FUNCIONARAM

Exemplos compactos de edicoes que RESOLVERAM o problema definitivamente.

### E-01: Secao negativa resolveu alucinacao de produto
**Problema:** IA oferecia trofeus (produto inexistente)
**Edicao:** Adicionou "## O QUE NAO FAZEMOS: Nao fabricamos trofeus, somente placas."
**Resultado:** Nunca mais ofereceu trofeus. *(Placas & Brindes)*

### E-02: Tabela de precos resolveu cotacao errada
**Problema:** IA dava estimativa sem valores reais
**Edicao:** Criou tabela | Modelo | Servico | Preco | na base de dados
**Resultado:** Precos corretos imediatamente. *(King Manutencoes)*

### E-03: Pausa automatica resolveu conflito humano-IA
**Problema:** Comando de pausa nao funcionava, IA falava por cima do atendente
**Edicao:** Pausa automatica: msg do atendente = IA para por 45min
**Resultado:** Zero conflitos humano-IA. *(Star)*

### E-04: Frase de identidade resolveu confusao lead-IA
**Problema:** Lead pensou que falava com humano, ficou estressado
**Edicao:** "Sou assistente virtual da [EMPRESA]. Vou acionar nosso atendimento humano."
**Resultado:** Zero confusao. *(Placas & Brindes)*

### E-05: Regra de encerramento evitou desmarcacao
**Problema:** IA continuava apos reuniao agendada → lead desmarcou
**Edicao:** "Apos confirmacao de agendamento, UMA msg de encerramento e PARAR"
**Resultado:** Reducao significativa de desmarcacoes. *(Vancini)*

### E-06: Extracao de contexto da 1a mensagem
**Problema:** Lead disse modelo+defeito, IA perguntou de novo
**Edicao:** "ANTES de perguntar, extrair dados ja fornecidos na conversa"
**Resultado:** IA reconhece dados da msg inicial. *(King)*

### E-07: Roteamento cliente existente vs lead novo
**Problema:** Cliente mandou boleto, IA iniciou fluxo de venda
**Edicao:** Mensagem de redirecionamento para numero de suporte
**Resultado:** Clientes existentes redirecionados corretamente. *(Nuvtech)*

### E-08: Delay de resposta para bloco de mensagens
**Problema:** IA respondia cada msg individual (4 respostas pra 4 msgs)
**Edicao:** Delay de 40s antes de responder
**Resultado:** IA responde ao bloco completo. *(Vancini)*

### E-09: Proibicao de gerar links financeiros
**Problema:** IA gerou link de pagamento FALSO e PIX inventada
**Edicao:** "NUNCA gerar URLs ou chaves PIX. Para pagamento, SEMPRE humano."
**Resultado:** Zero links falsos. *(Imagem Soccer)*

### E-10: Dados sensiveis sempre em texto
**Problema:** Telefone 0800 e site enviados por audio (ininteligivel)
**Edicao:** "Telefones, links, CNPJ, PIX = SEMPRE texto, NUNCA audio"
**Resultado:** Resolvido apos regra explicita. *(Star)*

### E-11: Remocao de pergunta obsoleta
**Problema:** IA perguntava "qual estado?" mas empresa ja atendia todos
**Edicao:** Removeu a pergunta do fluxo inteiramente
**Resultado:** Fluxo mais rapido, sem pergunta desnecessaria. *(Star V2)*

### E-12: Linguagem natural para comando de pausa
**Problema:** Comando com emoji/hashtag nao era natural para o lead ver
**Edicao:** Trocou por frase natural: "Ola, [NOME] aqui" como gatilho
**Resultado:** Handoff invisivel para o lead. *(Star V2)*

### E-13: Script como guia vs texto literal
**Problema:** Script de objecoes forçado verbatim → IA ficou mais robotica
**Edicao:** Reverteu: script virou CONHECIMENTO, nao texto obrigatorio
**Resultado:** Tom natural voltou. *(King)*

### E-14: Regra hard em vez de soft
**Problema:** "Tente nao mencionar precos" → IA mencionava mesmo assim
**Edicao:** REMOVEU todos os precos da base. Regra impossivel de violar.
**Resultado:** Zero vazamento de precos. *(Imagem Soccer)*

### E-15: Fluxo sequencial obrigatorio resolveu salto de etapas
**Problema:** IA ia direto para prova de bolsas sem sondar interesse do lead
**Edicao:** Definiu fluxo: 1.Qualificar → 2.Sondar → 3.Material → 4.Oferta. IA so avanca quando etapa cumprida.
**Resultado:** Leads melhor qualificados antes da oferta. *(Hudson)*

### E-16: Lista "NAO fazemos" resolveu alucinacao de servico medico
**Problema:** IA oferecia exames e especialidades que o laboratorio nao tem (otorrino, espermograma, eletrocardiograma)
**Edicao:** Secao "SERVICOS QUE NAO OFERECEMOS" com lista explicita
**Resultado:** Zero ofertas de servicos inexistentes. *(Lameds)*

### E-17: Pausa indefinida resolveu invasao de atendimento humano
**Problema:** IA continuava respondendo apos transferencia para humano, mesmo com etiqueta
**Edicao:** Pausa INDEFINIDA apos transferencia. Reativacao somente manual.
**Resultado:** Zero conflitos humano-IA. *(Kohll Beauty)*

### E-18: Janela horaria resolveu follow-ups de madrugada
**Problema:** Follow-ups disparados as 23h, 00h, 02h — irritando leads
**Edicao:** Regra: follow-ups SOMENTE entre 8h e 20h
**Resultado:** Zero reclamacoes de horario. *(Traiano Advogados)*

### E-19: Uma pergunta por vez resolveu metralhadora de msgs
**Problema:** IA fazia todas as perguntas de qualificacao de uma vez (idade, CPF, tempo de contribuicao)
**Edicao:** Regra: 1 pergunta por mensagem. Aguardar resposta antes de proxima.
**Resultado:** Leads respondem melhor, conversa mais natural. *(Traiano Advogados)*

### E-20: Tabela pre-calculada resolveu parcelas erradas
**Problema:** IA calculava parcelas na hora → valores errados
**Edicao:** Tabela fixa: | Modelo | A vista | 2x | 3x | 4x | com valores exatos
**Resultado:** Parcelas sempre corretas. *(Titancell)*

### E-21: Bloco unico por entidade resolveu confusao de atributos
**Problema:** Cor do vidro confundida com cor do acabamento; medicos misturados
**Edicao:** Cada entidade em bloco individual com TODOS os atributos claramente separados
**Resultado:** Zero confusao entre entidades. *(Plastbox, Lameds)*

### E-22: Buffer de mensagens resolveu respostas precipitadas
**Problema:** IA respondia cada mensagem individual do lead em sequencia rapida
**Edicao:** Buffer de 30-60s para aguardar lead terminar de digitar
**Resultado:** IA processa contexto completo antes de responder. *(Curta)*

---

## SECAO 6: ANTI-PADROES (O QUE NAO FAZER AO EDITAR)

| Anti-padrao | O que aconteceu | Fonte |
|-------------|----------------|-------|
| Script rigido verbatim | Forcar IA a seguir script palavra por palavra → ficou mais robotica | King |
| Editar A e quebrar B | Corrigir follow-up quebrando regra de horario comercial | Elishop |
| Nao limpar cache apos edicao | Prompt novo mas conversa de teste com contexto antigo | Imagem |
| Regra soft em vez de hard | "Tente nao mencionar" em vez de REMOVER dado da base | Imagem |
| Corrigir e nao testar | "Ajustado" sem verificar → mesmo problema 2 dias depois | Star, Placas, Elishop |
| Comando complexo de pausa | Frase longa case-sensitive → ninguem conseguia usar | Imagem, Star |
| Agrupar perguntas demais | Pedir 5+ dados numa so msg → lead nao responde tudo | Star (consultoria) |
| Valor calculado pela IA | Frete calculado pela IA → sempre errado | Placas |
| Follow-up para quem nao respondeu | Enviar follow-up pra quem nunca interagiu = spam | Nuvtech |
| Numero parametrizado errado | Valor regional (70% vs 80%) nao ajustado por franquia | Star V2 |
| Feedback ignorado 3+ vezes | Mesma correcao pedida 3x sem persistir → cliente desiste | Hudson, Lameds |
| Reativacao por timeout | IA reativa automaticamente apos X min → conflito com humano | Kohll, Traiano |
| Follow-up para desqualificado | Lead disse "nao quero" e recebeu follow-up → reclamacao | Traiano |
| Descricao de tom sem exemplos | "Seja humanizado" sem exemplos concretos → IA ignora | Hudson, Arck1pro |
| Dados volateis hardcoded | Precos/datas no prompt fixo → desatualizam em dias | Lameds, Titancell |
| PDFs duplicados na base | Novo PDF substitui antigo mas ambos ficam → conflito | Plastbox |
| Calculo delegado a IA | Somas/parcelas calculadas pela IA → sempre errado | Lameds, Titancell |
| Pergunta invasiva no inicio | "Como isso afeta seus planos?" na 2a msg → lead estranha | Arck1pro |
