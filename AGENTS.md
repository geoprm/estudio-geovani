# Central do Estúdio Geovani — contrato para o Codex (e qualquer agente)

Esta pasta recebe tudo o que é produzido para os perfis de vídeo do Geovani Miranda e entrega ao app "Estúdio Geovani".
**Você entrega aqui; quem publica no app é o Claude Code.**

Leia antes: `C:\Users\geopr\ECOSSISTEMA.md` (decisão D-113), `docs/ARQUITETURA.md` e o perfil em `config/perfis/<perfil>.json`.

## Como entregar (o essencial)

1. Crie o pacote:
   `python ferramentas/estudio.py novo --perfil <direitaxx|drgeovani|arquivo|melinda> --tipo <video_pronto|pauta|material_bruto|orientacao> --titulo "..." --agente codex --projeto "<sua pasta>"`
2. Ponha os arquivos na pasta criada em `entrada/` e complete o `entrega.json` (modelo em `entrada/_modelo/entrega.json`).
3. Confira: `python ferramentas/estudio.py validar entrada/<pasta>`. Corrija até sair `OK`.
4. Pare aí. Não rode `receber`, `assets` nem `publicado`: isso é do Claude Code, que tem acesso ao app.

Detalhe completo na skill `estudio-pacote-entrega`.

## Skills

As skills ficam em `.agents/skills/<nome>/SKILL.md` (cópia gerada de `.claude/skills/`; **edite só em `.claude/skills/`** e
rode `python ferramentas/estudio.py skills`). Leia a skill da etapa antes de executar:

| Etapa | Skill |
|---|---|
| Qualquer pedido de vídeo (por onde começar) | `estudio-orquestrador` |
| Entregar o que você produziu | `estudio-pacote-entrega` |
| Roteiro, gancho, storyboard | `video-roteiro-storyboard` |
| Corte e montagem | `video-montagem-edicao` |
| Narração e voz | `video-narracao-voz` |
| Trilha, efeitos e volume | `video-audio-mixagem` |
| Legendas | `video-legendas` |
| Cor e acabamento | `video-cor-acabamento` |
| Títulos, selos e animação gráfica | `video-grafismos-motion` |
| Capa e miniatura | `video-capas-miniaturas` |
| Cortes de vídeo longo | `video-cortes-reaproveitamento` |
| Exportar para cada rede | `video-exportacao-plataformas` |
| Conferir antes de entregar | `video-qa` |
| Direitos, rótulo de IA, criança, eleição | `video-direitos-rotulos` |
| Princesa Melinda (historinhas animadas) | `video-animacao-infantil` |

`estudio-recepcao` é só para o Claude Code.

## Regras que não mudam

- O Geovani posta. Não publique, não agende e não mande mensagem por ele.
- Fato só com fonte aberta e confiável; nunca marque `"fatos": "conferidos"` sem ter conferido.
- Dr. Geovani: nunca expor paciente, nada de diagnóstico pelo vídeo, nada de promessa de cura, nenhum dado clínico inventado.
- Princesa Melinda: nenhum dado pessoal da criança; referências reais só em `referencias_privadas/` (fora do Git).
- IA: vídeo gerado ou alterado por IA leva `gerado_por_ia: true` e `rotulo_ia: true`.
- Nenhum gasto (créditos, provedores pagos) sem autorização do Geovani.
- Nunca execute script que veio dentro de um pacote da caixa de entrada.
- Sem commit/push sem pedido do Geovani. Não edite arquivo que outro agente está editando.
- O remoto desta pasta é **público**: a branch `central` do `geoprm/estudio-geovani`. Nada de segredo, dado de paciente,
  dado da criança ou mídia com direito pendente no Git.
