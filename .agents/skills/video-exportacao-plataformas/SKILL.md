---
name: video-exportacao-plataformas
description: Exporta os vídeos do Estúdio Geovani no formato certo para cada destino (Reels, TikTok, Shorts, YouTube, Kwai, app do estúdio) e monta o texto do post. Cobre resolução, proporção, fps, codec, bitrate, loudness, faststart, versão do app com até 19 MiB, master de arquivo, nomes de arquivo, legenda do post, hashtags, título e descrição do YouTube e rótulo de IA. Use ao finalizar qualquer vídeo, quando a rede recusa ou piora o arquivo, ou para preparar o pacote do post.
---

# Exportação e pacote do post

## Uma regra

Exporte **uma vez em alta** (master) e derive o resto dele. Nunca exporte a partir de um arquivo já comprimido para rede:
cada recompressão perde qualidade.

## Presets da Central

```bash
python ferramentas/estudio.py exportar <entrada> <saida> --preset <preset> [--enquadrar blur|crop|pad] [--lufs -14]
```

| Preset | Saída | Uso |
|---|---|---|
| `master` | resolução original, CRF 16, AAC 320k | arquivo do estúdio, base de tudo |
| `reels` / `tiktok` / `shorts` | 1080x1920, H.264 High CRF 19, AAC 192k 48 kHz, −14 LUFS, faststart | redes verticais |
| `youtube` | 1920x1080, CRF 18, AAC 256k, −14 LUFS | vídeo longo 16:9 |
| `app` | H.264/AAC, faststart, até 19 MiB (duas passadas) | aba Prontos do app (a recepção já gera) |

O fps segue o original até 60. Material a 25 fps fica a 25; não converta para 30 sem motivo (gera tremido).

Specs e limites de cada rede, com data de conferência: [references/specs-plataformas.md](references/specs-plataformas.md).
**Plataformas mudam regras sem aviso**: confira a referência antes de um formato novo.

## Nome de arquivo

`AAAAMMDD_perfil_titulo-curto_destino.mp4` (sem acento, sem espaço). Ex.: `20261112_direitaxx_ponte-do-rio_reels.mp4`.

## Texto do post (vai em `post` no pacote)

**Legenda (Instagram, TikTok, Kwai):**
1. Primeira linha = gancho escrito (aparece antes do "mais"): até ~125 caracteres.
2. Corpo curto: o que o vídeo prova ou ensina, em 2–4 linhas.
3. Fonte, quando houver dado: "Fonte: IBGE, Censo 2022."
4. Chamada única (salvar, compartilhar, comentar uma pergunta concreta).
5. 3 a 5 hashtags específicas. Hashtag genérica (#viral, #fyp) não ajuda e polui.

**YouTube (longo):** título até ~60 caracteres com a palavra que as pessoas buscam no começo; descrição com resumo nas 2
primeiras linhas, fontes com link, capítulos (`00:00 Introdução`; o primeiro precisa ser 00:00, pelo menos 3 capítulos de
10 s ou mais). Shorts: título curto, `#Shorts` opcional.

**Rótulo de IA:** vídeo gerado ou alterado de modo realista por IA leva a marcação da plataforma ("conteúdo gerado por
IA" no TikTok e no Instagram, "conteúdo alterado ou sintético" no YouTube) **e** `post.rotulo_ia: true` no pacote. O
Arquivo Oculto marca sempre. Em período eleitoral, ver `video-direitos-rotulos`.

**Princesa Melinda:** no YouTube, o vídeo é marcado como "conteúdo para crianças". Sem link externo e sem chamada para
comentar.

## Versão do app

A recepção (`estudio-recepcao`) gera `_app/video_app.mp4` sozinha. Se o vídeo é longo demais para caber com qualidade em
19 MiB (acima de ~3 min em 1080p), a qualidade cai muito: avise no pacote e sugira cortar ou enviar por outro meio.

## Checklist

- [ ] Master guardado.
- [ ] Versão por rede derivada do master, com o preset certo.
- [ ] Loudness medido (−14 LUFS, TP ≤ −1 dBTP) e faststart presente (o QA confere).
- [ ] Nome de arquivo no padrão.
- [ ] Legenda do post com gancho na primeira linha, fonte e no máximo 5 hashtags.
- [ ] Rótulo de IA marcado quando aplicável.
