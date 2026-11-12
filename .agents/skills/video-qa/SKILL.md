---
name: video-qa
description: Faz o controle de qualidade técnico e editorial dos vídeos do Estúdio Geovani antes de entregar. Roda o QA automático da Central (ffprobe e FFmpeg: formato, codec, tela preta, imagem congelada, silêncio, loudness, true peak, faststart) e conduz a revisão humana assistida (quadros, legenda contra a fala, fatos e fontes, selos, direitos, pessoas, regras do perfil), com status pass, pass_with_warnings ou fail. Use antes de todo pacote video_pronto e sempre que alguém perguntar se o vídeo está pronto.
---

# QA de vídeo

O QA responde uma pergunta: **o Geovani pode postar isto sem se arrepender?** Técnica é metade; a outra metade é verdade,
direito e respeito às pessoas.

## Status (mesmo vocabulário do motor e do app)

- `pass`: nada a corrigir.
- `pass_with_warnings`: entregável; cada aviso está explicado no pacote (`orientacoes` ou `checagem.observacoes`).
- `fail`: não entra. Corrija e rode de novo.

Nunca marque `pass` sem ter rodado as duas partes abaixo.

## Parte 1 — técnica (automática)

```bash
python ferramentas/estudio.py qa video.mp4 --max 110 --json qa_tecnico.json      # vertical
python ferramentas/estudio.py qa video_16x9.mp4 --horizontal                      # YouTube longo
```

| Check | Falha (erro) | Aviso |
|---|---|---|
| legível / tem vídeo / duração | arquivo não abre, sem faixa de vídeo, < 1 s | — |
| tela_preta | > 90% do vídeo preto | — |
| preto_no_inicio, trechos_pretos | — | começa no preto; > 1 s de preto no total |
| imagem_congelada | — | trecho parado ≥ 3 s (aceitável em still animado de propósito: explique) |
| silencio | — | silêncio ≥ 2 s |
| loudness / true_peak | — | fora de −17 a −11 LUFS; pico acima de −1 dBTP |
| codec, pix_fmt, áudio | — | não H.264 / yuv420p / AAC |
| proporcao_9x16, resolucao, fps | — | fora de 9:16, abaixo de 1080 de largura, fps fora de 24–60 |
| duracao_formato | — | acima do máximo do formato |
| faststart | — | moov no fim do arquivo |

A recepção roda este QA de novo em todo pacote e recusa `fail`.

## Parte 2 — revisão (você olha e ouve)

### Imagem
Gere a folha de contato e **olhe**:
```bash
ffmpeg -i video.mp4 -vf "fps=1/2,scale=270:-2,tile=5x4" -frames:v 1 folha.jpg
```
- [ ] Texto cortado, fora da zona segura ou sobreposto à legenda.
- [ ] Erro de grafia em título, selo, legenda ou capa.
- [ ] Plano repetido, quadro preto no meio, salto estranho.
- [ ] Marca d'água de terceiro, logotipo de outro canal.
- [ ] Rosto de paciente, de criança de terceiros ou de pessoa sem autorização.

### Som
- [ ] Voz compreensível em volume baixo, sem estalo nas emendas, trilha sem cobrir a voz.
- [ ] Nenhum áudio original de terceiro sem licença (no Arquivo Oculto, nunca).

### Legenda
- [ ] Ouça o vídeo inteiro lendo a legenda. Cada palavra bate com a fala.
- [ ] Nomes, números e siglas corretos.

### Verdade
- [ ] Cada fato, número, data e citação tem fonte anotada e foi conferido na fonte (não no resumo de outra IA).
- [ ] O gancho é fiel ao dado.
- [ ] Nenhum corte muda o sentido do que alguém disse.
- [ ] Selos certos: FONTE em todo fato; RECONSTITUIÇÃO IA ou ILUSTRAÇÃO em toda cena encenada ou gerada.
- [ ] Arquivo Oculto: fato, alegação, interpretação e falso separados; ninguém acusado sem documento.

### Perfil
- [ ] Tom, cores, fontes e assinatura conforme `config/perfis/<id>.json`.
- [ ] Dr. Geovani: sem diagnóstico pelo vídeo, sem promessa de cura, sem dado clínico sem fonte, sem paciente.
- [ ] Princesa Melinda: nada assustador, perigoso de imitar ou com dado pessoal da criança.

### Direitos e rótulos
- [ ] Origem e licença de cada imagem, trecho e música (`video-direitos-rotulos`).
- [ ] Pendência de direito = versão "Prévia privada".
- [ ] Rótulo de IA quando aplicável.

## Registro

Grave o resultado no pacote: `qa.status` e, se houver, `qa.relatorio` com o JSON técnico. Avisos aceitos vão explicados em
`checagem.observacoes`. Arquivo Oculto: siga também o QA V2 do motor (`estudio-gm/.claude/skills/arquivo-oculto-qa`).

## Erros que o QA existe para pegar

- Legenda "corrigida" pelo transcritor que mudou a palavra dita.
- Número no gancho arredondado para cima.
- Prévia privada entregue como pública.
- Vídeo que começa com 1 s de preto (a rede corta a retenção ali).
- Trilha com Content ID que derruba o vídeo depois de postado.
