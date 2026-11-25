---
name: arquivo-oculto-qa
description: Audita cada reel com verificações técnicas, editoriais, visuais, acessibilidade e links de download.
---

# Skill — Controle de qualidade e liberação

## Gate obrigatório
**Nunca** mudar um episódio para `completed` sem MP4 real abrindo, `.srt`, capa e manifesto de assets. Exibir `blocked` quando faltarem créditos/licenças, não fingir sucesso.

## Checklist automático
- `ffprobe`: resolução e proporção do formato, H.264, framerate previsto, duração na faixa do formato, áudio AAC presente.
- `ffmpeg`/amostra de frames: primeiro frame útil, primeiro e último planos não pretos, sem keyframe de glitch, aspecto correto, nenhuma imagem cortada grotescamente.
- Trilha/voz: TTS em pt-BR, intensidade normalizada, falas completas, sem cortes; captions com faixa de tempo monotônica e sincronização conferida.
- Personagem: máscara/roupa/ambiente consistentes, sem mutações entre cenas/episódios.
- Editorial: claims com fontes, reconstruções rotuladas, sem falsos depoimentos ou fake archival footage, sem imputações de crimes sem prova.
- Legal: licenças/créditos, material de terceiros revisado, música permitida, marcas d'água preservadas quando exigidas.
- Comercial: não fazer upload social ou anúncio sem aprovação.

Na pré-produção V3, leia os beats em sequência. Confira o gancho na imagem, a mudança introduzida por cada pista, a distinção entre documento e encenação e o desfecho. Verifique também se título, legenda ou corte criam uma imputação que a fala não faz. Separe o resultado dessa leitura do QA do vídeo final.

## Gate por estatuto
`pass`, `pass_with_warnings`, `fail`; `completed` só com `pass` ou `pass_with_warnings` explícito, sem defeitos impeditivos. Salvar `qa_report.json` com evidências automáticas e observações humanas.

## Entrega final
Arquivo MP4 e botão/link de download testado; duração exata; formato; status por etapa; recursos usados; alertas de direitos; sugestão de ajuste sem prometer execução assíncrona. Recusar autoaprovação de publicação final.

## V2 — 04/11/2026
O QA V2 (`fabrica_v2.qa`) grava `qa.json` com ffprobe, duração, moov, quadros, loudness, SRT, movimento e tempo de tela do personagem, tipos de imagem, selos e direitos, fontes, capa e voz fixa. A voz aprovada consta no lock. `completed` requer `pass` ou `pass_with_warnings`. `publicacao_aprovada` permanece `false` na fábrica.
