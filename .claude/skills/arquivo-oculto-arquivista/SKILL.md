---
name: arquivo-oculto-arquivista
description: Mantém identidade visual e performance do Arquivista constantes em cenas, dublagem, avatar e temporadas.
---

# Skill — Bíblia de personagem e consistência do Arquivista

## Identidade imutável
`character_id=arquivista-classico-v1`. Referência principal `assets/arquivista_legado_referencia_privada.png`: capuz preto, máscara branca ligeiramente sorridente, olhos negros, figura inteira de preto, luvas, sala escura com quadros de eventos ao fundo. Referência de **estilo alternativo** `assets/arquivista_conceito_premium.png` com acabamento bronze/dourado; nunca substitua sem registro de escolha. Mantenha máscara e figurino iguais entre EP01 e EP02.

## Character lock
Crie registro de: `character_id`, `canon_reference`, `style_reference`, `mask_shape`, `outfit`, `negative_prompt`, `voice_profile`, `seed_or_character_reference`, `approved_look`, `last_qa`. Use imagens anteriores como referência de identidade quando o gerador suportar.

## Aparições e atuação
Introdução 1–3s; pontes 1–2s; fecho 2–4s. O personagem pode mover cabeça/ombros/mãos, virar páginas, apontar para documento e erguer o olhar. Quero a ilusão de que conduz a história, mas não obrigar lábios humanos numa máscara rígida. Sincronize gestos, microinclinação de cabeça, luz no rosto e movimentos respiratórios com a voz. Se o usuário pedir lipsync real, só usar animação de mandíbula da máscara se artisticamente convincente; evite boca grotesca ou desfazer a máscara.

## Prompt-base para gerador visual
"Same fictional masked investigator The Archivist, strictly consistent canonical white ivory smiling porcelain mask with deep dark eye holes, black hooded coat, black gloves, full human anatomy, elegant shadowy library with archival drawers, documentary thriller lighting, amber rim light, cinematic 35mm texture, realistic restrained movements, no visible human face, no identity changes, vertical 9:16, premium original IP." Ajustar ângulo/plano, não a identidade.

## Negative prompt
No bare face, no skin, no eye color shift, no mask redesign, no modern streetwear, no exaggerated horror, no blood, no weapons, no warped hands, no changing number of fingers, no mangled text, no unrelated logos, no screen watermark. Inspecionar 3 frames de cenas com personagem.

## Direitos
Print original do Kwai é apenas referência interna; personagens de terceiros do screenshot nunca devem ser publicados. A recriação deve ser estética original e consistente.

## V2 — 04/11/2026 (substitui a escolha de referência acima)
- **Cânone de aparência V2:** `arquivo_oculto/assets/arquivista.png` (idêntica pixel a pixel a `arquivista_conceito_premium.png`), com a máscara tratada como **marfim envelhecido com veios dourados** (`ator.mascara_marfim_ouro`). `character_id=arquivista-v2`. A máscara branca sorridente do Kwai fica só como referência privada de movimento/legado; não é mais o cânone. Decisão registrada em `config/profiles/arquivo_oculto_v2.lock.json`.
- **Atuação V3:** preserve a silhueta e o material da máscara. A voz em off continua disponível. Para uma fala em cena, marque `mascara_falada: true` no manifesto e apenas no plano que fala. O motor local articula sutilmente a boca da máscara com o envelope da voz, sem substituir o rosto nem prometer sincronia por fonema. Combine com postura, cabeça, olhar e ritmo de câmera.
- **Atuação implementada (`arquivo_oculto/v2/ator.py`, modo `performance_2_5d`):** `aparicao` (A1), `corredor` (A2), `olhar_camera`, `virar_cabeca`, `ombro` (over-the-shoulder com foco seletivo sobre a prova), `debrucar` (A4/A5), `silencio` (A7, 1–2 s), `encerramento` (A8). Camadas com paralaxe (fundo, personagem, mesa).
- **Regras de quantidade:** ≥ 3 tipos de plano do personagem por 60 s; nenhum plano do personagem acima de 4 s (QA tolera +0,6 s); tempo de tela 12–28%; ele entra e sai do quadro.
- **Limite honesto:** as mãos não manipulam objetos (as luvas permanecem unidas na referência). Manipulação de prova é mostrada por over-the-shoulder, inserts e luz. Gesto real de mão exige provedor image-to-video (bloqueado em 04/11/2026).
- **Referência de movimento ausente:** `video_antigo_kwai_1202.mp4` não está no disco; quando chegar, comparar ritmo de entrada/saída e gestos.
