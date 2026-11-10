"""Testes do perfil Arquivo Oculto V2. Rode na raiz do estúdio: python tests/test_arquivo_oculto_v2.py
(sem pytest; não renderiza vídeo — confere contrato, isolamento, direitos, manifesto e as entregas quando existirem)."""
import copy
import hashlib
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
OK, FALHAS = [], []


def teste(f):
    try:
        f(); OK.append(f.__name__)
    except Exception as e:  # noqa: BLE001
        FALHAS.append((f.__name__, repr(e)))
    return f


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


@teste
def perfil_v2_valido_e_fiel_ao_pacote():
    from arquivo_oculto.v2 import perfil
    p = perfil.carregar()
    assert perfil.validar(p) == [], perfil.validar(p)
    assert sha(perfil.PERFIL_JSON) == sha(os.path.join(RAIZ, 'docs', 'v2', 'originals', 'arquivo_oculto_v2.json'))


@teste
def validador_reprova_perfil_quebrado():
    from arquivo_oculto.v2 import perfil
    p = copy.deepcopy(perfil.carregar())
    p['character']['mask_flexible_or_lipsync'] = True
    del p['formats']['microdrama']
    p['isolation']['do_not_modify_other_brands'] = ['direitaxx']
    e = perfil.validar(p)
    assert any('mask_flexible' in x for x in e) and any('microdrama' in x for x in e) and any('dr-geovanimiranda' in x for x in e), e


@teste
def seis_formatos_com_um_clique():
    from arquivo_oculto.v2 import perfil
    p = perfil.carregar()
    for k in perfil.FORMATOS_OBRIGATORIOS:
        f = perfil.formato(p, k)
        assert f['largura'] * f['altura'] == 1080 * 1920
    assert perfil.formato(p, 'youtube_5min')['largura'] == 1920
    assert perfil.metas_personagem(p, 85)['min_planos_distintos'] == 5
    assert perfil.metas_personagem(p, 85)['boca_da_mascara_anima'] is False


@teste
def perfis_antigos_intactos():
    import perfis
    base = subprocess.run(['git', 'show', 'origin/main:perfis.py'], cwd=RAIZ, capture_output=True, text=True, encoding='utf-8')
    if base.returncode == 0:
        ns = {'__file__': os.path.join(RAIZ, 'perfis.py')}
        exec(compile(base.stdout, 'perfis_origin.py', 'exec'), ns)
        for k in ('direitaxx', 'drgeovani'):
            assert ns['PERFIS'][k] == perfis.PERFIS[k], f'perfil {k} mudou em relação ao GitHub'
    for k in ('direitaxx', 'drgeovani'):
        texto = json.dumps(perfis.PERFIS[k], ensure_ascii=False, default=str).lower()
        assert 'arquivista' not in texto and 'arquivo_oculto' not in texto, f'{k} herdou algo do Arquivista'
    ao = perfis.PERFIS['arquivo-oculto']
    assert ao['profile_version'] == '2.0.0' and ao['formato_padrao'] == 'investigacao_90'


@teste
def lock_da_voz_e_do_personagem():
    from arquivo_oculto.v2 import perfil, voz
    lk = perfil.carregar_lock()
    assert lk['voice']['voice_id'] in voz.PRESETS
    if lk['voice']['approved']:
        assert lk['voice'].get('aprovado_por') and lk['voice'].get('evidencia_aprovacao'), 'aprovação de voz sem registro de quem e onde'
    for k in ('voice_id', 'voice_model', 'locale', 'rate', 'pitch', 'style', 'version'):
        assert k in lk['voice'], k
    assert os.path.exists(os.path.join(RAIZ, lk['character']['reference_image']))


@teste
def filtro_de_direitos():
    from arquivo_oculto.v2.perfil import gate_direitos as g
    assert g('private_research', 'private_preview') and not g('private_research', 'public_release')
    assert g('quotation_excerpt', 'private_preview') and not g('quotation_excerpt', 'public_release')
    assert g('fact_citation', 'public_release') and g('original_production', 'public_release')
    assert not g('unknown', 'private_preview') and not g('restricted', 'private_preview') and not g('inventado', 'private_preview')


