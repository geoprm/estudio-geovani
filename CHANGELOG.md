# CHANGELOG — Estúdio Audiovisual GM

Formato: data · o que mudou · arquivos · regressões e pendências. Sem commits locais: o estado de referência é `origin/main` = `53f5865`.

## 2026-11-12 a 17 — Dossiês v2 com atuação, finais abertos, TikTok completo, Shorts e primeiro longo no YouTube (Claude Code)

- **Arquivista em atuação.** Biblioteca de seis planos de 4 s em `v2/ator_biblioteca.py` (aparição, olhar para a câmera,
  silêncio, debruçar, virar a cabeça, encerramento). O `reel_leve` monta os blocos de retrato com esses planos, em modo
  `performance_2_5d`.
- **Finais abertos (D-115).** `montar_roteiros.py` troca o título do placar por "O ARQUIVO CONTINUA ABERTO" e cobre as
  telas pretas com a última imagem. Os T12–T25 trazem fala final de pulga atrás da orelha (`specs/mapas.json`, bloco "-1").
- **Não refazer o pronto (D-116).** T01–T07 ficaram como estavam. O re-render de T08–T11 foi cancelado.
- **Render.** T01–T25 v2 prontos em `saida_v2/top25/` (96–106 s cada). Novo motor 16:9 em `v2/reel_longo.py`
  (1920×1080, crf 19): OAR-L01 com 390 s em `saida_v2/longos/OAR-L01/`.
- **TikTok.** Os 25 Dossiês estão agendados no Metricool com a mídia v2, de 14/11 a 26/11, às 10:30 e às 18:30, com
  rótulo de IA. Ids em `producao/top50/PUBLICACAO_TOP25.json`. Gerador de agendamento: `producao/top50/infos_metricool.py`.
- **YouTube (Studio, pelo Chrome).**
  - Automação na própria página: injeta o arquivo hospedado, preenche os campos, marca "não é para crianças" e "IA: sim",
    e escolhe o dia no calendário.
  - Ela só clica em "Programar" depois de conferir a data e a hora.
  - O Short do T01 foi ao ar na hora em 12/11, por uma versão anterior do script, e ficou público.
  - O longo OAR-L01 está programado para 18/11 às 20:00.
  - Shorts programados e conferidos: T09, T03, T10, T11, T04 e T12. O T10 tinha ido para as 00:00 e foi corrigido para as 18:30.
  - A hora agora é escolhida clicando na lista de horários: o texto digitado podia não gravar.
  - Parado no limite diário de envios em 17/11. Faltam 16 Shorts.
  - Ficou um rascunho quebrado do T04 (envio interrompido). Apagar só com o OK do Geovani.
- **Metricool.** Em 17/11 a conta bateu o limite e recusou T07 e T08. Os demais seguem PENDING, em risco.
- **Central.** Orientação do Geovani deixada na caixa de entrada
  (`20261112-arquivo-decisao-do-geovani-nao-refazer-o-pronto`), validada.

## 2026-11-11 — Top 50 do nicho, 25 versões do Arquivista e Shorts no YouTube (Claude Code)

- **Levantamento.** yt-dlp em 20 consultas do nicho (800 resultados, só metadados), curadoria de 50 vídeos por views.
  Fora da lista: música, conteúdo infantil, acusação a pessoa viva sem fonte e crime com vítima privada.
  Resultado em `arquivo_oculto/producao/top50/TOP50_NICHO.json` e `PLANO_TOP25.md` (25 versões + 25 planejadas).
- **Formato "Dossiê".** 25 roteiros em `producao/top50/specs/T01–T25.json`:
  - abertura "Olá, criancinhas... Hoje";
  - carimbo em cada alegação e placar final "O ARQUIVO JULGA";
  - imagens reais do Wikimedia Commons, com crédito na tela (autor · licença), escolhidas na folha de contato.
