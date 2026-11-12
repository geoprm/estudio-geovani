---
name: video-animacao-infantil
description: Planeja e produz historinhas animadas do canal infantil Princesa Melinda (perfil planejado do Estúdio Geovani), estreladas por uma personagem desenhada inspirada na filha do Geovani. Cobre proteção da criança, ficha de personagem e consistência visual, bíblia do mundo, roteiro infantil em três atos, storyboard, animação 2.5D por camadas, narração e música para crianças, exportação e marcação de conteúdo para crianças no YouTube. Use para qualquer trabalho da Princesa Melinda, da ideia ao pacote de entrega.
---

# Princesa Melinda — historinhas animadas

**Estado:** perfil planejado (`config/perfis/melinda.json`, `status: planejado`). Ainda não existe no app, não tem canal e
não tem motor. Tudo aqui é o pipeline proposto; as decisões marcadas **[Geovani]** são dele.

## 0. A criança vem antes de tudo

A personagem é inspirada numa criança real, filha do Geovani. Regras que nenhuma meta de audiência muda:

1. **Desenho estilizado**, nunca fotorrealista. A personagem lembra a criança no espírito (cabelo, cor favorita, um
   acessório), não reproduz o rosto.
2. **Referências reais** (fotos e vídeos da filha) ficam só em `referencias_privadas/melinda/` nesta Central, que está fora
   do Git. Nunca em pasta sincronizada pública, nunca enviadas a serviço de terceiro sem decisão do Geovani, nunca no
   pacote de entrega.
3. **Nenhum dado pessoal** no vídeo, na descrição, nas tags, no nome de arquivo ou nos metadados: sobrenome, escola,
   cidade, bairro, rotina, data de nascimento, rosto real, voz real.
4. **Voz:** **[Geovani]** decide entre TTS, a voz dele ou dubladora contratada. A voz da criança não é usada nem clonada sem
   decisão expressa dele, registrada em `docs/DECISIONS.md`.
5. Nome público do canal e da personagem: **[Geovani]**. Se "Melinda" é o nome real dela, ele decide se mantém.
6. Revisão humana do Geovani antes de qualquer publicação.

## 1. Bíblia do canal (fazer uma vez, antes do episódio 1)

Crie `config/perfis/melinda/BIBLIA.md` com:
- **Público:** faixa etária **[Geovani]**. Sugestão: 3 a 6 anos, com pais assistindo junto.
- **Promessa do canal:** em uma frase (ex.: "toda história, uma pequena coragem nova").
- **Personagem principal:** personalidade (curiosa, gentil, às vezes teimosa), o que ela quer, o que a faz rir, o
  bordão (curto, repetível).
- **Elenco fixo:** 2 a 3 coadjuvantes (um bichinho, um amigo, um adulto que acolhe). Poucos e reconhecíveis.
- **Mundo:** 3 a 5 cenários fixos reaproveitáveis (quarto, jardim, castelo do bairro, floresta clara).
- **Paleta e traço:** 6 a 8 cores fixas; contorno, sombra e textura definidos. Nada de neon nem cortes rápidos.
- **O que nunca acontece:** perigo imitável (subir em janela, tomar remédio, mexer em tomada), violência, medo como
  diversão, vergonha, estereótipo, comida ou produto de marca.

## 2. Ficha de personagem (consistência visual)

Sem ficha, a personagem muda de rosto a cada cena, e criança percebe. Monte `config/perfis/melinda/personagem/`:
- **Turnaround:** frente, 3/4, perfil, costas, na mesma escala.
- **Expressões:** alegre, surpresa, triste, brava, pensativa, com sono, rindo.
- **Bocas (visemas):** fechada, A/E aberta, O/U arredondada, M/B/P fechada pressionada, F/V. Bastam 5 a 6 para leitura labial
  convincente.
- **Poses-chave:** andando, correndo, apontando, abraçando, sentada.
- **Partes separadas em camadas** (cabeça, olhos, boca, braços, cabelo, roupa), PNG transparente, para animar por camadas.

