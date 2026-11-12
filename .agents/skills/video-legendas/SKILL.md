---
name: video-legendas
description: Cria e corrige legendas para os vídeos do Estúdio Geovani. Cobre transcrição automática (Whisper local do motor), revisão contra a fala real, quebra de linha e tempo de leitura em português, estilo por perfil, legenda palavra a palavra, zonas seguras do Reels, TikTok e Shorts, arquivos SRT e ASS e legenda queimada com FFmpeg. Use quando o vídeo precisa de legenda, quando a legenda está errada ou fora de tempo, ou para entregar o SRT junto do vídeo.
---

# Legendas

A maioria assiste vídeo curto **sem som**. A legenda é o roteiro para quem não ouve. E legenda errada é desinformação
com a sua cara.

## 1. Transcrever

O motor tem transcrição local em `C:\Projetos\ARQUIVO OCULTO\estudio-gm\asr\transcribe.mjs` (Node). Ela gera os tempos por
palavra. Alternativa em Python: `faster-whisper` com modelo `small` ou `medium`, `language="pt"`, `word_timestamps=True`.

A transcrição é **rascunho**. Revise sempre:
- nomes próprios, siglas, números e unidades (o modelo inventa grafia);
- palavra que o modelo "corrigiu" para outra parecida;
- regionalismos do sertão: escreva como foi dito, sem "corrigir" o falante;
- nunca acrescente na legenda o que não foi dito, e nunca suavize o que foi dito.

## 2. Regras de texto

| Regra | Valor |
|---|---|
| Linhas por legenda | 1 a 2 (vertical: prefira 1 linha grande ou 2 curtas) |
| Caracteres por linha | até ~32 no vertical, ~42 no horizontal |
| Tempo mínimo na tela | 0,8 s (legenda palavra a palavra: 0,25 s por palavra) |
| Velocidade de leitura | até ~17 caracteres por segundo |
| Quebra | entre unidades de sentido: não separe artigo do substantivo nem preposição do complemento |
| Pontuação | sem ponto final no fim de cada legenda; mantenha interrogação e exclamação |
| Números | algarismos na legenda ("46,8%"), mesmo que a fala diga por extenso |

## 3. Estilo por perfil

Fonte e cores vêm de `config/perfis/<id>.json` (e do `perfis.py` do motor, que é a fonte da verdade):

| Perfil | Fonte | Destaque da palavra-chave | Contorno |
|---|---|---|---|
| @direitaxx | Montserrat ExtraBold, branco | amarelo-girassol `#FFD400` | preto, grosso |
| Dr. Geovani | Montserrat Bold, branco | dourado `#E5A93C` | sem contorno, sombra suave |
| Arquivo Oculto | Montserrat ExtraBold, marfim `#F1E9D6` | dourado `#D6A854` | preto |
| Princesa Melinda | a definir (arredondada, alto contraste, tamanho grande) | — | — |

Destaque **uma** palavra por legenda, a que carrega o sentido (o número, o nome, o verbo da virada).

## 4. Zona segura (vertical 1080x1920)

A interface das redes cobre parte da tela: botões à direita, legenda do post e nome embaixo, abas em cima. Margens
práticas para manter texto importante visível em Reels, TikTok e Shorts ao mesmo tempo:

- topo: livre a partir de ~220 px;
- base: nada importante abaixo de ~1500 px (os últimos ~420 px são da interface);
- direita: deixe ~140 px livres (coluna de botões);
- esquerda: ~60 px.

Posição recomendada da legenda: centro vertical entre 1150 e 1450 px. Essas margens são prática conferida em 11/11/2026; as
interfaces mudam. Na dúvida, olhe uma captura de tela da rede por cima do quadro.

## 5. Arquivos

- **SRT:** vai no pacote (`arquivos.legendas`) para quem quiser subir a legenda separada (YouTube aceita e indexa).
- **ASS:** para legenda queimada com estilo (fonte, cor, contorno, posição, destaque por palavra).

Exemplo de cabeçalho ASS para 1080x1920 (@direitaxx):

```
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,Montserrat ExtraBold,72,&H00FFFFFF,&H0000D4FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,2,2,60,140,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.20,0:00:02.10,Base,,0,0,0,,Quase {\c&H0000D4FF&}METADE{\c&H00FFFFFF&} das casas
```

Cores ASS são `&HAABBGGRR` (ordem invertida): `#FFD400` vira `&H0000D4FF`. `Alignment 2` = centro embaixo; `MarginV 560`
põe a legenda acima da área da interface.

## 6. Queimar a legenda (FFmpeg)

```bash
# ASS com as fontes do motor (caminho da pasta de fontes)
ffmpeg -i video.mp4 -vf "ass=legenda.ass:fontsdir=C\\:/Projetos/ARQUIVO OCULTO/estudio-gm/fontes" <padrão de saída> legendado.mp4

# SRT simples com estilo forçado
ffmpeg -i video.mp4 -vf "subtitles=legenda.srt:force_style='FontName=Montserrat ExtraBold,FontSize=18,Outline=3,MarginV=90'" <padrão> legendado.mp4
```

No Windows, o filtro `ass`/`subtitles` exige escapar o `:` do drive (`C\\:/...`). Se der erro de caminho, copie o `.ass`
para a pasta atual e use só o nome do arquivo. `<padrão de saída>` está em `video-montagem-edicao/references/receitas-ffmpeg.md`.

## Checklist

- [ ] Transcrição revisada palavra por palavra contra o áudio.
- [ ] Nenhuma legenda muda o sentido do que foi dito.
- [ ] Até 2 linhas, até ~32 caracteres por linha no vertical.
- [ ] Dentro da zona segura (conferido sobre captura da interface).
- [ ] Uma palavra de destaque por legenda, na cor do perfil.
- [ ] SRT final no pacote, gerado depois do corte final.
