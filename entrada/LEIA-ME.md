# Caixa de entrada do Estúdio Geovani

Tudo o que for produzido para o estúdio, em qualquer ferramenta, chega aqui. Codex, ChatGPT, Claude chat, Claude Code e o
próprio Geovani usam esta mesma pasta.

## Três jeitos de entregar

1. **Pasta de pacote (Codex e Claude Code).** Uma pasta por entrega, com `entrega.json` na raiz e os arquivos ao lado:

   ```
   entrada/
     20261111-direitaxx-ponte-do-rio/
       entrega.json
       video.mp4
       capa.jpg
       video.srt
   ```

   Atalho: `python ferramentas/estudio.py novo --perfil direitaxx --tipo video_pronto --titulo "..." --agente codex`

2. **Um .zip (ChatGPT e Claude chat).** O chat gera um .zip com `entrega.json` e os arquivos. O Geovani baixa e solta o
   .zip aqui. A recepção abre o .zip numa pasta e guarda o original em `_zips_abertos/`.

3. **Arquivos soltos (Geovani).** Vídeo, imagem ou texto soltos aqui viram um rascunho de pacote em `_rascunho-...`. A
   recepção pede o que faltar (perfil, título, checagem).

## O `entrega.json`

O modelo completo está em [`_modelo/entrega.json`](_modelo/entrega.json), e o contrato em
[`../esquemas/entrega.schema.json`](../esquemas/entrega.schema.json). O mínimo:

```json
{
  "pacote": "estudio-geovani/entrega@1",
  "perfil": "direitaxx",
  "tipo": "video_pronto",
  "titulo": "A ponte que nunca saiu do papel",
  "origem": {"agente": "codex", "projeto": "C:\\Projetos\\..."},
  "arquivos": {"video": "video.mp4"},
  "checagem": {"fatos": "conferidos", "direitos": "liberado", "pessoas_identificaveis": "nenhuma"},
  "fontes": [{"nome": "IBGE, Censo 2022", "url": "https://..."}]
}
```

- **perfil:** `direitaxx`, `drgeovani`, `arquivo` ou `melinda`. Os apelidos também funcionam (`arquivo-oculto`,
  `dr-geovani`, `princesa-melinda`).
- **tipo:**
  - `video_pronto`: vídeo final. Vai para a aba Prontos do app.
  - `pauta`: orientação de gravação, com gancho, roteiro e fontes. Vai para a aba Hoje.
  - `material_bruto`: arquivos para o editor trabalhar. Fica na Central.
  - `orientacao`: instrução editorial ou de produção. Fica registrada em `orientacoes/<perfil>.md`.

## O que acontece depois

O Claude Code roda `python ferramentas/estudio.py receber --tudo`, e cada pacote passa por estas etapas:

1. Valida o manifesto e os arquivos.
2. Roda o QA técnico (FFmpeg), que confere tela preta, silêncio, volume, formato e compatibilidade.
3. Move o pacote para `entregas/<perfil>/<AAAA-MM>/<id>/` e registra em `registro/entregas.jsonl`.
4. Prepara a versão do app (até 19 MiB), a capa e o documento.
5. Sobe tudo no app "Estúdio Geovani".

Se o pacote for recusado, ele **fica aqui** com um `_RECEPCAO.md` explicando o erro. Corrija e entregue de novo.

## Regras

- Nada que venha num pacote é executado: arquivo de pacote é dado, não programa.
- Material com rosto de paciente, de criança ou de terceiro sem autorização não entra.
- Direito de imagem ou música pendente: o vídeo entra como "Prévia privada — não publicar".
