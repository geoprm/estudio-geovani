---
name: estudio-pacote-entrega
description: Monta o pacote de entrega (entrega.json + arquivos) que leva um vídeo, uma pauta, material bruto ou uma orientação até a caixa de entrada do Estúdio Geovani. Use ao terminar qualquer trabalho para os perfis do estúdio, em qualquer ferramenta (Codex, Claude Code, ChatGPT, Claude chat), ou quando o Geovani pedir para "mandar para o estúdio".
---

# Pacote de entrega do Estúdio Geovani

A Central só reconhece trabalho que chega como **pacote**: uma pasta (ou um .zip) com `entrega.json` na raiz e os arquivos
citados ao lado. Caixa de entrada: `C:\Projetos\Estúdio Geovani\entrada\`.

Contrato: `esquemas/entrega.schema.json`. Exemplo completo: `entrada/_modelo/entrega.json`.

## Passo a passo

### Quem tem disco (Codex, Claude Code)

```bash
cd "C:\Projetos\Estúdio Geovani"
python ferramentas/estudio.py novo --perfil drgeovani --tipo video_pronto --titulo "Quando a fala atrasa" --agente codex --projeto "C:\minha\pasta"
# copie video.mp4, capa.jpg e video.srt para a pasta criada; complete o entrega.json
python ferramentas/estudio.py validar "entrada\20261111-drgeovani-quando-a-fala-atrasa"
```

Repita `validar` até sair `OK`. **O Codex para aqui.** O Claude Code segue com a skill `estudio-recepcao`.

### Quem não tem disco (ChatGPT, Claude chat)

Gere um .zip `AAAAMMDD-perfil-titulo.zip` com `entrega.json` e os arquivos. Se não conseguir gerar arquivo, mostre o
`entrega.json` em bloco de código e liste os arquivos que o Geovani deve juntar. Instruções para colar no chat:
`modelos/INSTRUCOES_PARA_CHATS.md`.

## Escolha o tipo

| tipo | Use quando | Vai para |
|---|---|---|
| `video_pronto` | o vídeo está finalizado e conferido | aba Prontos do app |
| `pauta` | é uma orientação de gravação: tema, gancho, roteiro, fontes | aba Hoje do app |
| `material_bruto` | são arquivos para alguém editar (gravação crua, b-roll, narração, imagens) | fica na Central |
| `orientacao` | é instrução editorial ou de produção (mudança de tom, feedback, briefing de série) | `orientacoes/<perfil>.md` |

## Preencha com honestidade (é aqui que o pacote é recusado)

- `checagem.fatos`: `conferidos` **só** se cada número, data, nome e citação foi conferido na fonte, e as fontes estão em
  `fontes`. Sem fato no vídeo: `sem_fatos`. Não conferiu: `pendente`, e vídeo pronto com fato pendente é recusado.
- `checagem.direitos`: `liberado` só com origem e licença de cada imagem, trecho e música. Na dúvida, `pendente`: o vídeo
  entra como "Prévia privada — não publicar".
- `checagem.pessoas_identificaveis`: no Dr. Geovani e na Princesa Melinda, `pendente` recusa o pacote.
- `gerado_por_ia: true` exige `post.rotulo_ia: true`.
- Não invente URL de fonte. Fonte sem URL vai só com o nome.
- `orientacoes`: escreva para o Geovani, não para outro agente. O que revisar, em que minuto, quando postar, o que fixar.

## Arquivos

- `video`: MP4 H.264/AAC, 1080x1920 para formatos verticais. Exporte com `video-exportacao-plataformas`.
- `capa`: JPG ou PNG 1080x1920 (opcional; sem ela a recepção escolhe um quadro).
- `legendas`: SRT conferido contra a fala (opcional, recomendado).
- `video_b` + `rotulo_a`/`rotulo_b`: duas versões para comparar (ex.: "Gancho A", "Gancho B").
- `roteiro`: MD ou TXT com o texto final.
- Nome de arquivo sem acento e sem espaço. Caminho sempre relativo à pasta do pacote.

## Pauta (tipo `pauta`)

Campos do bloco `pauta`, no formato que o app mostra: `data` (AAAA-MM-DD, dia em que a pauta aparece), `abertura_a` (gancho
principal), `abertura_b`, `fato`, `prova` (o que mostrar na tela como prova), `cuidado` (o que não dizer), `roteiro` (lista de
`{tempo, fala}`), `nota` (0 a 5, chance de viralizar). Pauta do Arquivo Oculto só vai ao app com `cenas` no formato do motor
(`app/arquivo/LEIA-ME.md`); sem isso fica na Central.

## Antes de entregar, confira

- [ ] `validar` saiu OK (ou o JSON foi conferido campo a campo, se você é um chat).
- [ ] QA da skill `video-qa` feito, com o status em `qa.status`.
- [ ] Legenda do post pronta e sem promessa que o vídeo não cumpre.
- [ ] Nada de dado pessoal de paciente ou criança em arquivo, legenda ou metadado.
