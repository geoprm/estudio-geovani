---
name: arquivo-oculto-visuais
description: Gera e organiza imagens e cenas de IA, preserva proveniência e distingue arquivo autêntico de reconstituições.
---

# Skill — Fotografia, arte, vídeo generativo e proveniência

## Sequência
1. Transforme cenas do storyboard em prompts sem detalhes que contradigam fatos, lugar, época ou figurino.
2. Para cada cena selecione `asset_class`: `historical_original`, `licensed_stock`, `editorial_image`, `ai_reenactment`, `ai_abstract`, `character_clip`, `kinetic_typography`.
3. Se original, verificar autoria, edição/data, licença/justificativa de uso, URL de origem, atributo `authenticity=verified`. Em ausência de verificação, placeholder ou imagem criada e **rotulada**.
4. Se IA, gerar imagem-base e 5–8 segundos de movimento quando houver vídeo generativo disponível. Manter personagem canônico quando presente; asset IDs imutáveis.
5. Otimizar imagens para mobile (resolução vertical, sem bordas). Não aplicar movimento que torne cartas ou textos ilegíveis; cartas podem ganhar push-in e hover com frente verdadeira apenas se autorizado.

## Direção artística
Lentes longas, claro-escuro, imperfeições analógicas discretas, profundidade de campo, partículas sutis, recortes de jornal em perspectiva, mapas e envelopes; combinar imagens autênticas e reconstruções honestas. Uma matéria com 30s deve variar entre 7–10 planos reais/gerados (nem 30s em único close do avatar, nem slideshow preguiçoso).

## Template de prompt visual
`[tipo de cena]; [referência do Arquivista quando aplicável]; [ação verificável ou cena reconstituída]; [época e ambiente]; [luz preta/dourada e contraste]; [composição 9:16]; [movimento específico]; [negative prompt]; [legenda RECONSTITUIÇÃO IA se dramatização de fato]`.

## Guardrails
Nunca usar IA como prova de um acontecimento. Não gerar “fotos vazadas” ou falsas capas apresentadas como reais. Em cenas envolvendo crimes, vítimas ou pessoas identificáveis, evitar imagens fabricadas que sugiram participação real em rituais ou delitos. Informar licença de B-roll, música e fontes. Não burlar marca d'água nem contornar autenticação de provedores.

## Fallback realista
Se a API de vídeo indisponível, criar composição de ilustrações IA + textura + camadas de parallax/camera move no renderer. Registrar modo `animated_stills`, não `generative_video`.

## V2 — 04/11/2026
- **Provedores conferidos em 04/11/2026:** Canva (vídeo só em plano pago: bloqueado), Figma Weave (conta não vinculada: bloqueado), sem credencial Veo/HeyGen/Runway. Nenhum crédito foi gasto. Modo atual: `performance_2_5d` + evidências desenhadas por código. Não chamar de vídeo generativo.
- **Filtro de direitos por modo** (`arquivo_oculto/v2/perfil.py:gate_direitos`): `private_preview` aceita `private_research` e `quotation_excerpt` com a marca PRÉVIA PRIVADA; `public_release` só aceita `verified_license`, `public_domain`, `owner_provided`, `original_production`, `fact_citation`. Asset barrado usa a variante honesta do manifesto (placeholder "ARTE ORIGINAL RETIDA" ou paráfrase com fonte), nunca um desenho fingindo ser o original.
- **Acervo privado** (`arquivo_oculto/acervo_privado/`, fora do Git): arte oficial `bavaria.gif` e `2nd-bullet.gif` (galeria da editora) e o snapshot da lista oficial de 18/04/1995. O repositório `geoprm/estudio-geovani` é PÚBLICO: nunca versionar essa pasta.
- Selos usados: DOCUMENTADO, DOCUMENTO DE 1995, ARTE ORIGINAL, INTERPRETAÇÃO, ANÁLISE, ILUSTRAÇÃO, RECONSTITUIÇÃO ILUSTRADA; `RECONSTITUIÇÃO COM IA` só quando houver imagem gerada por IA.
