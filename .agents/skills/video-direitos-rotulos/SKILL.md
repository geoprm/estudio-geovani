---
name: video-direitos-rotulos
description: Decide o que pode entrar nos vídeos do Estúdio Geovani quanto a direitos e rótulos. Cobre imagem e trecho de terceiros, música, domínio público, crédito na tela, imagem de pessoas, pacientes e crianças (ECA e LGPD), rótulo de conteúdo gerado por IA nas plataformas, regras eleitorais do TSE para conteúdo sintético, e quando um vídeo vira Prévia privada. Use quando houver material de terceiros, pessoas reconhecíveis, IA realista, tema eleitoral ou dúvida se algo pode ir ao ar.
---

# Direitos, pessoas e rótulos

Esta skill orienta decisões editoriais. **Não é parecer jurídico.** Caso de risco real (acusação, uso comercial de obra de
terceiro, notificação recebida) vai ao Geovani, que decide se consulta advogado.

## 1. Material de terceiros

Para cada imagem, trecho de vídeo, música ou fonte tipográfica, anote **origem, autor, licença e data** no pacote
(`checagem.observacoes` ou um `direitos.md` em `extras`).

| Origem | Pode? | Como |
|---|---|---|
| Gravado ou criado pelo estúdio | sim | — |
| Gerado por IA pelo estúdio | sim, com rótulo | selo RECONSTITUIÇÃO IA ou ILUSTRAÇÃO |
| Domínio público verificado (ex.: documentos de governo dos EUA, obras com autor morto há mais de 70 anos no Brasil) | sim | crédito da fonte na tela; guarde a prova de domínio público |
| Licença aberta (Creative Commons) | conforme a licença | atribuição exigida; CC-NC não serve para uso comercial |
| Banco com licença paga ou gratuita documentada | conforme a licença | guarde o comprovante |
| Material de terceiro sem licença | **não, por padrão** | vira "Prévia privada" |

**Exceção registrada (D-111, Arquivo Oculto):** o Geovani autorizou, assumindo o risco ("eu me responsabilizo"), imagens
reais de cartas, documentos, fotos e materiais na versão pública, e inserts curtos e creditados dos vídeos de *A Chegada*,
sempre com crédito de origem na tela. Prefira o original em domínio público ao quadro com marca d'água. **Nunca o áudio
original de terceiros.** Esta exceção vale só para o Arquivo Oculto.

A Lei de Direitos Autorais (Lei 9.610/1998, art. 46) permite citação de trechos para crítica ou estudo, na medida
justificada e com indicação de autor e origem. Não existe "fair use" amplo no Brasil: citar não é usar a obra inteira
como trilha ou como imagem principal.

## 2. Pessoas

- **Pessoa identificável** em vídeo do estúdio: autorização de uso de imagem, ou fora do quadro, de costas, desfocada.
- **Paciente (Dr. Geovani): nunca.** Nem rosto, nem voz, nem nome, nem história reconhecível, mesmo com autorização. Isso
  também protege a ética profissional.
- **Criança:** a imagem é protegida pelo ECA (art. 17, preservação da imagem e da identidade), e o tratamento de dado de
  criança exige o melhor interesse dela e consentimento de um dos pais (LGPD, art. 14). Criança de terceiros: só com
  autorização escrita dos responsáveis, e no Dr. Geovani nunca paciente.
- **Princesa Melinda:** a personagem é inspirada na filha do Geovani. Regras extras na skill `video-animacao-infantil`:
  desenho estilizado, nenhum dado pessoal, referências reais só em `referencias_privadas/`.
- **Pessoa pública em fato real (Arquivo Oculto):** só de costas ou em silhueta, sem fala inventada. Nada de simular de
  forma realista político ou vítima.
- **Acusação:** nenhuma acusação a pessoa identificável sem documento que a individualize. Fale do fato e do órgão.

## 3. Rótulo de IA

- **Plataformas:** TikTok, Instagram/Facebook e YouTube exigem marcar conteúdo realista gerado ou alterado por IA (o nome
  do controle muda: "conteúdo gerado por IA", "conteúdo alterado ou sintético"). Marque ao postar. No pacote:
  `gerado_por_ia: true` e `post.rotulo_ia: true`.
- **Na tela:** cena encenada ou gerada leva o selo RECONSTITUIÇÃO IA ou ILUSTRAÇÃO, mesmo que o post esteja rotulado.
- **Arquivo Oculto:** rótulo sempre; a bio já diz "Personagem criado por IA".
- **Animação infantil:** desenho animado evidente não engana ninguém, mas declare o uso de IA na descrição, por
  transparência com as famílias.

## 4. Período eleitoral (@direitaxx sobretudo)

- Res. TSE 23.610/2019, art. 9º-B: propaganda eleitoral com conteúdo fabricado ou manipulado por IA precisa informar isso
  de modo explícito e destacado.
- Art. 9º-C: é vedado conteúdo fabricado ou manipulado para difundir fato inverídico ou descontextualizado, e é proibido
  usar conteúdo sintético que crie, substitua ou altere imagem ou voz de pessoa (deepfake) para prejudicar ou favorecer
  candidatura, mesmo com autorização da pessoa.
- Fora do período, a mesma prudência vale: o perfil é político e qualquer manipulação vira munição contra ele.
- Datas do calendário eleitoral: confira no TSE quando houver eleição no ano. Dúvida sobre se um vídeo é propaganda: o
  Geovani decide, com advogado se preciso.

## 5. Prévia privada

Quando algum material do vídeo tem direito pendente:
1. `checagem.direitos: pendente` (ou `so_privado`) no pacote.
2. A Central entrega ao app com o título "PRÉVIA PRIVADA · ..." e a nota "Não publicar".
3. Se der, produza também a versão pública sem o material (placeholder com selo IMAGEM RETIDA, ou paráfrase com fonte) como
   `video_b`, com `rotulo_a`/`rotulo_b` claros.

**A Prévia privada nunca vai para a rede.** Nem "só no story", nem "só por hoje".

## 6. Música

Ver `video-audio-mixagem`: biblioteca do app da rede para música popular; trilha embutida só com licença guardada; Content
ID pode derrubar vídeo dias depois de postado.

## Decisão rápida

```
Tem material de terceiro sem licença?          → Prévia privada (exceto a regra D-111 do Arquivo Oculto)
Tem paciente?                                    → não entra
Tem criança de terceiros sem autorização?        → não entra
Tem pessoa real acusada sem documento?           → não entra
Tem IA realista?                                 → rótulo na plataforma + selo na tela
É tema eleitoral com IA?                         → art. 9º-B e 9º-C; na dúvida, Geovani decide
```
