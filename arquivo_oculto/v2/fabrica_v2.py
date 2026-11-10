#!/usr/bin/env python3
"""Fábrica Arquivo Oculto V2: manifesto de episódio -> video.mp4 + voice.wav + subtitles.srt + cover.png
+ timeline.json + sources.json + qa.json (+ status.json com o estado real de cada etapa).

Uso (na raiz do estúdio):
  python -m arquivo_oculto.v2.fabrica_v2 arquivo_oculto/producao/v2/AO-S01-E01.v2.json [--modo private_preview|public_release]
         [--workers 4] [--refazer S07,S09] [--so-qa]

- Estados: planned -> sources_verified -> generating_voice -> generating_visuals -> assembling -> qa -> completed | blocked.
  `completed` só depois de MP4 conferido por ffprobe e QA pass/pass_with_warnings.
- Cada plano é renderizado em um segmento próprio, com cache por hash (plano + tempos + legendas + código):
  corrigir uma cena refaz só aquele trecho.
- Filtro de direitos por modo: o que não passa usa a variante honesta declarada no manifesto.
- Nada é publicado: publicacao_aprovada fica false até revisão humana.
"""
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
AO = os.path.dirname(AQUI)
RAIZ = os.path.dirname(AO)
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from arquivo_oculto.v2 import perfil as perfil_mod  # noqa: E402

FPS, W, H = 30, 1080, 1920
SR_VOZ = 24000
SR_MIX = 48000
ATOR_TIPOS = ('aparicao', 'corredor', 'olhar_camera', 'virar_cabeca', 'debrucar', 'silencio', 'encerramento')
CATEGORIAS = {'personagem': 'personagem', 'arte_autentica': 'carta_ou_arte_real', 'documento_autentico': 'documento_historico',
              'dado_documental': 'documento_historico', 'reconstituicao_ilustrada': 'reconstituicao', 'reconstituicao_ia': 'reconstituicao',
              'ilustracao': 'ilustracao', 'tipografia': 'tipografia', 'video_arquivo': 'video_historico',
              'foto_arquivo': 'fotografia_historica', 'ficcao': 'encenacao_original'}
ARQUIVO_VISUAL = ('arte_autentica', 'documento_autentico', 'dado_documental', 'video_arquivo', 'foto_arquivo')
# planos cujo topo é ocupado por papel, terminal ou monitores: título por cima vira colisão (QA visual de 04/11/2026)
SEM_TITULO = ('ombro', 'documento_1995', 'trecho_documento', 'lista_oficial', 'arte_original', 'terminal', 'telas', 'dossie_abre',
              'pagina_documento', 'imagem_arquivo')
SELOS_OBRIGATORIOS = {'ilustracao': ('ILUSTRAÇÃO', 'INTERPRETAÇÃO', 'ANÁLISE'), 'reconstituicao_ilustrada': ('RECONSTITUIÇÃO ILUSTRADA',),
                      'reconstituicao_ia': ('RECONSTITUIÇÃO COM IA',), 'ficcao': ('FICÇÃO',)}


def agora():
    return dt.datetime.now().astimezone().isoformat(timespec='seconds')


def sha_arquivo(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def ff(args, **kw):
    return subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + args, check=True, **kw)


def ease(k):
    k = min(1.0, max(0.0, k)); return k * k * (3 - 2 * k)


class Estado:
    def __init__(self, pasta, eid, modo):
        self.p = os.path.join(pasta, 'status.json')
        self.d = {'episode_id': eid, 'modo': modo, 'estado': None, 'historico': []}

    def ir(self, estado, detalhe=''):
        self.d['estado'] = estado
        self.d['historico'].append({'estado': estado, 'em': agora(), 'detalhe': detalhe})
        with open(self.p, 'w', encoding='utf-8') as f:
            json.dump(self.d, f, ensure_ascii=False, indent=1)
        print(f'[{estado}] {detalhe}', flush=True)


# ---------------------------------------------------------------------------------------------------- validação
def validar_manifesto(man, perfil):
    if man.get('schema') == 'arquivo-oculto/roteiro-v3':
        return ['Roteiro editorial V3 em pré-produção. Feche fontes, direitos e planos no manifesto técnico antes de renderizar.']
    e = []
    if str(man.get('status_editorial', '')).startswith('rascunho'):
        e.append(f"manifesto em {man['status_editorial']}: ler as fontes, classificar os claims e trocar para pronto_para_render antes de renderizar")
    for k in ('episode_id', 'formato', 'titulo', 'linhas', 'fontes', 'claims', 'assets'):
        if k not in man:
            e.append(f'manifesto sem {k}')
    if man.get('formato') not in perfil['formats']:
        e.append(f"formato {man.get('formato')} não existe no perfil")
    if man.get('formato') == 'microdrama':
        if 'FICÇÃO' not in man.get('outro', {}).get('aviso', ''):
            e.append('microdrama sem identificação de ficção na cartela final')
        for ln in man.get('linhas', []):
            for s in ln.get('shots', []):
                if s.get('visual_source_type') in ('ficcao', 'personagem') and s.get('selo') != 'FICÇÃO':
                    e.append(f"plano {s['id']}: a encenação exige selo FICÇÃO")
    fontes = {f['id'] for f in man.get('fontes', [])}
    for c in man.get('claims', []):
        if c['status'] == 'documented' and not (c.get('fontes') and set(c['fontes']) <= fontes):
            e.append(f"claim {c['id']} documentado sem fonte registrada")
        if c['status'] not in ('documented', 'supported_inference', 'interpretation', 'allegation', 'speculative', 'refuted', 'unknown'):
            e.append(f"claim {c['id']} com status inválido")
    assets = {a['id']: a for a in man.get('assets', [])}
    for a in assets.values():
        if a['rights_status'] not in perfil_mod.RIGHTS:
            e.append(f"asset {a['id']} com rights_status inválido")
    claims = {c['id'] for c in man.get('claims', [])}
    for ln in man.get('linhas', []):
        for c in ln.get('claims', []):
            if c not in claims:
                e.append(f"linha {ln['id']} cita claim inexistente {c}")
        for s in ln['shots']:
            if s.get('asset') not in assets:
                e.append(f"plano {s['id']} sem asset registrado")
            tela = s.get('tela', '')
            if tela and s['tipo'] in SEM_TITULO:
                e.append(f"plano {s['id']} ({s['tipo']}): título na tela colide com o documento/tela desenhado; use a legenda ou o selo")
            if len(tela.split()) > perfil['storytelling']['on_screen_text_max_words']:
                e.append(f"plano {s['id']}: texto na tela com mais de {perfil['storytelling']['on_screen_text_max_words']} palavras")
            for k in ('shot_type', 'visual_source_type', 'movement', 'sound_design', 'prompt', 'negative_prompt'):
                if not s.get(k):
                    e.append(f"plano {s['id']} sem {k}")
            if s.get('personagem'):
                for k in ('action', 'gesture', 'camera_motion', 'emotional_beat'):
                    if not s.get(k):
                        e.append(f"plano de personagem {s['id']} sem {k}")
    return e


