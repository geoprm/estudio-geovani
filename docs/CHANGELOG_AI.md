# CHANGELOG_AI — Central do Estúdio Geovani

## 12/11/2026 — Primeiras entregas reais e ajustes (Claude Code, Opus 5.5)

- **Formato do app conferido contra o banco real** (leitura de `pedidos/v2-ao-s01-e01` e de 6 pautas):
  - o pedido da Central usa os mesmos campos que o app lê;
  - nas pautas faltavam `ordem` e `criadoEm`, e o app ordena as pautas do dia por `ordem`. Agora as duas vão em toda
    pauta (padrão 9), e o pacote pode trazer `pauta.ordem` e `pauta.porque`.
- **Primeiras entregas recebidas**, todas da sessão do Claude Code do motor:
  - a orientação "Passagem do Arquivo Oculto para o Estúdio";
  - os Dossiês T01 (Illuminati, 106,6 s) e T02 (Olho na nota de 1 dólar, 97,6 s), com QA `pass_with_warnings` e
    revisão por quadros feita.
- **Orientação com documento anexado:** o registro em `orientacoes/<perfil>.md` passa a linkar o documento completo
  (`arquivos.roteiro` e extras .md/.txt), não só o resumo.
- **`receber --app-depois` + `estudio.py app <id>`:** recebe na hora e adia a recodificação da versão do app quando a
  memória está no limite. Hoje havia ~300 MB livres com a fila de render do motor rodando.
- **Skill de grafismos:** o FFmpeg desta máquina derruba o `drawtext` sem `fontfile` (sem config de fontes do sistema).
- **Perfil `arquivo`:** bloco `passagem_2026_11_12` com séries ativas, regras reforçadas e a linha Creator Search
  Insights.
- **Testes:** 17 casos, com o novo `test_17_app_depois`.

## 11/11/2026, 21h17 — Ligações aplicadas (Claude Code, Opus 5.5)

- Bloco da Central acrescentado no fim de `~/.codex/AGENTS.md` (estava vazio), de `ARQUIVO OCULTO\AGENTS.md` e de
  `estudio-gm\CLAUDE.md`. Conferido: os bytes anteriores de cada arquivo ficaram idênticos à cópia de antes.
- A primeira edição do `AGENTS.md` do Arquivo Oculto tinha trocado os 2 fins de linha CRLF por LF. Foi refeita a partir da
  cópia original, com o bloco acrescentado por bytes.
- `tools/package.py` do Arquivo Oculto só copia o `AGENTS.md` para o pacote, sem conferir hash: o acréscimo não quebra
  o build do Codex.
- Cópias de antes em `ligacoes/antes_2026-11-11/`. Também atualizados: `ligacoes/LEIA-ME.md`, `docs/DECISIONS.md` (C-006) e
  a D-113 no `ECOSSISTEMA.md`.

## 11/11/2026 — Criação da Central (Claude Code, Opus 5.5)

- Código do app (versão 8, `1793893451-76de`) extraído do `Estúdio Geovani.zip` para `app/`. Hash do `index.html`
  conferido contra o zip, a cópia do motor e a versão publicada: `b3b56845…`, idênticos.
- Perfis em `config/perfis/`: `direitaxx`, `drgeovani` e `arquivo` (ativos), e `melinda` (planejado). Também
  `config/app.json` (coleções, limites e rotina) e `config/agentes.json` (como cada ferramenta entrega).
- Contrato `esquemas/entrega.schema.json`, modelo `entrada/_modelo/entrega.json` e guia `entrada/LEIA-ME.md`.
- Ferramenta `ferramentas/estudio.py` (só biblioteca padrão + FFmpeg), com os módulos `comum`, `pacote`, `midia`,
  `app_docs` e `skills`.
- 16 skills em `.claude/skills/`, espelhadas em `.agents/skills/`:
  - entrega e recepção: orquestrador, pacote de entrega, recepção;
  - produção: roteiro e storyboard, montagem, narração, áudio, legendas, cor;
  - acabamento: grafismos, capas, cortes, exportação;
  - controle: QA, direitos e rótulos;
  - perfil novo: animação infantil.
- `modelos/INSTRUCOES_PARA_CHATS.md`: bloco para colar no ChatGPT e no Claude chat.
- Testes: `tests/test_central.py`, com 16 casos e vídeos sintéticos. As 39 receitas FFmpeg citadas nas skills foram
  executadas uma a uma com FFmpeg 9.0.2, sem falha.
- Nada foi alterado no motor `estudio-gm`, no app publicado ou em outros projetos.
