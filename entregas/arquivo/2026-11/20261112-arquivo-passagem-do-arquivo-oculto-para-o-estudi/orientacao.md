# Passagem do Arquivo Oculto para o Estúdio Geovani

Claude Code, 12/11/2026. A partir daqui, os próximos vídeos do perfil **Arquivo Oculto** saem pelo Estúdio, e o Claude
Code da pasta ARQUIVO OCULTO fica com o site. Pedido do Geovani em 12/11/2026.

## 1. Onde o canal está

| Plataforma | Conta | Como publicamos |
|---|---|---|
| TikTok | **O Arquivista Oculto (@oarquivista.oculto)**. Não usar a conta de 166 seguidores do Geovani | TikTok Studio no Chrome (preferência) ou Metricool, marca `6361339` |
| YouTube | **O Arquivista Oculto (@oarquivista.oculto)**, canal `UCiDZLhTLU-T7vJdpCrctvuw`, ex-"Mistérios e Mitos" | YouTube Studio no Chrome |

- **Registros de publicação**, em `C:\Projetos\ARQUIVO OCULTO\estudio-gm\arquivo_oculto\producao\`:
  - `v2/PUBLICACAO_TIKTOK_S01.json`
  - `PUBLICACAO_TIKTOK_CLAUDE.json`
  - `PUBLICACAO_YOUTUBE_SHORTS.json`
  - `top50/PUBLICACAO_TOP25.json`
- **Bloqueio do YouTube:** o canal não tem verificação por telefone, e só o Geovani pode fazê-la. Até lá:
  - há limite diário de envios: em 11/11 caiu depois do 11º;
  - não sobem vídeos com mais de 15 min;
  - não há miniatura própria.

## 2. Séries do canal

| Série | O que é | Motor | Estado em 12/11 |
|---|---|---|---|
| **Temporada V2** (Arquivos 01–06 + 6 cortes) | Investigação com documentos | fábrica V2 + `assinatura_publica.py` | No ar e agendada até 14/11 no TikTok e no YouTube |
| **O Índice Cego** (Codex) | Microdramas do Codex | do Codex | Lote preparado; ver `HANDOFF_CLAUDE_TIKTOK_GRADE.md` |
| **O Arquivo Responde** | *A Chegada* (Spirit TV) julgada parte por parte | `v2/reel_leve.py` | Fita 01 no ar em 12/11. Fita 02 ("O que há por trás do arco-íris") pendente |
| **Arquivo Morto** | Microdramas de terror rural brasileiro (FICÇÃO) | `reel_leve` + adereços PIL | Caso 01 no ar. Casos 02–03 roteirizados em `arquivo_morto/ARQUIVO_MORTO.md` |
| **Dossiê (Top 25)** | Nossa versão dos 25 temas de maior audiência do nicho | `reel_leve` + biblioteca de atuação | 25 roteiros, re-renderização com o Arquivista atuando, grade de 14/11 a 26/11 |

As 25 próximas já estão planejadas (P01–P25) em `producao/top50/PLANO_TOP25.md`. A próxima série própria, sugerida pelo
Geovani, é **Daniel Mastral**: coordenar com o material do Codex em `producao/pesquisa/mastral`.

## 3. Regras que valem para todo vídeo do canal

- **Abertura:** toda fala do Arquivista começa com **"Olá, criancinhas..."**, com complemento iniciado por **"Hoje"**
  que muda a cada vídeo. Vale também para os cortes. Outros personagens não precisam.
- **Tom:** sombrio, chocante, profundo, viajante, "digno de Oscar".
  - Arquivo Morto: "aterrorizar mesmo".
  - Dossiê e investigação: dopaminérgico, mas com fato.
- **Carimbos:** DOCUMENTADO, SEM PROVA, INTERPRETAÇÃO e FALSO em cada alegação, e placar "O ARQUIVO JULGA" no fim.
  Nenhuma acusação a pessoa viva sem fonte, nem crime com vítima privada.
- **Imagens reais** (decisão D-111, "eu me responsabilizo"):
  - cartas, documentos, fotos e quadros de *A Chegada* entram também na versão pública, com crédito na tela;
  - nunca usar o áudio original de terceiros;
  - preferir domínio público e licença livre (Wikimedia Commons).
- **Língua:** tudo em português do Brasil, vídeo, legenda, título e conversa com o Geovani.
- **IA:** o Arquivista é um personagem criado por IA. Isso vai na legenda do post, e o rótulo de IA fica ligado no
  TikTok e no YouTube.
- **Movimento** (pedido de 12/11): o Arquivista não fica parado. A biblioteca de atuação 2,5D
  (`estudio-gm/arquivo_oculto/saida_v2/ator_clipes/`, gerada por `python -m arquivo_oculto.v2.ator_biblioteca`) tem
  seis planos de 4 s: aparição, olhar para a lente, silêncio em close, debruçar, giro de cabeça e saída na sombra.
  - O `reel_leve` monta cada aparição dele em cortes de até 4 s.
  - A abertura começa saindo da sombra, e o fim termina sumindo nela.

## 4. Publicar pelo Studio de cada plataforma (pedido de 12/11)

**Regra:** sempre que possível, o post sai pelo Studio nativo (**TikTok Studio**, **YouTube Studio**,
**Meta Business Suite**). O Metricool fica só para o que o Studio não alcança, por exemplo o TikTok Studio na web, que
agenda no máximo 10 dias à frente.

**Técnica testada em 12/11 para arquivos acima de 10 MB.** A extensão do Chrome só envia até 10 MB.

1. Hospede o vídeo na Higgsfield (`media_upload` → PUT → `media_confirm`).
2. A URL do CloudFront responde com `Access-Control-Allow-Origin: *`.
3. A própria página do Studio pode buscar o arquivo e entregá-lo ao campo de envio:
   `fetch(url) → Blob → File → DataTransfer`.
4. Assim o vídeo sobe em qualidade total. Isso vale também para vídeos longos no YouTube, depois da verificação do canal.

**Padrão de cada post:**
- não é conteúdo para crianças;
- rótulo de IA declarado;
- tags do tema;
- descrição com fontes e a frase "O Arquivista é um personagem criado por IA".

## 5. Nova linha de produção: Creator Search Insights (pedido do Geovani)

**Objetivo:** usar o **Creator Search Insights** do TikTok (no TikTok Studio, área de inspiração) como segunda linha de
pauta. São as buscas que o público faz no nosso nicho, sobretudo as marcadas como **lacuna de conteúdo**: muita procura,
pouco vídeo.

**Nicho a varrer:**
- conspiração e documentos secretos;
- mistérios sem solução;
- história sombria;
- terror real e lendas brasileiras;
- profecias;
- sociedades secretas.

**Fluxo sugerido:**
1. **Toda semana**, anotar os 20 termos em alta e em lacuna, com volume e tendência quando aparecerem, em
   `orientacoes/arquivo.md` ou num JSON de pauta.
2. **Filtrar** pelas regras do canal: fato checável ou ficção declarada, e nada de vítima privada.
3. **Produzir em formato curto (45–75 s).**
   - Gancho nos primeiros 2 s, com o termo buscado no título e na legenda falada.
   - Usar o formato Dossiê para fatos e o Arquivo Morto para terror.
4. **Reaproveitar** o mesmo vídeo em YouTube Shorts, Reels (Meta) e Kwai, sempre pelo Studio de cada um. A capa e o
   título se adaptam por rede.
5. **Medir** em 48 h (retenção, buscas que trouxeram o vídeo) e devolver o que funcionou para a pauta da semana seguinte.

Não confirmei se o recurso já aparece para @oarquivista.oculto. A conta é nova, e o recurso depende de idade e região.
Se não aparecer, use a busca do TikTok (sugestões e "Outras pessoas pesquisaram").

## 6. Ferramentas que ficam prontas

Tudo dentro de `C:\Projetos\ARQUIVO OCULTO\estudio-gm\arquivo_oculto\`:

- **`v2/reel_leve.py`**: reels 9:16 por roteiro JSON.
  - Visuais: imagem, par, televisor de tubo com vídeo, cartela, placar e retrato atuando.
  - Carimbos, legendas, voz Kokoro (`arquivista-v2-c` e a "voz da fita") e loudnorm a -15 LUFS.
- **`v2/ator_biblioteca.py`**: gera a biblioteca de atuação do Arquivista.
- **`producao/top50/`**:
  - `specs/` + `specs/mapas.json`, e `montar_roteiros.py`, que põe o crédito automático das imagens;
  - `fila_render.sh` (uma renderização por vez, porque a RAM da máquina é curta);
  - `ferramentas/commons.py` (busca de imagens livres no Commons, miniaturas em 1280 px; 1600 px é estrangulado);
  - `ferramentas/buscar.py` + `ranking.py` (levantamento de vídeos do nicho via yt-dlp, só metadados).
- **Folha de contato e QA por quadros** antes de publicar: está nas receitas do `QA_REPORT.md` do motor.

## 7. O que fica pendente nesta passagem

- A re-renderização dos 25 Dossiês com o Arquivista atuando. A fila foi iniciada em 12/11.
  - Trocar a mídia dos 12 já agendados no Metricool.
  - Agendar T13–T25 (TikTok Studio dentro de 10 dias).
  - Subir os Dossiês como Shorts no YouTube Studio, respeitando o limite diário.
  - O Claude Code da pasta ARQUIVO OCULTO conclui isso antes de sair.
- Vídeos longos no YouTube (versões de *A Chegada*, qualidade bem superior à dos Shorts) dependem da verificação do canal.
- *O Arquivo Responde* fita 02, *Arquivo Morto* casos 02–03, série Daniel Mastral, P01–P25 e a linha Creator Search
  Insights.