- **Ferramentas novas:**
  - `producao/top50/montar_roteiros.py`: spec + `specs/mapas.json` viram o roteiro do `reel_leve`.
  - `producao/top50/fila_render.sh`: renderiza uma versão por vez, por causa da memória.
  - Busca no Commons: miniaturas em 1280 px; o tamanho 1600 px é estrangulado pelo servidor.
- **T08** usa os vídeos Gimbal e GoFast da Marinha dos EUA (domínio público), só a imagem, no televisor.
- **Publicado no TikTok** (Metricool, publicação automática, rótulo de IA): T01 em 14/11 10:30 e T02 em 14/11 18:30.
  Grade das 25: duas por dia, 10:30 e 18:30, até 26/11. Registro em `producao/top50/PUBLICACAO_TOP25.json`.
- **YouTube Shorts.** 10 dos 14 estão agendados pelo Studio, com IA declarada e não indicados para crianças.
  - O canal atingiu o limite diário de envios: falta a verificação por telefone, que só o Geovani faz.
  - E05, C05, E06 e C06 esperam 24 h ou a verificação. Registro em `producao/PUBLICACAO_YOUTUBE_SHORTS.json`.
  - Um primeiro envio do E05 travou o Chrome e não virou rascunho.
- **Observado.** O EP01 foi ao ar às 12:30 (77 views na primeira hora e meia), mas o Metricool seguia mostrando "Pending".
- **Pendente.**
  - Renderizar e agendar T03–T25.
  - Vídeos longos no YouTube exigem o canal verificado (mais de 15 min, miniatura própria) e envio acima de 10 MB,
    que a extensão do Chrome não aceita.

## 2026-11-11 — Motor leve de reels e as duas séries novas do Claude (D-111)

- **Motor.** `arquivo_oculto/v2/reel_leve.py` monta reels a partir de um roteiro JSON, um bloco por vez e só com ffmpeg:
  - visuais: fotos com movimento, televisor de tubo com trechos creditados de *A Chegada*, par de imagens, cartelas,
    placar e o retrato do Arquivista;
  - carimbos DOCUMENTADO / SEM PROVA / INTERPRETAÇÃO / FALSO;
  - vozes Kokoro (Arquivista do lock e "voz-da-fita", com pf_dora passada por filtro de TV velha);
  - som: cama grave, chiado, batidas e silêncio;
  - legendas no padrão V2 e volume em duas passadas para -15 LUFS;
  - encode final com teto de 3,8 Mb/s.
- **O Arquivo Responde · Fita 01 — O Homem Mais Maligno do Mundo.** 1:58, conferido contra a transcrição da Parte 1.
  - Imagens originais em domínio público, mais a capa de *Sgt. Pepper's* e a captura do Cannonfire.
  - Roteiro em `producao/o_arquivo_responde/OAR-E01.roteiro.json`; saída em `saida_v2/OAR-E01_reel/`.
- **Arquivo Morto · Caso 01 — Carta Sem Remetente.** Terror rural, ficção declarada, 57 s.
  - Adereços desenhados por `producao/arquivo_morto/AM-E01/aderecos.py`, com a fonte Homemade Apple (Apache 2.0).
- **Agenda TikTok.** Caso 01 em 11/11 às 23:15; Fita 01 em 12/11 às 14:30. Registro em
  `producao/PUBLICACAO_TIKTOK_CLAUDE.json`.
- **Pendências.**
  - O piloto passou dos 90 s, porque a voz do lock é lenta.
  - O YouTube ainda não está ligado: falta o canal e a conexão no Metricool.
  - O Chrome travou com a memória cheia durante a renderização.

## 2026-11-11 — TikTok @oarquivista.oculto: temporada V2 agendada (Claude Code)

- **Conta.** O TikTok antigo "Geo" (@geo58350, vazio, login por e-mail) virou **O Arquivista Oculto
  (@oarquivista.oculto)**. Foto do Arquivista, bio, conexão com a Higgsfield. A conta de 166 seguidores da marca
  Dr. Geovani ficou intocada.
