---
name: video-cor-acabamento
description: Corrige e dá acabamento de imagem aos vídeos do Estúdio Geovani. Cobre exposição, balanço de branco, tom de pele, contraste, saturação, look por perfil, aplicação de LUT, nitidez, redução de ruído, retoque leve de pele, granulação e consistência entre planos, com receitas FFmpeg. Use quando a imagem está escura, amarelada, lavada, com ruído ou diferente de um plano para outro, ou para aplicar o visual do perfil.
---

# Cor e acabamento

Ordem que não se inverte: **corrigir** (deixar a imagem certa) → **igualar** (todos os planos iguais) → **estilizar**
(o look do perfil) → **acabar** (nitidez, grão). Estilizar imagem errada só exagera o erro.

## 1. Corrigir

| Problema | Ajuste FFmpeg | Ponto de partida |
|---|---|---|
| Escuro | `eq=brightness=0.04:gamma=1.10` | gamma sobe meios-tons sem estourar o branco |
| Estourado | `curves=all='0/0 0.7/0.62 1/0.94'` | baixa as altas sem mexer nas sombras (o que estourou de vez não volta) |
| Amarelado (luz de casa) | `colorbalance=rs=-0.06:bs=0.06:rm=-0.04:bm=0.04` | puxa para o azul |
| Azulado (sombra, nublado) | `colorbalance=rs=0.05:bs=-0.05` | puxa para o quente |
| Lavado | `eq=contrast=1.08:saturation=1.10` | contraste antes de saturação |
| Saturado demais | `eq=saturation=0.88` | pele primeiro |

**Pele é a referência.** Depois de qualquer ajuste, olhe o rosto: pele não pode ficar laranja, cinza, magenta ou verde. Se
a pele está certa, o resto quase sempre está.

Use `video-montagem-edicao/references/receitas-ffmpeg.md` para o padrão de saída. Exemplo combinado:

```bash
ffmpeg -i in.mp4 -vf "eq=gamma=1.08:contrast=1.06:saturation=1.05,colorbalance=rs=-0.04:bs=0.04" <padrão de saída> corrigido.mp4
```

Teste em um quadro antes do vídeo inteiro: `ffmpeg -ss 3 -i in.mp4 -frames:v 1 -vf "<filtros>" teste.jpg`.

## 2. Igualar planos

Planos gravados em horas ou lugares diferentes precisam parecer o mesmo vídeo. Faça uma folha de contato
(`fps=1/3,scale=270:-2,tile=4x3`) e compare lado a lado. Ajuste cada plano até a pele e o branco baterem com o plano de
referência (o do gancho).

## 3. Look por perfil

| Perfil | Look | Filtros de partida |
|---|---|---|
| @direitaxx | Quente, contraste alto, sol do sertão; amarelo vivo sem pele laranja | `eq=contrast=1.10:saturation=1.08,colorbalance=rh=0.04:gh=0.02` |
| Dr. Geovani | Limpo, neutro-quente, suave; consultório acolhedor | `eq=contrast=1.03:saturation=1.0:gamma=1.04` |
| Arquivo Oculto | Frio nas sombras, âmbar nas luzes, preto profundo, grão de arquivo | `curves=all='0/0.03 0.5/0.47 1/0.95',colorbalance=bs=0.06:rh=0.05,noise=alls=7:allf=t` |
| Princesa Melinda | Desenho: cores saturadas e planas da bíblia visual; não corrigir como vídeo real | — |

LUT (`.cube`): `lut3d=arquivo.cube`. Aplique na imagem já corrigida, com intensidade reduzida se for forte:

```bash
ffmpeg -i corrigido.mp4 -filter_complex "[0:v]split[a][b];[b]lut3d=look.cube[l];[a][l]blend=all_mode=normal:all_opacity=0.6" <padrão> look.mp4
```

LUT só com licença de uso; guarde a origem junto do projeto.

## 4. Retoque leve (rosto do Geovani)

O motor `estudio-gm` tem retoque calibrado por perfil (`beleza.py`: pele 0,40, dentes 0,85), ligado por padrão em
@direitaxx e Dr. Geovani, desligado quando o pedido tiver `retoque = false`. Use o motor. Regra: **retoque que se nota é
retoque demais.** Nunca mudar formato de rosto, corpo ou idade aparente.

## 5. Acabamento

- **Ruído** (gravação noturna): `hqdn3d=2:1.5:3:3` leve, antes da nitidez.
- **Nitidez:** `unsharp=5:5:0.6:5:5:0.0` (só luminância, suave). Nitidez forte cria halo em volta do texto e do rosto.
- **Grão** (Arquivo Oculto): `noise=alls=6:allf=t` depois de tudo. Grão por cima de compressão forte vira chiado: teste a
  versão do app (19 MiB).
- **Upscale** de material pequeno: `scale=1080:-2:flags=lanczos`. Não cria detalhe; só evita borrão maior.

## Checklist

- [ ] Pele natural em todos os planos.
- [ ] Planos iguais entre si (folha de contato conferida).
- [ ] Look do perfil aplicado sobre imagem já corrigida.
- [ ] Sem halo de nitidez, sem preto esmagado escondendo detalhe importante.
- [ ] Versão comprimida do app conferida (grão e gradiente sem faixas).