Geração com IA de imagem: use a ficha aprovada como referência fixa em toda imagem e registre ferramenta, modelo, prompt e
data em `personagem/procedencia.json`. Ferramenta paga ou com créditos: só com autorização e custo estimado. Nunca envie a
foto real da criança a um gerador; envie o desenho já aprovado.

## 3. Roteiro infantil

Duração-alvo: **3 a 6 min** (16:9) por história; Shorts de até 60 s com um momento completo.

Estrutura em três atos curtos:
1. **Mundo e desejo** (até 20%): a personagem quer algo pequeno e concreto.
2. **Obstáculo e tentativas** (60%): três tentativas (regra de três: a criança antecipa a terceira e adora acertar).
3. **Solução e aprendizado** (20%): ela resolve com uma qualidade dela, não por mágica gratuita. O aprendizado aparece
   na ação, nunca em sermão.

Linguagem:
- frases de até 8–10 palavras, vocabulário do dia a dia, uma palavra nova por história explicada pelo contexto;
- **repetição deliberada:** bordão, refrão, a mesma fala a cada tentativa;
- pergunta ao público com pausa ("Onde será que ela escondeu?" + 2 s), sem pedir comentário;
- ritmo calmo: plano de 3 a 6 s; nada de cortes de 1 s.

Roteiro em tabela (cena, fala de cada personagem, ação, emoção, cenário). A partir dele, o storyboard segue o formato da
skill `video-roteiro-storyboard`.

## 4. Produção (pipeline proposto, 2.5D por camadas)

1. **Cenários:** imagem fixa por cenário, em camadas (fundo, meio, frente) para paralaxe.
2. **Personagem por camadas:** posição, escala e rotação animadas por tempo; piscar a cada 3–5 s; respiração sutil.
3. **Boca:** troca de visema guiada pelo áudio (fonemas da narração ou amplitude). O motor do Arquivo Oculto já anima em
   camadas (`performance_2_5d`); é a base técnica natural para um motor da Melinda, adaptado ao traço infantil.
4. **Movimento de câmera:** paralaxe lenta, zoom suave; nunca tremido.
5. **Vídeo generativo** (imagem para vídeo por IA): opcional, para planos especiais, sempre a partir de quadro aprovado da
   ficha, com rótulo e custo autorizado.

## 5. Som

- Narração calorosa, ritmo de 2,0 a 2,3 palavras por segundo (mais lento que adulto).
- Vozes de personagem distintas pelo timbre e pela energia (TTS Kokoro tem `pf_dora`, `pm_alex`, `pm_santa`; ajuste fino na
  skill `video-narracao-voz`).
- Música simples e alegre, sob a narração, com ducking (`video-audio-mixagem`); música cantada só com letra própria.
- Efeitos suaves (plim, passos, folhas). Nada de susto sonoro.
- Loudness −14 LUFS; sem picos.

## 6. YouTube

- Marcar **"Sim, é conteúdo para crianças"** no YouTube Studio. É exigência da plataforma (COPPA): desliga comentários,
  anúncios personalizados e alguns recursos. Não tente contornar.
- Título simples e descritivo, sem caixa alta gritada; miniatura com a personagem alegre (`video-capas-miniaturas`).
- Descrição curta, sem link externo, sem dado pessoal, com a declaração de uso de IA.
- Playlists por tema ("Coragem", "Amizade", "Hora de dormir").

## 7. Entrega

Pacote `video_pronto` (ou `material_bruto` para ficha e cenários) com `perfil: melinda`,
`checagem.pessoas_identificaveis: nenhuma`, `gerado_por_ia: true`, `post.rotulo_ia: true`. Enquanto o perfil não existir no
app, a recepção guarda na Central (`na_central`).

## Para ativar o perfil (lista do Geovani)

- [ ] Decidir nome público, faixa etária e voz.
- [ ] Aprovar a bíblia e a ficha de personagem.
- [ ] Autorizar a inclusão do perfil `melinda` no app (republicar o Artifact).
- [ ] Criar o canal no YouTube (ato dele).
- [ ] Decidir orçamento, se algum, para geração de imagem ou vídeo por IA.