- **Abertura em todos.** Regra do Geovani: a primeira fala do Arquivista começa com "Olá, criancinhas..." e o
  complemento, iniciado por "Hoje", muda a cada vídeo. Os seis episódios V2 receberam a abertura sem re-renderizar.
  - A ferramenta nova `arquivo_oculto/v2/assinatura_publica.py` gera ~6 s com o retrato, o título dourado, a legenda e a
    voz do lock, e emenda no corte público aprovado.
  - A emenda decodifica sem erro, o áudio fica sincronizado e o volume bate: -15,3 LUFS na abertura, -15,4 no corpo.
  - As saídas ficam em `saida_v2/AO-S01-E0N_public_release_assinatura_v2/`.
- **Cortes.** Seis cortes de 37 a 48 s, um por episódio, recortados em frases completas e com a mesma abertura. As saídas
  ficam em `saida_v2/AO-S01-E0N_corte_assinatura/`.
- **Agenda.** Doze posts no Metricool, com publicação automática e rótulo de IA, entre 11 e 14/11, às 9:00, 12:30,
  16:30 e 20:00. O registro está em `producao/v2/PUBLICACAO_TIKTOK_S01.json`. O EP03 e o corte dele foram liberados
  pelo Geovani depois de assistir (11/11).
- **Pendências e regressões.**
  - A fábrica V2 completa falha por falta de RAM (OpenBLAS/numpy) com Codex, Chrome e Edge abertos.
  - O manifesto variante `producao/v2/AO-S01-E01.v2.assinatura.json` ficou sem render.
  - O lote de *O Índice Cego* do Codex segue só preparado, e os horários livres estão no handoff
    `producao/HANDOFF_CLAUDE_TIKTOK_GRADE.md`.

## 2026-11-10 — Dois novos episódios de O Índice Cego

- *A Voz Atrás do Ombro* e *O Número na Margem* estão produzidos em 9:16, com abertura falada, legendas e artes de cena originais. Ambos passaram pelo QA com avisos de duração e composição visual.
- A máscara reage discretamente à voz em planos marcados no manifesto. Identidade e voz do Arquivista continuam as do lock aprovado.
- A sala de projeção local reúne os três cortes, com cartazes extraídos dos MP4 e acesso aos dois roteiros de gravação para YouTube.
- As seis entregas V2 registradas pelo Claude Code continuam como uma temporada separada no app. Os novos cortes V3 ficam no estúdio local.

## 2026-11-10 — Temporada V2 completa no app (Claude Code)

- **EP03 no app.** Subiram as duas versões, a pública e a prévia privada, com a capa. O pedido é `v2-ao-s01-e03`.
- **EP01 e EP02 reenviados.** As versões públicas foram reenviadas já com o selo IMAGEM RETIDA e o crédito "retida nesta versão" nos planos com arte retida.
  - Os pedidos `v2-ao-s01-e01` e `v2-ao-s01-e02` foram atualizados para a versão 2. Eles estavam intocados no app (versão 1).
  - As duas públicas antigas, que subi em 05/11, foram apagadas do armazenamento do app.
  - As prévias não mudaram: o hash é igual ao das que já estavam lá.
- Com isso, EP01–EP06 V2 estão todos em Prontos. Ids e hashes em `arquivo_oculto/producao/v2/entregas_app.json`.
- O EP03 público só pode ir ao ar depois de revisão: sem licença, as cartas viram IMAGEM RETIDA e sobram 14% de imagem de arquivo.
- **GitHub** (pedido do Geovani): versão atual na branch `arquivo-oculto-v2` (commit `95104cb`, 117 arquivos), com o link do app no `README.md`.
  - Antes do commit: varredura de segredos e caminhos privados, nada encontrado.
  - Testes: V1 7/7, V2 17/17, editorial V3 5/5.
  - A `main` só muda com o merge.

## 2026-11-10 — Corte narrativo de O Quadro 33 e assinatura do Arquivista