@teste
def manifesto_ep01_v2_valido():
    from arquivo_oculto.v2 import perfil, fabrica_v2 as fb
    man = json.load(open(os.path.join(RAIZ, 'arquivo_oculto', 'producao', 'v2', 'AO-S01-E01.v2.json'), encoding='utf-8'))
    assert fb.validar_manifesto(man, perfil.carregar()) == []
    falas = [l['fala'] for l in man['linhas']]
    assert not any('Drug Companies' in json.dumps(x) for x in man['listas'].values()), 'linha não verificada na lista'
    pub = copy.deepcopy(man); fb.resolver_direitos(pub, 'public_release')
    priv = copy.deepcopy(man); fb.resolver_direitos(priv, 'private_preview')
    s_pub = {s['id']: s for l in pub['linhas'] for s in l['shots']}
    s_priv = {s['id']: s for l in priv['linhas'] for s in l['shots']}
    assert s_priv['S07']['_gate_ok'] and not s_pub['S07']['_gate_ok']
    assert s_pub['S07']['rights_status'] == 'original_production'           # placeholder honesto
    assert s_pub['S02']['_asset_efetivo'] == 'A-DOC-1995-PARAFRASE'          # paráfrase com fonte
    assert all(not s['_privado'] for s in s_pub.values())
    assert len(falas) >= 12


@teste
def fabrica_recusa_titulo_sobre_documento_e_rascunho():
    from arquivo_oculto.v2 import perfil, fabrica_v2 as fb
    man = json.load(open(os.path.join(RAIZ, 'arquivo_oculto', 'producao', 'v2', 'AO-S01-E02.v2.json'), encoding='utf-8'))
    ruim = copy.deepcopy(man)
    next(s for l in ruim['linhas'] for s in l['shots'] if s['tipo'] == 'trecho_documento')['tela'] = 'COLIDE'
    assert any('colide' in e for e in fb.validar_manifesto(ruim, perfil.carregar()))
    rasc = copy.deepcopy(man); rasc['status_editorial'] = 'rascunho_pendente_checagem'
    assert any('rascunho' in e for e in fb.validar_manifesto(rasc, perfil.carregar()))
    assert fb.validar_manifesto(man, perfil.carregar()) == []


@teste
def cache_por_tipo_de_plano():
    from arquivo_oculto.v2 import fabrica_v2 as fb
    assert fb.hash_codigo('aparicao') != fb.hash_codigo('lista_oficial') != fb.hash_codigo('leituras')
    assert fb.hash_codigo('ombro', 'arte_original') != fb.hash_codigo('ombro', 'lista_oficial')


