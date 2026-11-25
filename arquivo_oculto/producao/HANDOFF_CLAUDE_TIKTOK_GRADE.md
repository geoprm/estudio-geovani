# Handoff — grade do TikTok @oarquivista.oculto (Claude Code, 11/11/2026)

Para o Codex, antes de agendar o lote de *O Índice Cego* (`microdramas/PUBLICACAO_TIKTOK.json`, estado `prepared`).
Esse arquivo dele não foi alterado.

## O que já está agendado

A temporada V2 está agendada **no Metricool**, marca `6361339`, com publicação automática e rótulo de IA ligado, na
conta @oarquivista.oculto. A mídia está hospedada na Higgsfield. O registro completo, com ids, hashes e trechos, está
em [`v2/PUBLICACAO_TIKTOK_S01.json`](v2/PUBLICACAO_TIKTOK_S01.json).

| Dia | 09:00 | 12:30 | 16:30 | 20:00 |
|---|---|---|---|---|
| 11/11 | — | EP01 | corte EP01 | EP02 |
| 12/11 | corte EP02 | EP03 | corte EP03 | EP04 |
| 13/11 | corte EP04 | EP05 | corte EP05 | EP06 |
| 14/11 | corte EP06 | — | — | — |

O EP03 e o corte dele foram liberados pelo Geovani em 11/11, depois de ele assistir.

**Reservados para as séries novas do Claude:**
- 11/11, 23:15: *Arquivo Morto*, caso 01 (*Carta Sem Remetente*).
- 12/11, 14:30: *O Arquivo Responde*, fita 01 (*O Homem Mais Maligno do Mundo*).

Os dois são do motor leve `arquivo_oculto/v2/reel_leve.py`.

**Horários livres sugeridos para O Índice Cego:** 22:30 em 11, 12 e 13/11, ou 12:30, 16:30 e 20:00 a partir de 14/11.
Agendar pelo mesmo Metricool evita post duplicado. Antes de criar um post, conferir com `getScheduledPosts`.

## Regra nova do canal

A primeira fala do Arquivista em todo vídeo narrado por ele começa com "Olá, criancinhas...", e o complemento, iniciado
por "Hoje", muda a cada vídeo. Ela vale também para os cortes.

Os cortes V2 não tinham essa abertura. Para não re-renderizar, criei `arquivo_oculto/v2/assinatura_publica.py`.

- **O que faz:** aceita corte `public_release` aprovado pelo QA e gera ~6 s de abertura com o retrato canônico, o mesmo
  cabeçalho, título e legenda da fábrica e a voz do lock. Emenda por concat, sem recodificar o episódio.
- **Opções:** `--inicio` e `--fim` fazem cortes curtos.
- **Diferença para `assinatura.py`:** a do Codex põe o selo FICÇÃO e só aceita prévia privada.

A fábrica inteira não roda com a memória atual da máquina. Duas renderizações morreram por falta de RAM e derrubaram
a sessão.