- *O Quadro 33* agora acompanha a ação do envelope até a cabine. Inclui o bilhete original, a descoberta da poltrona e a pista de Aiwass. A abertura usa a voz aprovada e a frase fixa “Olá, criancinhas...”, seguida do gancho do episódio.
- O perfil e os templates passam a trazer a assinatura. A prévia de 78,62 s foi decodificada por inteiro, com 29 legendas verificadas. [Evidência do corte](../evidence/ao-indice-cego-ep01-assinatura-verificacao.json)
- O próximo episódio tem roteiro completo de pré-produção sobre o relato de Crowley, o vínculo textual entre as obras e a representação de reis. [A Voz Atrás do Ombro](arquivo_oculto/producao/microdramas/AO-IC-E02_A_VOZ_ATRAS_DO_OMBRO.md)

## 2026-11-09 — O Índice Cego, piloto O Quadro 33

- Pesquisa de referência em *A Chegada* e criação de uma série ficcional do Arquivista. Piloto vertical de 50,17 s com voz aprovada, atuação em 2,5D, película, lata, planta da cabine e lente originais.
- A fábrica exige a identificação da encenação nos planos ficcionais e na cartela final de um microdrama. Os dados históricos do piloto têm fontes e créditos próprios.
- O corte final usa o verso da lata no plano S10. A prévia local passou pelo QA da fábrica e pela decodificação integral de áudio e vídeo. [Evidências](../evidence/ao-indice-cego-ep01-verificacao.json)
- O roteiro inicial de *A Margem do Livro* está no [caderno da série](arquivo_oculto/producao/microdramas/O_INDICE_CEGO.md). Seguem pendentes a produção dos próximos episódios e a revisão de publicação.

## 2026-11-09 — Direção editorial V3 do Arquivo Oculto

- O perfil local passa a oferecer seis templates com investigação, atuação, virada e desfecho para Reels, YouTube e microdramas. Atualizadas as Skills do Arquivo Oculto.
- Temporada EP01–EP10 revisada com fala, ação de cena, som, fontes e pendências. Em COINTELPRO, a criação do clube de selos passa a ser tratada como proposta, conforme o arquivo consultado pelo National Archives.
- A fábrica técnica recusa roteiros V3 de pré-produção. A identidade aprovada, os manifestos V2 e os outros perfis foram conferidos contra o estado anterior.
- O próximo lote de produção começa pelo manifesto técnico do EP01, com validação de direitos, locução medida e QA antes de renderizar.

## 2026-11-05 — Temporada V2 no app, cena de época e entrega automatizada (sessão Claude Code)

### Aprovações registradas
- Voz `arquivista-v2-c` e visual do Arquivista aprovados pelo Geovani no chat ("Aprovo, siga"). Registro em
  `config/profiles/arquivo_oculto_v2.lock.json` (`lock_version` 2.0.0-local.2, `approved: true`, `approved_look: true`).

### App "Estúdio Geovani" (autorizado: "lembra de atualizar a aplicação")
- Página V2 publicada: versão 8 do Artifact (`1793893451-76de`).
  - Antes de publicar, a página no ar foi conferida byte a byte com `app/index_original_v1793804553.html`, que segue preservado.
  - O que mudou na página:
    - seletor de formato do perfil Arquivo, com o Investigação 90s como padrão;
    - pedidos levam `formatoAO` e `perfilVersao`;
    - o episódio prefere o vídeo V2 pronto;
    - selos "Perfil V2" e formato em Prontos;
    - rótulos "Pública" / "Prévia privada" no lugar de A/B;
    - herói `arquivo/arquivista_v2.jpg`.
  - As capacidades da página foram mantidas sem mudança.
- Vídeos enviados ao armazenamento do app, com os ids registrados em `arquivo_oculto/producao/v2/entregas_app.json`:
  - EP01 e EP02 em duas versões (pública e prévia privada), mais as capas.
