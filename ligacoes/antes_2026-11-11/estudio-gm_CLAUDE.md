# Estúdio de Reels do Geovani Miranda (Estúdio Audiovisual GM)

Programa de edição de vídeo do Geovani (fonoaudiólogo em Barreiras/BA) para três perfis com objetivos diferentes:
- @direitaxx: liderança política e social em Xique-Xique e no sertão da Bahia. Firme, com fonte.
- Dr. Geovani Miranda: autoridade que acolhe, ensina e guia famílias. Calmo, educativo, sem susto.
- Arquivo Oculto: vídeos 100% gerados por IA, narrados pelo personagem fictício O Arquivista (pasta `arquivo_oculto/`).

Quem usa: o "Editor do Estúdio" (tarefa agendada) e conversas com o Claude. Os pedidos chegam pelo app privado do
Geovani (o link vem no pedido da tarefa): banco `pedidos`, `pautas` e `config/app`.

Antes de editar, leia LEIA-ME.md, modelo_video.py e exemplos/tela_dividida_educacao.py.

Fluxo: instalar.py (uma vez) → preparar.py → ritmo.py → videos/<id>.py (copiado do modelo) → preview → finalizar.py.

Regras que não mudam:
- Fato só com fonte aberta e confiável; o selo mostra veículo e data. Gancho fiel ao dado (46,8% é "quase metade").
- Nada de corte ou montagem que mude o sentido do que alguém disse. Corrija a legenda contra a fala real.
- Dr. Geovani: nunca expor paciente, nada de diagnóstico pelo vídeo nem promessa de cura.
- Não publicar em rede social nem mandar mensagem por ele: ele posta.
- Retoque leve vem ligado pelo perfil; desligue (R.retoque = None) quando o pedido tiver retoque = false.
- Período eleitoral: conteúdo alterado por IA exige rótulo (Res. TSE 23.610, art. 9º-B).

## Arquivo Oculto (perfil `arquivo-oculto`) — mesclado do CLAUDE_ADDENDUM.md

Caminho próprio, isolado dos outros dois perfis (não usa preparar/ritmo/finalizar). Ponto de entrada: Skill `/arquivo-oculto-orquestrador`
(`.claude/skills/arquivo-oculto-*`). Leia `arquivo_oculto/README.md` antes de mexer.

- Formato "ia": `python3 arquivo_oculto/fabrica.py <manifesto do pacote> <producao.json> <pasta>` gera MP4 1080x1920 H.264/AAC, `.srt`,
  capa `.png`, `_manifest.json` (fontes, claims, voz, provedores, hashes) e `_qa.json`. Só é `completed` com QA `pass`/`pass_with_warnings`.
- Formato "filtro": `python3 arquivo_oculto/filtro.py bruto.mp4 saida.mp4` põe máscara e capuz do Arquivista no rosto de quem gravou e troca o fundo.
- Personagem `arquivista-classico-v1`: máscara de porcelana marfim, capuz e luvas pretas, biblioteca de arquivo; voz `arquivista-voz-01` fixa.
  A referência `assets/referencias_privadas/` é só interna (nunca publicar).
- Modo visual atual: `animated_stills` (Arquivista animado por deformação + cenas desenhadas por código). Não chamar de vídeo generativo.
  Para imagens/vídeo por IA, criar um adapter em `fabrica.PROVEDORES` só quando houver credencial testada; geração paga exige autorização.
- Editorial: separar fato documentado, alegação, interpretação, coincidência e incerteza; cena dramatizada leva selo RECONSTITUIÇÃO IA ou ILUSTRAÇÃO;
  nenhuma acusação a pessoa identificável sem fonte sólida; religiões com respeito; nada de prometer evento futuro.
- Credenciais só em `.env` (nunca no repositório). Não publicar em rede social nem comprar créditos sem autorização do Geovani.
- Rastreabilidade: manter claims, fontes, assets, hashes e custos no manifesto; renderizações idempotentes (cache de TTS por hash).

