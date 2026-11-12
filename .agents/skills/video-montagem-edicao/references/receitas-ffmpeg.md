# Receitas FFmpeg de montagem

Testadas com FFmpeg 9.0.2 (gyan.dev, Windows). No PowerShell, troque `\` de quebra de linha por crase (`) ou escreva numa
linha só. Caminho com espaço vai entre aspas.

Padrão de saída para rede (use em toda receita que recodifica):

```
-c:v libx264 -preset slow -crf 19 -profile:v high -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart
```

## Cortar

```bash
# Corte exato (recodifica): de 12,4 s a 31,0 s
ffmpeg -ss 12.4 -to 31.0 -i in.mp4 -c:v libx264 -crf 18 -preset fast -c:a aac -b:a 192k corte.mp4

# Corte rápido sem recodificar (só começa em keyframe: pode adiantar alguns quadros)
ffmpeg -ss 12.4 -to 31.0 -i in.mp4 -c copy -avoid_negative_ts make_zero corte_rapido.mp4
```

Use o corte exato para o trabalho final. O rápido serve para separar brutos.

## Juntar

```bash
# Clipes com o mesmo codec, resolução e fps: lista + concat demuxer (sem recodificar)
# lista.txt:
#   file 'c1.mp4'
#   file 'c2.mp4'
ffmpeg -f concat -safe 0 -i lista.txt -c copy junto.mp4

# Clipes diferentes: concat filter (recodifica e iguala)
ffmpeg -i c1.mp4 -i c2.mp4 -filter_complex \
 "[0:v]scale=1080:1920,setsar=1,fps=30[v0];[1:v]scale=1080:1920,setsar=1,fps=30[v1];[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" \
 -map "[v]" -map "[a]" <padrão de saída> junto.mp4
```

## Transição (fade cruzado de 0,3 s)

`offset` = duração do primeiro clipe − duração da transição.

```bash
# c1 tem 8,0 s → offset 7,7
ffmpeg -i c1.mp4 -i c2.mp4 -filter_complex \
 "[0:v][1:v]xfade=transition=fade:duration=0.3:offset=7.7[v];[0:a][1:a]acrossfade=d=0.3[a]" \
 -map "[v]" -map "[a]" <padrão de saída> com_fade.mp4
```

Outras transições do `xfade`: `fadeblack`, `slideleft`, `smoothup`, `circleopen`, `zoomin`. Use pouco.

## Reenquadrar 16:9 → 9:16

```bash
# Crop central (rosto no meio)
ffmpeg -i h.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1" <padrão> v.mp4

# Crop deslocado (pessoa à esquerda): x de 0 (esquerda) a in_w-out_w (direita)
ffmpeg -i h.mp4 -vf "scale=-2:1920,crop=1080:1920:(in_w-out_w)*0.25:0,setsar=1" <padrão> v.mp4

# Quadro inteiro sobre fundo desfocado da própria imagem
ffmpeg -i h.mp4 -filter_complex \
 "[0:v]split[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:2,eq=brightness=-0.08[b];[fg]scale=1080:-2[f];[b][f]overlay=(W-w)/2:(H-h)/2,setsar=1[v]" \
 -map "[v]" -map 0:a? <padrão> v.mp4
```

## Tela dividida vertical (prova em cima, pessoa embaixo)

```bash
ffmpeg -i prova.png -i fala.mp4 -filter_complex \
 "[0:v]scale=1080:840:force_original_aspect_ratio=decrease,pad=1080:840:(ow-iw)/2:(oh-ih)/2:color=0x0D0E10[top];\
  [1:v]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080[bot];\
  [top][bot]vstack=inputs=2,setsar=1[v]" -map "[v]" -map 1:a -shortest <padrão> dividida.mp4
```

O motor `estudio-gm` faz uma tela dividida mais elaborada (faixa dourada, recorte de pessoa, legenda). Prefira o motor
para @direitaxx e Dr. Geovani.

## Picture-in-picture (rosto no canto)

```bash
ffmpeg -i fundo.mp4 -i rosto.mp4 -filter_complex \
 "[1:v]scale=360:-2[p];[0:v][p]overlay=W-w-48:H-h-420" -map 0:a? <padrão> pip.mp4
```

`H-h-420` deixa o rosto acima da área que a interface do TikTok/Reels cobre embaixo.

## Velocidade

```bash
# 1,25× vídeo e áudio (atempo aceita 0,5 a 2,0 por instância)
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=PTS/1.25[v];[0:a]atempo=1.25[a]" -map "[v]" -map "[a]" <padrão> rapido.mp4

# Câmera lenta 0,5× só do vídeo (sem áudio)
ffmpeg -i in.mp4 -vf "setpts=PTS/0.5" -an <padrão> lento.mp4
```

## Zoom de corte (jump cut alternado)

```bash
# 112% centralizado, para alternar com o plano a 100%
ffmpeg -i in.mp4 -vf "scale=iw*1.12:-2,crop=1080:1920" <padrão> zoom112.mp4
```

## Emendas sem estalo

Ao juntar áudio cortado, aplique `afade=t=in:d=0.015` no início e `afade=t=out:st=<fim-0.015>:d=0.015` no fim de cada
trecho, ou use `acrossfade=d=0.02` entre trechos.

## Conferir quadro a quadro

```bash
ffmpeg -ss 5.0 -i saida.mp4 -frames:v 1 -q:v 2 q5.jpg        # um quadro
ffmpeg -i saida.mp4 -vf "fps=1/5,scale=270:-2,tile=4x3" -frames:v 1 folha.jpg   # folha de contato (1 quadro a cada 5 s)
```

Olhe a folha de contato antes de entregar: ela mostra texto cortado, plano repetido e tela preta em um relance.
