"""Entrega dos episódios V2 ao app "Estúdio Geovani" (Artifact MUNdJL4BwN9ovWQeVdboHt).

O envio em si é feito pelo Claude Code (ferramenta Artifact, upload de asset; ArtifactData, banco `pedidos`): este módulo
prepara os arquivos, guarda os ids devolvidos e monta os documentos de pedido a partir do manifesto e do QA.

  python -m arquivo_oculto.v2.entrega_app preparar AO-S01-E03 [...] --pasta <dir>   # copia vídeo do app e capa, mostra hashes
  python -m arquivo_oculto.v2.entrega_app registrar AO-S01-E03 a=<id> b=<id> capa=<id>  # grava os ids em entregas_app.json
  python -m arquivo_oculto.v2.entrega_app pedidos AO-S01-E03 [...] --pasta <dir>     # um JSON por pedido, pronto para o banco

Regras: só entra episódio com QA pass/pass_with_warnings nos dois modos. A versão A é sempre a public_release.
A prévia privada (B) só é enviada quando o episódio tem material privado por direito (senão seria um vídeo repetido).
"""
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone

AQUI = os.path.dirname(os.path.abspath(__file__))
AO = os.path.dirname(AQUI)
SAIDA = os.path.join(AO, 'saida_v2')
PROD = os.path.join(AO, 'producao', 'v2')
REGISTRO = os.path.join(PROD, 'entregas_app.json')
ARTIFACT = 'https://claude.ai/artifact/MUNdJL4BwN9ovWQeVdboHt'
BRT = timezone(timedelta(hours=-3))
AVISOS = {
    'visuais_de_arquivo': 'pouca imagem de arquivo na tela',
    'quatro_categorias_de_imagem': 'arte real retida na versão pública',
    'duracao_perto_do_padrao': 'duração acima dos 85 s de referência, dentro da faixa do formato',
    'tempo_de_tela_do_personagem': 'Arquivista fora da faixa de tempo em tela',
    'numero_de_planos': 'número de planos fora do alvo',
    'voz_aprovada_pelo_proprietario': 'voz sem aprovação registrada',
    'visual_aprovado_pelo_proprietario': 'visual sem aprovação registrada',
    'bitrate_master_alvo': 'master acima de 8 Mbps',
}


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def manifesto(eid):
    return json.load(open(os.path.join(PROD, f'{eid}.v2.json'), encoding='utf-8'))


def qa_de(eid, modo):
    p = os.path.join(SAIDA, f'{eid}_{modo}', 'qa.json')
    if not os.path.exists(p):
        raise SystemExit(f'{eid} {modo}: sem qa.json (renderize antes)')
    q = json.load(open(p, encoding='utf-8'))
    if q['status'] not in ('pass', 'pass_with_warnings'):
        raise SystemExit(f'{eid} {modo}: QA {q["status"]} — não entra no app')
    return q


def tem_material_privado(eid):
    """True quando a prévia privada mostra algo que a pública retém (cartas, trechos com direitos em verificação)."""
    tl = json.load(open(os.path.join(SAIDA, f'{eid}_private_preview', 'timeline.json'), encoding='utf-8'))
    return any(p.get('privado') for p in tl['planos'])


def ler_registro():
    if os.path.exists(REGISTRO):
        return json.load(open(REGISTRO, encoding='utf-8'))
    return {'artifact': ARTIFACT, 'nota': 'ids de asset devolvidos pelo upload; servidos em /_blob/<id> só a quem abre o app', 'episodios': {}}


def preparar(eids, pasta):
    os.makedirs(pasta, exist_ok=True)
    from PIL import Image
    for eid in eids:
        qa_de(eid, 'public_release'); qa_de(eid, 'private_preview')
        pub, priv = (os.path.join(SAIDA, f'{eid}_{m}') for m in ('public_release', 'private_preview'))
        saidas = [(os.path.join(pub, 'video_app.mp4'), f'{eid}_v2_publica.mp4')]
        if tem_material_privado(eid):
            saidas.append((os.path.join(priv, 'video_app.mp4'), f'{eid}_v2_previa_privada.mp4'))
        for orig, nome in saidas:
            shutil.copyfile(orig, os.path.join(pasta, nome))
        Image.open(os.path.join(pub, 'cover.png')).convert('RGB').save(os.path.join(pasta, f'{eid}_v2_capa.jpg'), quality=88, optimize=True)
        for _, nome in saidas + [(None, f'{eid}_v2_capa.jpg')]:
            p = os.path.join(pasta, nome)
            print(f'{p}\t{os.path.getsize(p)}\t{sha(p)[:16]}')