def resolver_direitos(man, modo):
    """Decide, por plano, se o asset entra neste modo ou se a variante honesta é usada."""
    assets = {a['id']: a for a in man['assets']}
    decisoes = []
    for ln in man['linhas']:
        for s in ln['shots']:
            a = assets[s['asset']]
            ok = perfil_mod.gate_direitos(a['rights_status'], modo)
            efetivo = a
            if not ok:
                fb = a.get('fallback')
                if fb == 'placeholder':
                    # o placeholder não pode herdar o selo "CARTA/ARTE ORIGINAL" nem o crédito da reprodução que não aparece
                    base = (a.get('credito') or '').split(' · reprodução')[0].split(' · galeria oficial')[0].strip()
                    efetivo = {**a, 'id': a['id'] + '#placeholder', 'rights_status': 'original_production',
                               'autenticidade': 'placeholder honesto (imagem original retida)',
                               'credito': (base + ' · ' if base else '') + 'retida nesta versão, aguardando licença'}
                    s['selo'] = 'IMAGEM RETIDA'
                elif fb in assets:
                    efetivo = assets[fb]
                else:
                    raise RuntimeError(f"plano {s['id']}: asset {a['id']} barrado no modo {modo} e sem fallback")
            s['_gate_ok'] = ok
            s['_asset_efetivo'] = efetivo['id']
            s['rights_status'] = efetivo['rights_status']
            s['source_id'] = a.get('fonte') or efetivo.get('fonte') or None
            s['_credito'] = efetivo.get('credito') if s.get('credito') else None
            s['_privado'] = efetivo['rights_status'] in ('private_research', 'quotation_excerpt')
            s['asset_path'] = a.get('arquivo') if ok else (efetivo.get('arquivo') or 'gerado no render (placeholder/paráfrase)')
            decisoes.append({'plano': s['id'], 'asset': a['id'], 'rights_status': a['rights_status'], 'modo': modo,
                             'liberado': ok, 'efetivo': efetivo['id']})
    return decisoes


# ---------------------------------------------------------------------------------------------------- voz
def gerar_voz(man, lock, pasta):
    from arquivo_oculto.v2 import voz as vz
    v = vz.Voz(lock['voice']['voice_id'])
    cursor = 0.40
    spans, partes = [], []
    for ln in man['linhas']:
        s = v.sintetizar(ln.get('tts') or ln['fala'])
        d = len(s) / SR_VOZ
        spans.append({'linha': ln['id'], 'ini': round(cursor, 3), 'fim_voz': round(cursor + d, 3)})
        partes.append((cursor, s))
        cursor += d + ln.get('pausa_ms', 300) / 1000
        spans[-1]['fim'] = round(cursor, 3)
    fim_fala = cursor
    dur = fim_fala + man.get('outro', {}).get('duracao_s', 2.6)
    trilha = np.zeros(int(math.ceil(dur * SR_VOZ)) + 1, np.float32)
    for st, s in partes:
        i0 = int(st * SR_VOZ); trilha[i0:i0 + len(s)] += s
    cru = os.path.join(pasta, '_voz_crua.wav')
    vz.escrever_wav(cru, trilha / max(1e-6, np.abs(trilha).max()) * 0.9)
    final = os.path.join(pasta, 'voice.wav')
    ff(['-i', cru, '-filter_complex', v.filtro_ffmpeg() + ';[v]loudnorm=I=-16:TP=-1.5[o]', '-map', '[o]', '-ar', str(SR_MIX), '-ac', '1', final])
    os.remove(cru)
    return spans, fim_fala, dur, v.config_registro()


# ---------------------------------------------------------------------------------------------------- timeline
def montar_timeline(man, spans, fim_fala, dur):
    shots = []
    nlin = len(man['linhas'])
    for i, (ln, sp) in enumerate(zip(man['linhas'], spans)):
        ini = 0.0 if i == 0 else sp['ini']
        fim = spans[i + 1]['ini'] if i + 1 < nlin else fim_fala
        pesos = [s.get('peso', 1.0) for s in ln['shots']]
        tot = sum(pesos); t = ini
        for s, p in zip(ln['shots'], pesos):
            d = (fim - ini) * p / tot
            shots.append({**s, 'linha': ln['id'], 'beat': ln['beat'], 'ini': t, 'fim': t + d,
                          'voice_span': [sp['ini'], sp['fim_voz']], 'sync_to_voice': True})
            t += d
    shots.append({'id': 'OUTRO', 'tipo': 'outro', 'linha': None, 'beat': 'assinatura', 'ini': fim_fala, 'fim': dur,
                  'voice_span': None, 'visual_source_type': man['outro']['visual_source_type'],
                  'rights_status': man['outro']['rights_status'], 'asset': 'A-PRODUCAO-ORIGINAL', 'tela': '',
                  'shot_type': 'cartela final', 'movement': 'fade e push-in lento', 'sound_design': 'sting e cauda da trilha',
                  'prompt': 'cartela da série com próximo arquivo e aviso de IA', 'negative_prompt': 'promessa falsa',
                  'source_id': None, 'asset_path': 'gerado no render', '_privado': False, '_gate_ok': True})
    total_f = int(round(dur * FPS))
    for s in shots:
        s['f0'] = int(round(s['ini'] * FPS)); s['f1'] = int(round(s['fim'] * FPS))
    shots[-1]['f1'] = total_f
    for s in shots:
        s['duration'] = round((s['f1'] - s['f0']) / FPS, 3)
    return shots


def legendas(man, spans):
    from arquivo_oculto.v2 import fundo_motor as fm
    out = []
    for ln, sp in zip(man['linhas'], spans):
        bl = fm.blocos_legenda(ln['fala'])
        # sem palavra órfã: um bloco de uma palavra volta para o anterior (a renderização garante 2 linhas)
        junt = []
        for b in bl:
            if junt and (len(b.split()) == 1 or len(junt[-1].split()) == 1) and len(junt[-1]) + len(b) <= 60:
                junt[-1] = junt[-1] + ' ' + b
            else:
                junt.append(b)
        bl = junt
        d_voz = sp['fim_voz'] - sp['ini']; tot = sum(len(b) for b in bl); t = sp['ini']
        for j, b in enumerate(bl):
            d = d_voz * len(b) / tot
            fim = t + d if j < len(bl) - 1 else min(sp['fim'], sp['fim_voz'] + 0.35)
            out.append((round(t, 3), round(fim, 3), b))
            t += d
    return out


# ---------------------------------------------------------------------------------------------------- render por plano (processos)
_W = {}
CODIGO = None


def hash_codigo(tipo, prova=None):
    """Impressão digital só do código que desenha este TIPO de plano (corrigir um tipo não refaz os outros)."""
    import inspect
    from arquivo_oculto.v2 import evidencia as ev
    fonte = lambda f: inspect.getsource(f)
    lido = lambda n, base=AQUI: open(os.path.join(base, n), 'rb').read().decode('utf-8', 'replace')
    partes = [fonte(render_plano), fonte(_overlays), fonte(_legenda_img), fonte(_camera), fonte(_pre), lido('fundo_motor.py')]
    ajudantes = ''.join(fonte(f) for f in (ev.ease, ev.janela, ev._np, ev.mesa, ev.papel, ev.colar, ev.circulo_tinta, ev.feixe))

    def evid(t):
        if t in ('telas', 'escritorio', 'dossies', 'terminal'):
            return fonte(ev.adaptar_extra) + lido('cenas_extra.py', AO) + lido('motor.py', AO)
        extra = fonte(ev._verso) if t == 'cartas_caem' else ''
        return fonte(ev.PLANOS[t]) + ajudantes + extra
    if tipo in ATOR_TIPOS:
        partes.append(lido('ator.py'))
    elif tipo == 'outro':
        partes += [lido('ator.py'), fonte(_outro)]
    elif tipo == 'ombro':
        partes += [lido('ator.py'), evid(prova)]
    else:
        partes.append(evid(tipo))
    return hashlib.sha256(''.join(partes).encode()).hexdigest()[:16]


def _init_worker():
    import cv2
    from arquivo_oculto.v2.ator import Atores
    from arquivo_oculto.v2 import fundo_motor as fm
    cv2.setNumThreads(1)
    _W['ator'] = Atores(W, H)
    _W['ctx'] = {'base': fm.Base()}
    _W['vin'] = fm.vinheta()
    _W['gr'] = fm.graos()