@teste
def lista_oficial_bate_com_o_snapshot():
    import re, html
    p = os.path.join(RAIZ, 'arquivo_oculto', 'acervo_privado', 'sjgames_inwo_lists_ill_1995-04-18.html')
    if not os.path.exists(p):
        return  # acervo privado fica fora do Git
    t = open(p, encoding='latin-1').read()
    rows = {}
    for r in re.findall(r'<tr[^>]*>(.*?)</tr>', t, flags=re.S | re.I):
        c = [html.unescape(re.sub(r'<[^>]+>', ' ', x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>', r, flags=re.S | re.I)]
        if len(c) >= 5 and c[1] in ('C', 'U', 'R', 'I', 'S'):
            rows[' '.join(c[0].split())] = c
    assert len(rows) == 412, len(rows)
    man = json.load(open(os.path.join(RAIZ, 'arquivo_oculto', 'producao', 'v2', 'AO-S01-E01.v2.json'), encoding='utf-8'))
    for ln in man['listas']['ep01']:
        if ln[0] == '…':
            continue
        c = rows[ln[0]]
        assert [c[1], c[2], f'{c[3]} / {c[4]}'] == ln[1:4], (ln, c)


@teste
def boca_da_mascara_nunca_anima():
    src = open(os.path.join(RAIZ, 'arquivo_oculto', 'v2', 'ator.py'), encoding='utf-8').read()
    assert 'w_jaw' not in src and 'jaw' not in src.lower(), 'ator V2 não pode deformar a boca da máscara'


@teste
def acervo_privado_fora_do_git():
    ign = open(os.path.join(RAIZ, '.gitignore'), encoding='utf-8').read()
    for x in ('arquivo_oculto/acervo_privado/', 'arquivo_oculto/assets/referencias_privadas/', '.venv/', 'arquivo_oculto/tts/'):
        assert x in ign, x


@teste
def entrega_ep01_v2_com_qa():
    base = os.path.join(RAIZ, 'arquivo_oculto', 'saida_v2')
    if not os.path.isdir(base):
        return
    for d in os.listdir(base):
        q = os.path.join(base, d, 'qa.json')
        if not os.path.exists(q) or '_rodada' in d:      # rodadas antigas ficam só como histórico
            continue
        r = json.load(open(q, encoding='utf-8'))
        nomes = {c['check'] for c in r['checks']}
        assert {'bitrate_master', 'versao_app_ate_19MiB'} <= nomes, f'{d}: QA sem checagem de tamanho'
        assert os.path.getsize(os.path.join(base, d, 'video_app.mp4')) < 19 * 1048576
        st = json.load(open(os.path.join(base, d, 'status.json'), encoding='utf-8'))
        assert r['status'] in ('pass', 'pass_with_warnings'), (d, [c for c in r['checks'] if not c['ok']])
        assert st['estado'] == 'completed', st['estado']
        assert r['publicacao_aprovada'] is False
        for n in ('video.mp4', 'voice.wav', 'subtitles.srt', 'cover.png', 'timeline.json', 'sources.json'):
            assert os.path.exists(os.path.join(base, d, n)), n
            assert sha(os.path.join(base, d, n)) == r['arquivos'][n]['sha256'], f'{n} mudou depois do QA'


@teste
def reconstituicao_sem_anacronismo():
    """A cena 'escritorio' (V1) tem monitor bege e disquete: só serve a partir de 1980. Antes disso, 'escritorio_epoca'."""
    import glob
    import re
    from arquivo_oculto.v2 import evidencia as ev
    assert 'escritorio_epoca' in ev.PLANOS
    for f in glob.glob(os.path.join(RAIZ, 'arquivo_oculto', 'producao', 'v2', 'AO-*.v2.json')):
        m = json.load(open(f, encoding='utf-8'))
        for l in m['linhas']:
            anos = [int(x) for x in re.findall(r'\b(19\d\d|20\d\d)\b', l['fala'] + ' ' + ' '.join(s.get('tela', '') for s in l['shots']))]
            for s in l['shots']:
                if s['tipo'] == 'escritorio' and anos:
                    assert min(anos) >= 1980, f"{os.path.basename(f)} {s['id']}: escritório de 1990 numa cena de {min(anos)}"
                if s['tipo'] in ('escritorio', 'escritorio_epoca'):
                    assert s.get('selo') == 'RECONSTITUIÇÃO ILUSTRADA', f"{os.path.basename(f)} {s['id']} sem selo de reconstituição"


@teste
def titulo_longo_nao_vaza_da_tela():
    """O subtítulo do titulo_obra diminui e quebra em 2 linhas; nada de texto nas margens laterais de 90 px do quadro."""
    import numpy as np
    from PIL import Image
    from arquivo_oculto.v2 import evidencia as ev

    class Base:
        def recorte(self, reg, esc):
            return Image.new('RGB', (400, 700), (30, 24, 18))
    r = ev.titulo_obra({'base': Base()}, {'linhas': ['6 DE 149'], 'sub': 'SUBPROJETOS COM TESTES SEM CONHECIMENTO DOCUMENTADOS · 1977'})
    q = r['dyn'](3.0, 3.0)
    x0, y0 = (ev.PW - ev.W) // 2, (ev.PH - ev.H) // 2
    faixa = q[y0 + 500:y0 + 1300, x0:x0 + ev.W]
    assert faixa[:, :90].max() < 90 and faixa[:, -90:].max() < 90, 'texto encostando na borda do quadro'


@teste
def placeholder_nao_finge_ser_original():
    """Na versão pública, o plano com imagem retida diz IMAGEM RETIDA e não credita a reprodução que não aparece."""
    import glob
    from arquivo_oculto.v2 import fabrica_v2 as fab
    vistos = 0
    for f in glob.glob(os.path.join(RAIZ, 'arquivo_oculto', 'producao', 'v2', 'AO-*.v2.json')):
        m = json.load(open(f, encoding='utf-8'))
        fab.resolver_direitos(m, 'public_release')
        for l in m['linhas']:
            for s in l['shots']:
                if str(s.get('_asset_efetivo', '')).endswith('#placeholder'):
                    vistos += 1
                    assert s.get('selo') == 'IMAGEM RETIDA', (os.path.basename(f), s['id'], s.get('selo'))
                    cred = s.get('_credito') or ''
                    assert 'reprodução' not in cred and 'galeria oficial' not in cred, (s['id'], cred)
    assert vistos >= 3


@teste
def microdrama_identifica_encenacao_e_cartela():
    from arquivo_oculto.v2 import fabrica_v2 as fab, perfil
    caminho = os.path.join(RAIZ, 'arquivo_oculto', 'producao', 'microdramas', 'AO-IC-E01.v3.prod.json')
    with open(caminho, encoding='utf-8') as f:
        roteiro = json.load(f)
    p = perfil.carregar()
    assert fab.validar_manifesto(roteiro, p) == []
    assert all(s['selo'] == 'FICÇÃO' for ln in roteiro['linhas'] for s in ln['shots'])
    roteiro['linhas'][0]['shots'][0].pop('selo')
    roteiro['outro']['aviso'] = 'VOZ SINTÉTICA'
    erros = fab.validar_manifesto(roteiro, p)
    assert any('plano S01' in erro and 'FICÇÃO' in erro for erro in erros)
    assert any('cartela final' in erro for erro in erros)


if __name__ == '__main__':
    print(f'{len(OK)} ok: {OK}')
    for n, e in FALHAS:
        print('FALHOU', n, e)
    sys.exit(1 if FALHAS else 0)
