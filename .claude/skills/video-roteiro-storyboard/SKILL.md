---
name: video-roteiro-storyboard
description: Escreve roteiro de vídeo curto ou longo e transforma em storyboard e lista de planos para os perfis do Estúdio Geovani. Cobre briefing, gancho dos primeiros 3 segundos, estrutura por duração, contagem de palavras para narração em português, decupagem, ganchos A/B e chamada final. Use antes de gravar, narrar ou montar qualquer vídeo, ou para revisar um roteiro que não está segurando a atenção.
---

# Roteiro e storyboard

Roteiro de vídeo curto não é texto: é uma **sequência de promessas cumpridas**. Cada bloco tem que pagar o anterior e
abrir o próximo.

## 1. Briefing em cinco linhas (antes de escrever qualquer frase)

```
Perfil:      direitaxx | drgeovani | arquivo | melinda
Objetivo:    o que a pessoa sabe, sente ou faz ao final (UMA coisa)
Público:     quem para de rolar o dedo por isso, e por quê
Prova:       o dado, documento, imagem ou demonstração que sustenta o vídeo (com fonte)
Formato:     duração-alvo, proporção (9:16 ou 16:9), rede principal
```

Sem prova, não há vídeo: há opinião. Para @direitaxx e Arquivo Oculto, a prova vai **na tela**, não só na fala.

## 2. Gancho (0 a 3 s)

O gancho tem três trabalhos: parar o polegar, prometer algo específico e ser verdade. Fórmulas que funcionam sem mentir:

| Fórmula | Exemplo fiel |
|---|---|
| Número concreto + consequência | "Quase metade das casas da cidade não tem esgoto. Olha o que isso custa." |
| Pergunta que o público já se fez | "Seu filho de 2 anos fala pouco. Quando é hora de se preocupar?" |
| Contradição documentada | "Em 1962, militares americanos propuseram atacar o próprio país. Está no papel." |
| Começar no meio da ação | Primeira imagem já é a prova (o documento, o buraco na rua, a carta). |
| Erro comum corrigido | "Não é preguiça de falar. É outra coisa." |

Regras do gancho:
- **Fiel ao dado.** 46,8% é "quase metade", nunca "a maioria".
- Sem introdução, sem "oi gente", sem logo animado antes da primeira frase.
- Imagem e fala dizem a mesma coisa no primeiro segundo. Texto na tela até 5 palavras.
- Escreva **dois ganchos** (A e B). O pacote leva os dois quando der para gravar os dois.

Aberturas fixas: Arquivo Oculto abre com "Olá, criancinhas..." (regra do canal); @direitaxx fecha com
"Aqui é o sertão falando." três vezes.

## 3. Estrutura por duração

Narração em português brasileiro, ritmo natural de rede: **2,4 a 2,8 palavras por segundo** (cerca de 150 por minuto).
Calcule antes de gravar: roteiro longo demais é cortado na montagem, e quase sempre perde a lógica.

| Duração | Palavras | Estrutura |
|---|---|---|
| 15–30 s | 35–80 | Gancho (3 s) → 1 fato com prova → virada ou consequência → fecho |
| 45–60 s | 110–160 | Gancho → contexto mínimo → prova 1 → prova 2 ou exemplo → o que fazer / o que significa → fecho |
| 60–90 s | 150–240 | Gancho → pergunta central → 3 blocos de evidência (um por cena) → virada → resposta → chamada |
| 3–8 min (YouTube) | 450–1200 | Gancho de 15 s com promessa → mapa do vídeo em uma frase → capítulos de 60–90 s, cada um com mini-gancho → síntese → chamada |

**Reengate a cada 7–10 s** no vídeo curto: novo plano, nova informação, pergunta, número na tela. Se em 10 s nada mudou na
imagem, a pessoa já foi embora.

## 4. Fecho e chamada

- Feche a promessa do gancho. Vídeo que promete e não entrega queima o perfil.
- Uma chamada só, coerente com o objetivo: salvar, compartilhar, comentar uma pergunta concreta, seguir a série.
- Dr. Geovani: o fecho de alerta sempre orienta "procure avaliação de um fonoaudiólogo", sem assustar.
- Princesa Melinda: sem chamada para comentar ou clicar (conteúdo para crianças). Ver `video-animacao-infantil`.

## 5. Do roteiro ao storyboard

Quebre o roteiro em **planos** (unidade de corte). Cada plano tem uma função. Formato que o resto do estúdio entende:

```json
{
  "titulo": "Quando a fala atrasa",
  "perfil": "drgeovani",
  "formato": "reel_60",
  "planos": [
    {"n": 1, "t": "0.0-2.8", "funcao": "gancho", "fala": "Seu filho de 2 anos fala pouco?",
     "imagem": "Geovani em close, olhar na lente", "tela": "FALA POUCO AOS 2?", "som": "sem trilha nos 2 primeiros s"},
    {"n": 2, "t": "2.8-7.0", "funcao": "contexto", "fala": "...", "imagem": "b-roll: brinquedos no chão (próprio)",
     "tela": "", "selo": "", "fonte": ""}
  ]
}
```

Campos: `funcao` (gancho, contexto, prova, virada, exemplo, resposta, chamada), `imagem` (o que se vê e a **origem**:
gravado, próprio, domínio público, gerado por IA), `tela` (texto curto), `selo` (DOCUMENTADO, RECONSTITUIÇÃO IA, ILUSTRAÇÃO,
FONTE: veículo e data), `fonte` (de onde vem o fato daquele plano).

Duração de plano em vídeo curto: **1,5 a 4 s**. Plano parado acima de 4 s precisa de movimento (Ken Burns, zoom lento,
grafismo entrando). Arquivo Oculto: o Arquivista fica 12–28% do tempo em tela e nenhum plano dele passa de 4 s.

## 6. Decupagem de material gravado

Quando o Geovani grava e manda o bruto: transcreva (`video-legendas`), marque as frases boas com tempo de entrada e saída,
classifique por função, descarte tropeços e repetições, e monte o roteiro a partir do que **foi dito**. Nunca junte duas
frases de modo que mudem o sentido do que ele quis dizer.

## 7. Checklist do roteiro

- [ ] O gancho é verdade e cabe em 3 s.
- [ ] Cada fato tem fonte anotada no plano.
- [ ] A contagem de palavras cabe na duração.
- [ ] Há reengate a cada 7–10 s.
- [ ] O fecho paga a promessa do gancho.
- [ ] O tom bate com `config/perfis/<id>.json`.
- [ ] Nada que exponha paciente, criança ou terceiro.

Exemplos completos por perfil: [references/exemplos-por-perfil.md](references/exemplos-por-perfil.md).
