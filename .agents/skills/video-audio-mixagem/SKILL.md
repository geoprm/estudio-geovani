---
name: video-audio-mixagem
description: Mixa e masteriza o áudio dos vídeos do Estúdio Geovani. Cobre escolha e licença de trilha, efeitos sonoros, ducking da música sob a voz, equalização, loudness por plataforma (LUFS e true peak), limpeza de ruído e receitas FFmpeg com medição em duas passadas. Use ao pôr música ou efeito num vídeo, quando a voz some sob a trilha, o volume varia entre vídeos ou a rede abaixa o som.
---

# Áudio: trilha, efeitos e mixagem

No vídeo curto, **o som é metade da retenção**. Voz inteligível em celular com alto-falante ruim é o primeiro requisito;
trilha e efeito vêm depois.

## Hierarquia da mixagem

1. **Voz** sempre na frente, compreensível até no volume baixo do celular.
2. **Efeitos** pontuam o que se vê (carimbo, virada de página, transição). Curtos e poucos.
3. **Trilha** sustenta o clima, embaixo da voz. Sem voz, ela pode subir.

Referências de nível (aproximadas, a ouvir sempre): voz em torno de −16 LUFS isolada; trilha sob a voz 18–24 dB abaixo dela;
mix final em **−14 LUFS integrado, true peak até −1 dBTP**.

## Loudness por plataforma

| Destino | Alvo prático | Por quê |
|---|---|---|
| YouTube (longo e Shorts) | −14 LUFS, TP ≤ −1 dBTP | O YouTube reduz o volume do que passa de cerca de −14; não aumenta o que está baixo |
| Instagram, TikTok, Kwai | −14 LUFS, TP ≤ −1 dBTP | Não publicam alvo oficial; −14 é o padrão de mercado e evita distorção na conversão |
| App do estúdio | igual ao destino final | O app só mostra; não altera |

Esses alvos são prática de mercado, não promessa das plataformas. O QA da Central aceita de −17 a −11 LUFS.

## Trilha: escolha e licença

- **Música adicionada dentro do app da rede** (biblioteca do Instagram ou do TikTok) é o caminho mais seguro para música
  popular: a licença é da plataforma. O vídeo sai do estúdio sem trilha, ou com trilha baixa e livre, e a orientação do
  pacote diz qual música pôr.
- **Trilha embutida no arquivo** só com licença clara para o uso: trilha própria, biblioteca com licença comercial
  documentada, ou domínio público verificado. Guarde a licença (print ou PDF) junto do pacote e cite em `checagem`.
- Biblioteca de áudio do YouTube: a licença cobre vídeos no YouTube. Para outras redes, confira a licença de cada faixa.
- Música sem licença conferida = `checagem.direitos: pendente` (o vídeo vai como "Prévia privada").
- Arquivo Oculto: **nunca o áudio original de terceiros** (é o que mais derruba vídeo no TikTok), mesmo quando a imagem
  original é usada com crédito (D-111).

Clima por perfil:
- **@direitaxx:** percussão discreta, tensão crescente na prova, respiro no fecho. Nada de trilha épica sobre dado simples.
- **Dr. Geovani:** piano ou violão leve, andamento lento, sem tensão. A trilha acolhe.
- **Arquivo Oculto:** drones graves, ruído de fita, clique de projetor, silêncio usado como efeito.
- **Princesa Melinda:** melodia simples, alegre, volume baixo sob a narração; música cantada só com letra própria.

## Efeitos sonoros

- Um efeito por evento visual que importa: carimbo DOCUMENTADO, virada do placar, número aparecendo.
- Duração de 0,1 a 0,8 s; fade de saída sempre.
- Efeito de "whoosh" em toda transição cansa em 10 s. Use em no máximo 2 ou 3 pontos por vídeo.
- Mesma licença da trilha: própria, livre com licença guardada, ou gerada.

## Receitas FFmpeg

```bash
# 1) Ducking: trilha abaixa sozinha quando a voz fala (sidechain)
ffmpeg -i voz.wav -i trilha.mp3 -filter_complex \
 "[0:a]asplit=2[v1][v2];[1:a]volume=0.35[m];[m][v2]sidechaincompress=threshold=0.03:ratio=10:attack=15:release=350[duck];\
  [v1][duck]amix=inputs=2:duration=first:normalize=0[mix]" -map "[mix]" -ar 48000 mix.wav

# 2) Trilha com entrada e saída suaves, cortada no tamanho do vídeo (D segundos)
ffmpeg -i trilha.mp3 -af "atrim=0:D,afade=t=in:d=1.5,afade=t=out:st=D-2:d=2" trilha_d.wav

# 3) Efeito no tempo exato (carimbo aos 12,4 s)
ffmpeg -i mix.wav -i carimbo.wav -filter_complex \
 "[1:a]adelay=12400|12400,volume=0.8[fx];[0:a][fx]amix=inputs=2:duration=first:normalize=0[o]" -map "[o]" mix_fx.wav

# 4) Mixagem final no vídeo, com loudness em duas passadas
python ferramentas/estudio.py exportar video_com_mix.mp4 final.mp4 --preset reels --lufs -14
```

Medir sem alterar:

```bash
ffmpeg -i final.mp4 -af ebur128=peak=true -f null -   # resumo no fim: I (LUFS), LRA, True peak
```

O `exportar` da Central já faz o `loudnorm` em duas passadas (mede e aplica com os valores medidos), que é mais preciso que
uma passada só.

## Limpeza de ruído

Na voz, use a cadeia da skill `video-narracao-voz`. Em som ambiente de b-roll: `highpass=f=100,afftdn=nf=-22`, ou tire o
som do b-roll e deixe só trilha e voz. Ruído forte e constante (gerador, vento) não se conserta bem: corte o som ou regrave.

## Checklist

- [ ] Voz compreensível no alto-falante do celular, em volume baixo.
- [ ] Trilha não compete com a voz (ducking ativo).
- [ ] Mix final entre −15 e −13 LUFS, true peak ≤ −1 dBTP (medido).
- [ ] Nenhum estalo nas emendas (fades de 10–20 ms).
- [ ] Licença de cada música e efeito anotada no pacote, ou música indicada para pôr no app da rede.
