# Manual de publicação — O Arquivista Oculto

Manual escrito pelo Claude Code do motor em 18/11/2026, para a passagem da publicação à Central do Estúdio Geovani.
Decisão do Geovani (18/11): as postagens ficam com o Estúdio; o motor volta ao site e só faz vídeo quando ele pedir.

## Contas e canais

| Rede | Conta | Via | Quem cuida |
|---|---|---|---|
| TikTok | @oarquivista.oculto ("O Arquivista Oculto") | TikTok Studio no Chrome do Geovani | Central, desde 18/11 |
| YouTube | O Arquivista Oculto (`UCiDZLhTLU-T7vJdpCrctvuw`) | YouTube Studio no Chrome | motor até 18/11; depois a Central |
| Metricool | marca 6361339 | conta no limite desde 17/11 | não usar para o TikTok; os posts pendentes vão para rascunho |

Nunca usar a conta pessoal de TikTok do Geovani (166 seguidores). Antes de postar, confira o `uniqueId` na página: tem
que ser `oarquivista.oculto`.

## Registros (fonte da verdade)

- `producao/top50/PUBLICACAO_TOP25.json`: os 25 Dossiês (TikTok), com mídia, horário e estado.
- `producao/PUBLICACAO_YOUTUBE_SHORTS.json`:
  - temporada (14 Shorts);
  - `dossies_top25`, com id, estado e pendentes;
  - `longos` (OAR-L01).
- `producao/youtube_fila_pendente.json`: Shorts dos Dossiês que ainda faltam no YouTube, com título, descrição,
  URL hospedada, data e hora.

## YouTube Studio: como agendar sem erro

1. **Hospedar o vídeo** com CORS liberado. Na Higgsfield: `media_upload` (vários arquivos de uma vez) → `curl PUT` com
   `Content-Type: video/mp4` e `If-None-Match: *` → `media_confirm`. A URL do CloudFront serve para o `fetch` na
   página do Studio.
2. **Uma aba nova do Studio**, na lista de Shorts. Cole `producao/youtube_studio_agendar.js` no javascript_tool com 3 a 4
   itens em `FILA`. Leia o andamento em `document.documentElement.dataset.ytlog`, a cada 4 ou 5 minutos.
3. **Conferir depois:** abra `studio.youtube.com/video/<id>/edit` e clique em "Editar status de visibilidade do vídeo".
   Confira se `#datepicker-trigger` e `#time-of-day-container input` mostram a data e a hora certas.

### Armadilhas conhecidas

- **Hora:** digitar no campo de hora mostra o valor, mas pode não gravar (o T10 foi parar às 00:00). Abra a lista de
  horários e clique na opção.
- **Data:** clique no dia em `ytcp-scrollable-calendar span.calendar-day`, contando a partir do dia `.today`. O calendário
  pode levar até uns 40 s para abrir com a máquina carregada. Não clique de novo antes disso: o segundo clique fecha.
- **Visibilidade:** não clique em "Avançar" às cegas. O padrão do canal é **Público**, e foi assim que o T01 saiu na
  hora. Pare quando `#second-container-expand-button` ("Programar") aparecer.
- **Janela "Vídeo programado":** feche pelo `#close-button`. Se ficar aberta, o envio seguinte trava.
- **Limite diário de envios:** o canal sem verificação aceita cerca de 10 envios a cada 24 h. Quando estoura, o diálogo
  avisa e o script para com `LIMITE`. A verificação por telefone, que só o Geovani faz, aumenta esse teto.
- **Memória:** com render rodando (`ffmpeg`/`reel_leve`), a máquina chega a ficar com 16 MB livres e o Chrome congela ou
  troca a aba. Não renderize enquanto publica. Se a aba cair, os ids de aba mudam: chame `tabs_context_mcp` de novo.
- **Envio interrompido** vira rascunho com "Retomar o envio". Não clique nesse botão: ele abre o seletor de arquivo do
  sistema. Suba o vídeo de novo e deixe o rascunho quebrado para o Geovani decidir. Hoje há um do T04.

### Grade do YouTube (Dossiês)

- T08–T25 nos mesmos horários do TikTok, às 10:30 e às 18:30, até 26/11.
- T02–T07 às 14:00, de 17/11 a 22/11.
- O longo OAR-L01 em 18/11 às 20:00.

## TikTok Studio (método da Central)

A Central sobe o arquivo original em 1080p, em pedaços de 8 MB conferidos por sha256. Cada post leva a legenda do
Metricool, o rótulo de IA e o horário da grade. O post equivalente no Metricool vai para rascunho, para não sair em dobro.

Se for preciso agendar pelo Chrome com a janela fora da tela, use:
- **Legenda:** `insertText` com a seleção limitada ao editor. Confira se o post salvo ficou com o texto completo: no T07
  das 14:00, o editor mostrou o texto e gravou só "T07".
- **Programar:** `input[value=schedule].click()`.
- **Hora:** PointerEvents sintéticos em `.Picker__trigger` e nas opções `[role=option]`. As horas vão de 00 a 23 e os
  minutos andam de 5 em 5.
- **Rótulo de IA:** o switch ao lado de "Conteúdo gerado por IA".
- **Por fim, o botão "Agendar"**, e depois conferir a lista de conteúdo.

## Limites editoriais (valem para qualquer post)

- O rótulo de IA vai sempre ligado. O YouTube não é para crianças.
- Créditos das imagens na descrição ou na tela. Nas cartas, "reprodução da internet".
- D-115 e D-116:
  - fato real e conferido, teoria contada como teoria;
  - nenhuma pessoa viva acusada;
  - nada de saúde, eleição ou ódio a grupos;
  - não refazer o que já foi publicado.

## Pendências para o Geovani

- Verificar o canal do YouTube por telefone.
- Decidir se apaga o rascunho quebrado do T04 no YouTube.
- Duplicata do T07 no TikTok (18/11 14:00, legenda só "T07"): o Geovani mandou deixar. Sem pendência.
