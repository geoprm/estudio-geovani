# Specs por plataforma

**Conferido em 11/11/2026, a partir do conhecimento consolidado das plataformas até 2026. Não é cópia de documentação
oficial.** Plataformas mudam limites sem aviso: antes de um formato novo (duração longa, resolução alta, carrossel),
confira na central de ajuda da rede e atualize esta tabela com a data.

## Parâmetros comuns (servem para todas)

| Item | Valor seguro |
|---|---|
| Contêiner | MP4 |
| Vídeo | H.264 (High), `yuv420p`, CRF 18–20 ou 8–12 Mbps em 1080p |
| Áudio | AAC, 48 kHz, estéreo, 192 kbps |
| Faststart | `-movflags +faststart` |
| fps | o original (24, 25, 30 ou 60); sem conversão desnecessária |
| Loudness | −14 LUFS integrado, true peak ≤ −1 dBTP (prática de mercado) |

## Por rede

| Rede | Proporção / resolução | Duração (referência) | Observações |
|---|---|---|---|
| Instagram Reels | 9:16, 1080x1920 | até ~3 min | Grade do perfil recorta a capa ao centro. Música da biblioteca do app é licenciada pela plataforma |
| TikTok | 9:16, 1080x1920 | vídeos longos permitidos (minutos) | Interface cobre a base e a direita. Rótulo de IA obrigatório para conteúdo realista gerado por IA |
| YouTube Shorts | 9:16, 1080x1920 | até 3 min | Vídeo vertical curto é classificado como Short automaticamente |
| YouTube | 16:9, 1920x1080 (ou 3840x2160) | longo | Miniatura 1280x720; capítulos na descrição; marcação de conteúdo para crianças quando for o caso |
| Kwai | 9:16, 1080x1920 | curto | Mesmo arquivo do Reels serve |
| App do estúdio | igual ao destino | — | Até 19 MiB por vídeo (maior upload testado: 18,9 MB) |

## Zona segura vertical (prática)

Texto importante entre y ≈ 220 e y ≈ 1500, com ~140 px livres à direita e ~60 px à esquerda (1080x1920). Detalhes na
skill `video-legendas`.

## Histórico de conferências

| Data | O que | Quem |
|---|---|---|
| 11/11/2026 | Tabela inicial | Claude Code (criação da Central) |
