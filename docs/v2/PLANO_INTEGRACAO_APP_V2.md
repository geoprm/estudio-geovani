# Plano de integração da V2 ao app e à rotina (NÃO aplicado — aguarda autorização do Geovani)

Hoje a fábrica V2 roda localmente (Claude Code no PC). O app "Estúdio Geovani" e a rotina "Editor do Estúdio" continuam
gerando os episódios pelo caminho V1 (`arquivo/LEIA-ME.md` → `fabrica.py`/`motor.py`). Levar a V2 para lá muda um app em uso e
uma tarefa agendada, por isso cada passo abaixo precisa de um "sim" explícito.

## O problema de onde guardar o código

A rotina roda na nuvem e só enxerga duas coisas: o GitHub `geoprm/estudio-geovani` (**público**) e os arquivos do próprio app.

| Opção | Como | Risco |
|---|---|---|
| A. Publicar `arquivo_oculto/v2/*.py`, o perfil, o lock e os manifestos dentro do app em `arquivo/v2/` | Artifact publish com `files`; a página do app continua igual | Baixo: os arquivos ficam privados. Exige republicar o Artifact (lendo antes a versão viva) |
| B. Commit + push no GitHub, sem `acervo_privado/` e sem `referencias_privadas/` | `git add` seletivo + push numa branch | O código fica público (não há segredo nele). O acervo com direitos pendentes **não pode** ir |
| C. Ficar local | Gerar no PC e enviar o MP4 ao app como pedido pronto | Nenhum: só escreve um pedido novo no banco do app (ainda assim pede autorização) |

Recomendação: **C agora** (entregar o EP01/EP02 V2 no app como pedidos novos, sem tocar na página nem na rotina) e **A** quando
a voz e o visual forem aprovados. O acervo privado (arte oficial, snapshots) iria para o armazenamento de arquivos do app, nunca para o GitHub.

**Atenção antes de qualquer push (opção B):** `arquivo_oculto/assets/arquivista.png` é a arte canônica do personagem (marca do
canal). Num repositório público ela fica disponível para qualquer pessoa copiar. As alternativas são tornar o repositório privado ou
tirar a imagem do Git e guardá-la só no app. A decisão é do Geovani.

## Mudanças na página do app (opção A)

1. No perfil Arquivo, um seletor de formato com seis botões: Reel 30s, Investigação 90s (padrão), Reel Profundo, YouTube 5min, YouTube 10min e Microdrama. O formato escolhido é gravado em `pedido.formatoAO`.
2. Um campo `pedido.modoRender`: `private_preview` (padrão) ou `public_release`.
3. Em Prontos, os dois arquivos aparecem: `video.mp4` (master) e `video_app.mp4` (até 19 MiB, que é o que o player usa).

## Texto para a rotina (passo 3A V2, para colar só quando autorizado)

> 3A-V2. ARQUIVO OCULTO, formato "ia" com `pedido.formatoAO` presente: baixe do app `arquivo/v2/` (código, perfil, lock, manifestos)
> e `arquivo/acervo/` (fontes salvas). Instale pelo PyPI: numpy, pillow, opencv-python-headless, onnxruntime, soundfile e kokoro-onnx.
> Baixe a voz Kokoro das releases oficiais. Rode
> `python -m arquivo_oculto.v2.fabrica_v2 <manifesto> --modo <pedido.modoRender>`.
> Só marque "pronto" se `status.json` terminar em `completed`. Envie `video_app.mp4` como resultado.a e `cover.png` como capa.
> Caso novo: escreva o manifesto V2 com fontes lidas e claims classificados. Se não conseguir verificar, grave o pedido como erro explicando o que faltou e nunca renderize um rascunho.

## O que a V2 não resolve sozinha

- **Gesto de mão real e caminhada de corpo inteiro:** exigem um provedor image-to-video, hoje bloqueado (Canva pago, Figma Weave sem vínculo, sem chaves). Custo e escolha são decisões do Geovani.
- **Versão pública com arte oficial:** exige licença ou revisão humana documentada do uso (citação crítica).
