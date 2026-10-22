# Estúdio de Reels v2.5 — @direitaxx e Dr. Geovani Miranda

Um motor de edição, dois perfis de marca e dois formatos. Para usar numa conversa nova com o Claude:
anexe este .zip e diga "monte o estúdio e edite este vídeo no perfil X, formato Y".

## Perfis (perfis.py)

| Perfil | Visual | Tom |
| --- | --- | --- |
| direitaxx | Preto + amarelo #FFD400 + dourado, bandeira LED, carimbo vermelho (Anton) | Liderança política e social, "Aqui é o sertão falando." |
| drgeovani | Azul-marinho #030B1E + dourado #E5A93C, títulos Playfair, legenda sem contorno | Acolher, ensinar, guiar. Lower third com CRFa |

## Formatos

| Formato | Quando usar | Como fica |
| --- | --- | --- |
| dividida | Há prova: manchete, vídeo, número | Prova em cima (0–900 px), você embaixo, legenda na divisão |
| depoimento | Opinião, experiência, resposta a comentário | Você em tela cheia, cenário real desfocado, palavra-carimbo atrás da cabeça |

## Regras do Manual v2 já embutidas no motor

- Gancho de até 6 palavras sozinho na tela de 0 a ~2,5 s; legenda só depois
- Impacto sonoro no frame 0 e em cada carimbo
- Zoom de abertura 100→110% em 1,5 s; depois, jump cuts alternando 100/113/105/118%
- Lower third de 2,5 a 5 s (1420–1520 px)
- Palavra ativa da legenda em destaque (#FFD400 ou dourado)
- Legenda em tela cheia em 1380 px; no depoimento, 1320 px (fora da área coberta pelo app)
- Selo de fonte em 150–210 px
- Versão B (--B): prova em tela cheia durante o gancho, depois divide
- Capa 1080×1920 com 3 palavras na faixa segura (384–1536 px)
- Voz em −14 LUFS, pico −1,5 dBTP; sem tela final
- Retoque leve automático (beleza.py): pele mais lisa sem perder textura de barba, olhos e boca; dentes
  com aparelho mais claros (some o escuro dos bráquetes e o brilho do metal). Boca fechada não muda
- Carimbo legível: a palavra fica inteira acima da cabeça, só a base passa por trás

## Arquivos

| Arquivo | Função |
| --- | --- |
| preparar.py | Passo 1: normaliza a gravação, transcreve (Whisper), rastreia o rosto |
| ritmo.py | Passo 2: corta pausas > 0,17 s, acelera 1,06×, jump cuts |
| modelo_video.py | Passo 3: copie e preencha (gancho, selos, prova do topo, carimbos) |
| motor.py | O motor (render, áudio, capa, versões A/B) |
| pessoa.py / fundos.py | Recorte do rosto, luz, fundos (bandeira LED, marinho, real) |
| beleza.py | 468 pontos do rosto (MediaPipe), pele suave, dentes/aparelho |
| kit.py | Legenda automática e leitura do corte de ritmo |
| instalar.py | Monta o estúdio a partir das partes guardadas no app (sem internet) |
| finalizar.py | Renderiza versões A e B (a B só refaz a abertura), comprime para ~14 MB e gera a capa |
| exemplos/tela_dividida_educacao.py | Exemplo completo de tela dividida: o padrão de qualidade |

## Instalação

O código mora neste repositório privado (`geoprm/estudio-geovani`). O modelo de transcrição (Whisper small, dados
`.onnx`) fica guardado no app do Geovani, em partes (`whisperPartes` em `config/app`).

1. `git clone` deste repositório.
2. ArtifactData get `config/app` do app com out_dir (gera um JSON) e Artifact read de cada id de `whisperPartes`
   no mesmo out_dir de partes.
3. `python3 instalar.py <config.json> <pasta_das_partes>`: instala `@huggingface/transformers` pelo npm oficial
   (em `asr/`, versões travadas no package-lock) e o `ai-edge-litert` pelo PyPI, se faltarem; confere o SHA-256 do
   modelo, extrai em `modelos/whisper/` e testa.

Pré-requisitos: Python 3.13, Node 18+, ffmpeg, numpy, opencv e pillow (já vêm no ambiente do Claude).
Não use pacotes de terceiros para o modelo (como `sts-whisper-small`).
Pastas de trabalho: variável ESTUDIO_TRABALHO (padrão: estudio/trabalho).

## Desempenho

~1,3 s por quadro com 2 CPUs: um Reel de 30 s leva cerca de 20 minutos. O comando `part` divide o render
em pedaços para rodar em paralelo.