- Pedidos novos `v2-ao-s01-e01` e `v2-ao-s01-e02` no banco: status `pronto`, legenda do manifesto e nota com o resultado do QA.
  - Os pedidos V1 continuam intactos.

### Fábrica
- `fabrica_v2.py --so-qa`: refaz só o QA sobre o vídeo já montado. Recusa se planos ou tempos mudaram. Vídeo, versão do app e capa ficam intocados (conferido por hash).
  - Usado para registrar a aprovação da voz nos QAs do EP01/EP02. Resultado: as prévias passaram a `pass`; as públicas seguem com aviso de arte retida.
- Check `quatro_categorias_de_imagem` fiel ao prompt mestre: personagem, carta/foto/filme real, documento histórico e reconstituição.
  - Filme e foto de arquivo contam no mesmo grupo da carta.
  - A mensagem diz qual grupo falta. Ela dizia "arte real retida" mesmo em episódio sem carta.
- **Cena nova `escritorio_epoca`** (`evidencia.py`): repartição dos anos 1960–70, com arquivos de aço, máquina de escrever, luminária, pastas e persiana.
  - Ações: `lanterna`, `gaveta` e `luminaria`, com som próprio (trilho de gaveta, clique de interruptor).
  - Motivo: a cena V1 `escritorio` tem monitor bege e disquete. No EP04 (1971) e no EP05 (1973) era anacronismo dentro de uma RECONSTITUIÇÃO.
  - Trocada nesses dois episódios e usada no EP06 (S02, "chega ao secretário de Defesa"), onde também quebra três páginas seguidas na abertura.
  - `temporada.py` escolhe a cena de época quando o fato é anterior a 1980.
- `arquivo_oculto/v2/entrega_app.py` (novo) cuida de três etapas da entrega ao app:
  - prepara os arquivos (vídeo do app e capa);
  - registra os ids devolvidos pelo upload;
  - monta os documentos de pedido a partir do manifesto e do QA.
  - Só entra episódio com QA aprovado nos dois modos. A prévia privada só sobe quando tem material privado.
- `instalar_ao.sh` passa a instalar `pymupdf`, usado para ler as páginas de documento.
- `README.md` (novo): mapa dos perfis, link do app, comandos e o que fica fora do Git.
  - O link volta ao repositório por pedido explícito do Geovani. Em 22/10 ele tinha sido tirado do `CLAUDE.md` (`dececd2`).
  - O app continua privado: o link sozinho não dá acesso.
- Teste novo `reconstituicao_sem_anacronismo`: ele pegaria a versão antiga do EP04.
- **`titulo_obra` não deixa mais o subtítulo vazar da tela.** A revisão visual do EP05 achou o problema no S14: "SUBPROJETOS COM TESTES SEM CONHECIMENTO DOCUMENTADOS · 1977" tinha 1335 px num quadro de 1080.
  - Agora o subtítulo diminui até 38 px e, se ainda não couber, quebra em até 2 linhas, dentro de 860 px.
  - Medidos todos os subtítulos da temporada: só esse vazava.
  - Teste novo `titulo_longo_nao_vaza_da_tela`.
- **Plano com imagem retida não finge mais ser original (versão pública).** A revisão visual do EP03 público achou o problema: os 8 planos com "IMAGEM RETIDA" mantinham o selo "CARTA ORIGINAL" e o crédito "reprodução CardGameGeek".
  - O mesmo valia para EP01 S06/S07 e EP02 S15 ("ARTE ORIGINAL").
  - `resolver_direitos` agora troca o selo para IMAGEM RETIDA e o crédito para "<obra> · © <titular> · retida nesta versão, aguardando licença".
  - A prévia privada não muda.
  - Só os planos retidos foram refeitos. Teste novo `placeholder_nao_finge_ser_original`.
  - As versões públicas do EP01 e do EP02 foram reenviadas ao app; os arquivos substituídos foram removidos do armazenamento.

## 2026-11-04 — Recuperação do estúdio e perfil Arquivo Oculto V2 (sessão Claude Code)

