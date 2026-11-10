# COMANDO MESTRE — ATUALIZAÇÃO DO PERFIL ARQUIVO OCULTO NO ESTÚDIO GM

Você é o arquiteto sênior de software, diretor de cinema, editor documental, supervisor de VFX/IA, diretor de narração TTS e responsável técnico pela aplicação já existente **Estúdio Audiovisual GM** (que atualmente serve @direitaxx e @dr.geovanimiranda). Você recebeu um pacote `ARQUIVO_OCULTO_CLAUDE_STUDIO_V2.zip`.

**MISSÃO EXECUTIVA:** RECONFIGURE o perfil `arquivo-oculto` e implemente capacidade real de gerar vídeos cinematográficos com IA, preservando todas as funções e perfis existentes. NÃO crie um novo estúdio, NÃO descarte código funcional e NÃO entregue apenas roteiro ou projeto visual. Primeiro faça auditoria da aplicação; depois modifique-a e teste renderizações concretas. Se um provedor de geração de cenas não estiver disponível, informe o bloqueio real, gere a melhor prévia possível com recursos autorizados e não simule conclusão.

## 1. Referências reais são obrigatórias
Leia/assista, extraia frames e analise os ÁUDIOS dos seguintes arquivos deste pacote:
- `referencias/video_antigo_kwai_1202.mp4` — **padrão desejado de MOVIMENTAÇÃO, atuação, entrada/saída, voz sintética, atmosfera e participação do personagem**; formato legado 720×720, ~119s.
- `referencias/video_estudio_ep02_1204.mp4` — qualidade gráfica recente, mas edição genérica, Arquivista parado e pouco material documental; 1080×1920, ~46s. **É contrarreferência de DIREÇÃO e ritmo, não o padrão definitivo de montagem.**
- `referencias/arquivista_premium_referencia.png` — **REFERÊNCIA CANÔNICA DE APARÊNCIA**; rosto/máscara marfim envelhecida com detalhes dourados, capa preta, luvas e arquivo escuro. Preserve os traços entre cenas.
- `referencias/capa_ep02_atual.jpg` — referência de tipografia/capa, não referência de cena em movimento.
- `referencias/grade_canal_antigo.png` — referência contextual da identidade anterior.

**REGRA CENTRAL: MANTER O VISUAL NOVO + MOVIMENTAÇÃO E VOZ DA VERSÃO ANTIGA.** Não trocar a máscara por uma nova em cada cena. Não modificar boca da máscara para simular fala humana. A fala é voz em off do próprio personagem; a performance deve refletir a locução por gestos, olhar, caminhada e manipulação de provas.

## 2. Resultado editorial e artístico
Não queremos um PowerPoint com ruído e voz: queremos um **mini documentário cinematográfico dirigido pelo Arquivista**, com sensação de suspense e descoberta. Sempre construir uma HISTÓRIA, não uma lista de datas. Fatos corretos integrados ao drama em vez de blocos didáticos quebrando o suspense.

Narrativa-base: abrir com conflito ou imagem que interrompe o scroll, criar pergunta, revelar evidências visualmente, aprofundar uma hipótese, descobrir uma informação surpreendente, fechar com nova pergunta que legitimamente continua o dossiê. **Não prometa comprovação quando ela não existir.** Explorar a teoria em profundidade, reproduzir fielmente as versões e tensioná-las com fontes verificadas; usar questões e hipóteses de modo instigante. Jamais inventar documentos, cartas ou confissões como se fossem reais.

Tom: sombrio, conceitual, artístico, magnético, levemente inquietante, com contenção elegante; nada caricato. A intensidade nasce da montagem, roteiro, som e imagem, não de gritos, desinformação ou gatilhos de pânico. Técnicas éticas de retenção: reconhecimento visual, pattern interrupts, pistas, revelações, suspense e payoff; sem manipular espectadores com fatos falsos.

## 3. Movimento obrigatório do Arquivista
O personagem é um ATOR virtual. Variações naturais: caminhar lentamente pelo arquivo, surgir à contraluz, virar a cabeça em reação a um documento, virar páginas, apontar uma data em papel, abrir gavetas, levantar uma carta, passar a mão em mapas, colocar duas imagens lado a lado, fechar uma pasta, ficar imóvel só num silêncio dramático breve, voltar a olhar para câmera. Movimentos devem ser coerentes com o gesto e o ambiente, e consistentes com a máscara rígida. Animação corporal e câmera, não apenas zoom numa imagem.

Regras: usar ao menos 3 cenas diferentes do personagem por 60s; nenhum still do personagem isolado mais que 4s; identificar cenas em JSON com `action`, `gesture`, `camera_motion`, `emotional_beat`, `reference_image`, `duration`, `sync_to_voice`. O Arquivista entra e sai do quadro, não ocupa 100% do vídeo. Priorização de imagens e documentos: pelo menos uma peça histórica concreta e legítima por bloco de argumento quando disponível, com crédito e checagem de direitos. Imagens inventadas por IA rotuladas como reconstituição se confundíveis com documento histórico.

## 4. Locução TTS — ouvir antes de ajustar
O arquivo `video_antigo_kwai_1202.mp4` contém a **referência primária de SOM**. Primeiro extraia áudio e faça análise perceptiva (timbre, textura, cadência, pausas, articulação, intensidade, velocidade); gere amostra de 10s com três variações de voz sintética em pt-BR e selecione/configure a mais próxima se permitido pelo provedor e direitos. Não prometa clone exato sem mecanismo e autorização adequados.

