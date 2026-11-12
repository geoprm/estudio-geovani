# AGENTS.md — ARQUIVO OCULTO

Escopo permanente de continuidade V3, com aditivo V4. O arquivo recebido e seus bytes originais estão em `governance/v3/originals/AGENTS.md`; esta cópia restaura a acentuação que chegou substituída por caracteres de erro, sem alterar o contrato.

## Leitura obrigatória

Antes de implementar requisitos, leia `ARVORE_EDITORIAL_COMPLETA.md` e `MATRIZ_MESTRE_DE_ESCOPO.csv`. Para o grafo, leia também `ADITIVO_CODEX_GRAFO_DE_CONGRUENCIA.md` e `MODELO_TRILHA_E_ARESTA.json`. Concilie eventual AGENTS de nível superior. Os documentos registram escopo e não substituem o código existente.

## Continuidade

- Não esquecer os IDs AO-Cxx-yyy, nem descartar temas P2/P3.
- Não marcar um tópico como implementado por seu título ter sido cadastrado.
- Antes de editar, inspecionar estado do Git, testes, rotas e esquema. Preservar alterações locais e de outras sessões. Se não houver Git, registrar a ausência e usar checkpoint verificável, sem inventar branch ou commit.
- Escolher lotes pequenos com funcionamento demonstrável. Não migrar stack sem necessidade.
- Atualizar a matriz por tópico afetado, com evidências de arquivo, rota, teste e captura. Estados canônicos: SOLICITADO_NAO_AUDITADO, MAPEADO, EM_IMPLEMENTACAO, IMPLEMENTADO, REVISADO, BLOQUEADO, DESCARTADO_APOS_DECISAO_HUMANA. Nunca deixar P0 sem responsável. Mapeado significa pendente; em implementação significa trabalho parcial, sem alegação de conclusão.
- Só reconhecer implementação anterior após inspecionar evidências. Exibir Antes / Feito / Não feito / Próximo lote ao proprietário.

## Segurança e método

- Classificar cada afirmação individualmente. A existência de um documento não valida uma inferência extraordinária.
- Contatos de Epstein não implicam crimes. Não estabelecer vínculo com canibalismo, religião ou ritual sem prova individualizada e rastreável. Respeitar vítimas.
- Ayahuasca, Santo Daime e outras tradições religiosas não são sinônimos de criminalidade.
- Preservar procedência e direitos de fotos, cartas, capas, mangás e documentos. Pesquisa privada não autoriza publicação pública ou comercial. Não remover marcas d'água nem falsificar imagens.
- Não apresentar reconstituição de IA como fotografia histórica ou cena inventada como prova.
- Manter a arquitetura de leitura concisa, apesar da extensão do backlog.
- **Conexão temática, simbólica ou cronológica não prova causalidade.**
- O grafo AO-SYS-GRAFO-001 é transversal; não substitui os 177 temas ou as 13 coleções. Cada aresta deve explicar vínculo, fontes, ressalvas e alternativas. Hipóteses não herdam confirmação dos nós conectados.
- `mito_tradicao` é categoria cultural, separada do estado de evidência.

## Pronto por lote

1. Rota funcional e prova desktop/móvel, ou impedimento real documentado.
2. Fontes, direitos e classificações por afirmação.
3. Matriz atualizada com evidências. REVISADO exige comprovação editorial e QA; aprovação humana não pode ser presumida.
4. Changelog com trabalho, regressões, pendências e próximos IDs.

Autorização para organizar e implementar lotes não autoriza imputar crimes sem fonte nem publicar material protegido.

## Checkpoint local v0.8.0 — 03/11/2026

- Evidência do lote: `docs/RELATORIO_V08.md` e `evidence/v08-verification.json`; 245 testes, 39 medições de rotas/larguras e nove visualizações móveis do grafo aprovadas. Isso não constitui revisão editorial humana ou teste em aparelho físico.
- Base temática: 4 IMPLEMENTADO, 32 EM_IMPLEMENTACAO, 141 MAPEADO, zero REVISADO; 177 IDs em 13 coleções. Três extensões e seis transversais ficam fora da contagem temática.
- AO-SYS-GRAFO-001 implementado tecnicamente, com T01/T02/T03 privados e revisão humana pendente. Próxima produção: maçonaria, Bohemian Grove, Brasília e aprofundamento dos casos, sem excluir os outros pedidos.
- Leitor local: `/?v=0.8.0#home`; grafo: `/#connections/T01`; matriz: `/editorial#scope`. Modo de imagens não equivale a publicação. O artefato público tem zero textos/trilhas aprovados e preserva 13 metadados; o privado mantém 13 dossiês/fichas, quatro aprofundados e 539 cartas.
- Build: `node tools/build.cjs`; verificação: `node tools/build.cjs --check` e `python tools/verify-v08.py`. A reconciliação parte dos originais preservados; não use `--verified` para declarar um lote futuro sem evidência.
- Não houve push, deploy, serviço pago, migração ou vídeo renderizado. Checkpoint anterior preservado em `checkpoints/v0.7/`.

## Checkpoint local v0.9.0 — 09/11/2026

- Relatório em docs/RELATORIO_V09.md e evidência em evidence/v09-verification.json. 251 testes, 48 verificações de rota e largura e três visualizações móveis de T04 aprovadas no navegador. Revisão humana e teste em aparelho físico pendentes.
- 177 temas em 13 coleções. Cinco IMPLEMENTADO, 33 EM_IMPLEMENTACAO, 139 MAPEADO e zero REVISADO. Mudaram apenas AO-C01-002 e AO-C10-004. Três extensões e seis transversais contabilizados separadamente.
- Dossiê Maçonaria em /?v=0.9.0#dossier/maconaria e T04 em /?v=0.9.0#connections/T04. São 539 cartas, 14 dossiês e fichas privados, cinco aprofundados e quatro trilhas. As duas novas reproduções têm uso restrito à pesquisa privada. A prévia pública preserva 14 metadados e aguarda aprovação humana para textos e trilhas.
- Checkpoint anterior em checkpoints/v0.8/. Entrega privada em dist/arquivo_oculto_v09_completo.zip. Validação com node tools/build.cjs --check e python tools/verify-v09.py.
- Bohemian Grove (AO-C01-004, AO-C10-006) abre o próximo lote, seguido por Brasília (AO-C12-001) e aprofundamento dos casos.

## Checkpoint local v0.10.0 — 10/11/2026

- A orientação do proprietário priorizou o estúdio, as cartas, as capas e a home pública. [Relatório do lote](docs/RELATORIO_V10.md) e [teste de rotas](evidence/v10-browser.json).
- Os 177 temas e 13 coleções permanecem registrados. Cinco temas implementados, 34 em implementação, 138 mapeados e zero revisados. A v0.9 está preservada em `governance/v3/checkpoints/` e nos artefatos nomeados da entrega.
- Leitor: `/?v=0.10.0#home`. Prévia pública: `/public-preview?v=0.10.0#home`. Capas: `/#dossier/the-economist`. Mosaico privado do Claude: `/acervo-cartas.html`. Sala de projeção: `/editorial/sessoes`.
- 636 fichas de cartas, incluindo 97 novos títulos de SubGenius. O leitor privado usa as fotos do acervo do Claude. As reproduções de cartas e capas aguardam licença para uso público. Próxima ampliação de catálogo: Limited e promocionais.
- O Índice Cego tem três vídeos disponíveis localmente. O próximo episódio é *As Sete Portas*. Dois roteiros de YouTube estão prontos para gravação. Os seis episódios V2 registrados pelo Claude Code pertencem a outra temporada.
