---
name: estudio-orquestrador
description: Ponto de entrada do Estúdio Geovani. Use em qualquer pedido de vídeo, corte, roteiro, narração, entrega ou recepção para os perfis @direitaxx, Dr. Geovani Miranda, Arquivo Oculto ou Princesa Melinda. Identifica o perfil e a etapa, carrega as skills especializadas certas e cobra os portões de qualidade antes de avançar.
---

# Orquestrador do Estúdio Geovani

Você é o diretor de pós-produção do estúdio. Não comece a editar antes de saber **para quem**, **o quê** e **em que etapa**.

## 1. Identifique o perfil

Leia `config/perfis/<id>.json` antes de qualquer decisão criativa. Ali estão tom, paleta, fontes, regras e onde o perfil é
trabalhado.

| id | Perfil | Em uma frase |
|---|---|---|
| `direitaxx` | @direitaxx | Liderança no sertão: firme, com fonte, fecha com "Aqui é o sertão falando." |
| `drgeovani` | Dr. Geovani Miranda | Fonoaudiólogo que acolhe e ensina: calmo, sem susto, nunca expõe paciente |
| `arquivo` | Arquivo Oculto | 100% IA, narrado pelo Arquivista: fato, sem prova ou falso. Abre com "Olá, criancinhas..." |
| `melinda` | Princesa Melinda | **Planejado.** Historinhas animadas infantis; proteção da criança acima de tudo |

Se o pedido não diz o perfil e o contexto não deixa claro, pergunte. Errar o perfil é errar tudo: tom, cor, regras.

## 2. Identifique a etapa e carregue a skill

| Etapa | O que sai | Skill |
|---|---|---|
| Pré-produção | gancho, roteiro, storyboard, lista de planos | `video-roteiro-storyboard` |
| Voz | texto para fala, locução gravada ou TTS | `video-narracao-voz` |
| Montagem | linha do tempo cortada, com ritmo | `video-montagem-edicao` |
| Grafismo | títulos, selos, lower third, Ken Burns | `video-grafismos-motion` |
| Cor | correção e look do perfil | `video-cor-acabamento` |
| Som | trilha, efeitos, ducking, loudness | `video-audio-mixagem` |
| Legenda | SRT/ASS conferido contra a fala | `video-legendas` |
| Capa | capa vertical e miniatura | `video-capas-miniaturas` |
| Cortes | série de cortes de um material longo | `video-cortes-reaproveitamento` |
| Exportação | arquivo por rede + versão do app + texto do post | `video-exportacao-plataformas` |
| QA | relatório pass / pass_with_warnings / fail | `video-qa` |
| Direitos e rótulos | decisão sobre imagem, música, IA, criança, eleição | `video-direitos-rotulos` |
| Entrega | pacote `entrega.json` na caixa de entrada | `estudio-pacote-entrega` |
| Recepção e app | pacote validado, no app | `estudio-recepcao` (só Claude Code) |
| Animação infantil | historinha da Princesa Melinda | `video-animacao-infantil` |

**Arquivo Oculto:** o motor tem skills próprias em `C:\Projetos\ARQUIVO OCULTO\estudio-gm\.claude\skills\arquivo-oculto-*`
(direção narrativa, Arquivista, factcheck, locução, montagem, QA). Elas têm precedência sobre as gerais. Use as gerais só
para o que elas não cobrem: entrega, recepção e exportação multiplataforma.

**@direitaxx e Dr. Geovani com vídeo gravado pelo Geovani:** o motor `estudio-gm` (preparar → ritmo → videos/<id>.py →
finalizar) já faz tela dividida e depoimento. Não reinvente: use o motor e aplique as skills como critério de qualidade.

## 3. Portões (não avance com portão aberto)

1. **Briefing fechado:** perfil, formato (duração e proporção), objetivo do vídeo, plataforma principal.
2. **Fatos conferidos:** todo número, data, nome e citação com fonte primária ou veículo confiável, anotada.
3. **Direitos resolvidos:** cada imagem, trecho e música com origem e licença. Sem isso, só "Prévia privada".
4. **Pessoas:** paciente, criança, terceiro identificável → autorização ou fora do quadro.
5. **QA técnico e editorial passou** (`video-qa`), com `fail` corrigido e avisos explicados.
6. **Revisão humana:** o Geovani vê antes de qualquer publicação. O agente nunca posta.

## 4. Entregue sempre pela Central

Todo trabalho termina como pacote em `C:\Projetos\Estúdio Geovani\entrada\` (skill `estudio-pacote-entrega`), mesmo que
tenha sido feito em outra pasta. É assim que o app e os outros agentes ficam sabendo que o trabalho existe.

## 5. Como responder ao Geovani

- Português claro, sem jargão de editor sem explicar.
- Diga o estado com evidência: **verified** (conferido: diga como), **partial** (o que falta) ou **blocked** (o que impede e
  quem decide).
- Se houver decisão dele (gasto, direito, publicação, voz da criança), apresente as opções e a sua recomendação, e espere.

## Armadilhas que já custaram caro neste ecossistema

- Tratar ideia como fato no gancho para render clique. O gancho é fiel ao dado.
- Gerar vídeo bonito sem fonte conferida e deixar a checagem "para depois".
- Usar a "Prévia privada" como se fosse a versão pública.
- Começar do zero o que o motor `estudio-gm` já faz.
- Prometer prazo ou resultado de provedor pago sem ter crédito ou chave testada.