Perfil desejado: voz masculina sintética grave-média, íntima, com ressonância e leve aspereza/metalicidade, inteligível, baixa teatralidade, frases que começam contidas e crescem na revelação, pausas de 250–650ms, uma sensação de confidência/enigma; nunca tom comercial eufórico, locução robótica, exagero de sussurros ou efeito monstruoso. Fixar `voice_id`, `voice_model`, `locale`, `rate`, `pitch`, `style`, `version` no perfil para repetibilidade. Diálogo sincronizado com cortes e gestos; música e SFX cedem espaço à locução por ducking.

## 5. Formatos selecionáveis com um clique
Adicionar ao perfil `Arquivo Oculto` botões ou opções: `Reel 30s` (9:16, 25–35s); `Investigação 90s` (9:16, 60–105s); `Reel Profundo` (9:16, 105–180s); `YouTube 5min` (16:9, 3–8min, padrão ~5min); `YouTube 10min` (16:9, 8–15min); `Microdrama` (9:16, 20–180s). A seleção precisa alterar roteiro, número de cenas, capítulos, tom e duração real, mantendo o DNA do Arquivista. YouTube de 5min não pode ser um reel esticado ou slides parados. Long-form: 4–6 atos com arcos, b-roll investigativo, variação de cenários, resumos progressivos, documentação e clímax de descoberta.

Outros perfis existentes não podem herdar o Arquivista, sua voz, imagens ou identidade. Cada perfil tem assets, políticas e presets isolados.

## 6. Gerador de cenas e montagem — implementação real
No projeto existente, implementar/ajustar adapters desacoplados para `image-generation`, `image-to-video`, `video-generation`, `TTS`, `music/SFX`, `asset retrieval`, `subtitles`, `timeline renderer` (preferir capacidades já instaladas). Verificar providers disponíveis e credenciais com segurança; NÃO gastar créditos pagos nem assinar novos planos sem autorização. IA gera os clipes; FFmpeg/renderer faz timeline, mix, subtitles e MP4. Não presumir que um único modelo faça tudo.

Toda cena deve ter `shot_type`, `visual_source_type`, `duration`, `asset_path`, `prompt`, `negative_prompt`, `movement`, `sound_design`, `voice_span`, `source_id`, `rights_status`. Cache/reuso por hash; retry com limites; prevenção de duplicidades; recuperação de trabalhos parciais; estado real por etapa (`planned`, `sources_verified`, `generating_visuals`, `generating_voice`, `assembling`, `qa`, `completed`, `blocked`). `completed` só após arquivo MP4 testado, não após salvar roteiro.

Produção final: MP4 H.264/AAC, cover, SRT, manifesto/timeline JSON, fontes e QA; download direto funcional. Imagem/voz gerada por IA corretamente identificada quando necessário. Nunca publicar automaticamente em redes sociais. Modo público deve bloquear assets sem direitos adequados.

## 7. Primeiro ciclo obrigatório: recriar os dois episódios
1. **EP01 — O jogo que parecia prever o mundo**: REFAZER DO ZERO, agora versão mais profunda de 75–100s (preferir 85s). Incluir imagens autênticas de algumas cartas INWO quando legalmente utilizáveis, com versão/ano e fonte; apresentar a tese de supostas previsões, o contexto de 1994 e um mistério realmente investigável; Arquivista animado e locução conforme vídeo antigo.
2. **EP02 — A operação contra a editora**: REMONTAR de forma cinematográfica em 75–100s, desta vez com cartas efetivamente mostradas e identificadas, e com documentos da operação de 1990; explicar sem secar a história: a relação entre o imaginário do Illuminati, o ataque federal real à editora e a diferença cronológica para o INWO de 1994 como revelação (não como palestra). Mostrar material autêntico ou indicar visualmente 'RECONSTITUIÇÃO COM IA'.
3. Após testes e avaliação, preparar os manifestos da temporada 01 (EP03–EP10) e a série de microdramas; não gerar uma dezena de vídeos pagos automaticamente.

**Critérios para chamar os pilotos de aprováveis:** Arquivista reconhecível e fisicamente animado; voz realmente semelhante em intenção à referência antiga; ao menos 4 categorias de imagens por episódio (personagem, carta/fotografia real licitamente utilizável, documento histórico, reconstituição), nada de slides repetitivos; progresso dramático perceptível; textos claros; datas/fontes verificáveis; MP4 real, compartilhável e com teste de áudio/vídeo. Se falhar, corrija a cena e refaça somente o trecho, não todo o episódio.

## 8. Antes de alterar e depois de entregar
- Audite `git status`, arquitetura, presets atuais, providers e testes; crie branch/backup, sem sobrescrever mudanças em andamento.
- Mescle as Skills do pacote em `.claude/skills/`, o `CLAUDE_ADDENDUM_V2.md` em `CLAUDE.md`, e o JSON `config/profiles/arquivo_oculto_v2.json` com o modelo de perfis realmente usado pelo app. Nunca trocar o formato de configs sem migração.
- Rode schema validation, smoke test dos três outros perfis/canais, UI mobile, JSON, geração de cena, TTS, render, legenda e `ffprobe`.
- Relate o que efetivamente foi modificado, quais etapas foram executadas, provedores/custos, vídeos gerados e caminhos existentes; se travar, identifique exatamente o erro e próximos passos. Não me peça trabalho manual quando uma integração autorizada puder resolver.

**INICIE A IMPLEMENTAÇÃO DO PERFIL V2 E A GERAÇÃO DO EP01. NÃO FIQUE APENAS EXPLICANDO O QUE FARIA.**
