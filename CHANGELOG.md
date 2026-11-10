# CHANGELOG — Estúdio Audiovisual GM

Formato: data · o que mudou · arquivos · regressões e pendências. Sem commits locais: o estado de referência é `origin/main` = `53f5865`.

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
