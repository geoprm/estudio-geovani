---
name: video-narracao-voz
description: Prepara e produz narração para os vídeos do Estúdio Geovani. Cobre texto escrito para o ouvido, marcação de pausas e pronúncia, direção de voz por perfil, gravação pelo celular, TTS local com Kokoro (vozes em português, incluindo a voz aprovada do Arquivista), cadeia de tratamento de voz no FFmpeg e sincronia com a imagem. Use ao escrever ou gravar locução, gerar voz sintética ou corrigir uma narração abafada, robótica ou fora de ritmo.
---

# Narração e voz

## 1. Texto para o ouvido (não para o olho)

- Frase curta: uma ideia por frase, **até 15–18 palavras**. Frase longa é onde o TTS tropeça e o ouvinte se perde.
- Ordem direta: sujeito, verbo, complemento. A informação nova vai no fim da frase, onde a voz cai naturalmente.
- Número por extenso quando ajuda a fala: "mil novecentos e sessenta e dois", "quarenta e seis vírgula oito por cento".
- Sigla: escreva como se fala na primeira vez ("Fê-Bê-I", "IBGE" soletrado, "CIA" como "cê-i-á"). Ou use o campo `tts`
  separado do texto de legenda (padrão do motor do Arquivo Oculto: `fala` para a legenda, `tts` para a pronúncia).
- Nome estrangeiro: escreva a pronúncia aproximada no `tts` e teste ouvindo.
- Pausas: vírgula ≈ 0,2 s, ponto ≈ 0,4 s, reticências ≈ 0,6 s. Pausa dramática maior se faz na montagem, não no texto.
- Leia em voz alta antes de gravar. Onde você tropeçar, a voz vai tropeçar.

Ritmo: **2,4 a 2,8 palavras por segundo** no vertical. Meça: `palavras ÷ duração`. Fora disso, ajuste o texto, não a
velocidade da voz (acelerar acima de 1,1× soa artificial).

## 2. Direção por perfil

| Perfil | Voz | Energia | Cuidado |
|---|---|---|---|
| @direitaxx | Geovani, gravada | Firme, ritmo de conversa na praça | Ênfase no dado, não no grito |
| Dr. Geovani | Geovani, gravada | Calma, sorriso na voz, ritmo mais lento (2,3–2,5 p/s) | Nada de tom de alarme em sinal de alerta |
| Arquivo Oculto | `arquivista-v2-c` (Kokoro local, aprovada em 04/11/2026) | Grave, pausada, intrigante | Não trocar a voz sem aprovação do Geovani; parâmetros no lock do perfil V2 |
| Princesa Melinda | **a decidir pelo Geovani** (TTS, ele, ou dubladora com contrato) | Calorosa, expressiva | Nunca clonar a voz da criança; ver `video-animacao-infantil` |

## 3. Gravação pelo celular (guia para o Geovani)

- Ambiente pequeno com pano (quarto com cama e cortina) soa melhor que sala vazia.
- Celular a um palmo da boca, levemente de lado (evita o estouro do "p" e do "b").
- Microfone de lapela barato melhora mais que qualquer filtro.
- Grave 3 s de silêncio no início: servem de perfil de ruído.
- Errou: pausa, respira e repete a frase inteira. Corta-se depois.

## 4. TTS local (Kokoro)

O estúdio usa Kokoro (modelo aberto, Apache-2.0) rodando local, sem custo. Vozes em português brasileiro do Kokoro v1.0:
`pf_dora` (feminina), `pm_alex` e `pm_santa` (masculinas). A voz do Arquivista é uma configuração própria registrada em
`estudio-gm/config/profiles/arquivo_oculto_v2.lock.json`. Use a fábrica do motor para o Arquivo Oculto.

Uso direto (ambiente do motor `estudio-gm/.venv`, que já tem `kokoro-onnx` e os modelos):

```python
from kokoro_onnx import Kokoro
import soundfile as sf
k = Kokoro('kokoro-v1.0.int8.onnx', 'voices-v1.0.bin')
audio, sr = k.create('Seu filho fala pouco para a idade?', voice='pf_dora', speed=1.0, lang='pt-br')
sf.write('fala.wav', audio, sr)
```

Gere **frase por frase** (um arquivo por plano) e guarde em cache por hash do texto: refazer uma frase não obriga a
refazer o vídeo. Ouça cada arquivo. TTS erra tônica de palavra rara; corrija no `tts`.

Voz clonada ou serviço pago (ElevenLabs e similares): só com autorização do Geovani, custo estimado e, para voz de
terceiro, consentimento escrito. Voz de criança: nunca clonar.

## 5. Cadeia de tratamento de voz (FFmpeg)

Ordem: limpar → controlar dinâmica → suavizar sibilância → nivelar.

```bash
ffmpeg -i voz_bruta.wav -af "highpass=f=80,lowpass=f=14000,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,deesser=i=0.4,loudnorm=I=-16:TP=-1.5:LRA=9" -ar 48000 voz_tratada.wav
```

- `highpass=80`: tira ronco de ar-condicionado e batida na mesa. Voz grave (Arquivista): 70 Hz.
- `afftdn=nf=-25`: redução de ruído suave. Mais forte que −30 deixa a voz metálica.
- `acompressor`: segura picos e aproxima a voz.
- `deesser`: suaviza "s" e "x" estridentes.
- `loudnorm` a −16 LUFS na voz isolada. A mixagem final vai a −14 (`video-audio-mixagem`).

Voz com eco de sala: o FFmpeg não resolve bem. Regrave em ambiente mais abafado.

## 6. Sincronia

- Cada plano começa 0,1–0,2 s **antes** da fala que ele ilustra (o olho precisa de um instante).
- Palavra-chave na tela aparece junto da palavra falada, não antes.
- Depois de qualquer mudança de narração, refaça a legenda (`video-legendas`).

## Checklist

- [ ] Texto lido em voz alta antes de gravar ou gerar.
- [ ] Ritmo entre 2,4 e 2,8 palavras por segundo.
- [ ] Pronúncia conferida ouvindo (siglas, nomes, números).
- [ ] Voz tratada sem chiado, sem estouro, sem som metálico.
- [ ] Voz do perfil respeitada (Arquivista não muda sem aprovação).
