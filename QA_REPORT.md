# QA_REPORT — Arquivo Oculto

## O Quadro 33 · corte narrativo e assinatura · 10/11/2026

- Prévia de 78,62 s em 1080 × 1920, com 7,47 s de assinatura e voz `arquivista-v2-c`. Conferidos áudio e vídeo por decodificação integral, hashes, 29 intervalos de legenda e sincronismo na emenda.
- O trecho narrativo passou com avisos de duração e proporção de acervo para o perfil geral. Os 29 testes do estúdio passaram. [Verificação](../evidence/ao-indice-cego-ep01-assinatura-verificacao.json) · [Quadro da abertura](../evidence/ao-indice-cego-ep01-assinatura.jpg)

## O Índice Cego · O Quadro 33 · 09/11/2026

- Corte local de 50,17 s, com 19 planos, H.264 a 1080 × 1920 e 30 fps e áudio AAC. O MP4 de prévia foi decodificado por inteiro. As três suítes do estúdio passaram com 29 testes ao todo.
- A timeline corresponde ao manifesto final. A lata de película aparece no S10, a voz usa o perfil aprovado e a ficção tem selo nos 18 planos narrativos e identificação na cartela.
- A fábrica registrou `pass_with_warnings`. Os três avisos dizem respeito à duração inferior ao padrão de 90 s e à quantidade e às categorias de material documental. A peça usa principalmente adereços originais e atuação em 2,5D.
- [Registro da verificação e hashes](../evidence/ao-indice-cego-ep01-verificacao.json) · [Quadro da abertura](../evidence/ao-indice-cego-ep01-abertura.jpg)

## V3 · verificação de pré-produção · 09/11/2026

Revisão narrativa dos dez episódios e validação do perfil, dos templates, das sequências, dos intervalos,
das referências e dos selos dos roteiros. Verificações locais da identidade aprovada, dos outros perfis e do bloqueio da fábrica.
Os arquivos de base V2 foram comparados por hash. Os resultados estão no [registro do lote](../evidence/estudio-editorial-v3-verificacao.json).
Cada roteiro registra suas pendências de acervo e direitos. QA audiovisual, escuta e visualização em aparelho dependem do futuro render.

## Histórico V2

Relatórios automáticos completos ficam em `arquivo_oculto/saida_v2/<episódio>_<modo>/qa.json`. Aqui ficam o resumo, os erros
encontrados e as correções. Revisão visual feita por folha de contato e quadros extraídos do MP4 final. **Não houve escuta
humana nem teste em aparelho físico**; a aprovação editorial e de publicação continua com o Geovani.

## EP01 V2 — rodada 1 (04/11/2026, 22h15–22h34, prévia privada)

Saída preservada em `arquivo_oculto/saida_v2/AO-S01-E01_private_preview_rodada1/`.

| Verificação | Resultado |
|---|---|
| ffprobe | 1080×1920, H.264 yuv420p, 30 fps; AAC 48 kHz estéreo; 84,90 s |
| Duração no formato Investigação 90s (60–105 s, padrão 85 s) | ok |
| moov no início (faststart) | ok |
| Planos | 28 (alvo 18–32) |
| Nenhum plano preto | ok |
| Loudness | -15,3 LUFS integrado, pico -4,1 dBTP |
| Legendas | 31 blocos, monotônicas, texto = narração |
| Personagem | 8 tipos de plano; nenhum acima de 4,6 s; movimento medido de 8,4 a 23,5 em todos; tempo de tela 26,0% |
| Visuais de arquivo | 42,2% (alvo 40–65%) |
| Categorias de imagem | personagem, carta/arte real, documento histórico, reconstituição, ilustração, tipografia |
| Direitos / prévia privada | S02, S06 e S07 com a marca PRÉVIA PRIVADA; nenhum asset barrado no modo |
| Claims | 6 documentados com fonte e 3 interpretações rotuladas |
| Campos V2 por plano e de atuação | completos |
| Voz aprovada pelo proprietário | **aviso**: pendente |
| **Status** | `pass_with_warnings` |

### Erros encontrados na rodada 1 e corrigidos para a rodada 2

