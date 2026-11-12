---
name: video-cortes-reaproveitamento
description: Transforma vídeo longo, live, entrevista ou episódio em série de cortes curtos para os perfis do Estúdio Geovani. Cobre achar os melhores momentos pela transcrição, critérios de corte que se sustenta sozinho, gancho novo para cada corte, reenquadramento 16:9 para 9:16, numeração de série, calendário e lote de cortes com FFmpeg. Use quando houver material longo para render vários vídeos, ou quando o Geovani pedir mais cortes por dia.
---

# Cortes e reaproveitamento

Um vídeo longo bem decupado rende de 5 a 15 cortes. Mas corte só funciona se **se sustenta sozinho**: quem nunca viu o
original precisa entender e sentir algo em 30 a 60 s.

## 1. Achar os momentos

1. Transcreva o longo com tempos (`video-legendas`).
2. Leia a transcrição procurando:
   - **frase que é gancho natural** (pergunta forte, número, contradição, confissão, frase de efeito verdadeira);
   - **mini-história completa** (situação → virada → conclusão) em menos de 60 s;
   - **momento de emoção** genuína (riso, indignação, alívio);
   - **resposta direta** a uma dúvida comum do público.
3. Marque entrada e saída com folga de 0,5 s e dê uma nota de 1 a 5 para cada candidato.
4. Fique com os de nota 4–5. Corte de nota 3 enche calendário e cansa o público.

## 2. Critérios de um bom corte

- [ ] Entende-se sem o resto do vídeo (sem "como eu disse antes").
- [ ] Começa na frase forte, não na introdução dela.
- [ ] Termina numa conclusão, não no meio do raciocínio.
- [ ] **Não muda o sentido** do que foi dito no contexto original. Se o contexto muda o sentido, o corte não existe.
- [ ] Fato citado tem a fonte na tela, como no vídeo original.

## 3. Gancho novo

O começo do corte quase nunca é um gancho pronto. Opções, sem alterar a fala:
- texto de gancho na tela nos 2 primeiros segundos (`video-grafismos-motion`);
- reordenar trechos **só se** o sentido continuar idêntico (ex.: mostrar a conclusão primeiro como pergunta e depois o
  caminho), sempre com corte visível, nunca emenda escondida;
- começar pela imagem mais forte do trecho.

## 4. Reenquadrar

Material 16:9 para 9:16:
- uma pessoa falando: crop no rosto (`--enquadrar crop`), ajustando o x quando a pessoa não está no centro;
- duas pessoas: tela dividida vertical (uma em cima, outra embaixo) ou alternar o crop em quem fala;
- slide, documento ou cena larga: fundo desfocado (`--enquadrar blur`).

```bash
python ferramentas/estudio.py exportar corte_16x9.mp4 corte_9x16.mp4 --preset reels --enquadrar crop
```

## 5. Lote de cortes

Lista `cortes.csv` (`n;inicio;fim;titulo`) e um laço:

```bash
# PowerShell
Import-Csv cortes.csv -Delimiter ';' | ForEach-Object {
  ffmpeg -y -ss $_.inicio -to $_.fim -i longo.mp4 -c:v libx264 -crf 18 -preset fast -c:a aac -b:a 192k ("bruto_{0:D2}.mp4" -f [int]$_.n)
}
```

```bash
# bash
while IFS=';' read -r n ini fim titulo; do
  ffmpeg -y -ss "$ini" -to "$fim" -i longo.mp4 -c:v libx264 -crf 18 -preset fast -c:a aac -b:a 192k "bruto_$(printf %02d "$n").mp4"
done < <(tail -n +2 cortes.csv)
```

Depois, cada bruto passa por reenquadramento, legenda, grafismo, mix e QA como qualquer vídeo. Cada corte vira **um
pacote** de entrega, com `serie` igual e `titulo` próprio.

## 6. Série e calendário

- Nomeie a série e numere ("Fita 01", "Caso 03"): número cria hábito e dá vontade de ver o anterior.
- Espalhe os cortes de um mesmo longo em dias diferentes; não publique dois cortes do mesmo assunto no mesmo dia.
- A cadência e os horários são decisão do Geovani. O agente sugere; quem agenda e publica é ele.
- Registre na `orientacoes` do pacote a ordem sugerida e de qual longo veio cada corte.

## 7. Por perfil

- **@direitaxx:** cortes de discurso, entrevista ou sessão da câmara. Cuidado redobrado com sentido e contexto: corte
  político fora de contexto é a acusação mais fácil contra o perfil.
- **Dr. Geovani:** cortes de live ou aula, uma dúvida por corte, fecho com orientação de procurar avaliação.
- **Arquivo Oculto:** cortes de episódio longo com o selo de checagem preservado; cada corte tem o veredito do trecho.
- **Princesa Melinda:** cortes de história como Shorts, só momentos completos e alegres; sem chamada para comentar.
