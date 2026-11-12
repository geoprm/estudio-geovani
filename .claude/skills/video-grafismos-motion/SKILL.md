---
name: video-grafismos-motion
description: Cria grafismos e animação gráfica para os vídeos do Estúdio Geovani. Cobre título de gancho, palavra-chave na tela, lower third, selos de checagem (DOCUMENTADO, SEM PROVA, FALSO, RECONSTITUIÇÃO IA, FONTE), barra de progresso, Ken Burns em foto e documento, destaque em documento, contador e placar, com receitas FFmpeg (drawtext, overlay, zoompan) e regras de hierarquia, tempo de leitura e zona segura. Use para pôr texto, selo, crédito ou movimento em cima do vídeo.
---

# Grafismos e motion

Grafismo existe para **fazer entender mais rápido**. Se não acelera a compreensão nem prova nada, sai.

## Hierarquia de texto na tela (vertical)

| Nível | Uso | Tamanho em 1080x1920 | Duração mínima |
|---|---|---|---|
| Gancho | pergunta ou número do início | 90–130 px, caixa alta, até 5 palavras | todo o primeiro plano |
| Palavra-chave | reforço do que está sendo dito | 70–90 px | 1,2 s |
| Legenda | a fala (skill `video-legendas`) | 62–72 px | — |
| Selo / fonte | origem do fato, tipo de material | 34–44 px | o plano inteiro do fato |
| Lower third | quem fala | 44 / 30 px (nome / cargo) | 3–4 s, uma vez |

Nunca mais de **dois níveis** ao mesmo tempo além da legenda. Tudo dentro da zona segura (`video-legendas`, seção 4).

## Selos de checagem (padrão do estúdio)

O selo diz ao público **que tipo de material** ele está vendo. É obrigação editorial, não enfeite.

| Selo | Quando | Perfis |
|---|---|---|
| `FONTE: veículo, data` | todo fato, número ou citação na tela | todos |
| `DOCUMENTADO` | afirmação com documento primário mostrado | arquivo, direitaxx |
| `SEM PROVA` | alegação sem documento que a sustente | arquivo |
| `FALSO` | alegação desmentida por documento | arquivo |
| `INTERPRETAÇÃO` / `ANÁLISE` | leitura do autor, não fato | arquivo, direitaxx |
| `RECONSTITUIÇÃO IA` | cena encenada ou gerada por IA | todos |
| `ILUSTRAÇÃO` | imagem ilustrativa, não o fato | todos |
| `IMAGEM: origem` | crédito de imagem real de terceiro (D-111) | arquivo |

Selo fica no canto superior esquerdo (x ≥ 60, y ≥ 220), fundo sólido com 85% de opacidade, legível no celular.

## Receitas FFmpeg

```bash
# Texto de gancho centralizado nos 2,5 primeiros segundos (fonte do motor)
ffmpeg -i in.mp4 -vf "drawtext=fontfile='fontes/Anton_400Regular.ttf':text='FALA POUCO AOS 2?':fontsize=110:fontcolor=white:borderw=8:bordercolor=black:x=(w-text_w)/2:y=330:enable='lt(t,2.5)'" <padrão de saída> gancho.mp4

# Selo de fonte com caixa de fundo, do segundo 12 ao 18
ffmpeg -i in.mp4 -vf "drawtext=fontfile='fontes/Montserrat_800ExtraBold.ttf':text='FONTE\: IBGE, 2022':fontsize=38:fontcolor=white:box=1:boxcolor=0x0D0E10@0.85:boxborderw=18:x=60:y=230:enable='between(t,12,18)'" <padrão> selo.mp4

# Lower third (PNG transparente pronto) entrando com fade de 0,3 s aos 1,5 s e saindo aos 5 s
ffmpeg -i in.mp4 -loop 1 -t 5 -i lower.png -filter_complex \
 "[1:v]format=rgba,fade=t=in:st=1.5:d=0.3:alpha=1,fade=t=out:st=4.7:d=0.3:alpha=1[l];[0:v][l]overlay=0:H-h-460:eof_action=pass" <padrão> lower.mp4

# Barra de progresso fina no topo (cor do perfil); troque 60 pela duração do vídeo em segundos
ffmpeg -i in.mp4 -filter_complex "color=c=0xFFD400:s=1080x10[bar];[0:v][bar]overlay=x='-w+w*t/60':y=200:shortest=1" <padrão> barra.mp4
```

**Sempre passe `fontfile=` no `drawtext`.** No FFmpeg desta máquina (9.0.2, Windows) não há configuração de fontes do
sistema: `drawtext` sem `fontfile` falha com "Fontconfig error" e o processo cai (conferido em 12/11/2026).

Escape no `drawtext`: dois-pontos vira `\:`, apóstrofo é problema (troque por ’), vírgula dentro de `enable` exige aspas
simples em volta da expressão. Texto longo ou com acento delicado: gere um PNG com o texto (ver abaixo) e use `overlay`.

## Ken Burns em foto e documento

```bash
# Zoom lento de 100% a 115% em 5 s, centralizado (upscale antes evita tremido)
ffmpeg -loop 1 -i doc.jpg -t 5 -vf "scale=4320:-2,zoompan=z='min(zoom+0.0010,1.15)':d=150:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,format=yuv420p" -c:v libx264 -crf 18 kb.mp4

# Panorâmica de cima para baixo num documento comprido
ffmpeg -loop 1 -i doc_longo.jpg -t 6 -vf "scale=1080:-2,crop=1080:1920:0:'(ih-1920)*t/6',format=yuv420p" -c:v libx264 -crf 18 pan.mp4
```

Documento: comece no detalhe que prova (a data, a assinatura, a linha) e abra para o todo, ou o contrário. Nunca mova
rápido demais para ler: o público precisa de **1 s para cada 4–5 palavras** visíveis.

## Destaque em documento

Retângulo marca-texto sobre a linha que prova (semitransparente, cor do perfil):

```bash
ffmpeg -i doc.mp4 -vf "drawbox=x=120:y=860:w=840:h=64:color=0xFFD400@0.35:t=fill:enable='gte(t,1.2)'" <padrão> destaque.mp4
```

Nunca mude o conteúdo do documento. Destacar é permitido; editar o texto, apagar carimbo ou "limpar" o papel não é.

## Texto como imagem (quando o drawtext não serve)

Para tipografia com várias cores, quebra de linha controlada ou caracteres especiais, gere um PNG transparente 1080x1920
com o texto e sobreponha com `overlay`. No estúdio, o motor `estudio-gm` faz isso com Pillow (ambiente `.venv`). Sem
Pillow, um SVG convertido pelo FFmpeg também serve.

## Movimento

- Entradas de 0,2–0,35 s, saída mais rápida que a entrada.
- Um elemento animando por vez.
- Movimento de câmera em foto (Ken Burns) sempre lento e contínuo; nunca zoom e pan opostos no mesmo plano.
- Arquivo Oculto: movimentos de arquivo (projetor, papel, lanterna); nada de "neon" ou transição de vídeo de casamento.

## Checklist

- [ ] Todo fato na tela tem selo de fonte.
- [ ] Cena encenada ou gerada tem RECONSTITUIÇÃO IA ou ILUSTRAÇÃO.
- [ ] Texto dentro da zona segura e legível no celular (teste a 30% do tamanho).
- [ ] Tempo de leitura respeitado (1 s para cada 4–5 palavras).
- [ ] Fontes e cores do perfil.
- [ ] Documento destacado, nunca alterado.