### Recuperação, sem reconstrução
- Diagnóstico das quatro peças:
  - o app Artifact "Estúdio Geovani" foi lido e preservado (não republicado);
  - a rotina "Editor do Estúdio" foi lida e não alterada;
  - o repositório `geoprm/estudio-geovani` @ `53f5865`;
  - a fábrica Arquivo Oculto existe só no zip e no app.
- `estudio-gm/` foi extraído de `estudio-gm_arquivo-oculto.zip` (zip preservado). O Git local foi ligado ao `origin` com `git reset origin/main` (só índice), sem commit.
  - O diff contra o GitHub mostra apenas `CLAUDE.md` e `perfis.py` modificados, mais os acréscimos do Arquivo Oculto.
  - Os hashes da extração estão em `../checkpoints/estudio-gm-baseline/SHA256SUMS.txt`.
- Os 10 arquivos da fábrica publicados no app conferem por SHA-256 com o zip. O MP4 do EP01 em Downloads é idêntico ao do zip.

### Perfil V2
- `config/profiles/arquivo_oculto_v2.json`: cópia fiel do pacote. Os originais do prompt, do guia e do JSON estão em `docs/v2/originals/`.
- `config/profiles/arquivo_oculto_v2.lock.json`: voz `arquivista-v2-c` provisória, personagem `arquivista-v2`, modo `performance_2_5d`, modos de render.
- `perfis.py`: só o bloco `arquivo-oculto` ganhou as chaves V2 (versão, contrato, formatos, voz V2, personagem). @direitaxx e Dr. Geovani são idênticos ao GitHub (testado).
- `arquivo_oculto/v2/` (novo):
  - `perfil.py`: carga, validação de esquema, formatos, metas de atuação e filtro de direitos;
  - `voz.py`: adapter Kokoro com 4 presets, cache por hash, amostras e métricas;
  - `ator.py`: Arquivista em camadas com 8 planos de atuação; boca da máscara nunca anima;
  - `evidencia.py`: documento de 1995, título, arte original com filtro de direitos, lista oficial com lápis sincronizado, grade de 412 cartas, leituras, dossiê, linha do tempo e adaptadores das cenas V1;
  - `fundo_motor.py`: ponte para o motor V1, sem alterá-lo;
  - `fabrica_v2.py`: estados reais, voz, timeline, render paralelo por plano com cache, efeitos, ducking, SRT, capa, folha de contato e QA V2.
- `arquivo_oculto/producao/v2/AO-S01-E01.v2.json`: EP01 refeito do zero (15 falas, 28 planos, 4 fontes, 9 claims, 7 assets com direitos).
- `arquivo_oculto/acervo_privado/` (fora do Git): lista oficial INWO de 18/04/1995, página da editora sobre a busca de 1990 e duas artes oficiais. Todos com hash.
- `arquivo_oculto/producao/pautas_app_2026-11-04/`: cópia das 10 pautas do banco do app (procedência).
- `.claude/skills/arquivo-oculto-*`: seção "V2 — 04/11/2026" acrescentada às 10 Skills (texto V1 preservado). A Skill do Arquivista registra a troca do cânone para a aparência premium.
- `.gitignore`: `.venv/`, `.env`, `arquivo_oculto/tts/`, `cache/`, `acervo_privado/`, `assets/referencias_privadas/`.
- `tests/test_arquivo_oculto_v2.py`: 11 testes novos.
- Governança criada: `CLAUDE.md` (seção V2), `PROJECT_STATUS.md`, `VIDEO_PRODUCTION_PIPELINE.md`, `QA_REPORT.md` e este arquivo; também `../CLAUDE.md` (mapa site × estúdio).

