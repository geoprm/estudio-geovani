# Arquivo Oculto — fábrica de episódios do Arquivista

Terceiro perfil do Estúdio Audiovisual GM. Isolado de @direitaxx e Dr. Geovani (que continuam no fluxo
`preparar.py → ritmo.py → finalizar.py`, intocado).

## Direção editorial V3

Na raiz do estúdio, use o perfil para abrir um template ou revisar a primeira temporada.

```powershell
python -m arquivo_oculto.editorial
python -m arquivo_oculto.editorial --template youtube_5min
python -m arquivo_oculto.editorial --episodio AO-S01-E01
python -m arquivo_oculto.editorial --temporada
```

Os [roteiros revisados](producao/v3/ROTEIROS_TEMPORADA_01.md) estão em pré-produção. Antes de renderizar, converter o
roteiro em manifesto técnico, fechar direitos e acervo, conferir leitura da evidência e medir a locução. Usar a voz
e a aparência registradas no lock V2. O fluxo abaixo documenta a fábrica legada.

## Instalar (uma vez)
```
./arquivo_oculto/instalar_ao.sh            # voz Kokoro (grátis, GitHub oficial)
./arquivo_oculto/instalar_ao.sh --filtro   # + recorte de pessoa e pontos do rosto (Arquivista no seu rosto)
```

## Gerar um episódio (um comando)
```
./arquivo_oculto/gerar_episodio.sh AO-S01-E01
```
Saída em `arquivo_oculto/saida/AO-S01-E01/`:
`AO-S01-E01.mp4` (1080x1920, H.264/AAC, +faststart), `.srt`, `_cover.png`, `_manifest.json` (fontes, claims, voz, provedores,
hashes, custo), `_qa.json` (ffprobe, quadros, loudness, legendas, selos, claims) e `_status.json`.

## Como funciona
1. `examples/EP0x_*.json` (manifesto do pacote): fatos, fontes, claims, cenas planejadas. É a fonte editorial.
2. `producao/AO-S01-E0x.prod.json`: como cada cena vira imagem aqui: narração da cena, título, selo e tipo de cena.
3. `fabrica.py` → `motor.py`: voz (Kokoro pm_alex, cache por hash), trilha e efeitos sintetizados (sem direitos de terceiros),
   cenas, legendas sincronizadas com a voz real, mixagem com ducking e loudnorm, render FFmpeg, SRT, capa, manifesto e QA.

### Tipos de cena
`arq` (Arquivista animado: cabeça, máscara com a fala, respiração, olhos, luz e poeira; `close`, `zoom`, `surgir`),
`crop`, `data`, `doc`, `split`, `timeline`, `grade`, `pergunta` e, em `cenas_extra.py`: `cartas`, `dossies`, `telas`,
`escritorio`, `terminal`, `relogio`, `salto`, `tipo`. Todas as cenas extras são ilustrações desenhadas por código:
levam selo ILUSTRAÇÃO ou RECONSTITUIÇÃO IA e nunca imitam documento, carta ou foto real.

### Personagem
`arquivista-classico-v1`: figura de `assets/arquivista.png` com a máscara convertida para porcelana marfim (`AO_MASCARA=bronze`
volta ao acabamento original). `assets/arq_alpha.png` recorta a figura do cenário; `assets/arq_lmk106.json` são os 106 pontos
do rosto da máscara (usados na animação e no filtro). `assets/referencias_privadas/` é referência interna: nunca publicar.

## Modo visual e limites (honesto)
- Modo atual: `animated_stills`. Não é vídeo generativo.
- Imagem/vídeo por IA: só com um adapter novo em `fabrica.PROVEDORES` e credencial no `.env`. Geração paga exige autorização.
- Boca: a máscara é rígida; a fala aparece pela performance (cabeça, máscara, olhos), sem lábios humanos.

## Testes
`python3 tests/test_arquivo_oculto.py`
