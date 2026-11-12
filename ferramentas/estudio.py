"""Central do Estúdio Geovani — linha de comando.

  python ferramentas/estudio.py status                         # caixa de entrada e entregas em andamento
  python ferramentas/estudio.py novo --perfil direitaxx --tipo video_pronto --titulo "..." --agente codex
  python ferramentas/estudio.py validar <pasta-do-pacote>      # confere sem mover nada
  python ferramentas/estudio.py receber [--tudo | <pasta>]     # valida, QA, move para entregas/, prepara o app
  python ferramentas/estudio.py assets <id> a=<asset> capa=<asset> [b=<asset>]   # ids devolvidos pelo upload
  python ferramentas/estudio.py publicado <id>                 # marca como gravado no app
  python ferramentas/estudio.py qa <video> [--horizontal] [--max 90]
  python ferramentas/estudio.py exportar <entrada> <saida> --preset reels|tiktok|shorts|youtube|master|app [--enquadrar blur|crop|pad] [--lufs -14]
  python ferramentas/estudio.py capa <video> <saida.jpg> [--segundo 3.2]
  python ferramentas/estudio.py skills                         # espelha skills para o Codex e gera .zip para o claude.ai
  python ferramentas/estudio.py verificar                      # saúde da Central

Só o Claude Code publica no app (Artifact + ArtifactData). Os outros agentes param em `validar`.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app_docs  # noqa: E402
import comum  # noqa: E402
import midia  # noqa: E402
import pacote  # noqa: E402
import skills  # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

DURACAO_MAX = {'reel_30': 40, 'investigacao_90': 110, 'reel_profundo': 185, 'microdrama': 185,
               'youtube_5min': 500, 'youtube_10min': 920}


def _imprimir_relatorio(nome, rel):
    print(f'\n== {nome}: {"OK" if rel.ok else "RECUSADO"}')
    for e in rel.erros:
        print(f'  ERRO  {e}')
    for a in rel.avisos:
        print(f'  aviso {a}')


def cmd_status(_):
    entrada = pacote.pacotes_na_entrada()
    soltos = [n for n in os.listdir(comum.ENTRADA) if os.path.isfile(os.path.join(comum.ENTRADA, n))
              and n.upper() != 'LEIA-ME.MD' and not n.startswith('.')] if os.path.isdir(comum.ENTRADA) else []
    print(f'Caixa de entrada: {len(entrada)} pacote(s), {len(soltos)} arquivo(s) solto(s)')
    for p in entrada:
        aviso = ' (recusado antes: veja _RECEPCAO.md)' if os.path.exists(os.path.join(p, '_RECEPCAO.md')) else ''
        print(f'  - {os.path.basename(p)}{aviso}')
    for s in soltos:
        print(f'  · {s}')
    atual = comum.estado_atual()
    pend = {k: v for k, v in atual.items() if v.get('estado') not in ('no_app', 'na_central', 'orientacao_registrada', 'material_disponivel')}
    print(f'\nEntregas recebidas: {len(atual)} · pendentes de ação: {len(pend)}')
    for eid, ev in sorted(atual.items(), key=lambda kv: kv[1].get('em', ''), reverse=True)[:25]:
        print(f"  [{ev.get('estado')}] {eid} · {ev.get('perfil')} · {ev.get('tipo')} · de {ev.get('agente')}")


def cmd_novo(a):
    pasta = pacote.novo(a.perfil, a.tipo, a.titulo, a.agente, a.projeto or '')
    print(pasta)
    print('Coloque os arquivos na pasta, complete o entrega.json e rode: python ferramentas/estudio.py validar "' + pasta + '"')


def cmd_validar(a):
    m, rel, info = pacote.validar(os.path.abspath(a.pasta))
    _imprimir_relatorio(os.path.basename(os.path.abspath(a.pasta)), rel)
    if info and a.detalhe:
        print(json.dumps(info, ensure_ascii=False, indent=1))
    sys.exit(0 if rel.ok else 1)


def _escrever_recusa(pasta, rel):
    linhas = ['# Pacote recusado pela recepção', '', f'*{comum.agora_iso()}*', '',
              'Corrija os erros abaixo no `entrega.json` (ou nos arquivos) e rode a recepção de novo.', '']
    linhas += [f'- **Erro:** {e}' for e in rel.erros] + [f'- Aviso: {x}' for x in rel.avisos]
    with open(os.path.join(pasta, '_RECEPCAO.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(linhas) + '\n')


def receber_um(pasta):
    nome = os.path.basename(pasta)
    m, rel, info = pacote.validar(pasta)
    if not rel.ok:
        _imprimir_relatorio(nome, rel)
        _escrever_recusa(pasta, rel)
        return None
    recusa = os.path.join(pasta, '_RECEPCAO.md')
    if os.path.exists(recusa):
        os.remove(recusa)
    qa = None
    if m['tipo'] == 'video_pronto':
        vertical = not (m.get('formato', '').startswith('youtube_') or m.get('formato', '').endswith('16x9'))
        qa = midia.qa_tecnico(os.path.join(pasta, m['arquivos']['video']), vertical=vertical,
                              duracao_max=DURACAO_MAX.get(m.get('formato')))
        if qa['status'] == 'fail':
            for c in qa['checks']:
                if not c['ok'] and c['nivel'] == 'erro':
                    rel.erro(f"QA técnico: {c['check']} — {c['info']}")
            _imprimir_relatorio(nome, rel)
            _escrever_recusa(pasta, rel)
            return None
    destino = pacote.mover_para_entregas(pasta, m)
    hashes = {}
    for raiz, _, arquivos in os.walk(destino):
        for arq in arquivos:
            p = os.path.join(raiz, arq)
            hashes[comum.rel(p).split(m['id'] + '/', 1)[-1]] = comum.sha256(p)
    recepcao = {'recebido_em': comum.agora_iso(), 'validacao': rel.como_dict(), 'midia': info, 'sha256': hashes}
    if qa:
        comum.gravar_json(os.path.join(destino, 'qa_estudio.json'), qa)
        recepcao['qa_tecnico'] = qa['status']
    comum.gravar_json(os.path.join(destino, 'recepcao.json'), recepcao)

    estado, app = 'na_central', None
    if m['tipo'] == 'video_pronto':
        app = app_docs.preparar_video(m, destino, qa)
        estado = 'aguardando_upload' if app else 'na_central'
    elif m['tipo'] == 'pauta':
        app = app_docs.preparar_pauta(m, destino)
        estado = 'pronto_para_app' if app else 'na_central'
    elif m['tipo'] == 'orientacao':
        pacote.registrar_orientacao(m, destino)
        estado = 'orientacao_registrada'
    elif m['tipo'] == 'material_bruto':
        estado = 'material_disponivel'
    comum.registrar_evento({'id': m['id'], 'estado': estado, 'perfil': m['perfil'], 'tipo': m['tipo'],
                            'agente': m['origem']['agente'], 'titulo': m['titulo'], 'caminho': comum.rel(destino),
                            'qa_tecnico': qa['status'] if qa else None, 'avisos': rel.avisos,
                            'doc_app': f"{app['colecao']}/{app['doc_id']}" if app else None})
    _imprimir_relatorio(nome, rel)
    print(f'  -> {comum.rel(destino)} [{estado}]' + (f" · QA técnico {qa['status']}" if qa else ''))
    if app and app['arquivos']:
        print('  Para o app (Claude Code): suba ' + ', '.join(f'{k}={v}' for k, v in app['arquivos'].items()) +
              f" e depois: python ferramentas/estudio.py assets {m['id']} a=<id> capa=<id>")
    elif app:
        print(f"  Para o app (Claude Code): ArtifactData set {app['colecao']}/{app['doc_id']} com o doc de {comum.rel(destino)}/_app/doc_app.json")
    return m['id']


def cmd_receber(a):
    if not midia.ffmpeg_ok():
        sys.exit('FFmpeg/ffprobe não encontrados no PATH.')
    for n in sorted(os.listdir(comum.ENTRADA)):
        p = os.path.join(comum.ENTRADA, n)
        if os.path.isfile(p) and n.lower().endswith('.zip'):
            try:
                print(f'zip aberto: {os.path.basename(pacote.abrir_zip(p))}')
            except (ValueError, OSError) as e:
                print(f'zip recusado ({n}): {e}')
    rascunho = pacote.agrupar_soltos()
    if rascunho:
        print(f'arquivos soltos agrupados em {os.path.basename(rascunho)}: complete o entrega.json')
    alvos = pacote.pacotes_na_entrada() if a.tudo or not a.pasta else [os.path.abspath(a.pasta)]
    if not alvos:
        print('Caixa de entrada vazia.')
    recebidos = [eid for eid in (receber_um(p) for p in alvos) if eid]
    print(f'\n{len(recebidos)} de {len(alvos)} pacote(s) recebido(s).')


def cmd_assets(a):
    destino = comum.localizar_entrega(a.id)
    pa, faltam = app_docs.registrar_assets(destino, a.pares)
    estado = 'aguardando_upload' if faltam else 'pronto_para_app'
    comum.registrar_evento({'id': a.id, 'estado': estado, 'assets': {k: pa['doc']['resultado'].get(k) for k in ('a', 'b', 'capa') if k in pa['doc']['resultado']}})
    if faltam:
        print(f'Ainda faltam: {", ".join(faltam)}')
    else:
        print(f"Pronto para gravar no app: ArtifactData set {pa['colecao']}/{pa['doc_id']} com o campo doc de "
              f"{comum.rel(destino)}/_app/doc_app.json; depois: python ferramentas/estudio.py publicado {a.id}")


def cmd_publicado(a):
    destino = comum.localizar_entrega(a.id)
    pa = comum.ler_json(os.path.join(destino, '_app', 'doc_app.json'))
    if pa['colecao'] == 'pedidos' and not (pa['doc']['resultado'].get('a') and pa['doc']['resultado'].get('capa')):
        sys.exit('Os ids de asset ainda não foram registrados (rode assets antes).')
    comum.registrar_evento({'id': a.id, 'estado': 'no_app', 'doc_app': f"{pa['colecao']}/{pa['doc_id']}"})
    print(f"{a.id}: no app como {pa['colecao']}/{pa['doc_id']}")


def cmd_qa(a):
    r = midia.qa_tecnico(a.video, vertical=not a.horizontal, duracao_max=a.max)
    for c in r['checks']:
        marca = 'ok  ' if c['ok'] else ('ERRO' if c['nivel'] == 'erro' else 'aviso')
        print(f"  {marca} {c['check']}: {c['info']}")
    print(f"status: {r['status']}")
    if a.json:
        comum.gravar_json(a.json, r)
    sys.exit(1 if r['status'] == 'fail' else 0)


def cmd_exportar(a):
    s = midia.exportar(a.entrada, a.saida, a.preset, a.enquadrar, a.lufs)
    v = s['video']
    print(f"{a.saida}: {v['largura']}x{v['altura']} {v['fps']} fps · {s['duracao_s']} s · {s['bytes'] / 1048576:.1f} MiB")


def cmd_capa(a):
    print(midia.extrair_capa(a.video, a.saida, a.segundo))


def cmd_skills(_):
    nomes, zips = skills.sincronizar()
    print(f'{len(nomes)} skills espelhadas em .agents/skills (Codex) e {len(zips)} .zip em dist/skills (claude.ai)')
    probs = skills.verificar()
    for p in probs:
        print('  problema:', p)
    sys.exit(1 if probs else 0)


def cmd_verificar(_):
    probs, avisos = [], []
    for pid, p in comum.perfis().items():
        for campo in ('id', 'nome', 'status', 'missao', 'tom', 'regras', 'trabalho'):
            if campo not in p:
                probs.append(f'perfil {pid}: falta {campo}')
        for pasta in p.get('trabalho', {}).get('pastas', []):
            if not os.path.isdir(pasta):
                avisos.append(f'perfil {pid}: pasta de trabalho não encontrada: {pasta}')
    app = comum.config_app()
    idx = os.path.join(comum.RAIZ, 'app', 'index.html')
    if not os.path.exists(idx):
        probs.append('app/index.html ausente')
    elif comum.sha256(idx) != app['index_sha256']:
        avisos.append('app/index.html difere da versão registrada em config/app.json (atualize o registro ou a cópia)')
    probs += skills.verificar()
    if not midia.ffmpeg_ok():
        probs.append('FFmpeg/ffprobe fora do PATH')
    for eid, ev in comum.estado_atual().items():
        if ev.get('caminho') and not os.path.isdir(os.path.join(comum.RAIZ, ev['caminho'])):
            probs.append(f'registro aponta para pasta sumida: {eid}')
    for x in avisos:
        print('  aviso:', x)
    for x in probs:
        print('  PROBLEMA:', x)
    print('Central OK' if not probs else f'{len(probs)} problema(s)')
    sys.exit(1 if probs else 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Central do Estúdio Geovani')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('status').set_defaults(f=cmd_status)
    s = sub.add_parser('novo')
    s.add_argument('--perfil', required=True)
    s.add_argument('--tipo', required=True, choices=comum.TIPOS)
    s.add_argument('--titulo', required=True)
    s.add_argument('--agente', required=True, choices=comum.AGENTES)
    s.add_argument('--projeto')
    s.set_defaults(f=cmd_novo)
    s = sub.add_parser('validar')
    s.add_argument('pasta')
    s.add_argument('--detalhe', action='store_true')
    s.set_defaults(f=cmd_validar)
    s = sub.add_parser('receber')
    s.add_argument('pasta', nargs='?')
    s.add_argument('--tudo', action='store_true')
    s.set_defaults(f=cmd_receber)
    s = sub.add_parser('assets')
    s.add_argument('id')
    s.add_argument('pares', nargs='+')
    s.set_defaults(f=cmd_assets)
    s = sub.add_parser('publicado')
    s.add_argument('id')
    s.set_defaults(f=cmd_publicado)
    s = sub.add_parser('qa')
    s.add_argument('video')
    s.add_argument('--horizontal', action='store_true')
    s.add_argument('--max', type=float)
    s.add_argument('--json')
    s.set_defaults(f=cmd_qa)
    s = sub.add_parser('exportar')
    s.add_argument('entrada')
    s.add_argument('saida')
    s.add_argument('--preset', default='reels', choices=list(midia.PRESETS) + ['app'])
    s.add_argument('--enquadrar', default='blur', choices=('blur', 'crop', 'pad'))
    s.add_argument('--lufs', type=float)
    s.set_defaults(f=cmd_exportar)
    s = sub.add_parser('capa')
    s.add_argument('video')
    s.add_argument('saida')
    s.add_argument('--segundo', type=float)
    s.set_defaults(f=cmd_capa)
    sub.add_parser('skills').set_defaults(f=cmd_skills)
    sub.add_parser('verificar').set_defaults(f=cmd_verificar)
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == '__main__':
    main()
