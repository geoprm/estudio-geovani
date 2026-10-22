"""Atalhos para montar a configuração de um vídeo a partir da pasta preparada."""
import json, os, re
import numpy as np
from motor import G


def carregar_mix(pasta):
    """Lê o resultado do ritmo.py. Retorna SEGS (para o Reel), T (tempo da gravação -> tempo do vídeo) e o rastreio."""
    mix = json.load(open(os.path.join(pasta, 'mix_segs.json')))
    sp, ms = mix['speed'], mix['segs']
    segs = [(m['off'], m['off'] + m['n'] / 30, m['z0'], m['z1']) for m in ms]

    def T(t):
        for m in ms:
            if m['src0'] <= t < m['src1']:
                return m['off'] + (t - m['src0']) / sp
        depois = [m for m in ms if m['src0'] > t]
        if depois:
            return min(depois, key=lambda m: m['src0'])['off']
        return ms[-1]['off'] + ms[-1]['n'] / 30

    return segs, T, np.load(os.path.join(pasta, 'mix_track.npy'))


def palavras(pasta):
    d = json.load(open(os.path.join(pasta, 'palavras.json')))
    out = []
    for c in d.get('chunks', []):
        w = c['text'].strip()
        if not w:
            continue
        if out and (w[0] in ',.%' or c['text'][:1] not in (' ', '')) and not w[0].isalpha():
            out[-1] = (out[-1][0] + w, out[-1][1])      # junta '46' ',8' '%' -> '46,8%'
        else:
            out.append((w, float(c['timestamp'][0])))
    return out


LIGACAO = {'a', 'o', 'as', 'os', 'da', 'do', 'das', 'dos', 'de', 'e', 'em', 'no', 'na', 'nos', 'nas',
           'que', 'um', 'uma', 'pra', 'para', 'com', 'por', 'se', 'ao', 'à'}


def grupos_auto(pasta, destaque=(), max_palavras=4, frases=None):
    """Legenda automática: 2 a 4 palavras por grupo, quebra na pontuação.
    Números e grupos curtos com ! ou ? viram ênfase ('e'). `frases` = os mesmos trechos [ini, fim] usados no ritmo.py."""
    ws = palavras(pasta)
    destaque = {d.upper() for d in destaque}
    grupos, cur = [], []

    def fecha():
        if not cur:
            return
        texto = [w for w, _ in cur]
        enf = any(re.search(r'\d', w) for w in texto) or (len(texto) <= 2 and texto[-1][-1:] in '!?')
        cols = {i: (255, 212, 0) for i, w in enumerate(texto) if w.strip('.,!?:;').upper() in destaque}
        grupos.append(G([(w.upper(), t) for w, t in cur], 'e' if enf else 'n', cols))
        cur.clear()

    for w, t in ws:
        if frases and not any(a <= t < b for a, b in frases):
            continue
        if cur and t - cur[0][1] > 1.6:
            fecha()
        cur.append((w, t))
        if w[-1:] in '.,!?;:':
            fecha()
        elif len(cur) >= max_palavras:
            sobra = cur.pop() if w.lower() in LIGACAO and len(cur) > 2 else None
            fecha()
            if sobra:
                cur.append(sobra)
    fecha()
    return grupos


def corrigir(grupos, mapa):
    """Corrige palavras que a transcrição errou, mantendo a pontuação. mapa = {'TODO': 'TODOS', 'DEIS': 'DEIXE'}.
    Use depois de grupos_auto e antes de R.set_groups. Revise sempre nomes próprios, siglas e números."""
    m = {k.upper(): v for k, v in mapa.items()}
    for g in grupos:
        novo = []
        for w, t in g['w']:
            nucleo = w.rstrip('.,;:!?…')
            fim = w[len(nucleo):]
            troca = m.get(nucleo.upper())
            novo.append(((troca if troca is not None else nucleo) + fim, t))
        g['w'] = novo
    return grupos
