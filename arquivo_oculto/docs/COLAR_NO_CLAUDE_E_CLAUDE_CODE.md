# COMANDO MESTRE — ESTÚDIO AUDIOVISUAL GM / ARQUIVO OCULTO

**MISSÃO:** atualize a aplicação de produção audiovisual que eu e você já construímos no Claude/Claude Code. Ela já atende, ou foi concebida para atender, `@direitaxx` e `@dr.geovanimiranda`. Preserve-a, audite sua arquitetura e acrescente uma terceira identidade editorial: **ARQUIVO OCULTO**. Não comece outro app sem necessidade, não destrua dados, não substitua funcionalidades que já trabalham e não encerre apenas com planos. Execute mudanças reais, testes e entregas verificáveis.

Anexo o pacote `ARQUIVO_OCULTO_CLAUDE_VIDEO_FACTORY_V1.zip`, com Skills dentro de `.claude/skills/`, referências do personagem, bíblia visual, manifests dos dois primeiros episódios, critérios de qualidade e instruções. Integre os arquivos de Skills ao projeto **sem apagar Skills existentes**. Leia também `CLAUDE_ADDENDUM.md` e incorpore suas regras ao `CLAUDE.md` do repositório sem sobrescrever instruções legítimas anteriores. Se eu colar apenas este comando no Claude comum, produza uma especificação/patch aplicável, e não finja ter alterado um repositório que você não acessou.

## 1. PROPÓSITO

Quero transformar a aplicação existente num **estúdio automatizado de vídeos gerados por IA** para redes sociais. Entrego um tema/dossiê; a aplicação pesquisa fontes, estrutura argumentos, gera roteiro e storyboard, cria cenários, personagens e movimentos, produz **locução sintética em português brasileiro**, trilha e efeitos com licenças adequadas, monta tudo, cria legendas, capa, arquivo final e relatório. Entrega um **MP4 vertical direto para download**. Meu trabalho manual deve ser próximo de zero, exceto credenciais, aprovações necessárias, gastos pagos e publicação final.

**Prioridade zero: dois pilotos de ponta a ponta, não apenas roteiro!**
- **EP01 — O jogo que parecia prever o mundo:** refazer a versão anterior completamente no novo estúdio. Usar `examples/EP01_o_jogo_que_parecia_prever_o_mundo.json`; comparar qualidade com a versão feita no HeyGen sem copiar marcas d'água. Deve ser a primeira entrega.
- **EP02 — A operação federal contra a editora:** produzir a sequência utilizando `examples/EP02_a_operacao_contra_a_editora.json` e fontes sobre 1º de março de 1990 e o lançamento do INWO em dezembro de 1994. Deve ser a segunda entrega.

Não marque EP01/EP02 como concluídos sem MP4 renderizado e inspecionado com `ffprobe` ou equivalente. Se faltarem créditos, credenciais ou ferramenta de geração visual, não invente êxito: implemente pipeline funcional e renderização alternativa com imagens e movimentos de câmera (parallax/Ken Burns), sinalize a diferença entre animação de stills e cenas generativas, mostre o bloqueio e devolva o caminho do arquivo que de fato existir.

## 2. IDENTIDADE VISUAL: O ARQUIVISTA

Personagem ficcional fixo que eu usava num canal antigo do Kwai: homem/figura de capuz e roupa preta, máscara facial **branca/porcelana**, olhos escuros, expressão enigmática, luvas escuras, cenários de acervo sombrio, atrás dele gravuras de acontecimentos, arquivos e calamidades. A referência de rosto/atmosfera do personagem original está em `assets/arquivista_legado_referencia_privada.png`. Também incluí uma direção sofisticada em `assets/arquivista_conceito_premium.png`; essa é uma **variação artística**, não uma autorização para trocar permanentemente a máscara clássica. Padronize um `character_id: arquivista-classico-v1` e crie uma ficha de continuidade.

Ele é o anfitrião do universo, como narrador observador, não uma pessoa real. Quero aparições curtas porém memoráveis na abertura, 1–2 pontes e fechamento. Se for possível animá-lo falando, use movimentos discretos de cabeça, corpo, gestos e respiração associados ao áudio; uma máscara rígida pode transmitir fala pela performance sem inventar boca humana visível. Evite rostos sem consistência, mudança de máscara, dedos defeituosos e sincronismo obviamente falso. A locução permanece constante entre episódios.

