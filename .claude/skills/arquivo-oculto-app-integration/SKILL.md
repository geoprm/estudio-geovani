---
name: arquivo-oculto-app-integration
description: Integra ao aplicativo existente provedores de imagem, vídeo e TTS com fila, custos, retomada e download MP4.
---

# Skill — Adaptação do app existente e provedores

## Preservar patrimônio existente
Examinar a aplicação atual e seus perfis `direitaxx`, `dr-geovanimiranda` antes de editar. Extender modelos `Brand`, `Episode`, `MediaAsset`, `ProductionJob`, `ProviderRequest`, `Export`, sem quebrar migrações. Adicionar `brand_id=arquivo-oculto`, `character_id=arquivista-classico-v1`.

## Interface dos adapters
`generateImage(prompt, refs, format)`, `generateVideo(prompt, refs, duration, aspect)`, `synthesizeSpeech(text, voice)`, `generateMusic(prompt)`, `renderTimeline(manifest)`, `getJobStatus(id)`, `saveAsset(content,metadata)`. Não assumir provedores em uso nem que Google Flow dá API ao plano consumer; descobrir docs/credenciais. Disponibilidade e custo são propriedades de instância, não afirmação no código.

## Pipeline resistente
Persistência de status, chamadas idempotentes, retries com backoff em limites temporários, cancellation, cache por hash, custos/quotas antes de iniciar paid jobs, timeout configurável, logs sem segredos. Erro 404 não prova falha de render; status por endpoint confiável.

## UX zero-atrio
Tela de criação com tema/dossiê e marca; `Gerar episódio`, `Acompanhar estágios`, `Revisar preview`, `Baixar MP4`. Os provedores trabalham por trás. Permitir aprovação humana de publicação, sem exigir upload manual repetitivo. Exportação direta tem prioridade, inclusive após falha de download na UI do fornecedor.

## Segurança
Chaves de API em variáveis de ambiente, secrets manager ou infraestrutura segura. Nunca em client-side JS, commits, ZIP ou logs. Sem executar compras e sem publicar em conta social sem autorização. Exibir limitação explícita de créditos.

## Critério
Finalizar com diffs reais, testes, arquivos exportados e lista de pendências; não dizer “conectado ao Google” se não existe credencial e integração testada.

## V2 — 04/11/2026 — arquitetura real encontrada
1. App "Estúdio Geovani": Artifact `claude.ai/artifact/MUNdJL4BwN9ovWQeVdboHt` (perfis direitaxx, drgeovani e arquivo; banco `pautas`, `pedidos`, `config/app`; aciona a rotina por `fire_trigger`).
2. Rotina "Editor do Estúdio" (`trig_014YcZcx198rd5ZxMXJzXNz4`, 11h44/16h44/20h44, America/Bahia), com o passo 3A do Arquivo Oculto já aplicado.
3. Motor @direitaxx/Dr. Geovani: GitHub `geoprm/estudio-geovani` (PÚBLICO) @ 53f5865.
4. Fábrica Arquivo Oculto V1 (`arquivo_oculto/`) e V2 (`arquivo_oculto/v2/`): só neste checkout local e nos arquivos `arquivo/` do app; não estão no GitHub.
Republicar o Artifact, gravar no banco do app ou alterar a rotina exige autorização explícita do Geovani (configuração persistente / app em uso).