| # | Erro | Como foi achado | Correção |
|---|---|---|---|
| 1 | **MP4 de 265 MB (24,8 Mbps)**: impraticável para compartilhar e para o app (partes de 19 MiB) | ffprobe manual; o QA não checava | Encode com teto de 6 Mbps (`-crf 21 -maxrate 6M`); grão de filme pela metade; nova entrega `video_app.mp4` (2 passadas, ≤ 18 MiB); QA ganhou `bitrate_master` e `versao_app_ate_19MiB` |
| 2 | Títulos por cima do documento em S06 e S08a | folha de contato | Títulos removidos desses dois planos |
| 3 | O círculo do lápis em "Epidemic" (S09) cortado na borda | folha de contato | Enquadramento do macro deslocado |
| 4 | "PREVISÃO?" encostado na borda esquerda (fora da margem de 100 px) | folha de contato | Largura máxima do texto em `leituras` reduzida |
| 5 | Legenda creme sobre papel claro com pouco contraste (S08, S09) | folha de contato | Tarja escura suave atrás de cada linha de legenda |
| 6 | Palavra órfã na legenda ("futuro." sozinho por 0,8 s) e risco de truncar a terceira linha | leitura do SRT | Blocos de uma palavra se juntam ao anterior; a fonte diminui até caber em 2 linhas (nunca trunca) |
| 7 | Planos do Arquivista escuros para tela de celular (luminância média 12–19) | métrica por plano + quadros | +14% de exposição nos planos do personagem |
| 8 | Aviso "personagem fictício · voz sintética (IA)" quase ilegível na cartela final | quadro do fim | Fonte maior e mais clara |
| 9 | Checagem `marca_de_previa_privada` era tautológica | revisão do código | Passa a comparar o material privado por direito com o material marcado |

### Erros editoriais evitados antes do render

- "Drug Companies" estava na tabela por suposição e **não consta** da lista Unlimited de 18/04/1995: removido.
- As cores de "Terrorist Nuke" são de Derek, não de Jeff (leitura de colunas deslocada): corrigido. Teste novo compara cada linha exibida com o snapshot.
- A lista tem 412 cartas: uma linha com célula extra explicava a contagem de 411 do primeiro parser.
- O número de computadores apreendidos diverge entre fontes (4 na página da editora, 3 no relatório V1). O EP01 não cita número e o EP02 registra a divergência.

## EP01 V2 — rodada 2 (22h36–22h49): **bloqueada pelo QA**

Todas as correções acima foram aplicadas. Tamanho resolvido: master com 63 MB (5,9 Mbps) e versão para o app com 18,0 MiB.

O QA bloqueou a entrega com `sem_quadro_preto`: o plano S12 (primeira leitura, "PREVISÃO?") tinha luminância média 7,x, quase tela preta no celular.

O bloqueio também revelou uma falha de arquitetura: o hash do cache incluía módulos inteiros, então corrigir um tipo de plano refazia todos.

**Correções:**
- impressão digital do código **por tipo de plano** (`fabrica_v2.hash_codigo(tipo, prova)`);
- fundo das leituras mais claro (`brilho_fundo`, padrão 0,34);
- fallback do lápis para destaque que quebra entre linhas (EP02).

## EP01 V2 — rodada 3 (prévia privada, render completo por causa do novo esquema de hash) e versão pública

| | Prévia privada | Versão pública |
|---|---|---|
| Status | `pass_with_warnings` (só a voz pendente) | `pass_with_warnings` (voz + arte retida + arquivo abaixo da meta) |
| Duração / planos | 84,90 s / 28 | 84,90 s / 28 |
| Planos refeitos | 28 (851 s) | **3 (S02, S06, S07)**; 25 vieram do cache |
| Loudness | -15,3 LUFS, pico -4,1 dBTP | igual |
| Personagem | 8 tipos, 26,0% do tempo, movimento em todos | igual |
| Visuais de arquivo | 42,2% | 30,7% (aviso: a arte oficial vira "ARTE ORIGINAL RETIDA") |
| Categorias de imagem | 6, incluindo carta/arte real | 5, sem arte real (aviso) |
| Marca PRÉVIA PRIVADA | S02, S06, S07 (= material privado por direito) | nenhuma (nenhum material privado) |
| Master / app | 61,3 MiB (6,1 Mbps) / 18,0 MiB | 61,3 MiB / 18,0 MiB |

## EP01 V2 — rodada 4: regeneração cirúrgica (prova do requisito "refaça só o trecho")

