# PROJECT_STATUS — Estúdio Audiovisual GM

Atualizado em 18/11/2026. Estados: **verified** (com evidência), **partial**, **blocked**.

## Linha Dossiê, primeiro longo e publicação (18/11/2026)

- **Pronto (verified):**
  - 25 Dossiês v2, T01 a T25, em `arquivo_oculto/saida_v2/top25/`, com o Arquivista em atuação 2,5D. Os finais abertos valem do T12 em diante.
  - O longo OAR-L01, 16:9, 6 min 30 s, em `saida_v2/longos/OAR-L01/`.
- **TikTok, via Metricool:**
  - T01–T06 publicados.
  - T07 e T08 recusados em 17/11 por limite da conta Metricool.
  - T09–T25 agendados (PENDING), mas devem falhar pelo mesmo limite (**blocked**: decisão do Geovani).
- **YouTube, via Studio:**
  - Shorts T01, T02 e T08 publicados.
  - Programados e conferidos: T09, T03 e T10 (18/11) e T11, T04 e T12 (19/11).
  - O longo OAR-L01 está programado para 18/11 às 20:00.
  - Faltam 16 Shorts (T13, T05, T14, T15, T06, T16, T17, T07, T18–T25), parados pelo limite diário de envios do canal (cerca de 10 por dia; a verificação por telefone, que só o Geovani faz, aumenta esse teto).
- **Registros:** `producao/top50/PUBLICACAO_TOP25.json` e `producao/PUBLICACAO_YOUTUBE_SHORTS.json`.
- **Próximos vídeos:** saem pela Central, com tom "cabuloso" (D-116). A Central roda os pilotos com o `reel_leve` deste motor.

## O Índice Cego

