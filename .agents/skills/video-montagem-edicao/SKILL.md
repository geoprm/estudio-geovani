---
name: video-montagem-edicao
description: Monta e corta vídeo para os perfis do Estúdio Geovani com ritmo de rede social. Cobre linha do tempo, escolha de takes, corte seco e corte no movimento, J-cut e L-cut, jump cut, b-roll, reenquadramento 16:9 para 9:16, velocidade, transições e receitas FFmpeg testadas para cortar, juntar, sobrepor e reenquadrar. Use ao editar material gravado, montar planos gerados ou corrigir um vídeo que está lento ou confuso.
---

# Montagem e edição

Montar é decidir **o que a pessoa vê a cada segundo e por quê**. O roteiro diz o que contar; a montagem decide o ritmo.

## Princípios de corte para vídeo curto

1. **Corte quando a informação acabou, não quando a frase acabou.** Respiração, "é...", "então" e repetição saem.
2. **Corte no movimento.** Mão que aponta, cabeça que vira, objeto que entra: o corte some dentro do gesto.
3. **J-cut e L-cut.** O som do próximo plano entra antes da imagem (J) ou o som do anterior continua sobre a próxima imagem
   (L). Faz a narração fluir por cima do b-roll sem solavanco.
4. **Jump cut com intenção.** No depoimento, o salto entre frases é aceito se o enquadramento muda de leve (zoom de
   105–115% alternado). Dois planos idênticos colados parecem erro.
5. **Imagem nova a cada 2–4 s** no vertical. Se o plano precisa durar mais, ele precisa de movimento (zoom lento, grafismo,
   Ken Burns).
6. **O primeiro quadro é o gancho.** Nada de preto, logo ou respiro antes da primeira fala.
7. **Sentido intocável.** Nunca junte trechos para fazer alguém dizer o que não disse. Corte que muda o sentido é proibido
   em todos os perfis.

## Fluxo

1. **Organize:** brutos em uma pasta, renomeados `AAAAMMDD_cena_take.mp4`. Leia duração, fps e áudio com
   `python ferramentas/estudio.py qa <arquivo>` ou ffprobe.
2. **Transcreva** (`video-legendas`) e marque entrada e saída das frases boas.
3. **Corte bruto (assembly):** só a fala, na ordem do roteiro, sem enfeite. Meça a duração. Se passou do alvo, corte
   **ideias**, não sílabas.
4. **Corte fino:** tire respirações, ajuste J/L, alterne enquadramento, insira b-roll onde a fala cita algo visível.
5. **Camadas:** grafismos (`video-grafismos-motion`), cor (`video-cor-acabamento`), som (`video-audio-mixagem`) e legenda
   (`video-legendas`), **nesta ordem**. Legenda por último, porque o corte muda o tempo.
6. **Exporte e confira** (`video-exportacao-plataformas`, `video-qa`).

Para @direitaxx e Dr. Geovani, o motor `C:\Projetos\ARQUIVO OCULTO\estudio-gm` já faz o fluxo inteiro (preparar.py →
ritmo.py → videos/<id>.py → finalizar.py), com tela dividida, depoimento, legenda e retoque. Use o motor; estas regras são
o critério para julgar o resultado.

## Decisões frequentes

| Situação | Faça |
|---|---|
| Material 16:9 para Reels/TikTok | Rosto no centro: crop. Cena larga ou texto nas bordas: fundo desfocado (`--enquadrar blur`). Nunca esticar. |
| Fala longa sem imagem de apoio | Alterne zoom 100/112%, palavra-chave na tela, um b-roll a cada ideia. |
| Take com erro no meio da frase boa | Corte no ponto de respiração mais próximo; se não houver, use b-roll por cima (L-cut). |
| Vídeo acima da duração | Corte o bloco de contexto primeiro, depois exemplos repetidos. Gancho e prova ficam. |
| Ritmo arrastado no meio | Acelere o b-roll (até 1,25× sem áudio), encurte pausas para 0,15–0,25 s. |
| Transição | Corte seco é o padrão. Transição só com motivo (mudança de tempo ou lugar), até 0,3 s. |

## Receitas FFmpeg

Comandos testados (FFmpeg 9.0.2): [references/receitas-ffmpeg.md](references/receitas-ffmpeg.md). Inclui cortar sem e com
recodificação, juntar clipes com fade, reenquadrar 16:9 → 9:16, tela dividida, picture-in-picture, velocidade e zoom.

Atalho da Central para reenquadrar e exportar:

```bash
python ferramentas/estudio.py exportar bruto_16x9.mp4 saida_9x16.mp4 --preset reels --enquadrar blur
```

## Checklist da montagem

- [ ] Primeiro quadro já é o gancho.
- [ ] Nenhum plano parado acima de 4 s sem movimento.
- [ ] Nenhuma frase cortada de modo que mude o sentido.
- [ ] Duração dentro do formato.
- [ ] Som contínuo nos cortes (sem estalo: fade de 10–20 ms nas emendas de áudio).
- [ ] Legenda refeita depois do corte final.
