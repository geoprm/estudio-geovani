---
name: arquivo-oculto-montagem
description: Monta os episódios do Arquivo Oculto em formatos verticais e horizontais, com atuação, evidência legível, locução, som e legendas.
---

# Skill — Montagem, edição, render e exportação

## Motor
Reaproveitar montador existente. Se faltar, usar FFmpeg/Remotion sem reescrever a aplicação toda. Manifesto da timeline como contrato: shots com início/fim, asset, crop, movimento, overlays, voz e SFX.

## Padrão técnico
Use a resolução, o aspecto e os fps do formato técnico escolhido. A base define 1080×1920 em 9:16 para Reels e microdramas e 1920×1080 em 16:9 para YouTube. H.264 `yuv420p` CRF 18–23, AAC 48 kHz e MP4 `+faststart`. Validar duração, codec, tamanho, presença de áudio, posição do `moov atom` e legenda.

## Linguagem de edição
Siga [a direção narrativa](../arquivo-oculto-direcao-narrativa/SKILL.md) e o template do formato. Abra no movimento que revela o vestígio. Corte para a próxima ação ou mudança de leitura, com alternância entre espaço, gesto e detalhe. Segure um documento até a informação ficar legível. Use respiração, passos, papel e quedas de trilha para marcar descobertas. Alinhe planos e legendas à voz medida. Use marfim e ouro nas legendas curtas. Diferencie o material documental da encenação com enquadramento, textura e selo legível.

## Área segura para Shorts
Manter texto importante em zona central protegida da UI: margem lateral de >= 100 px, superior >= 180 px e inferior >= 330 px em 1080x1920 (valores iniciais, ajustar por plataforma e testar). Texto nunca colado à borda direita, onde ficam botões; usar no máximo 2 linhas.

## Entregas
`episode_id.mp4`, `episode_id.srt`, `episode_id_cover.png`, `episode_id_manifest.json`, `episode_id_qa.json`. Nomear com slugs seguros. Se cloud storage, gerar URL de download com política correta e verificar que abre. Preferir link direto para MP4, pois o usuário conseguiu baixar assim.

## Fallback e falhas
Se vídeo generativo falhar, aplicar movimento a imagens honestamente identificadas; não trocar imagens históricas por invenções sem rótulo. Não considerar concluído só pelo retorno `job_id`. Preserve checkpoints e não gere novamente assets pagos quando apenas render falhou.

## V2 — 04/11/2026
- Os roteiros editoriais V3 entram como referência de montagem após fechamento do manifesto técnico. A fábrica bloqueia seu uso direto.
- Fábrica V2: `python -m arquivo_oculto.v2.fabrica_v2 <manifesto.v2.json> --modo private_preview|public_release [--refazer S07]`.
- Cada plano é um segmento H.264 próprio com cache por hash (plano + tempos + legendas + código) em `arquivo_oculto/cache/planos_v2/`. Para corrigir uma cena: ajuste o manifesto e rode de novo (só o plano alterado é refeito) ou use `--refazer`.
- Saídas em `arquivo_oculto/saida_v2/<episode_id>_<modo>/`: `video.mp4`, `voice.wav`, `subtitles.srt`, `cover.png`, `timeline.json`, `sources.json`, `qa.json`, `status.json`, `frames.jpg` (folha de contato).
- Áreas seguras usadas: selo e marca em y=190; títulos a partir de y=290; crédito de fonte em y≈1270; legendas em 1380–1600; marca de prévia privada em y=1668; margem lateral de 100 px.
