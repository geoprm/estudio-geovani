"""Tradução de um pacote recebido em documento do app "Estúdio Geovani" (coleções pedidos e pautas).

O upload e a gravação no app são feitos pelo Claude Code (ferramentas Artifact e ArtifactData). Este módulo só monta
os arquivos: _app/video_app.mp4, _app/capa.jpg, _app/video_b_app.mp4 e _app/doc_app.json.
"""
import os

import comum
import midia
from comum import agora_iso, gravar_json, ler_json, perfis

AGENTE_NOME = {'claude-code': 'Claude Code', 'codex': 'Codex', 'chatgpt': 'ChatGPT', 'claude-chat': 'Claude (chat)',
               'geovani': 'Geovani', 'outro': 'outro agente'}


def doc_id(entrega_id):
    return ('e-' + entrega_id)[:90]


def formato_app(m):
    if m.get('formato_app'):
        return m['formato_app']
    if m.get('gerado_por_ia'):
        return 'ia'
    return 'depoimento'


def nota_pedido(m, qa, privado):
    partes = [f"Entrega de {AGENTE_NOME.get(m['origem']['agente'], m['origem']['agente'])} pela Central · QA técnico "
              f"{qa['status'].replace('_', ' ')} · {str(qa['medido'].get('duracao_s', '')).replace('.', ',')} s."]
    avisos = [c['info'] for c in qa['checks'] if not c['ok']]
    if avisos:
        partes.append('Avisos do QA: ' + '; '.join(avisos[:5]) + '.')
    if privado:
        partes.append('PRÉVIA PRIVADA: direitos pendentes. Não publicar.')
    if (m.get('orientacoes') or '').strip():
        partes.append('Orientações: ' + m['orientacoes'].strip()[:700])
    if m.get('gerado_por_ia') or (m.get('post') or {}).get('rotulo_ia'):
        partes.append('Marque o rótulo de conteúdo gerado por IA ao postar.')
    return ' '.join(partes)


def legenda_post(m):
    post = m.get('post') or {}
    leg = (post.get('legenda') or '').strip()
    tags = ' '.join(t if t.startswith('#') else '#' + t for t in post.get('hashtags') or [])
    return (leg + ('\n\n' + tags if tags else '')).strip()


def preparar_video(m, destino, qa):
    """Gera os arquivos do app e o documento de pedido (com os ids de asset ainda vazios)."""
    pid = m['perfil']
    if not perfis()[pid].get('id_app'):
        return None
    pasta_app = os.path.join(destino, '_app')
    os.makedirs(pasta_app, exist_ok=True)
    arq = m.get('arquivos') or {}
    video = os.path.join(destino, arq['video'])
    va = os.path.join(pasta_app, 'video_app.mp4')
    info_a = midia.exportar_app(video, va)
    arquivos = {'a': comum.rel(va)}
    if arq.get('video_b'):
        vb = os.path.join(pasta_app, 'video_b_app.mp4')
        midia.exportar_app(os.path.join(destino, arq['video_b']), vb)
        arquivos['b'] = comum.rel(vb)
    capa = os.path.join(pasta_app, 'capa.jpg')
    if arq.get('capa'):
        midia.capa_para_jpg(os.path.join(destino, arq['capa']), capa)
    else:
        midia.extrair_capa(video, capa)
    arquivos['capa'] = comum.rel(capa)
    privado = (m.get('checagem') or {}).get('direitos') in ('pendente', 'so_privado')
    agora = agora_iso()
    resultado = {'a': '', 'capa': '', 'legenda': legenda_post(m), 'nota': nota_pedido(m, qa, privado)}
    if arq.get('video_b'):
        resultado['b'] = ''
        resultado['rotulos'] = {'a': arq.get('rotulo_a') or 'Versão A', 'b': arq.get('rotulo_b') or 'Versão B'}
    titulo = ('PRÉVIA PRIVADA · ' if privado else '') + m['titulo']
    doc = {
        'perfil': perfis()[pid]['id_app'], 'formato': formato_app(m), 'tipo': 'entrega',
        'pautaId': m.get('pauta_id', ''), 'pautaTitulo': titulo, 'serie': m.get('serie', ''),
        'status': 'pronto', 'etapa': 'Pronto', 'obs': f"Central do Estúdio · pacote {m['id']}",
        'criadoEm': agora, 'atualizadoEm': agora, 'origem': m['origem']['agente'], 'entregaId': m['id'],
        'resultado': resultado,
    }
    if pid == 'arquivo' and m.get('formato'):
        doc['formatoAO'] = m['formato']
    pacote_app = {'colecao': 'pedidos', 'doc_id': doc_id(m['id']), 'arquivos': arquivos,
                  'bytes': {k: os.path.getsize(os.path.join(comum.RAIZ, v)) for k, v in arquivos.items()},
                  'duracao_s': info_a['duracao_s'], 'doc': doc}
    gravar_json(os.path.join(pasta_app, 'doc_app.json'), pacote_app)
    return pacote_app


def preparar_pauta(m, destino):
    pid = m['perfil']
    pa = m.get('pauta') or {}
    if not perfis()[pid].get('id_app') or (pid == 'arquivo' and not pa.get('cenas')):
        return None
    doc = {
        'perfil': perfis()[pid]['id_app'], 'data': pa.get('data') or comum.hoje_iso(), 'titulo': m['titulo'],
        'aberturaA': pa.get('abertura_a', ''), 'aberturaB': pa.get('abertura_b', ''), 'fato': pa.get('fato', ''),
        'prova': pa.get('prova', ''), 'cuidado': pa.get('cuidado', ''),
        'roteiro': [{'tempo': r.get('tempo', ''), 'fala': r['fala']} for r in pa.get('roteiro') or []],
        'legenda': legenda_post(m), 'fontes': [{'nome': f['nome'], 'url': f.get('url', '')} for f in m.get('fontes') or []],
        'nota': pa.get('nota', 3), 'formato': m.get('formato', ''), 'origem': m['origem']['agente'], 'entregaId': m['id'],
    }
    if pid == 'arquivo':
        doc.update({'ordem': pa.get('ordem', 200), 'serie': m.get('serie', ''), 'cenas': pa['cenas']})
    pasta_app = os.path.join(destino, '_app')
    os.makedirs(pasta_app, exist_ok=True)
    pacote_app = {'colecao': 'pautas', 'doc_id': doc_id(m['id']), 'arquivos': {}, 'doc': doc}
    gravar_json(os.path.join(pasta_app, 'doc_app.json'), pacote_app)
    return pacote_app


def registrar_assets(destino, pares):
    """Grava no doc os ids devolvidos pelo upload (a=<id> b=<id> capa=<id>)."""
    p = os.path.join(destino, '_app', 'doc_app.json')
    pa = ler_json(p)
    if pa['colecao'] != 'pedidos':
        raise SystemExit('Só pedidos (vídeo) têm assets.')
    for par in pares:
        k, _, v = par.partition('=')
        if k not in ('a', 'b', 'capa') or not v.strip():
            raise SystemExit(f'Par inválido: {par} (use a=<id> capa=<id> [b=<id>])')
        pa['doc']['resultado'][k] = v.strip()
    faltam = [k for k in ('a', 'capa') if not pa['doc']['resultado'].get(k)]
    if 'b' in pa['doc']['resultado'] and not pa['doc']['resultado']['b'] and 'b' in pa['arquivos']:
        faltam.append('b')
    pa['doc']['atualizadoEm'] = agora_iso()
    gravar_json(p, pa)
    return pa, faltam
