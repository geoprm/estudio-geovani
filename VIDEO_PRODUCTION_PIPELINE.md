# Pipeline real de produção de vídeo — Estúdio Audiovisual GM

Atualizado em 09/11/2026.

## 1. As quatro peças do estúdio

| Peça | Onde mora | O que faz |
|---|---|---|
| App "Estúdio Geovani" | Artifact privado `claude.ai/artifact/MUNdJL4BwN9ovWQeVdboHt` (página em `app/index.html`, versão 8 de 05/11/2026) | Interface no celular: perfis @direitaxx, Dr. Geovani e Arquivo; pautas, teleprompter, envio de vídeo, Prontos (download), metas. No perfil Arquivo: seletor de formato V2 e vídeos V2 com as versões Pública e Prévia privada. Banco: `pautas`, `pedidos`, `config/app` |
| Rotina "Editor do Estúdio" | Claude Code na nuvem, `trig_014YcZcx198rd5ZxMXJzXNz4`, 11h44/16h44/20h44 (America/Bahia) | Pega `pedidos` na fila, edita e devolve o MP4 no app. Passo 3A desvia o perfil Arquivo para `arquivo/LEIA-ME.md` (fábrica V1) |
| Motor @direitaxx / Dr. Geovani v2.5 | GitHub `geoprm/estudio-geovani` (**público**) e esta pasta | `preparar.py → ritmo.py → videos/<id>.py → finalizar.py`: transcrição, cortes, tela dividida/depoimento, retoque, versões A/B, capa |
| Fábrica Arquivo Oculto | `arquivo_oculto/` (V1) e `arquivo_oculto/v2/` (V2) — só nesta pasta e em `arquivo/` do app | Vídeo 100% gerado: voz, Arquivista, cenas, legendas, MP4, QA |

O site Arquivo Oculto (`C:\Projetos\ARQUIVO OCULTO\arquivo_oculto_v01`, feito no Codex) é **outro componente**: leitor de pesquisa, acervo de cartas, grafo. A fábrica usa o acervo do site como fonte (direitos e fontes verificadas), mas não altera o site.

## 2. Perfis isolados

`perfis.py` tem três entradas. @direitaxx e Dr. Geovani são idênticos ao commit `53f5865` do GitHub (o teste `perfis_antigos_intactos` compara). O perfil `arquivo-oculto` usa o contrato técnico V2 e a direção editorial V3.

## 3. Pré-produção V3 e fábrica técnica V2 do Arquivo Oculto

Consultar `python -m arquivo_oculto.editorial --template <formato>` para começar um roteiro e
`python -m arquivo_oculto.editorial --episodio <ID>` para recuperar a revisão da primeira temporada.
O [caderno da temporada](arquivo_oculto/producao/v3/ROTEIROS_TEMPORADA_01.md) apresenta fala, imagem, som, fontes e pendências.
A fábrica recusa o roteiro V3 direto. O manifesto de render recebe os planos, fontes, direitos, ativos e a locução com a identidade do lock.
A rotina de nuvem continua no fluxo histórico V1.

Comando da fábrica para um manifesto técnico V2. O exemplo usa o manifesto histórico do EP01.

```
python -m arquivo_oculto.v2.fabrica_v2 arquivo_oculto/producao/v2/AO-S01-E01.v2.json --modo private_preview --workers 4
```

| Etapa (status.json) | O que acontece de verdade |
|---|---|
| `planned` | Valida o perfil V2 e o manifesto (campos V2 por plano, campos de atuação, texto ≤ 8 palavras, claims, assets) |
| `sources_verified` | Filtro de direitos por modo: asset barrado usa a variante honesta declarada (placeholder ou paráfrase com fonte) |
| `generating_voice` | Kokoro local, voz travada no lock; cada fala é sintetizada isolada (cache por hash); a duração real define a timeline |
| `generating_visuals` | Cada plano vira um segmento H.264 próprio, em paralelo, com cache por hash do plano + tempos + legendas + código |
| `assembling` | Concat dos segmentos, trilha e efeitos sintetizados, ducking por sidechain, loudnorm, MP4 `+faststart`, capa |
| `qa` | ffprobe, quadros, loudness, legendas, atuação medida, direitos, rótulos, campos V2 |
| `completed` / `blocked` | `completed` só com MP4 conferido e QA pass/pass_with_warnings |

**Saídas** (`arquivo_oculto/saida_v2/<episode_id>_<modo>/`):
- `video.mp4`: master, ~6 Mbps, ~60 MiB para 85 s;
- `video_app.mp4`: até 19 MiB, 2 passadas, para o player e o download do app;
- `voice.wav`, `subtitles.srt`, `cover.png`;
- `timeline.json`, `sources.json`, `qa.json`, `status.json`;
- `frames.jpg`: folha de contato, o quadro do meio de cada plano, para a revisão humana.

**Refazer só o QA** (por exemplo, depois de uma aprovação gravada no lock): o mesmo comando com `--so-qa`. Ele recusa se planos
ou tempos mudaram desde a montagem e não toca no vídeo, na versão do app nem na capa.

**Refazer só um trecho:** altere o plano no manifesto e rode o mesmo comando. O cache é endereçado por:
- o próprio plano (parâmetros, tempos, legendas que caem nele);
- a impressão digital do código **daquele tipo** de plano (`hash_codigo(tipo, prova)`).

Assim, corrigir o desenho da lista oficial refaz só os planos de lista. Para forçar um plano: `--refazer S07,S09`.