def _pre(lay):
    a = np.asarray(lay, np.float32); al = a[..., 3:4] / 255.0
    return a[..., :3] * al, 1.0 - al


def _overlays(job):
    from PIL import Image, ImageDraw
    from arquivo_oculto.v2 import fundo_motor as fm
    s = job['shot']
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    g = np.zeros((H, W, 4), np.uint8); ys = np.arange(H, dtype=np.float32)
    a = np.clip((380 - ys) / 380, 0, 1) * 0.55 + np.clip((ys - 1180) / 520, 0, 1) * 0.80
    g[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)[:, None]
    lay.alpha_composite(Image.fromarray(g, 'RGBA'))
    if s['tipo'] != 'outro':
        f = fm.fonte('cinzel', 30); t = f'ARQUIVO OCULTO · Nº {job["num"]:02d}'
        d.text((W - 100 - f.getlength(t), 196), t, font=f, fill=fm.OURO + (210,))
    if s.get('selo'):
        f = fm.fonte('oswald', 32); txt = s['selo']
        cor = {'DOCUMENTADO': (52, 150, 96), 'DOCUMENTO DE 1995': (52, 150, 96), 'INTERPRETAÇÃO': (196, 140, 50),
               'ANÁLISE': (196, 140, 50), 'ARTE ORIGINAL': (52, 150, 96)}.get(txt, (150, 120, 70))
        w = f.getlength(txt)
        d.rounded_rectangle((100, 190, 100 + w + 36, 244), 8, fill=(10, 8, 6, 210), outline=cor + (255,), width=3)
        d.text((118, 195), txt, font=f, fill=fm.CREME + (255,))
    tit = None
    if s.get('tela'):
        tit = Image.new('RGBA', (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(tit)
        tam = 104
        while True:
            f = fm.fonte('anton', tam); ls = fm.quebrar(s['tela'], f, W - 220)
            if len(ls) <= 2 or tam < 64: break
            tam -= 6
        for i, l in enumerate(ls):
            fm.texto_centro(td, W / 2, 290 + i * tam * 1.1, l, f, fm.OURO_CLARO + (255,), stroke=3, stroke_cor=(20, 12, 4))
    if s.get('_credito'):
        f = fm.fonte('oswald4', 30)
        for i, l in enumerate(fm.quebrar(s['_credito'], f, W - 200)[:2]):
            d.text((100, 1268 + i * 38), l, font=f, fill=fm.CREME + (215,))
    if s.get('_privado'):
        f = fm.fonte('oswald', 28); t = 'PRÉVIA PRIVADA · DIREITOS EM VERIFICAÇÃO · NÃO PUBLICAR'
        d.text(((W - f.getlength(t)) / 2, 1668), t, font=f, fill=(210, 80, 70, 230))
    return _pre(lay), (_pre(tit) if tit else None)


def _legenda_img(txt):
    from PIL import Image, ImageDraw
    from arquivo_oculto.v2 import fundo_motor as fm
    lay = Image.new('RGBA', (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    tam = 64
    while True:                                   # nunca truncar: reduz a fonte até caber em 2 linhas
        f = fm.fonte('oswald', tam); ls = fm.quebrar(txt, f, W - 220)
        if len(ls) <= 2 or tam <= 44: break
        tam -= 4
    alt = int(tam * 1.31)
    # tarja escura suave atrás de cada linha: legível sobre papel claro e sobre fundo escuro
    for i, l in enumerate(ls):
        wl = f.getlength(l)
        d.rounded_rectangle((W / 2 - wl / 2 - 26, 14 + i * alt, W / 2 + wl / 2 + 26, 14 + i * alt + tam + 22), 14, fill=(6, 5, 4, 120))
    for i, l in enumerate(ls):
        fm.texto_centro(d, W / 2, 20 + i * alt, l, f, fm.CREME + (255,), sombra=False, stroke=5, stroke_cor=(0, 0, 0))
    return _pre(lay)


def _camera(ev, k, tl, dur):
    import cv2
    P = ev['dyn'](tl, dur)
    z0, z1 = ev['zoom']; (px0, py0), (px1, py1) = ev['pan']
    e = ease(k); z = z0 + (z1 - z0) * e; px = px0 + (px1 - px0) * e; py = py0 + (py1 - py0) * e
    ph, pw = P.shape[:2]
    cw, ch = pw / z, ph / z
    if cw / ch > W / H: cw = ch * W / H
    else: ch = cw * H / W
    cx = pw / 2 + px * (pw - cw) / 2; cy = ph / 2 + py * (ph - ch) / 2
    sx, sy = W / cw, H / ch
    M = np.array([[sx, 0, -(cx - cw / 2) * sx], [0, sy, -(cy - ch / 2) * sy]], np.float32)
    return cv2.warpAffine(P.astype(np.float32), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def _outro(job, k, t):
    from PIL import Image, ImageDraw
    from arquivo_oculto.v2 import fundo_motor as fm
    if 'outro_base' not in _W:
        base = _W['ator'].quadro('silencio', 0.5, 0.0, 1.0) * 0.22
        img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        o = job['outro']
        fm.texto_centro(d, W / 2, 1020, 'ARQUIVO OCULTO', fm.fonte('cinzel', 92), fm.OURO_CLARO + (255,))
        d.line((W / 2 - 170, 1140, W / 2 + 170, 1140), fill=fm.OURO + (255,), width=3)
        y = 1180
        for l in o['linhas'][1:]:
            fm.texto_centro(d, W / 2, y, l, fm.fonte('oswald', 50), fm.CREME + (240,)); y += 66
        fm.texto_centro(d, W / 2, 1500, o['linhas'][0], fm.fonte('oswald', 36), fm.OURO + (220,))
        fm.texto_centro(d, W / 2, 1580, o['aviso'], fm.fonte('oswald4', 34), (228, 218, 196, 240))
        _W['outro_base'] = np.asarray(img.convert('RGB'), np.float32)
    import cv2
    z = 1.0 + 0.03 * k
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
    a = cv2.warpAffine(_W['outro_base'], M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return a * min(1.0, k / 0.12) * min(1.0, (1 - k) / 0.18 + 0.0001)


def render_plano(job):
    import cv2
    from arquivo_oculto.v2 import evidencia as ev
    s = job['shot']; f0, f1 = s['f0'], s['f1']; n = f1 - f0; dur = n / FPS
    seg = job['saida']
    meta = seg + '.json'
    if os.path.exists(seg) and os.path.exists(meta) and not job.get('forcar'):
        r = json.load(open(meta, encoding='utf-8')); r['cache'] = 'hit'; return r
    t_ini = time.time()
    ator, ctx = _W['ator'], _W['ctx']
    params = dict(s.get('params', {}))
    tipo = s['tipo']
    if tipo in ATOR_TIPOS:
        abertura_boca = s.get('_abertura_boca')
        fn = lambda k, t, tl: ator.quadro(
            tipo, k, t, dur, params, abertura_boca[min(n - 1, round(tl * FPS))] if abertura_boca else 0.0)
    elif tipo == 'outro':
        fn = lambda k, t, tl: _outro(job, k, t)
    elif tipo == 'ombro':
        pv = s['prova']; pp = dict(pv.get('params', {})); pp['_gate_ok'] = s['_gate_ok']
        if pv['tipo'] == 'arte_original':
            pp.setdefault('arquivo', job['assets'][s['asset']].get('arquivo')); pp.setdefault('credito', job['assets'][s['asset']].get('credito'))
        if pv['tipo'] == 'lista_oficial':
            pp['linhas'] = job['listas'][pp['lista']]
        evp = ev.PLANOS[pv['tipo']](ctx, pp)
        fn = lambda k, t, tl: ator.ombro(k, t, _camera(evp, 0.6 + 0.4 * k, tl, dur), params)
    else:
        pp = dict(params); pp['_gate_ok'] = s['_gate_ok']
        if tipo == 'arte_original':
            pp.setdefault('arquivo', job['assets'][s['asset']].get('arquivo')); pp.setdefault('credito', job['assets'][s['asset']].get('credito'))
        if tipo == 'lista_oficial':
            pp['linhas'] = job['listas'][pp['lista']]
        e = ev.PLANOS[tipo](ctx, pp)
        fn = lambda k, t, tl: _camera(e, k, tl, dur)
    (ov_rgb, ov_inv), tit = _overlays(job)
    legs = [(a, b, _legenda_img(txt)) for (a, b, txt) in job['legendas'] if b > f0 / FPS and a < f1 / FPS]
    LY = 1380
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '6M', '-bufsize', '12M', '-pix_fmt', 'yuv420p', '-g', '60',
           '-r', str(FPS), seg + '.tmp.mp4']
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    rng = np.random.default_rng(f0 + 7)
    amostras = {}
    vin, gr = _W['vin'], _W['gr']
    for i in range(n):
        fi = f0 + i; t = fi / FPS; tl = i / FPS
        k = i / max(1, n - 1)
        a = fn(k, t, tl)
        if a.dtype != np.float32: a = a.astype(np.float32)
        a = a * ov_inv + ov_rgb
        if tit is not None:
            ap = min(1.0, tl / 0.25)
            trgb, tinv = tit
            a = a * (1 - (1 - tinv) * ap) + trgb * ap
        for (la, lb, (lr, li)) in legs:
            if la <= t < lb:
                a[LY:LY + 260] = a[LY:LY + 260] * li + lr; break
        if s.get('corte', True) and s['id'] != job['primeiro'] and tl < 0.10:
            a *= 0.35 + 6.5 * tl
        fl = 1.0 + 0.03 * math.sin(fi * 0.9) * rng.random()
        a = a * vin * fl + gr[fi % len(gr)] * 0.5          # grão leve: textura sem explodir o bitrate
        a[..., 2] *= 0.94
        q = np.clip(a, 0, 255).astype(np.uint8)
        for nome, kk in (('a', 0.15), ('m', 0.5), ('b', 0.85)):
            if i == int(kk * (n - 1)):
                amostras[nome] = cv2.resize(q, (216, 384), interpolation=cv2.INTER_AREA)
        proc.stdin.write(q.tobytes())
    proc.stdin.close(); proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f'ffmpeg falhou no plano {s["id"]}')
    os.replace(seg + '.tmp.mp4', seg)
    g = lambda x: cv2.cvtColor(x, cv2.COLOR_RGB2GRAY).astype(np.float32)
    mov = float(np.abs(g(amostras['a']) - g(amostras['b'])).mean()) if 'a' in amostras and 'b' in amostras else 0.0
    lum = float(g(amostras['m']).mean()) if 'm' in amostras else 0.0
    cv2.imwrite(seg + '.png', cv2.cvtColor(amostras.get('m', np.zeros((384, 216, 3), np.uint8)), cv2.COLOR_RGB2BGR))
    r = {'id': s['id'], 'seg': seg, 'mov': round(mov, 2), 'lum': round(lum, 1), 'quadros': n,
         'ms_por_quadro': round((time.time() - t_ini) * 1000 / max(1, n)), 'cache': 'miss'}
    json.dump(r, open(meta, 'w', encoding='utf-8'), ensure_ascii=False)
    return r


# ---------------------------------------------------------------------------------------------------- som
def _ruido(n, rng, lo, hi, sr=SR_MIX):
    x = rng.standard_normal(n)
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / sr)
    X[(fr < lo) | (fr > hi)] = 0
    y = np.fft.irfft(X, n)
    return (y / max(1e-9, np.abs(y).max())).astype(np.float32)


def efeitos(shots, dur):
    rng = np.random.default_rng(5)
    n = int(dur * SR_MIX) + 1; out = np.zeros(n, np.float32)

    def put(t, sig, g):
        i0 = int(t * SR_MIX)
        if i0 >= n: return
        m = min(len(sig), n - i0); out[i0:i0 + m] += sig[:m] * g

    def env(m, a, d):
        tt = np.arange(m) / SR_MIX
        return (np.minimum(1, tt / max(1e-4, a)) * np.exp(-tt / d)).astype(np.float32)
    for s in shots:
        t0, t1, tp = s['ini'], s['fim'], s['tipo']
        if tp == 'cartas_caem':
            for i in range(int(s.get('params', {}).get('n', 9))):
                tt = t0 + 0.05 + i * 0.16 + 0.28
                m = int(0.12 * SR_MIX)
                put(tt, _ruido(m, rng, 1500, 7000) * env(m, 0.001, 0.012) + np.sin(2 * np.pi * 70 * np.arange(m) / SR_MIX).astype(np.float32) * env(m, 0.002, 0.04) * 0.6, 0.55)
        if tp in ('documento_1995', 'lista_oficial', 'arte_original', 'dossie_abre', 'ombro', 'titulo_obra', 'bilhete_indice'):
            m = int(0.45 * SR_MIX); put(t0 + 0.02, _ruido(m, rng, 900, 6000) * env(m, 0.03, 0.12), 0.22)
        if tp in ('documento_1995',):
            m = int(0.5 * SR_MIX); sig = _ruido(m, rng, 2500, 9000) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * np.arange(m) / SR_MIX)).astype(np.float32)
            put(t0 + (t1 - t0) * 0.25, sig * env(m, 0.02, 0.3), 0.18)
        if tp == 'lista_oficial':
            for sy in s.get('params', {}).get('sync', []):
                if sy <= 1:
                    m = int(0.42 * SR_MIX); sig = _ruido(m, rng, 2500, 9000) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * np.arange(m) / SR_MIX)).astype(np.float32)
                    put(t0 + (t1 - t0) * sy, sig * env(m, 0.02, 0.25), 0.2)
        if tp == 'corredor':
            tt = t0 + 0.15
            while tt < t1:
                m = int(0.16 * SR_MIX)
                put(tt, _ruido(m, rng, 60, 600) * env(m, 0.003, 0.05), 0.5); tt += 0.55 + rng.uniform(-0.03, 0.03)
        if tp == 'silencio':
            tt = t0 + 0.2
            while tt < t1:
                m = int(0.03 * SR_MIX); put(tt, _ruido(m, rng, 2000, 8000) * env(m, 0.0005, 0.006), 0.25); tt += 1.0
        if tp == 'grade_cartas' and s.get('params', {}).get('fase') == 'contagem':
            for j in range(40):
                tt = t0 + (t1 - t0) * 0.75 * j / 40
                m = int(0.02 * SR_MIX); put(tt, _ruido(m, rng, 2500, 8000) * env(m, 0.0005, 0.004), 0.16)
        if tp == 'encerramento':
            m = int(0.06 * SR_MIX); put(t0 + (t1 - t0) * 0.62, _ruido(m, rng, 1500, 9000) * env(m, 0.0005, 0.01), 0.6)
        if tp == 'escritorio_epoca':
            acao = s.get('params', {}).get('acao', 'lanterna')
            if acao in ('gaveta', 'lanterna'):                    # trilho da gaveta de aço
                ab = 0.15 if acao == 'gaveta' else 0.50
                m = int(0.75 * SR_MIX); tt = np.arange(m) / SR_MIX
                sig = _ruido(m, rng, 250, 2400) * (0.55 + 0.45 * np.sin(2 * np.pi * 13 * tt)).astype(np.float32) * np.sin(np.pi * tt / 0.75).astype(np.float32)
                put(t0 + (t1 - t0) * ab, sig, 0.24)
            if acao == 'luminaria':                                   # clique do interruptor
                m = int(0.04 * SR_MIX); put(t0 + (t1 - t0) * 0.10, _ruido(m, rng, 1500, 8000) * env(m, 0.0005, 0.008), 0.55)
        if tp in ('quadro_cinema', 'lata_cinema'):
            modo = s['params'].get('modo')
            m = int(min(t1 - t0, 1.15) * SR_MIX)
            if m > 0:
                tt = np.arange(m) / SR_MIX
                if modo == 'pelicula':
                    sig = _ruido(m, rng, 340, 3400) * (0.44 + 0.56 * np.sin(2 * np.pi * 18 * tt) ** 6)
                    put(t0, sig * env(m, 0.045, 0.78), 0.32)
                else:
                    frequencia = 91 if modo == 'lente' else 66
                    sig = np.sin(2 * np.pi * frequencia * tt) + 0.36 * _ruido(m, rng, 150, 2000)
                    put(t0 + 0.11, sig * env(m, 0.011, 0.24), 0.25)
        if tp in ('telas', 'salto_datas', 'escritorio', 'escritorio_epoca', 'grade_cartas', 'leituras'):
            m = int(0.6 * SR_MIX); tt = np.arange(m) / SR_MIX
            sig = _ruido(m, rng, 200, 3000) * np.sin(np.pi * tt / 0.6).astype(np.float32)
            put(t0, sig, 0.12)
    return out


