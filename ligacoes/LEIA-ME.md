# Ligações: blocos para colar nos contratos dos outros projetos

A Central só funciona se os agentes que trabalham **em outras pastas** souberem que ela existe. Cada ferramenta lê o seu
contrato:

- Codex: `AGENTS.md` da pasta, ou o global `~/.codex/AGENTS.md`;
- Claude Code: `CLAUDE.md` da pasta e o global `~/.claude/CLAUDE.md`, que manda ler o `ECOSSISTEMA.md`;
- chats: as instruções do projeto.

**Aplicados em 11/11/2026, entre 21h17 e 21h19, com o OK do Geovani.** Cada bloco entrou no fim do arquivo, e o conteúdo
anterior foi preservado byte a byte, inclusive os fins de linha mistos do `AGENTS.md` do Arquivo Oculto. As cópias de antes
estão em [`antes_2026-11-11/`](antes_2026-11-11/). Para desfazer, apague a seção acrescentada no fim de cada arquivo, ou
restaure a cópia.

| Bloco | Aplicado em | Estado |
|---|---|---|
| [bloco_codex.md](bloco_codex.md) | `C:\Users\geopr\.codex\AGENTS.md` | aplicado; o arquivo estava vazio e agora também manda ler o `ECOSSISTEMA.md` |
| [bloco_codex.md](bloco_codex.md) | `C:\Projetos\ARQUIVO OCULTO\AGENTS.md` | aplicado no fim, com a menção a *O Índice Cego* |
| [bloco_claude_code.md](bloco_claude_code.md) | `C:\Projetos\ARQUIVO OCULTO\estudio-gm\CLAUDE.md` | aplicado no fim; sem commit (o repositório do motor é público) |
| `modelos/INSTRUCOES_PARA_CHATS.md` | instruções do projeto no ChatGPT e no claude.ai | **pendente: o Geovani cola** (nenhum agente tem acesso a essas configurações) |

Projeto novo de vídeo, com contrato próprio: acrescente o bloco correspondente no fim do contrato dele.

O Claude Code em qualquer pasta já fica sabendo da Central pelo `ECOSSISTEMA.md` (decisão D-113), que o `CLAUDE.md`
global manda ler.
