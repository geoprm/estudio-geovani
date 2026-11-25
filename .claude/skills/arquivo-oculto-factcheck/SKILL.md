---
name: arquivo-oculto-factcheck
description: Verifica pesquisas, datas e imagens; separa fatos de hipóteses e prepara créditos e status de direitos.
---

# Skill — Checagem documental e direitos

## Primeiro validar, depois dramatizar
Cada narrativa possui `claims[]`, com frase, data, fonte primária, segunda fonte quando possível, status e momento de aparição. Estados: `documented`, `supported_inference`, `alleged`, `speculative`, `refuted`, `unknown`.

## Fontes do piloto
- INWO: FAQ de Steve Jackson datado de dezembro/1994, com lançamento em 16 de dezembro: https://groups.google.com/g/rec.games.trading-cards.misc/c/pZqyQ8eJP48
- Operação de 1º de março de 1990 pelo Serviço Secreto dos EUA: https://law.justia.com/cases/federal/district-courts/FSupp/816/432/1976489/

## Checagens especiais
- A busca não aconteceu por causa das cartas INWO publicadas quatro anos depois; não dizer que foi o FBI.
- Cartas de 1994/95 não são automaticamente previsão ao serem associadas a eventos anos depois; comparar imagem original e origem da interpretação.
- Não imputar participação criminosa a pessoas apenas por fotos, contatos ou teorias.
- Não atribuir rituais criminosos a religiões legítimas sem evidência.
- Para ambientes com documentos, toda data/carimbo/capa devem ser fonte real ou `RECONSTITUIÇÃO IA` no vídeo/legenda.

## Proveniência obrigatória
Para assets: `source_url`, `source_type`, `author`, `rights_status`, `authenticity_status`, `capture_date`, `credit_line`, `public_use_allowed`, `internal_research_only`. Criar filtro de publicação que exclua assets com direitos desconhecidos/não autorizados. Não eliminar marcas d'água ou passar por cima de login.

## Entrega
Um relatório simples: `claim_id | status | url | localizador | asset_id | beat | ação editorial`. Na V3, atribuir cada alegação à sua origem quando ela entra na história. Qualificar a relação na mesma cena se o silêncio induzir causalidade ou imputação. Levar a fonte completa à descrição. Se a alegação não tiver origem rastreável ou precisar de uma acusação sem base para sustentar a cena, retirar a passagem.

## V2 — 04/11/2026
- Lista oficial INWO de 18/04/1995 (sjgames.com/inwo/lists/ill.html) lida e guardada em `arquivo_oculto/acervo_privado/`: 412 cartas (uma linha tem célula extra: International Cocaine Smugglers); informa o lançamento de 16/12; Epidemic C Dis. Shea/Jeff; Pentagon C Plc. Dan/Jeff; Terrorist Nuke C Plot Dan/Derek. Copyright 1995, permissão só de fotocópia pessoal: dados = `fact_citation`, trecho literal = `quotation_excerpt`.
- Lição de 04/11/2026: conferir CADA linha de tabela mostrada na tela contra a fonte. "Drug Companies" foi suposto e não está na lista Unlimited; foi removido antes do render.
- O Justia respondeu 403 nesta sessão; a decisão de 1993 continua conferida pelo grafo do site v0.8. Não contornar bloqueios.
