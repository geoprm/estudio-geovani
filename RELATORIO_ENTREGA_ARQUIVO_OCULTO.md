# Relatório de entrega — Arquivo Oculto (Video Factory V1) — 04/11/2026

## O que foi feito
- **Estúdio preservado:** esta pasta é o repositório `geoprm/estudio-geovani` (commit 53f5865) com acréscimos. Os arquivos de
  @direitaxx e Dr. Geovani não foram alterados, exceto `perfis.py` (só ganhou o perfil `arquivo-oculto`) e `CLAUDE.md`
  (o addendum foi mesclado no fim, sem apagar nada).
- **Skills:** as 10 Skills do pacote estão em `.claude/skills/arquivo-oculto-*`.
- **Fábrica:** fica em `arquivo_oculto/`. Cada episódio passa por voz, cenas, montagem, legendas, MP4, SRT, capa, manifesto e QA.
  - Um comando gera o episódio: `./arquivo_oculto/gerar_episodio.sh AO-S01-E01`.
  - O áudio é sintetizado na hora e a fala fica em cache, então os próximos episódios não regravam a voz.
- **App (Estúdio Geovani):**
  - o perfil Arquivo mostra os episódios e tem os botões "Gerar vídeo", "Caso novo" e "Enviar meu vídeo";
  - os MP4 do EP01 e do EP02 estão em Prontos, com botão "Baixar vídeo";
  - os arquivos da fábrica foram publicados dentro do app, em `arquivo/`.

## Entregas (QA automático)
| Episódio | Arquivo | Duração | Meta | QA |
|---|---|---:|---:|---|
| EP01 — O jogo que parecia prever o mundo | `arquivo_oculto/saida/AO-S01-E01/AO-S01-E01.mp4` | 34,9 s | 38 s | pass |
| EP02 — A operação federal contra a editora | `arquivo_oculto/saida/AO-S01-E02/AO-S01-E02.mp4` | 46,2 s | 42 s | pass |

Cada pasta tem também:

- `.srt` com as legendas;
- `_cover.png` com a capa em 1080x1920;
- `_manifest.json` com claims, fontes, voz, provedores, custo R$ 0 e o sha256 de cada arquivo;
- `_qa.json` com o resultado de cada checagem;
- `_status.json` com o andamento da produção.

Checagens que os dois passaram:

- vídeo 1080x1920, H.264 30 fps, yuv420p;
- áudio AAC 48 kHz em estéreo;
- `moov` no início do arquivo (o vídeo começa a tocar antes de baixar inteiro);
- nenhuma cena preta;
- volume entre -14,3 e -14,5 LUFS, com pico de -1,3 dBTP;
- legendas em ordem e com o mesmo texto da narração;
- selo de ILUSTRAÇÃO ou RECONSTITUIÇÃO IA nas cenas que pedem;
- claims com fonte (alegação marcada como alegação);
- o Arquivista aparece em 3 cenas.

Teste de download: o MP4 do EP01 baixado do app tem o mesmo sha256 do original
(e5f185a2cb89e2a8046be0d8dc4e6bc10446c4474faaefebff7571ed75d2f858).

Os testes do projeto passam todos (7 de 7): `python3 tests/test_arquivo_oculto.py`.

## Fatos conferidos nas fontes
- **Illuminati (1982) e INWO (1994):** SF Encyclopedia.
- **Lançamento do INWO em 16/12:** FAQ de Steve Jackson, postada em 25/12/1994.
- **A busca:** em 01/03/1990, feita pelo Serviço Secreto dos EUA (não pelo FBI), ligada ao documento E911 da BellSouth e ao BBS Phoenix.
  Foram levados 3 computadores, mais de 300 disquetes e o manuscrito de GURPS Cyberpunk.
  A editora venceu na Justiça em 12/03/1993 (816 F.Supp. 432).
- **"4 anos e 9 meses":** é o intervalo entre 01/03/1990 e 16/12/1994.

## Modo de produção e bloqueios reais
- **Modo `animated_stills`:** não é vídeo generativo. O Arquivista é animado por deformação da imagem de referência:
  - cabeça que balança e acena com a voz;
  - máscara que abre com a fala;
  - olhos que brilham;
  - respiração, figura recortada do cenário, luz de lanterna e poeira.

  As outras cenas são ilustrações desenhadas por código: cartas genéricas, dossiês, parede de monitores, escritório de 1990 com
  lanterna, terminal de BBS, relógio, linha do tempo animada e tipografia.
- **Máscara:** foi convertida para porcelana marfim, mais perto do cânone clássico. O sorriso largo da referência antiga não foi
  recriado: isso pede um gerador de imagem.
- **Imagens e vídeos por IA bloqueados pela rede deste ambiente:**
  - Canva gera a imagem, mas aqui só chega uma miniatura de 112x199 pixels;
  - os domínios de download de Canva, Gamma e Figma são bloqueados pelo proxy;
  - bancos de imagem livre (Wikimedia, Pexels, Arquivo Nacional) também são bloqueados;
  - Figma Weave não tem conta vinculada;
  - não há credencial de Veo/Flow ou de HeyGen.

  Para liberar: em claude.ai, Configurações > Capacidades, permitir os domínios, ou rodar esta pasta no seu PC com o Claude Code.
  Geração paga só com autorização.
- **Editor automático do app:** a tarefa agendada "Editor do Estúdio" ainda não aprendeu o caminho do Arquivo. A alteração foi
  negada duas vezes pela proteção de tarefas agendadas. O texto pronto está em `PASSO_3A_EDITOR.txt`.
- **Comparação com o HeyGen:** o vídeo antigo não está nesta pasta, então só dá para comparar no olho.
  - O HeyGen dá boca e corpo realistas, mas deixa marca d'água e tem limite de 1 vídeo por mês.
  - A fábrica entrega sem marca d'água, com custo zero e de forma repetível, com legendas, SRT, selos e QA; em troca, a animação é
    mais contida.

## Próximos passos sugeridos
1. Liberar os domínios de imagem ou levar esta pasta para o Claude Code no PC. Com uma credencial, criar o adapter `imagem_ia` em
   `fabrica.PROVEDORES` e trocar as ilustrações por cenas geradas, com selo RECONSTITUIÇÃO IA.
2. Colar o passo 3A na tarefa "Editor do Estúdio" para o botão "Gerar vídeo" e o filtro funcionarem sozinhos.
3. Converter os episódios 03 a 10 em `producao/AO-S01-E0x.prod.json`. Os roteiros já estão em `producao/temporada1_cenas.json`.