def mixar(pasta, shots, spans, fim_fala, dur):
    from arquivo_oculto.v2 import fundo_motor as fm
    from arquivo_oculto.v2 import voz as vz
    cortes = [s['ini'] for s in shots[1:] if s['tipo'] not in ATOR_TIPOS]
    mus = fm.trilha(dur, cortes, fim_fala)
    vz.escrever_wav(os.path.join(pasta, '_musica.wav'), mus / max(1e-6, np.abs(mus).max()) * 0.9, SR_VOZ)
    sfx = efeitos(shots, dur)
    vz.escrever_wav(os.path.join(pasta, '_sfx.wav'), sfx / max(1e-6, np.abs(sfx).max()) * 0.8, SR_MIX)
    filtro = ('[0:a]aformat=channel_layouts=mono,asplit=2[v][sc];'
              '[1:a]aresample=48000,volume=0.34[m];'
              '[m][sc]sidechaincompress=threshold=0.02:ratio=9:attack=15:release=320[md];'
              '[2:a]volume=0.8[s];'
              '[v][md][s]amix=inputs=3:weights=1 0.85 0.8:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=9[a]')
    mix = os.path.join(pasta, '_mix.wav')
    ff(['-i', os.path.join(pasta, 'voice.wav'), '-i', os.path.join(pasta, '_musica.wav'), '-i', os.path.join(pasta, '_sfx.wav'),
        '-filter_complex', filtro, '-map', '[a]', '-ar', str(SR_MIX), '-ac', '2', mix])
    os.remove(os.path.join(pasta, '_musica.wav')); os.remove(os.path.join(pasta, '_sfx.wav'))
    return mix, {'musica': 'sintetizada pelo motor (drone, pulso, impactos, sting)', 'sfx': 'sintetizados (cartas, papel, lápis, passos, relógio, lâmpada)',
                 'ducking': 'sidechaincompress ratio 9, threshold 0.02 (alvo 12–18 dB sob a voz)', 'loudnorm': 'I=-15 LUFS, TP=-1.5 dBTP'}


