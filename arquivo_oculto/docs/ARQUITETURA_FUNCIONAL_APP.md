# Arquitetura funcional da atualização do Estúdio Audiovisual GM

## Regra fundamental
O código existente é a fonte de verdade de UI e dependências. Audite primeiro. Adapte os componentes reais, evite migração sem benefício. Separar `brand_id` e configurações por marca: `direitaxx`, `dr-geovanimiranda`, `arquivo-oculto`.

## Esquema de dados mínimo
- `Brand`: id, palette, voice_profile, character_id, watermark_template, intro/outro.
- `Character`: id, reference_assets, wardrobe, negative_prompt, accepted_variants, voice_id.
- `Episode`: id, brand_id, series_id, research_brief, script, scenes[], claims[], source_ids[], status, approval_status.
- `MediaAsset`: id, type, path, src_url, credit, hash, license, rights_status, authenticity_status, created_at.
- `GenerationJob`: id, provider, input_hash, request_id, queue_status, error, credits_estimated, credits_used_if_available, started/completed timestamps.
- `Export`: id, episode_id, mp4_path/url, subtitles_path, thumbnail_path, ffprobe_results, qa_status.

## Serviços
1. `research`: fonte e verificação.
2. `script`: texto e temporalização, ritmo e diretrizes.
3. `storyboard`: composição por cenas/visual prompts.
4. `assets`: obtenção e organização de direitos, não misturar original/IA.
5. `character`: referência do Arquivista travada.
6. `providerAdapters`: imagens, vídeo, voz, música com credenciais seguras.
7. `audio`: TTS, normalização e trilha.
8. `timelineRenderer`: FFmpeg/Remotion ou implementação já existente.
9. `qa`: documento, áudio/vídeo, artefato e revisão.
10. `export`: download MP4, SRT, capa e metadados.

## Preferências de UI
Uma tela ‘Novo Episódio’ (marca, série, título, fontes opcionais) com botão **Gerar**. Etapas exibem porcentagem real por subtrabalho (não % inventado): pesquisa, roteiro, imagens, vídeo, locução, edição, QA, exportação. Ao concluir, oferecer preview e botão ‘Baixar MP4’ que baixa o **arquivo final da própria aplicação**.

## Provedores — validar antes de prometer
Google Flow / Veo: confirmar acesso a API, limites, cobrança e créditos no ambiente da aplicação. Claude/Claude Code: ótimo para orquestração e edição via código, mas não implica acesso automático a modelo de geração de vídeo. Outros providers: usar adapters quando contratados/configurados. Para falha de geração, recuar à montagem visual parallax com imagens e áudio de verdade; usuário verá o modo de produção.

## Comportamento em falhas
- Falha `404` no link de um fornecedor ≠ render necessariamente falhado; consultar job status. Preferir gerar link estável da aplicação para MP4 final.
- `quota_exceeded`: pausar provedores pagos, não repetir em loop nem duplicar cobrança, aguardar nova autorização.
- `asset_missing`: manter episódio bloqueado com nome da cena faltante.
- `sound_missing`: não marcar final; fazer fallback TTS autorizado, não exportar vídeo mudo sem aviso.
- `qa_failed`: conservar arquivos e logs para inspeção, oferecer correção concreta.

## Escopo de aceitação
EP01 e EP02 renderizados no formato final e com `qa_status`, sem perda dos outros perfis. Retorno com a lista real de modificações, como reproduzir e provas concretas.