**Paleta:** preto carvão, marfim, latão/dourado envelhecido, vermelho profundo usado apenas para tensão pontual. **Cenários:** arquivo oculto com gavetas, mapas, livros, documentos iluminados, portas metálicas e monitores analógicos; recortes históricos com movimento; corredores secretos, cenários geopolíticos e arquivos de jornal, sem tratar cenas geradas como imagens documentais.

## 3. TIPOS DE VÍDEOS / FORMATO DA EXPERIÊNCIA

Produzir seis formatos: (A) Microdossiê de 25–45 segundos com 7–10 planos; (B) Carta & previsão de 30–50s com comparação pré/pós-evento; (C) Conspiração documentada de 35–60s com evidência real e reviravolta; (D) Microdrama ficcional de 15–45s, claramente identificado como dramatização; (E) Símbolos & capas de 25–45s mostrando leituras concorrentes; (F) Cenário futuro/preparação de 35–60s com sinais verificáveis e medidas práticas. Episódios longos de 60–180s são expansão futura.

Padrão mínimo social: **9:16, 1080×1920, H.264/AAC, MP4**, 24/30 fps, som inteligível, legendas embutidas e arquivo `.srt`, capa `.png`; versões 1:1 e 16:9 opcionais. Abertura forte nos 0–2s, microrevelações a cada 3–5s, virada informativa no meio, encerramento memorável com convite à série, sem enganar, fabricar pânico nem prometer evento futuro certo. O objetivo é retenção *por narrativa*, não manipulação psicológica.

**Som:** voz IA masculina em pt-BR, grave, densa, próxima, levemente sintética, ritmo controlado, silêncio estratégico, sem imitar voz de pessoa real. Trilha original ou licenciada, dark ambient/cinematográfica, efeitos de documentos, rádio, máquinas, relógios e porta, volume sempre abaixo da locução. Mixar com ducking automático e limitar picos. Legendas de alto contraste na área segura do 9:16, nunca escondidas atrás dos controles das plataformas.

**Imagens:** MAIS imagens, não menos. Preferir fotografias originais verificadas e permitidas, documentos verdadeiros, capas e cartas autenticadas quando seu uso estiver autorizado; complementos criados por IA para atmosfera/encenações. Guardar metadados de fonte, data e direitos. Imagens geradas **não** podem se fazer passar por fotografias históricas, cartas verdadeiras, depoimentos ou fatos reais. Não raspar ou distribuir indiscriminadamente conteúdo protegido. Capturas do canal antigo servem só de referência de direção; não publicar pessoas de lá sem autorização.

## 4. CONTROLE EDITORIAL

O Arquivo Oculto investiga teorias, não prova por estética. Separar em cada roteiro: `fato_documentado`, `alegacao`, `interpretacao`, `coincidencia`, `incerteza`, `fonte`. Se houver conexão entre teorias, registrar se é documental, cronológica, temática, iconográfica ou apenas alegada. Não apresentar linhas temáticas como causalidade. Nenhuma acusação sobre pessoa identificável sem fonte sólida. Tratar religiões e práticas rituais com respeito. Evitar publicidade que prometa que guerras, colapsos, profecias ou outros eventos futuros vão acontecer com certeza.

No EP01, afirmar: jogo *Illuminati* original de 1982; **INWO de 1994**, publicado pela Steve Jackson Games; jogo satírico. O tema da suposta previsão é interpretação posterior e deve ser submetido a comparação antes/depois.

No EP02, afirmar: a busca na Steve Jackson Games ocorreu **em 1º de março de 1990 pelo Serviço Secreto dos EUA**, relacionada à investigação sobre computadores e comunicações, não pelo FBI por causa de cartas ainda não publicadas; o INWO saiu em **dezembro de 1994**. Essa diferença de datas é a reviravolta.

Fontes primárias iniciais: https://groups.google.com/g/rec.games.trading-cards.misc/c/pZqyQ8eJP48 (FAQ do próprio Steve Jackson, 1994); https://law.justia.com/cases/federal/district-courts/FSupp/816/432/1976489/ (decisão judicial). Verifique datas e contexto ao montar.

## 5. ARQUITETURA: ATUALIZAR, NÃO RECOMEÇAR