## Arquivo Oculto — direção editorial V3 (09/11/2026)

Para novos episódios e revisões, iniciar pelo [perfil editorial](config/profiles/arquivo_oculto_editorial_v3.json) e pela
[Skill de direção narrativa](.claude/skills/arquivo-oculto-direcao-narrativa/SKILL.md). Na raiz do estúdio,
`python -m arquivo_oculto.editorial --template <formato>` mostra a estrutura e a montagem do formato.
`python -m arquivo_oculto.editorial --episodio AO-S01-E01` abre a revisão do episódio escolhido (E01 a E10).
Fechar evidências, direitos e planos antes de montar o manifesto técnico. Os JSON da temporada V3 ficam em
`arquivo_oculto/producao/v3/` com estado de pré-produção. Esta direção é exclusiva do Arquivo Oculto.

## Arquivo Oculto V2 — contrato técnico e identidade (04/11/2026)

O perfil V2 substitui a orientação V1 acima onde houver conflito (aparência, voz, modo visual, formatos). O caminho V1
(`fabrica.py`, `motor.py`, `filtro.py`) continua funcionando e é o que a rotina do app usa até o Geovani aprovar a troca.

- **Contrato:** `config/profiles/arquivo_oculto_v2.json` (cópia fiel do pacote; original em `docs/v2/originals/`) e
  `config/profiles/arquivo_oculto_v2.lock.json` (decisões desta instância). Validar: `python -m arquivo_oculto.v2.perfil`.
- **Fábrica V2:** `python -m arquivo_oculto.v2.fabrica_v2 <manifesto.v2.json> --modo private_preview|public_release` (use `.venv/Scripts/python`).
  Manifestos em `arquivo_oculto/producao/v2/`. Saídas em `arquivo_oculto/saida_v2/<id>_<modo>/`. Detalhes em `VIDEO_PRODUCTION_PIPELINE.md`.
- **Personagem `arquivista-v2`:** aparência de `arquivo_oculto/assets/arquivista.png` com máscara rígida marfim envelhecida e veios dourados.
  No fluxo V3 de 10/11/2026, a boca da máscara pode articular de modo sutil em planos marcados com `mascara_falada`; cortes legados preservam a máscara imóvel. Ele atua (aparição à contraluz, caminhada, giro de cabeça, olhar para a lente, over-the-shoulder,
  debruçar, silêncio, saída na sombra), entra e sai do quadro, fica 12–28% do tempo em tela, nenhum plano dele passa de 4 s.
- **Voz `arquivista-v2-c`** (Kokoro local) aprovada em 04/11/2026, com parâmetros fixados no lock. O vídeo antigo do Kwai continua como referência histórica quando disponível.
- **Formatos:** reel_30, investigacao_90 (padrão), reel_profundo, youtube_5min, youtube_10min, microdrama. O formato muda duração, número de planos e QA.
- **Direitos:** material com direitos pendentes só em `private_preview`, com a marca PRÉVIA PRIVADA. Em `public_release` vira placeholder
  ou paráfrase com fonte. `arquivo_oculto/acervo_privado/` e `assets/referencias_privadas/` ficam FORA do Git: este repositório é público.
- **Fatos:** toda linha de tabela, data e número exibidos são conferidos na fonte primária salva em `acervo_privado/`, com hash.
  Interpretação aparece com selo INTERPRETAÇÃO ou ANÁLISE. Divergência entre fontes é registrada, não escondida.
- **Provedores:** sem gerador de vídeo/imagem utilizável em 04/11/2026; o modo é `performance_2_5d` e é declarado assim.
  Qualquer provedor pago só com autorização, custo estimado e adapter testado.
- **Governança:** ao fim de cada sessão, atualizar `PROJECT_STATUS.md`, `CHANGELOG.md` e `QA_REPORT.md`. Sem commit/push sem pedido explícito.
