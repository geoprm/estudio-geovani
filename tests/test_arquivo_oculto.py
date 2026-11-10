"""Testes do Arquivo Oculto. Rode: python3 tests/test_arquivo_oculto.py (não precisa de pytest).
Os testes de mídia usam os arquivos de arquivo_oculto/saida/ quando existirem (gerados por gerar_episodio.sh)."""
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AO = os.path.join(RAIZ, 'arquivo_oculto')
sys.path.insert(0, AO)          # motor.py do Arquivo Oculto tem prioridade sobre o motor.py do estúdio
sys.path.append(RAIZ)
OK, FALHAS = [], []


def teste(f):
    try:
        f(); OK.append(f.__name__)
    except Exception as e:  # noqa: BLE001
        FALHAS.append((f.__name__, repr(e)))
    return f


@teste
def perfis_antigos_preservados():
    import perfis
    assert {'direitaxx', 'drgeovani', 'arquivo-oculto'} <= set(perfis.PERFIS)
    assert perfis.PERFIS['direitaxx']['assinatura'] == 'Aqui é o sertão falando.'


@teste
def skills_instaladas():
    d = os.path.join(RAIZ, '.claude', 'skills')
    nomes = [n for n in os.listdir(d) if n.startswith('arquivo-oculto-')]
    assert len(nomes) == 11 and 'arquivo-oculto-direcao-narrativa' in nomes, nomes
    for n in nomes:
        assert os.path.exists(os.path.join(d, n, 'SKILL.md'))


@teste
def manifestos_do_pacote_validos():
    r = subprocess.run([sys.executable, os.path.join(AO, 'scripts', 'validar_manifests.py')], capture_output=True, text=True)
    # o validador do pacote procura ../examples e ../.claude a partir de scripts/: aceitamos a saída OK dos dois episódios
    assert 'Erros: 0' in r.stdout or 'OK' in r.stdout, r.stdout + r.stderr


@teste
def producao_bate_com_manifesto():
    for pid in ('AO-S01-E01', 'AO-S01-E02'):
        prod = json.load(open(os.path.join(AO, 'producao', pid + '.prod.json'), encoding='utf-8'))
        man = json.load(open(os.path.join(AO, 'examples', prod['manifesto_origem'].split('/')[-1]), encoding='utf-8'))
        assert man['episode_id'] == pid
        import re
        base = lambda x: re.match(r'S\d+', x).group(0)
        assert sorted(set(base(c['scene_id']) for c in prod['cenas'])) == sorted(s['scene_id'] for s in man['scenes'])
        for s in man['scenes']:
            c = next(c for c in prod['cenas'] if c['scene_id'] == s['scene_id'])  # a cena principal do manifesto
            if s.get('reconstruction_label_required'):
                assert c.get('selo') in ('RECONSTITUIÇÃO IA', 'ILUSTRAÇÃO'), (pid, s['scene_id'])
        for c in prod['cenas']:
            assert '≠' not in c.get('tela', '') and '→' not in c.get('tela', ''), 'símbolo sem glifo na fonte'


@teste
def tipos_de_cena_registrados():
    import motor, cenas_extra  # noqa: F401
    for t in ('cartas', 'dossies', 'telas', 'escritorio', 'terminal', 'relogio', 'salto', 'tipo'):
        assert t in motor.EXTRA_CENAS


@teste
def srt_formato():
    import motor
    p = os.path.join(tempfile.mkdtemp(), 'x.srt')
    motor.srt([(0, 1.5, 'Um'), (1.5, 3.25, 'Dois')], p)
    t = open(p, encoding='utf-8').read()
    assert '00:00:01,500 --> 00:00:03,250' in t


@teste
def entregas_com_qa():
    s = os.path.join(AO, 'saida')
    if not os.path.isdir(s):
        return
    for ep in os.listdir(s):
        q = json.load(open(os.path.join(s, ep, f'{ep}_qa.json'), encoding='utf-8'))
        assert q['status'] in ('pass', 'pass_with_warnings'), (ep, q['status'])
        for ext in ('.mp4', '.srt', '_cover.png', '_manifest.json'):
            assert os.path.exists(os.path.join(s, ep, ep + ext)), ep + ext


if __name__ == '__main__':
    print(f'{len(OK)} ok: {OK}')
    for n, e in FALHAS:
        print('FALHOU', n, e)
    sys.exit(1 if FALHAS else 0)