1. Auditar código e recursos atuais, mapear editor, banco de assets, pipeline, serviços e provedores. Preservar `direitaxx` e `dr-geovanimiranda` com suas respectivas identidades e aprovações; adicionar o tenant/marca `arquivo-oculto`.
2. Instalar e usar as Skills do pacote. Criar módulos separados: `research`, `script`, `storyboard`, `asset-manager`, `character-consistency`, `visual-providers`, `tts`, `sound-design`, `timeline`, `renderer`, `qa`, `export`.
3. Implementar interfaces/adapters para provedores disponíveis de vídeo, imagem e TTS, sem amarrar a aplicação a um fornecedor. Permitir Google Veo/Flow **se houver API ou interação autorizada**, outros provedores/Claude que estejam realmente disponíveis; não inventar endpoints. O Claude Code pode orquestrar o processo, mas por si só não garante acesso a um modelo gerador de vídeo.
4. Credenciais somente em `.env`/gerenciador seguro; nunca armazenar tokens em arquivos do repositório. Respeitar cotas e cobrar autorização antes de geração paga. Reaproveitar assets de personagens, trilhas e backgrounds para reduzir custo.
5. Montar de forma determinística com Remotion ou FFmpeg (ou o editor existente), usando plano de cenas `JSON`, locução com duração real, áudio normalizado, legendas temporizadas e trilha mixada. Implementar processamento em fila, persistência de estados, retomada idempotente e relatório de erros; nunca chamar 'renderizado' um vídeo com status apenas `queued`.
6. Expor botão `Gerar episódio`, histórico de trabalhos, etapa atual real, preview e botão de **download direto MP4**, sem depender da interface manual de cada fornecedor. Não publicar automaticamente.
7. Manter `production_manifest.json`: prompt, versão da voz, referências, modelos, custo aproximado quando conhecido, licenças, fontes, duração, checks técnicos e aprovação editorial. Não transformar créditos/limites em ações manuais repetitivas quando puder usar processamento automático.
8. Criar testes de render, integração, import/export, caminhos de arquivos, TTS, legendas, licenças, falhas de provider, repetição/retentativa e links diretos para MP4.

## 6. ORDEM DE EXECUÇÃO (SEM PERDER O ESCOPO)

**FASE 0:** inspecione o repositório real e identifique o que já funciona. Comite/registre o estado atual, sem sobrescrever trabalho em curso. Leia `README.md`, `CLAUDE.md` e as Skills existentes. Integre estas novas Skills cuidadosamente.

**FASE 1:** implemente o perfil `Arquivo Oculto`, o personagem, as bibliotecas e o pipeline mínimo para produção `roteiro -> cenas -> TTS -> timeline -> legendas -> MP4`.

**FASE 2:** produza **EP01 REFEITO DO ZERO** e verifique vídeo, áudio, grafia, fatos e visual. Exporte MP4 + SRT + capa. Guarde evidências e compare com HeyGen, mesmo que a comparação seja apenas qualitativa enquanto o vídeo antigo não estiver presente no repositório.

**FASE 3:** produza **EP02** do mesmo modo e teste consistência do Arquivista e da voz entre os dois vídeos.

**FASE 4:** crie templates para os outros oito episódios da temporada, sem gastar créditos antes da aprovação do pipeline. Depois automatize o lote, se custo e capacidade permitirem.

**FASE 5:** relatórios de pronto/pendente e instruções de operação: um clique para gerar e um para baixar. Se funcionar localmente, entregar arquivos em pasta de saída com caminhos verificáveis; se publicar em storage, usar link estável. Sem automação de postagem até minha autorização específica.

## 7. COMO AVALIO A ENTREGA

Preciso ver: (i) app antigo preservado; (ii) Skills instaladas; (iii) EP01 MP4 final de verdade; (iv) EP02 MP4 final; (v) cenas visualmente ricas, caráter consistente, voz IA constante, legendas e áudio bem mixados; (vi) botão download testado; (vii) relatório curto com nomes de arquivos, duração e resultados de QA; (viii) dependências, créditos, licenças e bloqueios explicitados. Não aceite dizer ‘100%’ sem arquivo final e reprodução testada.

Se você estiver operando apenas no Claude chat sem acesso ao código, diga isso e forneça o patch/especificação acionável; não alegue ter alterado a aplicação. No Claude Code com acesso, faça a mudança real e comece pela dupla EP01 e EP02.

**COMECE EXECUTANDO, NÃO APENAS EXPLICANDO.**