*O Quadro 33* (78,62 s), *A Voz Atrás do Ombro* (64,17 s) e *O Número na Margem* (49,10 s) estão disponíveis na [sala de projeção local](http://127.0.0.1:43127/editorial/sessoes). Os três MP4 foram decodificados integralmente. O [caderno da série](arquivo_oculto/producao/microdramas/O_INDICE_CEGO.md) aponta para *As Sete Portas* e para os dois roteiros longos de YouTube, que aguardam gravação. O primeiro corte de 50,17 s está preservado em `arquivo_oculto/saida_v2/AO-IC-E01_private_preview_final/`.

## Direção editorial V3

- Perfil e seis templates registrados no estúdio. Novos roteiros começam pelo perfil editorial V3 e usam o lock de identidade aprovado.
- EP01–EP10 revisados narrativamente e reunidos no [caderno da temporada](arquivo_oculto/producao/v3/ROTEIROS_TEMPORADA_01.md).
- Pré-produção em aberto por episódio. Fechar fontes e direitos dos recortes, elaborar o manifesto técnico, medir a locução e testar os planos antes do render.
- Resultados anteriores da fábrica e do app referem-se à V2. A pré-produção V3 é local.

## Implementado

| Item | Estado | Evidência |
|---|---|---|
| Estúdio recuperado do zip, sem recriação; diff contra GitHub `53f5865` limitado a `CLAUDE.md`, `perfis.py` e acréscimos | verified | `git status`; `../checkpoints/estudio-gm-baseline/SHA256SUMS.txt` |
| Perfis @direitaxx e Dr. Geovani preservados | verified | teste `perfis_antigos_intactos` (compara com `origin/main`) |
| Perfil Arquivo Oculto V2 (contrato fiel + lock + validação) | verified | `python -m arquivo_oculto.v2.perfil` → 0 erros |
| **Voz `arquivista-v2-c` e visual do Arquivista aprovados pelo Geovani** (04/11/2026, "Aprovo, siga") | verified | `config/profiles/arquivo_oculto_v2.lock.json` (`approved: true`, `approved_look: true`); check `voz_aprovada_pelo_proprietario` passa |
| Skills do Arquivo Oculto em `.claude/skills/` (10), com a V2 | verified | seção "V2 — 04/11/2026" em cada Skill |
| Fábrica V2: estados reais, render por plano com cache por tipo, QA V2, `--so-qa` | verified | `arquivo_oculto/v2/fabrica_v2.py`; `status.json` e `qa.json` de cada episódio |
| Cena de época `escritorio_epoca` (anos 1960–70) no lugar da cena de 1990 antes de 1980 | verified | `evidencia.py`; teste `reconstituicao_sem_anacronismo` |
| Seis formatos no perfil e seletor de formato no app | partial | Contrato, QA por formato e botões no app funcionam. **Só `investigacao_90` foi renderizado**; os pedidos feitos no app ainda vão para a fábrica V1 da rotina |
| **App V2 publicado** (versão 8, `1793893451-76de`) | verified | página conferida contra a versão anterior antes de publicar; `app/index.html`; original em `app/index_original_v1793804553.html` |
| Entrega automatizada ao app (`entrega_app.py`: preparar → registrar ids → pedidos) | verified | `arquivo_oculto/producao/v2/entregas_app.json` |
| Regras contra título sobre documento, render de rascunho e anacronismo | verified | `SEM_TITULO`, bloqueio de rascunho, teste de anacronismo |

## Temporada 1 — episódios V2

| Ep. | Título | Duração | QA pública / prévia | No app | Observação |
|---|---|---|---|---|---|
| EP01 | O jogo que parecia prever o mundo | 84,9 s | `pass_with_warnings` / `pass` | sim, as duas versões | Pública com a arte oficial retida (arquivo 35%); pública reenviada em 10/11 com o selo IMAGEM RETIDA |
| EP02 | A operação contra a editora | 87,8 s | `pass_with_warnings` / `pass` | sim, as duas versões | Revelação: o "Illuminati" da busca de 1990 era o BBS da editora; pública reenviada em 10/11 com o selo IMAGEM RETIDA |
| EP03 | A carta associada a Trump | 91,2 s | `pass_with_warnings` / `pass_with_warnings` | sim, as duas versões (10/11) | Cartas só na prévia; a pública tem 8 planos IMAGEM RETIDA e só 14% de arquivo — fraca para postar sem licença |
| EP04 | COINTELPRO: uma conspiração comprovada | 97,8 s | `pass_with_warnings` (só duração) | sim, versão única | Domínio público: FBI, Senado, Arquivo Nacional, cinejornal de 1957; abertura com reconstituição de época |
| EP05 | MKULTRA: quando o segredo foi confirmado | 95,3 s | `pass_with_warnings` | sim, versão única | Documentos da CIA de 1977; sem foto ou filme real; título "6 DE 149" corrigido |
| EP06 | Operação Northwoods | 95,6 s | `pass_with_warnings` (só duração) | sim, versão única | Memorando de 1962, cinejornal de 1962 e reconstituição de época; os 4 grupos de imagem |
| EP07–EP10 | rascunhos V2 | — | — | não | `rascunho_pendente_checagem`: a fábrica recusa renderizar |

## Publicação (Claude Code, 11/11/2026)

- **TikTok @oarquivista.oculto** (Metricool, marca 6361339, publicação automática):
  - temporada V2 de 11/11 a 14/11, mais *Arquivo Morto* 01 e *O Arquivo Responde* 01;
  - o EP01 já está no ar.
- **Top 25 "Dossiê"** (`arquivo_oculto/producao/top50/`): 25 roteiros prontos, T01 e T02 agendados para 14/11,
  o restante em renderização na fila. Grade: 10:30 e 18:30, até 26/11.
- **YouTube** (canal O Arquivista Oculto): 10 Shorts agendados pelo Studio. O limite diário de envios bloqueou os outros 4.
  Para destravar Shorts, vídeos longos e miniaturas, o Geovani precisa fazer a verificação do canal por telefone.

## Em andamento / pendente

1. **Publicação autorizada pelo Geovani em 11/11** (TikTok e YouTube, ver acima). A versão "Prévia privada" continua fora da rede.
2. **Direitos** — a arte oficial de Steve Jackson Games (cartas) e o trecho literal da editora só entram na prévia privada. Liberar a versão pública com eles exige licença ou parecer.
3. **Rotina "Editor do Estúdio"** — continua na fábrica V1 para pedidos novos do perfil Arquivo. Trocar para a V2 exige alterar a tarefa agendada e o ambiente da nuvem (Kokoro, PyMuPDF, acervo): **aguarda autorização**. Texto pronto em `docs/v2/PLANO_INTEGRACAO_APP_V2.md`.
4. **EP07–EP10** — roteiro V3 de 85 s planejados e fontes de base registradas. O manifesto técnico, a verificação por asset e o render seguem pendentes.
5. **Quatro grupos de imagem** — EP03 e EP06 sem reconstituição; EP05 sem foto ou filme real. Sem material verificado disponível, ficou como aviso, sem forçar.
6. **Referência antiga** — `video_antigo_kwai_1202.mp4` e o zip V2 completo continuam ausentes do disco.
7. **Provedores generativos** — bloqueados: Canva exige plano pago, Figma Weave não está vinculado e não há chave Veo/HeyGen/Runway. Gasto: R$ 0.
8. **GitHub** — versão atual publicada em 10/11/2026 na branch `arquivo-oculto-v2` de `geoprm/estudio-geovani` (commit `95104cb`), com o link do app no `README.md`. A `main` continua em `53f5865` até o merge. Acervo privado, saídas de vídeo e `.env` ficaram fora (conferido no GitHub).

## Próxima ação necessária

Geovani assiste aos episódios em Prontos (perfil Arquivo), revisa as versões públicas e decide:
- quais episódios posta, e em que ordem;
- se autoriza levar a fábrica V2 à rotina do app.
