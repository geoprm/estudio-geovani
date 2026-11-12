# Decisões da Central do Estúdio Geovani

Decisão que não está escrita aqui (ou no `ECOSSISTEMA.md`) não existe: será tomada de novo, provavelmente de outro jeito.

## C-001 · 11/11/2026 · A Central é uma pasta própria, separada do motor

Pedido do Geovani: criar uma pasta e um repositório para o estúdio (que nasceu como Artifact) e ligar a ele o que é
produzido no Codex, no ChatGPT, no Claude chat e no Claude Code.

- A Central fica em `C:\Projetos\Estúdio Geovani`, com repositório Git local (`main`, sem commit até o Geovani pedir).
- O motor `C:\Projetos\ARQUIVO OCULTO\estudio-gm` **não foi movido**: o Codex tinha edições abertas nele nesta data, e ele
  é ligado ao GitHub público `geoprm/estudio-geovani`. A Central aponta para ele.
- Remoto, se houver, deve ser **privado**: a Central vai guardar material da Princesa Melinda e orientações internas.

## C-002 · 11/11/2026 · Formato único de entrega `estudio-geovani/entrega@1`

Quatro tipos (`video_pronto`, `pauta`, `material_bruto`, `orientacao`), um manifesto (`entrega.json`), três jeitos de chegar
(pasta, .zip, arquivos soltos). Regras duras na recepção:

- fato marcado como conferido exige fonte;
- vídeo gerado por IA exige rótulo;
- paciente ou criança pendente recusa o pacote no Dr. Geovani e na Princesa Melinda;
- direito pendente vira "PRÉVIA PRIVADA · Não publicar" no app;
- QA técnico `fail` recusa.

## C-003 · 11/11/2026 · Só o Claude Code publica no app

Upload de asset (`Artifact`) e documento (`ArtifactData`) só pelo Claude Code, depois de olhar os quadros. Codex e chats
param na validação. Pacote é dado: nada que venha nele é executado.

## C-004 · 11/11/2026 · Skills com uma fonte só

Fonte em `.claude/skills/`, espelho gerado para o Codex em `.agents/skills/` e .zip para o claude.ai em `dist/skills/`
(`python ferramentas/estudio.py skills`). O teste confere a paridade. As skills `arquivo-oculto-*` do motor têm precedência
para aquele perfil.

## C-005 · 11/11/2026 · Princesa Melinda registrada como perfil planejado

Perfil `melinda` com regras de proteção da criança desde já:

- desenho estilizado;
- referências reais só em `referencias_privadas/` (fora do Git);
- nenhum dado pessoal;
- voz da criança não usada sem decisão expressa;
- conteúdo marcado "para crianças" no YouTube.

Ficam com o Geovani: nome público, faixa etária, voz, inclusão no app e criação do canal.

## C-006 · 11/11/2026 · Contratos dos outros projetos ligados à Central

Com o OK do Geovani ("Sim, aplique"), o bloco da Central entrou no fim de três contratos:

- `~/.codex/AGENTS.md`, que estava vazio. Agora também manda o Codex ler o `ECOSSISTEMA.md`.
- `C:\Projetos\ARQUIVO OCULTO\AGENTS.md`.
- `C:\Projetos\ARQUIVO OCULTO\estudio-gm\CLAUDE.md`, sem commit, porque o repositório é público.

O conteúdo anterior foi preservado byte a byte. Cópias em `ligacoes/antes_2026-11-11/`.

## C-007 · 12/11/2026 · Produção do Arquivo Oculto passa pela Central

A sessão do Claude Code do motor entregou a orientação "Passagem do Arquivo Oculto para o Estúdio", atribuída a pedido do
Geovani nesta data. A partir dela:

- os vídeos do perfil chegam à Central como pacote;
- a sessão do motor fica com o site e conclui antes os 25 Dossiês, em lotes.

Registrado em `orientacoes/arquivo.md` e no perfil (`passagem_2026_11_12`). A confirmação direta do Geovani está pendente.
Os posts já agendados por aquela sessão (TikTok e YouTube) seguem sob a autorização registrada no ECOSSISTEMA
(D-110 a D-112). A regra desta Central não muda: nenhum post novo sem pedido explícito do Geovani.

## C-008 · 12/11/2026 · O repositório do GitHub `geoprm/estudio-geovani` é do motor, não da Central

Ele é **público** e a rotina "Editor do Estúdio" depende dele. A Central guarda o código do app privado, orientações
internas e, no futuro, material da Princesa Melinda. Por isso não vai para esse repositório sem decisão do Geovani. O
privado `geoprm/CentralEditorialGM` é outro projeto (app administrativo de pautas em Next.js) e também não serve.

## Pendentes (decisão do Geovani)

1. Onde fica o remoto da Central: repositório novo e privado (recomendado) ou dentro do `geoprm/estudio-geovani` (público).
2. Confirmar quem trabalha cada perfil no ChatGPT e no Claude chat (campos "a confirmar" em `config/perfis/`).
3. Colar `modelos/INSTRUCOES_PARA_CHATS.md` nas instruções dos projetos do ChatGPT e do claude.ai.
4. Recepção automática (tarefa agendada local) ou só sob pedido.
