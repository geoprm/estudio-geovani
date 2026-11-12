---
name: video-capas-miniaturas
description: Cria capas verticais (Reels, TikTok, Shorts, app do estúdio) e miniaturas do YouTube para os perfis do Estúdio Geovani. Cobre escolha do quadro, texto de capa de até 4 palavras, contraste, recorte para a grade do perfil, tamanhos e formatos, teste de leitura em tamanho pequeno e receitas FFmpeg. Use ao finalizar um vídeo, quando a capa está ilegível ou quando a grade do perfil está desorganizada.
---

# Capas e miniaturas

A capa decide o clique na grade do perfil e na busca. A miniatura do YouTube decide quase tudo no vídeo longo.

## Tamanhos

| Peça | Tamanho | Observação |
|---|---|---|
| Capa vertical (Reels, TikTok, Shorts, app) | 1080x1920 JPG | a grade do Instagram mostra o centro em recorte mais curto: texto no **meio** |
| Recorte da grade do Instagram | área central ~1080x1440 | conferido em 11/11/2026; confira na rede |
| Miniatura do YouTube | 1280x720 JPG, até 2 MB | limite tradicional da plataforma; confira no YouTube Studio |
| Capa do app do estúdio | a mesma vertical | a Central converte para JPG leve |

## Composição

1. **Um assunto.** Rosto com expressão clara, o objeto da prova ou o documento. Nunca uma colagem de cinco coisas.
2. **Até 4 palavras** de texto, que **completam** a imagem, não repetem. Imagem do buraco + "3 ANOS ASSIM".
3. **Contraste:** texto claro com contorno ou faixa escura; testar em cima da imagem real.
4. **Teste do polegar:** reduza a capa a 15% (162x288) e veja se ainda se lê. Se não lê, não serve.
5. **Consistência:** o mesmo lugar do texto e a mesma família de fonte em todas as capas do perfil. A grade vira identidade.

## Por perfil

| Perfil | Capa |
|---|---|
| @direitaxx | Foto real do assunto, texto Anton/Montserrat Black branco com uma palavra em `#FFD400`; selo de fonte pequeno se houver número |
| Dr. Geovani | Geovani acolhedor ou cena de família (sem paciente), fundo marinho `#030B1E`, texto Playfair em dourado `#E5A93C` |
| Arquivo Oculto | Documento ou o Arquivista na sombra, preto profundo, texto Anton marfim, número do episódio; nunca pessoa real de frente |
| Princesa Melinda | A personagem com expressão alegre, cenário da história, título curto em fonte arredondada; nada de rosto real |

Capa não promete o que o vídeo não tem. Capa sensacionalista no Dr. Geovani fere a ética profissional.

## Receitas

```bash
# Quadro escolhido (segundo 3,2) como base de capa
python ferramentas/estudio.py capa video.mp4 base.jpg --segundo 3.2

# Quadro automático mais representativo (filtro thumbnail)
python ferramentas/estudio.py capa video.mp4 base.jpg

# Texto de capa com faixa escura atrás (meio da tela, dentro do recorte da grade)
ffmpeg -i base.jpg -vf "drawbox=x=0:y=820:w=iw:h=280:color=black@0.55:t=fill,drawtext=fontfile='fontes/Anton_400Regular.ttf':text='3 ANOS ASSIM':fontsize=150:fontcolor=white:x=(w-text_w)/2:y=860" -q:v 2 capa.jpg

# Miniatura do YouTube a partir de quadro 16:9
ffmpeg -ss 41 -i video_16x9.mp4 -frames:v 1 -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720" -q:v 2 thumb.jpg

# Teste do polegar
ffmpeg -i capa.jpg -vf scale=162:-2 teste_polegar.png
```

Para escolher o quadro, gere uma folha de contato (`fps=1,scale=216:-2,tile=5x4`) e escolha olhando. Olho fechado, boca
torta ou borrão de movimento = outro quadro.

## Entrega

A capa vai no pacote como `arquivos.capa` (JPG ou PNG 1080x1920). Sem capa, a Central escolhe um quadro automático, que é
pior que uma capa feita.

## Checklist

- [ ] Um assunto, até 4 palavras, legível a 15%.
- [ ] Texto no centro (recorte da grade do Instagram).
- [ ] Fonte e cor do perfil.
- [ ] Capa fiel ao conteúdo, sem rosto de paciente, criança de terceiros ou pessoa real exposta.
