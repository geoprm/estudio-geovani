# Arquitetura da Central do Estúdio Geovani

*Criada em 11/11/2026 (decisão D-113 do `ECOSSISTEMA.md`).*

## O problema

O estúdio é um app (Artifact do Claude) com quatro perfis de vídeo, trabalhados por ferramentas diferentes:

- Claude Code (desktop e rotina na nuvem);
- Claude chat (claude.ai);
- Codex;
- ChatGPT.

Nenhuma delas lê a conversa da outra, e só o Claude Code consegue escrever no app. Sem um ponto comum, o trabalho feito num
chat fica preso naquele chat, e o app não fica sabendo que ele existe.

## A solução: uma caixa de entrada única e um formato único

```
 Codex ─────────┐  pasta + entrega.json          ┌──────────────────────────────────────────────┐
 Claude Code ───┤  (ferramentas/estudio.py novo) │  C:\Projetos\Estúdio Geovani  (a Central)    │
 ChatGPT ───────┤  .zip com entrega.json ───────►│                                              │
 Claude chat ───┤  (Geovani solta em entrada/)   │  entrada/ ──► receber ──► entregas/<perfil>/ │
 Geovani ───────┘  arquivos soltos               │     │  valida · QA técnico · hashes · livro   │
                                                 │     ▼                                        │
                                                 │  _app/video_app.mp4 · capa.jpg · doc_app.json│
                                                 └──────────────────┬───────────────────────────┘
                                                                    │ Claude Code:
                                                                    │ Artifact (upload de asset)
                                                                    │ ArtifactData (set do doc)
                                                                    ▼
                                         App "Estúdio Geovani" (Artifact MUNdJL4BwN9ovWQeVdboHt)
                                         pautas → aba Hoje · pedidos → aba Prontos
```

## Peças e responsabilidades

| Peça | Caminho | Responsabilidade |
|---|---|---|
| Caixa de entrada | `entrada/` | Recebe pacotes (pasta, .zip ou arquivos soltos). Recusado fica aqui com `_RECEPCAO.md` |
| Contrato do pacote | `esquemas/entrega.schema.json` | `estudio-geovani/entrega@1`: perfil, tipo, origem, arquivos, post, checagem, fontes, QA |
| Ferramenta | `ferramentas/estudio.py` | `novo`, `validar`, `receber`, `assets`, `publicado`, `qa`, `exportar`, `capa`, `skills`, `verificar` |
| Regras de validação | `ferramentas/pacote.py` | Fato com fonte, rótulo de IA, paciente e criança, direitos → Prévia privada |
| Mídia e QA técnico | `ferramentas/midia.py` | ffprobe, tela preta, imagem congelada, silêncio, loudness, faststart, versão do app ≤ 19 MiB |
| Ponte com o app | `ferramentas/app_docs.py` | Traduz o pacote em documento de `pedidos` ou `pautas` no formato do app v8 |
| Arquivo de entregas | `entregas/<perfil>/<AAAA-MM>/<id>/` | Pacote aceito + `recepcao.json` + `qa_estudio.json` + `_app/` |
| Livro de entregas | `registro/entregas.jsonl` | Um evento por linha, só acrescenta. Estado atual = último evento do id |
| Histórico de orientações | `orientacoes/<perfil>.md` | Instruções editoriais recebidas, por data |
| Perfis | `config/perfis/*.json` | Tom, visual, regras, onde cada perfil é trabalhado e por quem |
| App (cópia) | `app/` | Código da versão 8 publicada (`1793893451-76de`, hash em `config/app.json`) |
| Skills | `.claude/skills/` (fonte) → `.agents/skills/` (Codex) → `dist/skills/*.zip` (claude.ai) | Conhecimento de edição, narração, entrega e recepção |

## Estados de uma entrega

```
(entrada) ──receber──► aguardando_upload ──assets──► pronto_para_app ──set no app──► no_app
                  ├──► pronto_para_app (pauta, sem upload)
                  ├──► na_central (perfil fora do app, pauta do Arquivo sem cenas)
                  ├──► orientacao_registrada
                  └──► material_disponivel
```

## Por que assim

- **Disco como estado compartilhado.** É o único lugar que todas as ferramentas com disco enxergam. Os chats sem disco
  entregam um .zip que o Geovani solta na pasta.
- **Um formato, quatro tipos.** Vídeo pronto, pauta, material bruto e orientação cobrem o que os agentes produzem hoje, sem
  um formato por ferramenta.
- **A Central não move o motor.** `C:\Projetos\ARQUIVO OCULTO\estudio-gm` continua onde está: o Codex e o Claude Code
  trabalham nele, e ele está ligado a um GitHub público. A Central aponta para ele em `config/perfis/*.json`.
- **Publicar no app é um passo separado e consciente.** O upload e a gravação no banco do app passam pelo Claude Code,
  com aprovação das ferramentas. O agente olha os quadros antes. Nenhum outro agente escreve no app.
- **Mídia fora do Git.** Vídeo é pesado e pode ter direito ou imagem de terceiros. O Git guarda manifestos, relatórios e o
  livro de entregas.

## Limites conhecidos

- A rotina "Editor do Estúdio" roda na nuvem e não vê esta pasta. A recepção é local: alguém precisa pedir "receba as
  entregas" ao Claude Code (ou agendar uma tarefa local, se o Geovani quiser).
- 19 MiB por vídeo no app é o maior tamanho testado, não um limite documentado.
- O perfil Princesa Melinda não existe no app. As entregas dele ficam na Central até o perfil ser ativado.
- Codex lê as skills por `.agents/skills/`. Se a versão instalada do Codex não descobrir skills nesse caminho, o
  `AGENTS.md` lista cada skill com o caminho para leitura direta.