Medido em 04/11/2026:
- clarear duas leituras do EP01 refez 2 de 28 planos em 46 s;
- a versão pública do EP02 refez 5 de 24.

**Regras que a fábrica impõe antes de renderizar** (`validar_manifesto`):
- campos V2 por plano e de atuação;
- texto na tela com no máximo 8 palavras;
- claims documentados com fonte registrada;
- **nenhum título na tela** em planos de documento, terminal, monitores, dossiê e over-the-shoulder (`SEM_TITULO`);
- **nenhum manifesto em `rascunho_pendente_checagem`**.

**Reconstituição de época:** `escritorio` (cena V1) tem monitor e disquete e só serve a partir de 1980. Antes disso, use
`escritorio_epoca`, com `acao` `lanterna`, `gaveta` ou `luminaria`: arquivos de aço, máquina de escrever e luminária, sem
logotipo e sem papel legível. O teste `reconstituicao_sem_anacronismo` confere todos os manifestos.

### Entrega ao app

`arquivo_oculto/v2/entrega_app.py` liga a fábrica ao app em três passos. Os uploads e as escritas no banco são feitos pelo Claude
Code com as ferramentas do Artifact, e só com autorização do Geovani.
1. `preparar AO-S01-E0N`: copia o `video_app.mp4` da versão pública (e da prévia, se ela tiver material privado) e gera a capa em JPEG.
2. Upload dos arquivos para o app; `registrar AO-S01-E0N a=<id> b=<id> capa=<id>` grava os ids e os hashes de origem em
   `arquivo_oculto/producao/v2/entregas_app.json`.
3. `pedidos AO-S01-E0N`: monta o documento `pedidos/v2-ao-s01-e0N`, com status `pronto`, a legenda do manifesto, a nota do QA,
   os rótulos Pública/Prévia privada, `v2: true` e o formato.

Só entra episódio com QA aprovado nos dois modos. A versão A é sempre a pública.

### Temporada (EP03–EP10)

`python -m arquivo_oculto.v2.temporada arquivo_oculto/producao/pautas_app_2026-11-04 arquivo_oculto/producao/v2/rascunhos` converte as pautas do
app em rascunhos V2:
- o Arquivista vira planos de atuação variados;
- documentos desenhados viram dossiês com selo ILUSTRAÇÃO;
- o escritório vira `escritorio_epoca` quando o fato é anterior a 1980;
- fontes ficam como "não verificadas";
- a duração é estimada.

Para renderizar um rascunho:
1. Ler as fontes e salvar o snapshot com hash em `acervo_privado/`.
2. Classificar os claims.
3. Expandir para 85 s, se for o caso.
4. Trocar `status_editorial` para `pronto_para_render`.

### Adapters e provedores (estado verificado em 04/11/2026)

| Capacidade | Adapter | Estado |
|---|---|---|
| TTS | `v2/voz.py` (Kokoro ONNX local) | Disponível, custo zero. Voz `arquivista-v2-c` aprovada pelo Geovani em 04/11/2026 |
| Personagem animado | `v2/ator.py` (performance 2,5D em camadas) | Disponível. Não é vídeo generativo |
| Evidências / documentos | `v2/evidencia.py` | Disponível. Material autêntico só com registro de fonte e direitos |
| Música / SFX | `motor.trilha` + `fabrica_v2.efeitos` | Disponível, sintetizados (sem direitos de terceiros) |
| Legendas | `fabrica_v2.legendas` (tempo pela voz real) | Disponível |
| Renderizador | FFmpeg 9 + NumPy/OpenCV | Disponível |
| Asset retrieval | download direto de fonte primária (ex.: lista oficial, galeria oficial) | Manual por sessão; snapshot com hash em `acervo_privado/` |
| Image generation | — | **Bloqueado:** Canva/Figma sem acesso utilizável; nenhuma credencial |
| Image-to-video / video generation | — | **Bloqueado:** Canva exige plano pago; Figma Weave sem conta vinculada; sem chave Veo/HeyGen/Runway |

Gasto em serviços pagos: R$ 0. Nenhuma compra, nenhuma publicação.

### Modos de render

- `private_preview`: inclui material de pesquisa privada (arte oficial, trecho literal) com a marca "PRÉVIA PRIVADA · NÃO PUBLICAR".
- `public_release`: só material liberável; arte original vira "ARTE ORIGINAL RETIDA", trecho literal vira paráfrase com fonte.

Nenhum dos dois modos publica nada. `publicacao_aprovada` é sempre `false` na fábrica.

## 4. Fábrica V1 (preservada)

`arquivo_oculto/fabrica.py` + `motor.py` + `cenas_extra.py` continuam funcionando (testes V1 7/7) e são o caminho que a rotina do app usa hoje (`arquivo/LEIA-ME.md`). A troca da rotina para a V2 depende de aprovação do Geovani.

## 5. Ambiente local

- `.venv/` com numpy, pillow, opencv-python-headless, onnxruntime, soundfile, kokoro-onnx e pymupdf (PyPI oficial; `arquivo_oculto/instalar_ao.sh`).
- Modelo de voz em `arquivo_oculto/tts/` (releases oficiais de thewh1teagle/kokoro-onnx; sha256 `6e742170…` e `bca610b8…`).
- Sem GPU; 4 núcleos físicos (8 lógicos); ~0,3–2 s por quadro por processo. Um episódio de 95 s leva ~12–13 min do zero e ~3 min quando só um plano muda.