def registrar(eid, pares, pasta=None):
    reg = ler_registro()
    ep = reg['episodios'].setdefault(eid, {})
    origem = {'a': ('public_release', 'video_app.mp4'), 'b': ('private_preview', 'video_app.mp4'), 'capa': ('public_release', 'cover.png')}
    for par in pares:
        k, v = par.split('=', 1)
        modo, arq = origem[k]
        p = os.path.join(SAIDA, f'{eid}_{modo}', arq)
        ep[k] = {'asset': v, 'origem': f'saida_v2/{eid}_{modo}/{arq}', 'sha256_origem': sha(p), 'bytes_origem': os.path.getsize(p),
                 'enviado_em': datetime.now(BRT).isoformat(timespec='seconds')}
    ep['pedido_doc'] = 'v2-' + eid.lower()
    json.dump(reg, open(REGISTRO, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(ep, ensure_ascii=False, indent=1))


def _aviso(c):
    if c['check'] == 'quatro_categorias_de_imagem' and ' · faltam: ' in c['info']:
        falta = c['info'].split(' · faltam: ')[1].split(' (')[0]
        return f'sem {falta} na versão pública (retida por direitos)' if 'retida' in c['info'] else f'episódio sem {falta}'
    return AVISOS.get(c['check'], c['check'])


def nota(eid, q_pub, q_priv, com_b):
    avisos = sorted({_aviso(c) for c in q_pub['checks'] if not c['ok']})
    partes = [f"QA {q_pub['status'].replace('_', ' ')} · {str(q_pub['duracao_s']).replace('.', ',')} s · Perfil V2: Arquivista em performance 2.5D "
              "(máscara rígida, a boca não anima), voz arquivista-v2-c aprovada, documentos reais com fonte."]
    if com_b:
        partes.append('Pública: só material liberado; é a que pode ser postada depois da sua revisão. '
                      'Prévia privada: mostra cartas ou trechos com direitos em verificação, com a marca PRÉVIA PRIVADA. Não publicar.')
    else:
        partes.append('Uma versão só: todo o material deste episódio é de domínio público ou produção original.')
    if avisos:
        partes.append('Avisos do QA: ' + '; '.join(avisos) + '.')
    partes.append('Marque o rótulo de conteúdo gerado por IA ao postar.')
    return ' '.join(partes)


def pedidos(eids, pasta):
    os.makedirs(pasta, exist_ok=True)
    reg = ler_registro()
    for eid in eids:
        man = manifesto(eid)
        ent = reg['episodios'].get(eid) or {}
        if not (ent.get('a') and ent.get('capa')):
            raise SystemExit(f'{eid}: registre os ids (a=, capa=) antes de montar o pedido')
        q_pub, q_priv = qa_de(eid, 'public_release'), qa_de(eid, 'private_preview')
        com_b = bool(ent.get('b'))
        agora = datetime.now(BRT).isoformat(timespec='seconds')
        res = {'a': ent['a']['asset'], 'capa': ent['capa']['asset'], 'legenda': man['legenda_post'], 'nota': nota(eid, q_pub, q_priv, com_b)}
        if com_b:
            res['b'] = ent['b']['asset']
            res['rotulos'] = {'a': 'Pública', 'b': 'Prévia privada'}
        doc = {'perfil': 'arquivo', 'formato': 'ia', 'tipo': 'ia', 'serie': man['serie'], 'pautaId': f"ao-ep{man['num']:02d}",
               'pautaTitulo': f"EP{man['num']:02d} · {man['titulo']}", 'status': 'pronto', 'etapa': 'Pronto',
               'obs': f'Fábrica V2 no PC (Claude Code) · manifesto producao/v2/{eid}.v2.json', 'criadoEm': agora, 'atualizadoEm': agora,
               'v2': True, 'formatoAO': man['formato'], 'perfilVersao': '2.0.0', 'episodeId': eid, 'resultado': res}
        p = os.path.join(pasta, ent['pedido_doc'] + '.json')
        json.dump(doc, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(p)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('acao', choices=('preparar', 'registrar', 'pedidos'))
    ap.add_argument('itens', nargs='+')
    ap.add_argument('--pasta', default=os.path.join(SAIDA, '_entrega_app'))
    a = ap.parse_args()
    if a.acao == 'preparar':
        preparar(a.itens, a.pasta)
    elif a.acao == 'registrar':
        registrar(a.itens[0], a.itens[1:])
    else:
        pedidos(a.itens, a.pasta)
