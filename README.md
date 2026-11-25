# Estúdio Geovani — fábrica de vídeos

Motor de edição e produção de vídeos verticais para três perfis do Geovani Miranda:

| Perfil | O que é | Onde ler |
|---|---|---|
| **@direitaxx** | Liderança política e social no sertão da Bahia | `LEIA-ME.md`, `perfis.py` |
| **Dr. Geovani Miranda** | Fonoaudiologia: acolher, ensinar e guiar famílias | `LEIA-ME.md`, `perfis.py` |
| **Arquivo Oculto** | Investigação documental narrada pelo personagem fictício O Arquivista, 100% gerada por IA | `CLAUDE.md`, `VIDEO_PRODUCTION_PIPELINE.md` |

## O app

**Estúdio Geovani:** https://claude.ai/artifact/MUNdJL4BwN9ovWQeVdboHt

É um Artifact privado do Claude. O link abre só na conta do Geovani ou para quem ele compartilhar; o link sozinho não dá acesso.
O app reúne pautas, teleprompter, envio de vídeo, vídeos prontos e metas dos três perfis.

- O código da página publicada fica em `app/index.html`: versão 8, de 05/11/2026, com o perfil Arquivo Oculto V2 e o seletor de formato.
- A versão anterior está preservada em `app/index_original_v1793804553.html`.
- Pedidos, pautas e vídeos prontos ficam no banco e nos arquivos do próprio app, não neste repositório.
- O registro do que foi enviado está em `arquivo_oculto/producao/v2/entregas_app.json`.

## Estado atual

O estado detalhado está em `PROJECT_STATUS.md`. O que mudou, data a data, está em `CHANGELOG.md`, e o resultado de cada render em `QA_REPORT.md`.

## Arquivo Oculto V2: comandos

```bash
python -m arquivo_oculto.v2.perfil                                      # valida o perfil V2
python -m arquivo_oculto.v2.fabrica_v2 arquivo_oculto/producao/v2/AO-S01-E01.v2.json --modo public_release
python -m arquivo_oculto.v2.fabrica_v2 <manifesto> --modo private_preview --so-qa   # refaz só o QA
python -m arquivo_oculto.v2.entrega_app preparar AO-S01-E01                 # arquivos para o app
python tests/test_arquivo_oculto_v2.py
```

No Windows, use `.venv/Scripts/python`. O ambiente vem de `arquivo_oculto/instalar_ao.sh` (Kokoro, OpenCV, PyMuPDF e os modelos de voz), além do FFmpeg.

## O que não entra neste repositório (ele é público)

Ficam fora do Git, por regra do `.gitignore`:

- acervo com direitos em verificação (`arquivo_oculto/acervo_privado/`);
- referências privadas do personagem;
- cópias locais de documentos de domínio público;
- vídeos, áudios e modelos baixados;
- cache, `.env` e credenciais.

Vídeo de Arquivo Oculto só é publicado depois da revisão humana do Geovani. A versão "Prévia privada" nunca é publicada.
