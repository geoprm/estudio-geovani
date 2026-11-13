# Estúdio Geovani — Central

A Central do estúdio de vídeo do Geovani Miranda. Tudo o que é produzido para os perfis, em qualquer ferramenta, chega
aqui; daqui vai para o app **Estúdio Geovani**.

| Perfil | Estado | O que é |
|---|---|---|
| **@direitaxx** | ativo | Liderança política e social em Xique-Xique e no sertão da Bahia |
| **Dr. Geovani Miranda** | ativo | Fonoaudiologia: acolher, ensinar e guiar famílias |
| **Arquivo Oculto** | ativo | Investigação documental narrada pelo Arquivista, 100% IA |
| **Princesa Melinda** | planejado | Historinhas animadas infantis para o YouTube |

## Como usar (Geovani)

- **Recebeu algo de um chat (ChatGPT ou Claude)?** Baixe o .zip e solte em `entrada\`. Depois peça ao Claude Code:
  *"receba as entregas do estúdio"*.
- **Quer que um chat entregue no formato certo?** Cole o bloco de `modelos\INSTRUCOES_PARA_CHATS.md` no começo da conversa.
- **Quer as skills no claude.ai?** Peça ao Claude Code para rodar `python ferramentas/estudio.py skills` e envie os .zip de
  `dist\skills\` na área de skills das configurações do claude.ai.
- **Quer saber o que está pendente?** Peça: *"status do estúdio"*.

O app: https://claude.ai/artifact/MUNdJL4BwN9ovWQeVdboHt (privado; só abre na sua conta).

No GitHub, a Central é a branch `central` do repositório **público** `geoprm/estudio-geovani`; a `main` dele é o motor.
Mídia, caixa de entrada, referências privadas e o material da Princesa Melinda ficam fora do Git.

## Como usar (agentes)

- Claude Code: [`CLAUDE.md`](CLAUDE.md).
- Codex e outros: [`AGENTS.md`](AGENTS.md).
- Ponto de entrada de qualquer pedido de vídeo: a skill `estudio-orquestrador`.

## O que tem aqui

```
entrada/          caixa de entrada (pacotes, .zip, arquivos soltos)
entregas/         pacotes aceitos, por perfil e mês (mídia fora do Git)
registro/         livro de entregas (entregas.jsonl)
orientacoes/      instruções editoriais recebidas, por perfil
config/           perfis, app e agentes
esquemas/         contrato do pacote de entrega
ferramentas/      estudio.py (recepção, QA, exportação, skills)
.claude/skills/   16 skills de edição, narração, entrega e recepção (fonte)
.agents/skills/   cópia das skills para o Codex (gerada)
modelos/          instruções para os chats
ligacoes/         blocos para colar nos contratos dos outros projetos
app/              código do app (versão 8 publicada)
docs/             arquitetura, decisões e changelog
tests/            testes da Central
```

## Skills

| Skill | Para quê |
|---|---|
| `estudio-orquestrador` | Por onde começar qualquer pedido de vídeo |
| `estudio-pacote-entrega` | Entregar na Central (qualquer ferramenta) |
| `estudio-recepcao` | Receber e subir no app (Claude Code) |
| `video-roteiro-storyboard` | Gancho, roteiro, storyboard, decupagem |
| `video-montagem-edicao` | Corte, ritmo, reenquadramento, receitas FFmpeg |
| `video-narracao-voz` | Texto para voz, gravação, TTS Kokoro, tratamento de voz |
| `video-audio-mixagem` | Trilha, efeitos, ducking, loudness, licença |
| `video-legendas` | Transcrição, legenda queimada, SRT/ASS, zona segura |
| `video-cor-acabamento` | Cor, look por perfil, retoque, nitidez |
| `video-grafismos-motion` | Títulos, selos de checagem, lower third, Ken Burns |
| `video-capas-miniaturas` | Capa vertical e miniatura do YouTube |
| `video-cortes-reaproveitamento` | Série de cortes a partir de vídeo longo |
| `video-exportacao-plataformas` | Formato por rede, versão do app, texto do post |
| `video-qa` | Controle de qualidade técnico e editorial |
| `video-direitos-rotulos` | Direitos, rótulo de IA, paciente, criança, eleição |
| `video-animacao-infantil` | Princesa Melinda |

## Regras de ouro

1. Você posta. Nenhum agente publica por você.
2. Revisão humana antes de qualquer publicação. "Prévia privada" nunca vai para a rede.
3. Fato só com fonte. Nenhum corte que mude o sentido do que alguém disse.
4. Paciente nunca aparece. A criança é protegida acima da audiência.
5. Nenhum gasto sem a sua autorização.

Arquitetura completa: [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).
