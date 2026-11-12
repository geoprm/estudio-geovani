# Arquivo Oculto: o caminho próprio do perfil "arquivo" (para o Editor do Estúdio)

O perfil `arquivo` NÃO usa o estúdio do GitHub nem os passos de edição dos outros perfis. Tem dois formatos:
- `formato: "ia"`: o vídeo inteiro é gerado aqui. O Arquivista animado narra (cabeça que se move, máscara que acompanha a voz, olhos que brilham, cenário com luz tremendo e poeira), com cenas de arquivo, legendas, trilha e selos.
- `formato: "filtro"`: o Geovani gravou o próprio vídeo (partes em `pedido.arquivo.partes`, como nos outros perfis). A máscara e o capuz do Arquivista vão para o rosto dele, acompanhando cabeça e boca, e o fundo vira a biblioteca do Arquivista.

## 1. Montar o motor (uma vez por execução)
1. Baixe do app (Artifact read, url do app, `path` = cada arquivo, todos com out_dir `ao`):
   `arquivo/motor.py`, `arquivo/cenas_extra.py`, `arquivo/fabrica.py`, `arquivo/filtro.py`, `arquivo/arquivista.jpg`, `arquivo/arq_alpha.png`, `arquivo/arq_lmk106.json`,
   `arquivo/fonts/anton-latin-400-normal.woff`, `arquivo/fonts/oswald-latin-700-normal.woff`, `arquivo/fonts/oswald-latin-400-normal.woff`,
   `arquivo/fonts/special-elite-latin-400-normal.woff`, `arquivo/fonts/cinzel-latin-700-normal.woff`.
2. `pip install --break-system-packages kokoro-onnx soundfile opencv-python-headless onnxruntime` (PyPI oficial). Para o filtro também `insightface`.
3. Modelos (releases oficiais no GitHub):
   - Voz (Kokoro, Apache-2.0), para o formato "ia":
     `mkdir -p ao/arquivo/tts && cd ao/arquivo/tts && curl -sSfLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx && curl -sSfLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin`
   - Só para o formato "filtro":
     `mkdir -p ao/arquivo/modelos && curl -sSfL -o ao/arquivo/modelos/u2net_human_seg.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx`
     `mkdir -p ~/.insightface/models && curl -sSfL -o /tmp/b.zip https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_s.zip && unzip -o -q /tmp/b.zip -d ~/.insightface/models/buffalo_s`
4. Variáveis: `AO_FONTS=ao/arquivo/fonts AO_TTS=ao/arquivo/tts AO_ARQ=ao/arquivo/arquivista.jpg AO_ALPHA=ao/arquivo/arq_alpha.png AO_LMK=ao/arquivo/arq_lmk106.json AO_SEG=ao/arquivo/modelos/u2net_human_seg.onnx`.

## 2. Formato "ia"
- Se o pedido tem `pautaId`, leia `pautas/<pautaId>`: o campo `cenas` já é o roteiro do motor.
- Caso novo (tema em `pedido.obs`, série em `pedido.serie`): pesquise em fontes abertas e confiáveis (WebSearch + WebFetch de toda página de onde tirar fato, data ou número) e escreva 6 ou 7 cenas no mesmo formato das pautas `ao-ep01`…`ao-ep10` (leia uma como modelo). Grave a pauta como `pautas/ao-<id do pedido>` (perfil "arquivo", ordem 100+, serie, titulo, cenas, legenda, fontes, cuidado) e ponha esse id em `pedido.pautaId`.
- Entrada do motor: lista JSON com um episódio `{num, titulo, serie, cenas}`.
- `python3 ao/arquivo/motor.py ep.json <num> saida.mp4 --capa capa.jpg` (4 a 6 minutos). Etapas para o Geovani: "Escrevendo o roteiro", "Gravando a voz do Arquivista", "Animando o Arquivista", "Enviando o resultado".

### Episódios com manifesto do pacote (AO-S01-E01, AO-S01-E02 e os próximos)
Se existir `arquivo/producao/<episode_id>.prod.json` (baixe também `arquivo/examples/<manifesto>.json`), use a fábrica, que já gera
MP4, SRT, capa PNG, manifesto de produção e QA: `python3 ao/arquivo/fabrica.py <manifesto> <producao> saida/`.
Só marque "pronto" se `saida/<id>_qa.json` tiver status "pass" ou "pass_with_warnings".

## 3. Formato "filtro"
- Baixe e junte as partes do vídeo (Artifact read de cada id de `pedido.arquivo.partes`, `cat` na ordem, confira com ffprobe).
- `python3 ao/arquivo/filtro.py bruto.mp4 saida.mp4 --capa capa.jpg --num <número do episódio, se houver>` (cerca de 0,5 s por quadro: 13 min para 1 min de vídeo). Por padrão a voz fica um pouco mais grave e com eco de sala; `--sem-voz-sombria` se `pedido.obs` pedir a voz natural.
- Se o rosto não for encontrado na maior parte do vídeo, marque erro pedindo para regravar com o rosto inteiro na tela e luz de frente.
- Legenda do post a partir do que ele falou (transcreva se precisar) e do tema da pauta, se houver.

## 4. Em ambos
- Confira 4 quadros (`ffmpeg -ss`) olhando as imagens: máscara desalinhada, texto cortado, sobreposição, legenda errada.
- Envie `saida.mp4` e `capa.jpg` (Artifact publish, asset true, file_paths) e grave no pedido: status "pronto", etapa "Pronto", resultado {a, capa, legenda, nota}.

## Formato das cenas (formato "ia")
`{fala, tts?, tela, selo?, v: {tipo, ...}}`
- `fala`: frase narrada e legendada (curta). `tts`: só quando a pronúncia precisa de ajuda (anos por extenso, nomes em inglês).
- `tela`: título curto em caixa alta (até 5 palavras). Não use os símbolos ≠ nem →: escreva "NÃO É" e "A"/"E".
- `selo`: "DOCUMENTADO" (fato com documento), "ILUSTRAÇÃO" (documento cenográfico), "RECONSTITUIÇÃO IA".
- `v.tipo`: `arq` (o Arquivista animado; `close: true` para o rosto), `crop` (`alvo`: mesa, ampulheta, globo, maos, gavetas, lanterna, livros), `data` (`texto`, `sub`), `doc` (`cabecalho`, `linhas`, `carimbo`), `split` (`a`: [grande, pequeno], `b`: [...], `riscar`: "b"), `timeline` (`pontos`: [[ano, rótulo] x3]), `grade` (17/169), `pergunta` (a tela vira a pergunta final).
- Estrutura: 1ª cena = gancho (pergunta ou data impactante, sem intro); o Arquivista aparece na 2ª cena e na penúltima; última cena = `pergunta`. 60 a 85 palavras no total (30 a 40 s).

## Regras editoriais (inegociáveis)
Separar fato, interpretação, especulação e lenda; nunca chamar teoria de fato; nunca acusar pessoa sem prova individualizada; não inventar documento, data ou fonte; não simular de forma realista políticos em fatos reais nem vítimas; tradições religiosas com respeito; temas sensíveis só como alegação, com crítica de fontes. Tom: sóbrio, intrigante, "chamativo, mas não mentiroso".