### Correções editoriais feitas antes do render
- "Drug Companies" tinha sido suposto como linha da lista oficial e **não está** na lista Unlimited; foi removido.
- A ficha "Terrorist Nuke" teve as cores corrigidas para Derek, não Jeff; a leitura linha a linha havia deslocado a coluna.
- A lista oficial tem 412 cartas: uma linha com célula extra explica a contagem de 411 do primeiro parser.
- Número de computadores apreendidos: a página da editora diz 4 e o relatório V1 diz 3 (decisão judicial, não relida). O EP01 não cita número.

### Renders e correções da noite (detalhe em QA_REPORT.md)
- **Rodada 1** do EP01 (`pass_with_warnings`) revelou:
  - MP4 de 265 MB;
  - títulos colidindo com documentos;
  - círculo cortado;
  - texto fora da margem;
  - legenda pouco legível sobre papel e palavra órfã;
  - personagem escuro;
  - aviso de IA ilegível;
  - checagem tautológica.
  Rodada preservada em `saida_v2/AO-S01-E01_private_preview_rodada1/`.
- **Correções:**
  - encode com teto de 6 Mbps e grão pela metade;
  - nova entrega `video_app.mp4` (≤ 19 MiB, 2 passadas);
  - tarja de legenda, sem truncar e sem palavra órfã;
  - +14% de exposição no Arquivista;
  - margens seguras;
  - QA com `bitrate_master`, `versao_app_ate_19MiB` e a marca de prévia privada de verdade.
- **Rodada 2:** bloqueada pelo próprio QA (S12 quase preto). A causa raiz levou ao **cache por tipo de plano** (`hash_codigo(tipo, prova)`): corrigir um tipo não refaz os outros.
- **Rodada 3:** prévia privada `pass_with_warnings`. A versão pública reaproveitou 25/28 planos e refez só os 3 com material retido.
- **Rodada 4:** S12/S12b mais claros pelo manifesto (`brilho_fundo`); só 2 planos refeitos (46 s); a pública veio 100% do cache.
- **Métrica de arquivo no QA:** a paráfrase de documento com fonte conta como arquivo; o placeholder de asset retido não conta.
- **EP02 V2:**
  - novos tipos `trecho_documento` (transcrição privada × paráfrase pública, lápis com fallback para destaque quebrado) e `terminal`;
  - manifesto com a página da editora sobre a busca de 1990 (snapshot com hash).
- **Temporada:** `arquivo_oculto/v2/temporada.py` gera rascunhos V2 de EP03–EP10 a partir das pautas do app. A fábrica **recusa** manifesto em `rascunho_pendente_checagem`.
- `docs/v2/PLANO_INTEGRACAO_APP_V2.md`: opções e textos para levar a V2 ao app e à rotina, sem aplicar nada.
- `.gitignore` agora também cobre `arquivo_oculto/saida_v2/`.

- **EP02 V2:**
  - rodada 1 bloqueada pelo QA (over-the-shoulder de 6,9 s, Arquivista com 32% do tempo, sem arte real);
  - corrigidas só as 4 falas afetadas (8 planos refeitos, 16 do cache);
  - prévia e pública `pass_with_warnings`.
- **Nova regra `SEM_TITULO`:** sem título na tela em planos de documento, terminal, monitores, dossiê e over-the-shoulder. Removidos S11 do EP01 e S07/S11 do EP02, refeitos sem título.
- Testes novos: `fabrica_recusa_titulo_sobre_documento_e_rascunho` e `cache_por_tipo_de_plano`.

### Regressões
- Nenhuma conhecida: testes V1 e V2 rodados de novo ao fim da sessão (ver QA_REPORT.md).
- A rotina do app continua no caminho V1, de propósito.

### Pendências
- Aprovação da voz pelo Geovani.
- `video_antigo_kwai_1202.mp4` e o zip V2 completo, incluindo as Skills V2 originais e o `CLAUDE_ADDENDUM_V2.md`.
- Revisão humana dos direitos para versão pública.
- Decisão sobre levar a V2 para o app e para a rotina.
- EP02 V2: manifesto a renderizar.
- EP03–EP10: checagem de fontes antes de converter.
