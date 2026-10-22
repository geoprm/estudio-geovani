# Estúdio de Reels do Geovani Miranda

Programa de edição de vídeo do Geovani (fonoaudiólogo em Barreiras/BA) para dois perfis com objetivos diferentes:
- @direitaxx: liderança política e social em Xique-Xique e no sertão da Bahia. Firme, com fonte.
- Dr. Geovani Miranda: autoridade que acolhe, ensina e guia famílias. Calmo, educativo, sem susto.

Quem usa: o "Editor do Estúdio" (tarefa agendada) e conversas com o Claude. Os pedidos chegam pelo app privado do
Geovani (o link vem no pedido da tarefa): banco `pedidos`, `pautas` e `config/app`.

Antes de editar, leia LEIA-ME.md, modelo_video.py e exemplos/tela_dividida_educacao.py.

Fluxo: instalar.py (uma vez) → preparar.py → ritmo.py → videos/<id>.py (copiado do modelo) → preview → finalizar.py.

Regras que não mudam:
- Fato só com fonte aberta e confiável; o selo mostra veículo e data. Gancho fiel ao dado (46,8% é "quase metade").
- Nada de corte ou montagem que mude o sentido do que alguém disse. Corrija a legenda contra a fala real.
- Dr. Geovani: nunca expor paciente, nada de diagnóstico pelo vídeo nem promessa de cura.
- Não publicar em rede social nem mandar mensagem por ele: ele posta.
- Retoque leve vem ligado pelo perfil; desligue (R.retoque = None) quando o pedido tiver retoque = false.
- Período eleitoral: conteúdo alterado por IA exige rótulo (Res. TSE 23.610, art. 9º-B).
