---
name: arquivo-oculto-orquestrador
description: Orquestra a produção automatizada de episódios do Arquivo Oculto, preservando o aplicativo existente e entregando MP4 validado.
---

# Skill — Orquestrador de produção audiovisual

## Quando usar
Quando o usuário pedir criar, revisar, dirigir, produzir ou editar episódio do Arquivo Oculto. Uma solicitação de revisão termina na pré-produção.

## Sequência obrigatória
1. Inspecione o repositório da aplicação existente e `CLAUDE.md` antes de alterações. Não crie um novo projeto por preferência tecnológica.
2. Carregue `../arquivo-oculto-factcheck/SKILL.md` para validar fatos e direitos, `../arquivo-oculto-roteiro/SKILL.md` para roteiro, `../arquivo-oculto-arquivista/SKILL.md` para consistência, `../arquivo-oculto-visuais/SKILL.md` para assets, `../arquivo-oculto-locucao/SKILL.md` para voz, `../arquivo-oculto-montagem/SKILL.md` para render e `../arquivo-oculto-qa/SKILL.md` para aprovação técnica e `../arquivo-oculto-retencao/SKILL.md` para ganchos e métricas honestas.
3. Carregue a [direção narrativa V3](../arquivo-oculto-direcao-narrativa/SKILL.md). Na raiz do estúdio, use `python -m arquivo_oculto.editorial --template <formato>` e, para a primeira temporada, `python -m arquivo_oculto.editorial --episodio AO-S01-E01` com o ID pedido. Para episódios novos siga o mesmo perfil. Em produção, transfira a narração, os planos e os direitos já conferidos para um manifesto técnico. Roteiros e renders V2 anteriores à revisão ficam como histórico.
4. Defina dependências e provedor disponível. Não invente assinatura, créditos ou API. Integração sempre através de adapters com retry idempotente, custo estimado, timeout e trilha de erros.
5. Gere e salve assets usando `job_id/scene_id/asset_id`, com fonte, direitos e hash para evitar recálculo; gere voz com voz fixa e duração real.
6. Monte **vídeo real**, `.srt`, thumbnail e relatórios, inspecionando com `ffprobe` e amostra de frames; teste reprodução e link de MP4.
7. Se faltar provedor, entregue melhor renderização alternativa legítima usando stills/parallax e narração, com rótulo honesto; não afirme que cenas foram geradas quando não foram.
8. Não publique nem compre créditos sem autorização. Uma solicitação de produção não é autorização de publicação pública.

## Marcos de aceitação
- `planned` / `scripting` / `asset_generation` / `audio_generation` / `rendering` / `qa` / `completed` / `blocked` / `failed` devem corresponder a evidências reais.
- Em revisão editorial, entregue texto falado, direção visual e sonora, fontes e pendências por episódio. Em produção, valide o episódio solicitado na versão correspondente.
- Forneça caminhos existentes para `video.mp4`, `captions.srt`, `cover.png`, `manifest.json`, `qa.json`; sem caminhos fictícios.

## V2 — 04/11/2026
- Contrato: `config/profiles/arquivo_oculto_v2.json` (cópia fiel do pacote) + `arquivo_oculto_v2.lock.json` (decisões locais). Validar com `python -m arquivo_oculto.v2.perfil`.
- Formatos: `reel_30`, `investigacao_90` (padrão, 85 s), `reel_profundo`, `youtube_5min`, `youtube_10min`, `microdrama`. O formato do manifesto define a faixa de duração, o número de planos e o QA.
- Entrada: manifesto `arquivo_oculto/producao/v2/<episode_id>.v2.json` (modelo: AO-S01-E01). Estados reais em `status.json`: planned, sources_verified, generating_voice, generating_visuals, assembling, qa, completed ou blocked.
- O app (Artifact "Estúdio Geovani") e a rotina "Editor do Estúdio" continuam no caminho V1 até o Geovani aprovar a troca; a fábrica V2 roda localmente (Claude Code no PC).