# ---------------------------------------------------------------------------------------------------- versão para o app
def versao_app(pasta, master, dur, alvo_mib=18.0):
    """Cópia de até ~18 MiB (2 passadas) para o player e o download do app, que guarda arquivos em partes de 19 MiB."""
    br = int(alvo_mib * 8 * 1048576 / dur / 1000) - 128
    log = os.path.join(pasta, '_2pass')
    ff(['-i', master, '-c:v', 'libx264', '-preset', 'medium', '-b:v', f'{br}k', '-pass', '1', '-passlogfile', log, '-an', '-f', 'null', '-'])
    out = os.path.join(pasta, 'video_app.mp4')
    ff(['-i', master, '-c:v', 'libx264', '-preset', 'medium', '-b:v', f'{br}k', '-pass', '2', '-passlogfile', log, '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out])
    for x in os.listdir(pasta):
        if x.startswith('_2pass'):
            os.remove(os.path.join(pasta, x))
    return out


# ---------------------------------------------------------------------------------------------------- capa
def capa(pasta, man):
    from PIL import Image, ImageDraw
    from arquivo_oculto.v2.ator import Atores
    from arquivo_oculto.v2 import fundo_motor as fm
    a = Atores(W, H).quadro('olhar_camera', 1.0, 2.0, 2.0)
    img = Image.fromarray(np.clip(a * 0.95, 0, 255).astype(np.uint8)).convert('RGBA')
    g = np.zeros((H, W, 4), np.uint8); ys = np.arange(H)
    g[..., 3] = (np.clip((ys - 1000) / 520, 0, 1) * 235).astype(np.uint8)[:, None]
    img.alpha_composite(Image.fromarray(g, 'RGBA')); d = ImageDraw.Draw(img)
    tam = 132
    while True:
        f = fm.fonte('anton', tam); ls = fm.quebrar(man['hook'], f, W - 200)
        if len(ls) <= 2 or tam < 70: break
        tam -= 8
    y = 1240
    for i, l in enumerate(ls):
        fm.texto_centro(d, W / 2, y + i * tam * 1.1, l, f, fm.OURO_CLARO + (255,), stroke=4, stroke_cor=(15, 10, 4))
    fm.texto_centro(d, W / 2, 1560, f'ARQUIVO OCULTO · Nº {man["num"]:02d}', fm.fonte('cinzel', 44), fm.CREME + (230,))
    p = os.path.join(pasta, 'cover.png'); img.convert('RGB').save(p)
    return p


# ---------------------------------------------------------------------------------------------------- QA
def qa(pasta, man, perfil, shots, legs, resultados, modo, voz_cfg):
    r = {'status': 'pass', 'checks': [], 'modo': modo, 'gerado_em': agora()}

    def add(nome, ok, info, grave=True):
        r['checks'].append({'check': nome, 'ok': bool(ok), 'grave': grave, 'info': info})
        if not ok:
            if grave: r['status'] = 'fail'
            elif r['status'] == 'pass': r['status'] = 'pass_with_warnings'
    mp4 = os.path.join(pasta, 'video.mp4')
    pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', mp4],
                                   capture_output=True, text=True).stdout or '{}')
    v = next((x for x in pr.get('streams', []) if x['codec_type'] == 'video'), {})
    a = next((x for x in pr.get('streams', []) if x['codec_type'] == 'audio'), {})
    dur = float(pr.get('format', {}).get('duration', 0))
    fmt = perfil_mod.formato(perfil, man['formato'])
    add('ffprobe_video', v.get('width') == fmt['largura'] and v.get('height') == fmt['altura'] and v.get('codec_name') == 'h264'
        and v.get('pix_fmt') == 'yuv420p' and v.get('r_frame_rate') == '30/1',
        f"{v.get('width')}x{v.get('height')} {v.get('codec_name')} {v.get('pix_fmt')} {v.get('r_frame_rate')}")
    add('ffprobe_audio', a.get('codec_name') == 'aac' and a.get('sample_rate') == '48000' and a.get('channels') == 2,
        f"{a.get('codec_name')} {a.get('sample_rate')} Hz {a.get('channels')} canais")
    lo, hi = fmt['duration_seconds']
    add('duracao_no_formato', lo <= dur <= hi, f'{dur:.2f} s (formato {fmt["label"]}: {lo}–{hi} s, padrão {fmt["default_seconds"]} s)')
    add('duracao_perto_do_padrao', abs(dur - fmt['default_seconds']) <= 10, f'{dur:.2f} s vs {fmt["default_seconds"]} s', grave=False)
    head = open(mp4, 'rb').read(256 * 1024)
    add('faststart_moov_no_inicio', head.find(b'moov') != -1 and (head.find(b'mdat') == -1 or head.find(b'moov') < head.find(b'mdat')), 'moov antes de mdat')
    nshots = len(shots)
    st = fmt.get('shots_target')
    if st:
        add('numero_de_planos', st[0] <= nshots <= st[1], f'{nshots} planos (alvo {st[0]}–{st[1]})', grave=False)
    res = {x['id']: x for x in resultados}
    escuros = [s['id'] for s in shots if s['tipo'] not in ('encerramento', 'outro') and res[s['id']]['lum'] < 8]
    add('sem_quadro_preto', not escuros, f'planos com luminância média < 8 no meio: {escuros}')
    # loudness
    lo_txt = subprocess.run(['ffmpeg', '-v', 'info', '-i', mp4, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = re.findall(r'I:\s+(-?[\d.]+) LUFS', lo_txt); TP = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', lo_txt)
    li = float(I[-1]) if I else None; tp = float(TP[-1]) if TP else None
    add('loudness', li is not None and -17 <= li <= -13 and (tp is None or tp <= -1.0), f'{li} LUFS integrado, pico {tp} dBTP (alvo -15±2, ≤ -1)')
    # legendas
    srtp = os.path.join(pasta, 'subtitles.srt')
    blocos = [b for b in open(srtp, encoding='utf-8').read().strip().split('\n\n') if b.strip()]
    tempos = []
    for b in blocos:
        ln = b.split('\n')
        x, y = ln[1].split('-->')
        conv = lambda q: sum(float(p_) * m for p_, m in zip(q.strip().replace(',', '.').split(':'), (3600, 60, 1)))
        tempos.append((conv(x), conv(y)))
    mono = all(tempos[i][0] < tempos[i][1] <= tempos[i + 1][0] + 1e-3 for i in range(len(tempos) - 1))
    add('srt_monotonico', mono and len(tempos) >= len(man['linhas']), f'{len(tempos)} legendas; última termina em {tempos[-1][1]:.2f} s')
    txt_srt = ''.join(''.join(b.split('\n')[2:]) for b in blocos).replace(' ', '')
    falas = ''.join(l['fala'] for l in man['linhas']).replace(' ', '')
    add('legenda_igual_narracao', txt_srt == falas, 'texto das legendas = texto narrado')
    # personagem
    metas = perfil_mod.metas_personagem(perfil, dur)
    pers = [s for s in shots if s.get('personagem')]
    pers_inteiro = [s for s in pers if not s.get('parcial')]
    tipos_pers = sorted({s['tipo'] for s in pers})
    add('planos_distintos_do_personagem', len(tipos_pers) >= metas['min_planos_distintos'],
        f'{len(tipos_pers)} tipos de plano {tipos_pers} (mínimo {metas["min_planos_distintos"]} para {dur:.0f} s)')
    longos = [f"{s['id']}={s['duration']}s" for s in pers if s['duration'] > metas['max_plano_estatico_s'] + 0.6]
    add('plano_do_personagem_curto', not longos, f'planos do personagem acima de {metas["max_plano_estatico_s"]} s (+0,6 de tolerância): {longos}')
    parados = [s['id'] for s in pers if res[s['id']]['mov'] < 2.0]
    add('personagem_em_movimento', not parados, 'diferença média entre 15% e 85% de cada plano do personagem: ' +
        ', '.join(f"{s['id']}={res[s['id']]['mov']}" for s in pers) + f' | parados: {parados}')
    tempo_pers = sum(s['duration'] * (0.5 if s.get('parcial') else 1) for s in pers)
    pct = 100 * tempo_pers / dur
    add('tempo_de_tela_do_personagem', metas['tempo_tela_pct'][0] <= pct <= metas['tempo_tela_pct'][1],
        f'{pct:.1f}% (alvo {metas["tempo_tela_pct"][0]}–{metas["tempo_tela_pct"][1]}%)', grave=False)
    planos_falados = [s for s in pers if s.get('mascara_falada')]
    if man.get('mascara_falada'):
        add('mascara_falada_em_cena', bool(planos_falados) and all(
            s.get('boca_pico', 0) > 0.25 for s in planos_falados),
            f'{len(planos_falados)} plano(s) com articulação guiada pelo envelope da voz')
    else:
        add('mascara_rigida_sem_boca', not planos_falados, 'corte legado com atuação corporal e boca estática')
    add('personagem_entra_e_sai', any(s['tipo'] == 'aparicao' for s in pers) and any(s['tipo'] in ('encerramento', 'corredor') for s in pers),
        'aparição + saída/caminhada presentes')
    # arquivo e categorias
    # conta material de arquivo real ou paráfrase com fonte; o placeholder de asset retido não conta
    arq = sum(s['duration'] for s in shots if s.get('visual_source_type') in ARQUIVO_VISUAL
              and not str(s.get('_asset_efetivo', '')).endswith('#placeholder'))
    pa = 100 * arq / dur
    alvo = perfil['storytelling']['archive_visuals_target_pct']
    add('visuais_de_arquivo', alvo[0] <= pa <= alvo[1], f'{pa:.1f}% (alvo {alvo[0]}–{alvo[1]}%)', grave=False)
    cats = sorted({CATEGORIAS.get(s.get('visual_source_type'), 'outro') for s in shots if s.get('_gate_ok', True) or s.get('visual_source_type') != 'arte_autentica'})
    # os 4 grupos do prompt mestre: personagem, carta/fotografia real, documento histórico, reconstituição
    grupo = {'personagem': 'personagem', 'carta_ou_arte_real': 'carta, foto ou filme real', 'video_historico': 'carta, foto ou filme real',
             'fotografia_historica': 'carta, foto ou filme real', 'documento_historico': 'documento histórico', 'reconstituicao': 'reconstituição'}
    presentes = {grupo[c] for c in cats if c in grupo}
    faltam = [g for g in ('personagem', 'carta, foto ou filme real', 'documento histórico', 'reconstituição') if g not in presentes]
    retida = (modo == 'public_release' and 'carta, foto ou filme real' in faltam
              and any(s.get('visual_source_type') == 'arte_autentica' for s in shots))
    add('quatro_categorias_de_imagem', not faltam,
        f'categorias presentes: {cats}' + (f" · faltam: {', '.join(faltam)}" if faltam else '') + (' (arte real retida neste modo)' if retida else ''),
        grave=False)
    # rótulos e direitos
    sem_selo = [s['id'] for s in shots if s.get('visual_source_type') in SELOS_OBRIGATORIOS
                and s.get('selo') not in SELOS_OBRIGATORIOS[s['visual_source_type']]]
    add('selos_de_ilustracao_e_reconstituicao', not sem_selo, f'sem selo adequado: {sem_selo}')
    barrados = [s['id'] for s in shots if s['tipo'] != 'outro' and not perfil_mod.gate_direitos(s['rights_status'], modo)]
    add('filtro_de_direitos', not barrados, f'planos com direitos incompatíveis com {modo}: {barrados}')
    por_direito = {s['id'] for s in shots if s.get('rights_status') in ('private_research', 'quotation_excerpt')}
    marcados = {s['id'] for s in shots if s.get('_privado')}
    add('marca_de_previa_privada', por_direito == marcados and (modo == 'private_preview' or not marcados),
        f'material privado por direito: {sorted(por_direito)}; com marca PRÉVIA PRIVADA: {sorted(marcados)}')
    fontes = {f['id'] for f in man['fontes']}
    sem_fonte = [c['id'] for c in man['claims'] if c['status'] == 'documented' and not set(c.get('fontes', [])) <= fontes]
    add('claims_com_fonte', not sem_fonte, ', '.join(f"{c['id']}:{c['status']}" for c in man['claims']))
    campos = perfil_mod.CAMPOS_CENA
    faltando = [(s['id'], k) for s in shots for k in campos if k not in s]
    add('campos_v2_por_plano', not faltando, f'faltando: {faltando[:10]}')
    campos_a = [k for k in perfil_mod.CAMPOS_ATUACAO if k != 'reference_image']
    falt_a = [(s['id'], k) for s in pers for k in campos_a if k not in s]
    add('campos_de_atuacao', not falt_a, f'faltando: {falt_a[:10]}')
    texto_longo = [s['id'] for s in shots if len((s.get('tela') or '').split()) > perfil['storytelling']['on_screen_text_max_words']]
    add('texto_na_tela_curto', not texto_longo, f'acima de 8 palavras: {texto_longo}')
    from PIL import Image
    add('capa_1080x1920', Image.open(os.path.join(pasta, 'cover.png')).size == (W, H), 'cover.png')
    add('voz_fixa_registrada', bool(voz_cfg.get('voice_id')) and bool(voz_cfg.get('version')), f"{voz_cfg.get('voice_id')} · {voz_cfg.get('version')}")
    lk = perfil_mod.carregar_lock()
    add('voz_aprovada_pelo_proprietario', lk.get('voice', {}).get('approved') is True and lk['voice'].get('voice_id') == voz_cfg.get('voice_id'),
        f"{lk.get('voice', {}).get('status')} — {lk.get('voice', {}).get('aprovado_por', 'sem aprovação')} {lk.get('voice', {}).get('aprovado_em', '')}", grave=False)
    add('visual_aprovado_pelo_proprietario', lk.get('character', {}).get('approved_look') is True, str(lk.get('character', {}).get('aprovacao', 'pendente')), grave=False)
    br = float(pr.get('format', {}).get('bit_rate', 0)) / 1e6
    add('bitrate_master', br <= 12, f'{br:.1f} Mbps ({os.path.getsize(mp4) / 1048576:.0f} MiB); alvo ≤ 8', grave=True)
    if br > 8: add('bitrate_master_alvo', False, f'{br:.1f} Mbps acima de 8', grave=False)
    app = os.path.join(pasta, 'video_app.mp4')
    add('versao_app_ate_19MiB', os.path.exists(app) and os.path.getsize(app) < 19 * 1048576,
        f'{os.path.getsize(app) / 1048576:.1f} MiB' if os.path.exists(app) else 'ausente')
    r['duracao_s'] = round(dur, 2)
    r['publicavel'] = (modo == 'public_release' and r['status'] != 'fail')
    r['publicacao_aprovada'] = False
    return r


# ---------------------------------------------------------------------------------------------------- principal
def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('manifesto'); ap.add_argument('--modo', default='private_preview', choices=('private_preview', 'public_release'))
    ap.add_argument('--workers', type=int, default=4); ap.add_argument('--refazer', default=''); ap.add_argument('--so-qa', action='store_true')
    ap.add_argument('--saida', default=None)
    a = ap.parse_args(argv)
    man = json.load(open(a.manifesto, encoding='utf-8'))
    perfil = perfil_mod.carregar(); lock = perfil_mod.carregar_lock()
    if man.get('schema') == 'arquivo-oculto/roteiro-v3':
        print(validar_manifesto(man, perfil)[0], file=sys.stderr)
        return 2
    eid = man['episode_id']
    pasta = os.path.abspath(a.saida or os.path.join(AO, 'saida_v2', f'{eid}_{a.modo}'))
    os.makedirs(pasta, exist_ok=True)
    est = Estado(pasta, eid, a.modo)
    if a.so_qa and os.path.exists(est.p):
        est.d = json.load(open(est.p, encoding='utf-8'))          # o histórico da montagem continua; o QA novo é acrescentado
    passo = (lambda e, d='': print(f'[{e}] {d}', flush=True)) if a.so_qa else est.ir
    erros = perfil_mod.validar(perfil) + validar_manifesto(man, perfil)
    if erros:
        est.ir('blocked', '; '.join(erros)); return 2
    passo('planned', f"{man['titulo']} · formato {man['formato']} · {sum(len(l['shots']) for l in man['linhas'])} planos")
    decisoes = resolver_direitos(man, a.modo)
    barr = [d for d in decisoes if not d['liberado']]
    passo('sources_verified', f"{len(man['fontes'])} fontes, {len(man['claims'])} claims; {len(barr)} asset(s) substituído(s) pela variante honesta no modo {a.modo}")
    passo('generating_voice', f"voz {lock['voice']['voice_id']} ({lock['voice']['status']})")
    spans, fim_fala, dur, voz_cfg = gerar_voz(man, lock, pasta)
    shots = montar_timeline(man, spans, fim_fala, dur)
    if man.get('mascara_falada'):
        from arquivo_oculto.v2.voz import ler_wav
        amostras, hz = ler_wav(os.path.join(pasta, 'voice.wav'))
        passo_audio = hz // FPS
        qtd = max(s['f1'] for s in shots)
        audio = np.pad(amostras[:qtd * passo_audio], (0, max(0, qtd * passo_audio - len(amostras))))
        rms = np.sqrt(np.mean(audio.reshape(qtd, passo_audio) ** 2, axis=1))
        rms = np.convolve(rms, [0.2, 0.6, 0.2], mode='same')
        boca = np.clip((rms - 0.012) / max(0.045, float(np.percentile(rms, 92))), 0, 1)
        for s in shots:
            if s.get('mascara_falada'):
                s['_abertura_boca'] = boca[s['f0']:s['f1']].round(4).tolist()
                s['boca_pico'] = max(s['_abertura_boca'], default=0)
    legs = legendas(man, spans)
    fm_ = __import__('arquivo_oculto.v2.fundo_motor', fromlist=['srt'])
    fm_.srt(legs, os.path.join(pasta, 'subtitles.srt'))
    for s in shots:
        s.setdefault('reference_image', lock['character']['reference_image'] if s.get('personagem') else None)
    # arquivos de acervo (PDF, imagem, vídeo) entram no plano como caminho absoluto; o hash do plano passa a incluí-los
    _ass = {x['id']: x for x in man['assets']}
    for s in shots:
        arq = _ass.get(s.get('asset'), {}).get('arquivo')
        if not arq:
            continue
        caminho = os.path.join(RAIZ, arq)
        if s['tipo'] in ('pagina_documento', 'imagem_arquivo', 'video_arquivo'):
            s.setdefault('params', {}).setdefault('arquivo', caminho)
        if s.get('prova', {}).get('tipo') in ('pagina_documento', 'imagem_arquivo', 'video_arquivo'):
            s['prova'].setdefault('params', {}).setdefault('arquivo', caminho)
    if a.so_qa:
        return _so_qa(pasta, man, perfil, shots, legs, a.modo, voz_cfg, est)
    cache = os.path.join(AO, 'cache', 'planos_v2'); os.makedirs(cache, exist_ok=True)
    refazer = set(x for x in a.refazer.split(',') if x)
    assets = {x['id']: x for x in man['assets']}
    jobs = []
    for s in shots:
        leg_s = [x for x in legs if x[1] > s['f0'] / FPS and x[0] < s['f1'] / FPS]
        chave = hashlib.sha256(json.dumps({'s': {k: v for k, v in s.items() if not k.startswith('ini') and k != 'fim'}, 'legs': leg_s,
                                           'num': man['num'], 'codigo': hash_codigo(s['tipo'], (s.get('prova') or {}).get('tipo')),
                                           'outro': man.get('outro') if s['tipo'] == 'outro' else None,
                                           'listas': man.get('listas') if 'lista' in json.dumps(s, default=str) else None},
                                          sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:20]
        s['_hash'] = chave
        jobs.append({'shot': s, 'saida': os.path.join(cache, f"{eid}_{s['id']}_{chave}.mp4"), 'legendas': legs, 'num': man['num'],
                     'assets': assets, 'listas': man.get('listas', {}), 'outro': man.get('outro'), 'primeiro': shots[0]['id'],
                     'forcar': s['id'] in refazer})
    est.ir('generating_visuals', f'{len(jobs)} planos, {a.workers} processos, cache {cache}')
    t0 = time.time(); resultados = []
    with cf.ProcessPoolExecutor(max_workers=a.workers, initializer=_init_worker) as ex:
        futs = {ex.submit(render_plano, j): j['shot']['id'] for j in jobs}
        for fu in cf.as_completed(futs):
            r = fu.result(); resultados.append(r)
            print(f"  plano {r['id']:6s} {r['cache']:4s} {r['quadros']:4d} quadros {r.get('ms_por_quadro', 0):5d} ms/q mov {r['mov']:6.2f} lum {r['lum']:5.1f}", flush=True)
    print(f'  render: {time.time() - t0:.0f} s', flush=True)
    est.ir('assembling', 'concat dos segmentos, trilha, efeitos, ducking e loudnorm')
    lista = os.path.join(pasta, '_segmentos.txt')
    with open(lista, 'w', encoding='utf-8') as f:
        for j in jobs:
            f.write(f"file '{j['saida'].replace(os.sep, '/')}'\n")
    mudo = os.path.join(pasta, '_mudo.mp4')
    ff(['-f', 'concat', '-safe', '0', '-i', lista, '-c', 'copy', mudo])
    mix, som_cfg = mixar(pasta, shots, spans, fim_fala, dur)
    final = os.path.join(pasta, 'video.mp4')
    ff(['-i', mudo, '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
        '-shortest', '-movflags', '+faststart', final])
    for x in (lista, mudo, mix):
        os.remove(x)
    versao_app(pasta, final, dur)
    capa(pasta, man)
    # folha de contato (meio de cada plano)
    import cv2
    res = {x['id']: x for x in resultados}
    thumbs = [cv2.imread(res[s['id']]['seg'] + '.png') for s in shots]
    while len(thumbs) % 8: thumbs.append(np.zeros_like(thumbs[0]))
    cv2.imwrite(os.path.join(pasta, 'frames.jpg'), np.vstack([np.hstack(thumbs[i:i + 8]) for i in range(0, len(thumbs), 8)]))
    # timeline e fontes
    pub = lambda s: {k: v for k, v in s.items() if not k.startswith('_')}
    tl = {'episode_id': eid, 'titulo': man['titulo'], 'formato': man['formato'], 'modo': a.modo, 'fps': FPS, 'resolucao': f'{W}x{H}',
          'duracao_s': round(dur, 3), 'fim_fala_s': round(fim_fala, 3), 'modo_visual': lock['visual_mode']['atual'],
          'aviso_modo': lock['visual_mode']['descricao'], 'voz': voz_cfg, 'som': som_cfg, 'falas': spans,
          'planos': [{**pub(s), 'gate_liberado': s.get('_gate_ok', True), 'asset_efetivo': s.get('_asset_efetivo'),
                      'privado': s.get('_privado', False), 'segmento_hash': s['_hash'], 'metricas': {k: res[s['id']][k] for k in ('mov', 'lum', 'cache')}}
                     for s in shots]}
    json.dump(tl, open(os.path.join(pasta, 'timeline.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    locais = {}
    for x in man['assets']:
        if x.get('arquivo') and os.path.exists(os.path.join(RAIZ, x['arquivo'])):
            locais[x['id']] = sha_arquivo(os.path.join(RAIZ, x['arquivo']))
    for f_ in man['fontes']:
        if f_.get('snapshot') and os.path.exists(os.path.join(RAIZ, f_['snapshot'])):
            locais[f_['id']] = sha_arquivo(os.path.join(RAIZ, f_['snapshot']))
    json.dump({'episode_id': eid, 'modo': a.modo, 'fontes': man['fontes'], 'claims': man['claims'], 'assets': man['assets'],
               'decisoes_de_direitos': decisoes, 'sha256_locais': locais, 'legenda_post': man.get('legenda_post'),
               'publicacao_aprovada': False}, open(os.path.join(pasta, 'sources.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    est.ir('qa', 'ffprobe, quadros, loudness, legendas, atuação, direitos, rótulos e campos V2')
    return _concluir(pasta, man, perfil, shots, legs, resultados, a.modo, voz_cfg, est)


def _so_qa(pasta, man, perfil, shots, legs, modo, voz_cfg, est):
    """--so-qa: refaz só o QA sobre o vídeo já montado nesta pasta (por exemplo, depois de uma aprovação gravada no lock).
    Movimento e luminância de cada plano vêm da timeline da própria montagem. Recusa se o manifesto mudou desde então."""
    tl_p = os.path.join(pasta, 'timeline.json')
    if not (os.path.exists(tl_p) and os.path.exists(os.path.join(pasta, 'video.mp4'))):
        print('--so-qa: esta pasta não tem vídeo montado; renderize primeiro', flush=True)
        return 3
    tl = json.load(open(tl_p, encoding='utf-8'))
    if [(p['id'], p['f0'], p['f1']) for p in tl['planos']] != [(s['id'], s['f0'], s['f1']) for s in shots]:
        print('--so-qa recusado: planos ou tempos mudaram desde a montagem; renderize de novo', flush=True)
        return 3
    resultados = [{'id': p['id'], **p['metricas']} for p in tl['planos']]
    est.ir('qa', 'só o QA, sobre o vídeo já montado (--so-qa); vídeo, versão do app e capa intocados')
    return _concluir(pasta, man, perfil, shots, legs, resultados, modo, voz_cfg, est)


def _concluir(pasta, man, perfil, shots, legs, resultados, modo, voz_cfg, est):
    final = os.path.join(pasta, 'video.mp4')
    rel = qa(pasta, man, perfil, shots, legs, resultados, modo, voz_cfg)
    rel['arquivos'] = {n: {'bytes': os.path.getsize(os.path.join(pasta, n)), 'sha256': sha_arquivo(os.path.join(pasta, n))}
                       for n in ('video.mp4', 'video_app.mp4', 'voice.wav', 'subtitles.srt', 'cover.png', 'timeline.json', 'sources.json')}
    json.dump(rel, open(os.path.join(pasta, 'qa.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    falhas = [c for c in rel['checks'] if not c['ok']]
    for c in falhas:
        print(f"  {'FALHA' if c['grave'] else 'AVISO'} {c['check']}: {c['info']}")
    if rel['status'] in ('pass', 'pass_with_warnings'):
        est.ir('completed', f"QA {rel['status']} · {rel['duracao_s']} s · {final}")
        return 0
    est.ir('blocked', 'QA reprovou: ' + '; '.join(c['check'] for c in falhas if c['grave']))
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