O S12 passou na rodada 3 com luminância 8,5, ainda escuro. Aumentei `brilho_fundo` só em S12 e S12b, pelo manifesto. Resultado:
- **prévia privada:** 26 planos do cache, 2 refeitos, 46 s;
- **versão pública:** 28 do cache, 4 s.

Ambas `pass_with_warnings`.

Revisão visual final na folha de contato (`frames.jpg`): os nove problemas da rodada 1 estão resolvidos.

**Observação ainda aberta, sem bloqueio:** em S11 o título "DÉCADAS DEPOIS" disputa espaço com os monitores.

## EP02 V2 — "A operação contra a editora"

**Rodada 1 (prévia privada, 21 planos, 724 s): bloqueada pelo QA.** Três problemas:
- `plano_do_personagem_curto`: S07 (over-the-shoulder) com 6,9 s, uma fala longa com um só plano;
- tempo de tela do Arquivista em 32,3% (alvo ≤ 28%);
- sem carta ou arte real.

**Correções só nas falas afetadas:**
- L05 dividida (over-the-shoulder + trecho em close);
- L08 com silêncio curto + tipografia;
- L11 com a arte oficial "Bavarian Illuminati" (filtro de direitos);
- L14 com cartas antes do olhar final.

**Rodada 2:** 16 planos do cache e 8 refeitos (195 s). Prévia privada `pass_with_warnings`:

| Verificação | Resultado |
|---|---|
| Duração / planos | 87,76 s / 24 |
| Loudness | -15,4 LUFS, pico -4,5 dBTP |
| Personagem | 8 tipos; nenhum acima de 4,6 s; 24,7% do tempo |
| Visuais de arquivo | 47,9% |
| Categorias | 6, incluindo carta/arte real |
| Master / app | 62 MiB (6,0 Mbps) / 18,3 MiB |

**Versão pública:** 19 planos do cache e 5 refeitos (S06, S07, S07b, S12, S15). `pass_with_warnings`, com o aviso de arte retida.

**Revisão visual:**
- o fallback do lápis circulou "Secret Service", "Illuminati BBS" e "816 F. Supp.", que quebravam entre linhas;
- duas colisões de título: S07 e S11.

**Correção estrutural:** a fábrica agora **recusa** título na tela em planos de documento, terminal, monitores, dossiê e over-the-shoulder (`SEM_TITULO`). A regra também pegou o "DÉCADAS DEPOIS" do EP01 (S11). Títulos removidos e planos refeitos nas versões finais.

**Fato tratado com cuidado:** a editora informa quatro computadores apreendidos e o relatório V1 registrava três (pela decisão judicial, não relida). O EP02 não cita número.

## Rodada final (04/11/2026, ~23h50) e testes

Após a regra `SEM_TITULO`, as quatro versões foram refeitas pelo cache:

| Versão | Planos refeitos | Do cache | Status |
|---|---|---|---|
| EP01 privada | 1 | 27 | `pass_with_warnings` |
| EP01 pública | 0 | 28 | `pass_with_warnings` |
| EP02 privada | 2 | 22 | `pass_with_warnings` |
| EP02 pública | 1 | 23 | `pass_with_warnings` |

Testes: V2 13/13 e V1 7/7. Perfil V2: 0 erros.

Arquivos: masters de 61–62 MiB e `video_app.mp4` de 18,0–18,3 MiB, todos 1080×1920 H.264/AAC.

## Arquivos entregues (EP01 e EP02)

`arquivo_oculto/saida_v2/AO-S01-E0{1,2}_private_preview/` e `.../AO-S01-E0{1,2}_public_release/`:
- `video.mp4` (master);
- `video_app.mp4` (≤ 19 MiB);
- `voice.wav`, `subtitles.srt`, `cover.png`;
- `timeline.json`, `sources.json`, `qa.json`, `status.json`;
- `frames.jpg`.

Os SHA-256 estão em `qa.json`. O teste `entrega_ep01_v2_com_qa` confere que os arquivos não mudaram depois do QA.

## O que este QA não cobre

- **Escuta humana** da voz e da mixagem.
- **Teste em aparelho físico** e na interface do Instagram/TikTok.
- **Revisão editorial humana.**
- **Avaliação jurídica** do uso da arte oficial na versão pública.
- **Comparação com o vídeo antigo**, que está ausente do disco.
