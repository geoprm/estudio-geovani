"""Motor leve de reels 9:16 do Arquivo Oculto (linha do Claude: O Arquivo Responde e Arquivo Morto).

Fotos com movimento, televisor de tubo, pares de imagens, carimbos, cartelas, o Arquivista em retrato animado, vozes
Kokoro e legendas no padrão visual da fábrica V2. Só o ffmpeg toca nos quadros, um bloco por vez: cabe na memória em que
a fábrica completa não roda.

Uso (na raiz do estúdio):  python -m arquivo_oculto.v2.reel_leve <roteiro.json> <pasta de saída>

Roteiro: {"id", "num", "serie", "selo_fixo": null|"FICÇÃO", "blocos": [ {
    "voz": "arquivista"|"fita"|null, "fala": str, "pausa": s, "dur": s (sem voz),
    "visual": {"tipo": "imagem"|"par"|"crt"|"retrato"|"cartao"|"placar"|"preto", ...},
    "selo": str, "credito": str, "tela": str, "carimbo": "DOCUMENTADO"|"SEM PROVA"|"INTERPRETAÇÃO"|"FALSO",
    "sfx": ["chiado", "batida", "silencio"] } ]}
Caminhos de arquivo são relativos à pasta do roteiro ou absolutos.
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import fundo_motor as fm
from . import perfil, voz

W, H, FPS, SR = 1080, 1920, 30, 48000
LY = 1380
# medidas de layout parametrizadas (o motor horizontal reel_longo.py troca estes valores)
FG_BOX, FG_DY = (960, 1180), -80          # imagem 'contain'
CRT_TELA, CRT_POS = (900, 745), (90, 495)  # tela do televisor de tubo
ATOR_X = None                               # None = clipe ocupa o quadro; número = posição x no quadro horizontal
ENC_FINAL = ['-crf', '22', '-maxrate', '3800k', '-bufsize', '7600k']
CARIMBO_COR = {'DOCUMENTADO': (52, 150, 96), 'SEM PROVA': (205, 150, 40), 'INTERPRETAÇÃO': (196, 120, 50),
               'FALSO': (190, 40, 36)}
SELO_COR = {'ALEGAÇÃO': (196, 140, 50), 'FICÇÃO': (150, 60, 160), 'DOCUMENTO': (52, 150, 96),
            'RECONSTITUIÇÃO': (150, 120, 70), 'ARQUIVO': (52, 150, 96)}
VENC = ['-c:v', 'libx264', '-profile:v', 'high', '-level', '4.0', '-preset', 'medium', '-crf', '19',
        '-pix_fmt', 'yuv420p', '-r', str(FPS), '-video_track_timescale', '15360', '-an']

# voz da fita: narradora que acredita em tudo, ouvida por um alto-falante de televisor velho
voz.PRESETS.setdefault('voz-da-fita', {
    'vozes': {'pf_dora': 1.0}, 'velocidade': 0.9, 'tom': 0.96,
    'cadeia': 'highpass=f=300,lowpass=f=3300,acrusher=bits=10:mode=log:aa=1:mix=0.12,aecho=0.8:0.35:22|47:0.18|0.09',
    'descricao': 'pf_dora, 0,90, tom 0,96, alto-falante de TV velho'})


def _ff(args, cwd):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', *args], cwd=cwd, check=True)


def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------ camadas desenhadas (PIL)
def _gradiente(lay):
    ys = np.arange(H, dtype=np.float32)
    a = np.clip((380 - ys) / 380, 0, 1) * 0.55 + np.clip((ys - 1180) / 520, 0, 1) * 0.80
    g = np.zeros((H, W, 4), np.uint8)
    g[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)[:, None]
    lay.alpha_composite(Image.fromarray(g, 'RGBA'))


def camada_bloco(caminho, rot, b):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    _gradiente(lay)
    d = ImageDraw.Draw(lay)
    f = fm.fonte('cinzel', 30)
    t = rot['serie']
    d.text((W - 100 - f.getlength(t), 196), t, font=f, fill=fm.OURO + (210,))
    selos = [s for s in (rot.get('selo_fixo'), b.get('selo')) if s]
    y = 190
    for s in selos:
        f = fm.fonte('oswald', 32)
        cor = next((c for k, c in SELO_COR.items() if s.startswith(k)), (150, 120, 70))
        w = f.getlength(s)
        d.rounded_rectangle((100, y, 100 + w + 36, y + 54), 8, fill=(10, 8, 6, 210), outline=cor + (255,), width=3)
        d.text((118, y + 5), s, font=f, fill=fm.CREME + (255,))
        y += 66
    if b.get('tela'):
        tam = 104
        while True:
            f = fm.fonte('anton', tam)
            ls = fm.quebrar(b['tela'], f, W - 220)
            if len(ls) <= 2 or tam < 64:
                break
            tam -= 6
        for i, linha in enumerate(ls):
            fm.texto_centro(d, W / 2, 330 + i * tam * 1.1, linha, f, fm.OURO_CLARO + (255,), stroke=3, stroke_cor=(20, 12, 4))
    if b.get('credito'):
        f = fm.fonte('oswald4', 28)
        for i, linha in enumerate(fm.quebrar(b['credito'], f, W - 200)[:2]):
            d.text((100, 1290 + i * 34), linha, font=f, fill=fm.CREME + (215,))
    lay.save(caminho)


def camada_legenda(caminho, txt):
    lay = Image.new('RGBA', (W, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tam = 64
    while True:
        f = fm.fonte('oswald', tam)
        ls = fm.quebrar(txt, f, W - 220)
        if len(ls) <= 2 or tam <= 44:
            break
        tam -= 4
    alt = int(tam * 1.31)
    for i, linha in enumerate(ls):
        wl = f.getlength(linha)
        d.rounded_rectangle((W / 2 - wl / 2 - 26, 14 + i * alt, W / 2 + wl / 2 + 26, 14 + i * alt + tam + 22), 14, fill=(6, 5, 4, 120))
    for i, linha in enumerate(ls):
        fm.texto_centro(d, W / 2, 20 + i * alt, linha, f, fm.CREME + (255,), sombra=False, stroke=5, stroke_cor=(0, 0, 0))
    lay.save(caminho)


def camada_carimbo(caminho, txt):
    cor = CARIMBO_COR.get(txt, (190, 40, 36))
    f = fm.fonte('anton', 120)
    tw = int(f.getlength(txt))
    img = Image.new('RGBA', (tw + 140, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((14, 14, img.width - 14, img.height - 14), 18, outline=cor + (255,), width=12)
    d.rounded_rectangle((34, 34, img.width - 34, img.height - 34), 10, outline=cor + (200,), width=4)
    d.text((70, 52), txt, font=f, fill=cor + (255,))
    rng = np.random.default_rng(len(txt))
    a = np.asarray(img).copy()
    furos = rng.random(a.shape[:2]) < 0.18          # tinta falhada de carimbo
    a[..., 3] = np.where(furos, (a[..., 3] * 0.35).astype(np.uint8), a[..., 3])
    img = Image.fromarray(a, 'RGBA').rotate(-8, expand=True, resample=Image.BICUBIC)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    esc = min(1.0, 900 / img.width)
    img = img.resize((int(img.width * esc), int(img.height * esc)), Image.LANCZOS)
    lay.alpha_composite(img, ((W - img.width) // 2, 1010 - img.height // 2))
    lay.save(caminho)


def cartao(caminho, linhas, sub=None, papel=False):
    """Cartela de texto: frase grande em tipografia da casa sobre papel escuro ou fundo preto."""
    base = Image.new('RGB', (W, H), (14, 11, 8))
    if papel:
        rng = np.random.default_rng(7)
        ruido = (rng.normal(0, 9, (H, W, 1)) + np.array([[[42, 34, 24]]])).clip(0, 255).astype(np.uint8)
        base = Image.fromarray(np.repeat(ruido, 1, axis=2) if ruido.shape[2] == 3 else np.concatenate([ruido] * 3, 2))
        base = base.filter(ImageFilter.GaussianBlur(1.2))
    d = ImageDraw.Draw(base)
    f = fm.fonte('anton', 96)
    y = 760 - len(linhas) * 60
    for linha in linhas:
        for l2 in fm.quebrar(linha, f, W - 200):
            fm.texto_centro(d, W / 2, y, l2, f, fm.OURO_CLARO, stroke=3, stroke_cor=(20, 12, 4))
            y += 112
    if sub:
        f2 = fm.fonte('oswald4', 40)
        for l2 in fm.quebrar(sub, f2, W - 220):
            fm.texto_centro(d, W / 2, y + 30, l2, f2, fm.CREME)
            y += 52
    base.save(caminho)


def placar(caminho, contagem, titulo):
    base = Image.new('RGB', (W, H), (12, 10, 8))
    d = ImageDraw.Draw(base)
    fm.texto_centro(d, W / 2, 520, titulo, fm.fonte('anton', 84), fm.OURO_CLARO, stroke=3, stroke_cor=(20, 12, 4))
    y = 700
    for nome, n in contagem:
        cor = CARIMBO_COR.get(nome, (150, 120, 70))
        d.rounded_rectangle((170, y, W - 170, y + 120), 14, fill=(22, 18, 14), outline=cor, width=5)
        d.text((210, y + 24), nome, font=fm.fonte('anton', 64), fill=cor)
        fn = fm.fonte('anton', 84)
        d.text((W - 210 - fn.getlength(str(n)), y + 10), str(n), font=fn, fill=fm.CREME)
        y += 150
    base.save(caminho)


def televisor(caminho):
    """Moldura de televisor de tubo com a tela vazada (alfa 0)."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((40, 430, W - 40, 1330), 60, fill=(28, 22, 18, 255), outline=(70, 56, 40, 255), width=6)
    d.rounded_rectangle((70, 470, W - 70, 1290), 50, fill=(12, 10, 9, 255))
    d.rounded_rectangle((90, 495, W - 90, 1240), 70, fill=(0, 0, 0, 0))
    for i, x in enumerate((W - 250, W - 170)):
        d.ellipse((x, 1252, x + 40, 1282), fill=(60, 48, 34, 255))
    lay.save(caminho)


def linhas_tv(caminho):
    a = np.zeros((H, W, 4), np.uint8)
    a[::4, :, 3] = 70
    Image.fromarray(a, 'RGBA').save(caminho)


# ------------------------------------------------------------------ vídeo de cada bloco (ffmpeg)
def _imagem_filtro(idx, modo, mov, dur, rotulo):
    n = max(2, int(round(dur * FPS)))
    z = {'in': f"1.0+0.10*on/{n}", 'out': f"1.10-0.10*on/{n}", 'pan': '1.06'}[mov]
    x = "iw/2-(iw/zoom/2)" if mov != 'pan' else f"(iw-iw/zoom)*on/{n}"
    if modo == 'cover':
        cw, ch = int(W * 1.1) // 2 * 2, int(H * 1.1) // 2 * 2
        return (f"[{idx}:v]scale={cw}:{ch}:force_original_aspect_ratio=increase,crop={cw}:{ch},setsar=1,"
                f"zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}[{rotulo}]")
    return (f"[{idx}:v]split[a{idx}][b{idx}];"
            f"[a{idx}]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=28:3,eq=brightness=-0.28:saturation=0.6[bg{idx}];"
            f"[b{idx}]scale={FG_BOX[0]}:{FG_BOX[1]}:force_original_aspect_ratio=decrease[fg{idx}];"
            f"[bg{idx}][fg{idx}]overlay=(W-w)/2:(H-h)/2{FG_DY:+d},setsar=1,"
            f"zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}[{rotulo}]")


# ------------------------------------------------------------------ Arquivista em atuação (biblioteca 2,5D)
BIB = Path(__file__).resolve().parents[1] / 'saida_v2' / 'ator_clipes'
SEQ_ATOR = {
    'abertura': ['aparicao', 'silencio', 'olhar_camera', 'debrucar', 'silencio', 'olhar_camera'],
    'meio': ['olhar_camera', 'silencio', 'virar_cabeca', 'debrucar', 'silencio', 'olhar_camera'],
    'final': ['olhar_camera', 'silencio', 'debrucar', 'silencio', 'olhar_camera'],
}


def _biblioteca():
    reg = BIB / 'biblioteca.json'
    if not reg.exists():
        return None
    planos = json.loads(reg.read_text(encoding='utf-8')).get('planos', {})
    precisa = {p for s in SEQ_ATOR.values() for p in s} | {'encerramento'}
    return BIB if precisa <= set(planos) and all((BIB / f'{p}.mp4').exists() for p in precisa) else None


def _sequencia_ator(papel, dur, lim=4.0):
    """Cortes de até `lim` s entre planos da biblioteca: (plano, duração, início dentro do clipe de 4 s)."""
    n = max(1, math.ceil(dur / lim - 1e-6))
    d = dur / n
    seq = SEQ_ATOR.get(papel, SEQ_ATOR['meio'])
    planos = (seq[:n - 1] + ['encerramento']) if papel == 'final' else (seq * 2)[:n]
    out = []
    for p in planos:
        ini = 0.0 if p == 'aparicao' else (lim - d if p == 'encerramento' else (lim - d) / 2)
        out.append((p, d, max(0.0, ini)))
    return out


def render_bloco(pasta, i, rot, b, dur, legendas, base_dir):
    v = b['visual']
    tipo = v['tipo']
    entradas, filtros = [], []
    lp = ['-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.4f}', '-i']

    def arq(p):
        q = Path(p)
        return str(q if q.is_absolute() else (base_dir / q).resolve())

    if tipo == 'retrato' and not v.get('estatico') and _biblioteca():
        segs = _sequencia_ator(v.get('papel', b.get('_papel', 'meio')), dur)
        for plano, d, ini in segs:
            entradas += ['-ss', f'{ini:.3f}', '-t', f'{d + 0.1:.4f}', '-i', str(BIB / f'{plano}.mp4')]
        partes = ''.join(f'[{j}:v]setsar=1,fps={FPS},trim=duration={d:.4f},setpts=PTS-STARTPTS[s{j}];'
                         for j, (_, d, _) in enumerate(segs))
        filtros.append(partes + ''.join(f'[s{j}]' for j in range(len(segs))) + f'concat=n={len(segs)}:v=1:a=0' + ('[v0]' if ATOR_X is None else
                       f"[cat];[cat]split[ca][cb];[ca]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                       f"boxblur=30:3,eq=brightness=-0.32[cbg];[cb]scale=-2:{H}[cfg];[cbg][cfg]overlay={ATOR_X}:0,setsar=1[v0]"))
        b['_atuacao'] = [p for p, _, _ in segs]
    elif tipo in ('imagem', 'retrato'):
        src = arq(v['arquivo']) if tipo == 'imagem' else str(Path(perfil.RAIZ) / perfil.carregar_lock()['character']['reference_image'])
        entradas += lp + [src]
        filtros.append(_imagem_filtro(0, v.get('modo', 'cover' if tipo == 'retrato' else 'contain'), v.get('mov', 'in'), dur, 'v0'))
    elif tipo == 'par':
        corte = v.get('corte', 0.45)
        entradas += lp + [arq(v['a'])]
        pa = pasta / f'par{i}.png'
        _par_png(pa, arq(v['a']), arq(v['b']), v.get('rot_a', ''), v.get('rot_b', ''))
        entradas += lp + [str(pa)]
        filtros.append(_imagem_filtro(0, 'contain', 'in', dur, 'pa'))
        filtros.append(f"[1:v]scale={W}:{H},setsar=1,zoompan=z='1.0+0.04*on/{int(dur * FPS)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}[pb]")
        filtros.append(f"[pa][pb]overlay=0:0:enable='gte(t,{dur * corte:.3f})'[v0]")
    elif tipo == 'crt':
        tv, lt = pasta / 'tv.png', pasta / 'linhas.png'
        if not tv.exists():
            televisor(tv), linhas_tv(lt)
        if v.get('video'):
            entradas += ['-ss', str(v.get('inicio', 0)), '-t', f'{dur:.4f}', '-i', arq(v['video'])]
        else:
            entradas += lp + [arq(v['arquivo'])]
        entradas += lp + [str(tv)] + lp + [str(lt)]
        filtros.append(f"color=c=0x0b0806:s={W}x{H}:r={FPS}:d={dur:.4f}[fundo]")
        filtros.append(f"[0:v]scale={CRT_TELA[0]}:{CRT_TELA[1]}:force_original_aspect_ratio=increase,crop={CRT_TELA[0]}:{CRT_TELA[1]},setsar=1,fps={FPS},"
                       f"eq=saturation=0.75:brightness='0.02*sin(2*PI*t*7)':eval=frame,colorchannelmixer=rr=0.9:gg=1.05:bb=0.85,"
                       f"noise=alls=22:allf=t,boxblur=1:1[tela]")
        filtros.append(f"[fundo][tela]overlay={CRT_POS[0]}:{CRT_POS[1]}[comtela]")
        filtros.append("[comtela][1:v]overlay=0:0[ctv]")
        filtros.append("[ctv][2:v]overlay=0:0,vignette=angle=PI/4.2[v0]")
    elif tipo in ('cartao', 'placar', 'preto'):
        c = pasta / f'cartao{i}.png'
        if tipo == 'cartao':
            cartao(c, v['linhas'], v.get('sub'), v.get('papel', False))
        elif tipo == 'placar':
            placar(c, v['contagem'], v.get('titulo', 'PLACAR'))
        else:
            Image.new('RGB', (W, H), (0, 0, 0)).save(c)
        entradas += lp + [str(c)]
        filtros.append(f"[0:v]scale={W}:{H},setsar=1,zoompan=z='1.0+0.03*on/{int(dur * FPS)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}[v0]")
    else:
        raise ValueError(f'visual desconhecido: {tipo}')

    n_base = len([e for e in entradas if e == '-i'])
    # camada do bloco
    cb = pasta / f'camada{i}.png'
    camada_bloco(cb, rot, b)
    entradas += lp + [str(cb)]
    k = n_base
    tom = "eq=saturation=0.86:contrast=1.04,noise=alls=5:allf=t" if tipo != 'crt' else "null"
    if tipo == 'retrato':
        tom = "eq=brightness='-0.05+0.022*sin(2*PI*t*1.7)':saturation=0.84:eval=frame,vignette=angle=PI/4.6"
    filtros.append(f"[v0]{tom}[g]")
    filtros.append(f"[g][{k}:v]overlay=0:0[c0]")
    atual = 'c0'
    k += 1
    if b.get('carimbo'):
        cc = pasta / f'carimbo{i}.png'
        camada_carimbo(cc, b['carimbo'])
        tc = b.get('carimbo_em', max(0.3, dur - 1.7))
        entradas += lp + [str(cc)]
        filtros.append(f"[{k}:v]format=rgba,fade=t=in:st={tc:.3f}:d=0.07:alpha=1[ci]")
        filtros.append(f"[{atual}][ci]overlay=0:0[c1]")
        atual, k = 'c1', k + 1
    for j, (a0, a1, txt) in enumerate(legendas):
        lg = pasta / f'leg{i}_{j}.png'
        camada_legenda(lg, txt)
        entradas += lp + [str(lg)]
        filtros.append(f"[{atual}][{k}:v]overlay=0:{LY}:enable='between(t,{a0:.3f},{a1:.3f})'[l{j}]")
        atual, k = f'l{j}', k + 1
    if v.get('fade_preto'):
        filtros.append(f"[{atual}]fade=t=out:st={max(0, dur - 0.5):.3f}:d=0.5[fp]")
        atual = 'fp'
    filtros.append(f"[{atual}]format=yuv420p[out]")
    _ff([*entradas, '-filter_complex', ';'.join(filtros), '-map', '[out]', '-t', f'{dur:.4f}', *VENC, f'bloco{i:02d}.mp4'], pasta)


def _par_png(caminho, a, b, rot_a, rot_b):
    base = Image.new('RGB', (W, H), (12, 10, 8))
    d = ImageDraw.Draw(base)
    for n, (src, rotulo) in enumerate(((a, rot_a), (b, rot_b))):
        im = Image.open(src).convert('RGB')
        im.thumbnail((500, 760))
        x0 = 30 + n * 530 + (500 - im.width) // 2
        y0 = 470 + (760 - im.height) // 2
        base.paste(im, (x0, y0))
        f = fm.fonte('oswald', 30)
        for k, linha in enumerate(fm.quebrar(rotulo, f, 480)[:2]):
            fm.texto_centro(d, 30 + n * 530 + 250, 1250 + k * 38, linha, f, fm.OURO_CLARO, stroke=3, stroke_cor=(0, 0, 0))
    d.line((W / 2, 520, W / 2, 1200), fill=fm.OURO, width=2)
    base.save(caminho)


# ------------------------------------------------------------------ áudio
def _wav_float(p):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy()


def fala_processada(pasta, preset, texto, nome):
    narrador = voz.Voz(preset)
    cru = narrador.sintetizar(texto)
    voz.escrever_wav(str(pasta / f'{nome}_cru.wav'), cru / max(0.001, float(np.abs(cru).max())) * 0.9)
    _ff(['-i', f'{nome}_cru.wav', '-filter_complex', narrador.filtro_ffmpeg('0:a', 'v'), '-map', '[v]', '-ar', str(SR),
         '-ac', '1', f'{nome}.wav'], pasta)
    return _wav_float(pasta / f'{nome}.wav')


def sfx(nome, dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if nome == 'carimbo':
        env = np.exp(-t * 18)
        return (np.sin(2 * np.pi * 62 * t) * env * 0.9 + rng.normal(0, 1, n) * np.exp(-t * 60) * 0.35).astype(np.float32)
    if nome == 'batida':
        env = np.exp(-t * 3.2)
        return (np.sin(2 * np.pi * 38 * t + 3 * np.sin(2 * np.pi * 2 * t)) * env * 1.0).astype(np.float32)
    if nome == 'chiado':
        x = rng.normal(0, 1, n).astype(np.float32)
        x = np.convolve(x, np.ones(6) / 6, mode='same')
        return (x * 0.05).astype(np.float32)
    raise ValueError(nome)


def cama(n, rng):
    t = np.arange(n) / SR
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)
    x = (0.05 * np.sin(2 * np.pi * 55 * t) + 0.035 * np.sin(2 * np.pi * 82.41 * t) * lfo
         + 0.018 * np.sin(2 * np.pi * 110.3 * t) * (1 - lfo) + 0.012 * np.sin(2 * np.pi * 164.8 * t) * lfo)
    ruido = np.convolve(rng.normal(0, 1, n), np.ones(40) / 40, mode='same') * 0.02
    return (x + ruido).astype(np.float32)


# ------------------------------------------------------------------ legendas
def dividir(fala):
    frases = [s.strip() for s in re.split(r'(?<=[.!?…])\s+', fala) if s.strip()]
    pedacos = []
    for fr in frases:
        palavras, atual = fr.split(), ''
        for p in palavras:
            if len(atual) + len(p) + 1 > 46 and atual:
                pedacos.append(atual)
                atual = p
            else:
                atual = (atual + ' ' + p).strip()
        if atual:
            pedacos.append(atual)
    return pedacos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('roteiro', type=Path)
    ap.add_argument('saida', type=Path)
    a = ap.parse_args()
    rot = json.loads(a.roteiro.read_text(encoding='utf-8'))
    base_dir = a.roteiro.resolve().parent
    saida = a.saida.resolve()
    saida.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(11)
    presets = {'arquivista': perfil.carregar_lock()['voice']['voice_id'], 'fita': 'voz-da-fita'}
    with TemporaryDirectory(dir=saida) as temp:
        pasta = Path(temp)
        trilha_voz, eventos, srt, silencios = [], [], [], []
        t0 = 0.0
        blocos_ok = []
        retratos = [j for j, bb in enumerate(rot['blocos']) if bb['visual']['tipo'] == 'retrato']
        for j in retratos:   # papel do Arquivista em cada aparição: abertura, meio ou final (saída na sombra)
            bb = rot['blocos'][j]
            bb['_papel'] = 'final' if bb['visual'].get('fade_preto') else ('abertura' if j == retratos[0] else 'meio')
        for i, b in enumerate(rot['blocos']):
            lead = 0.22
            if b.get('voz'):
                fala = fala_processada(pasta, presets[b['voz']], b['fala'], f'f{i:02d}')
                vdur = len(fala) / SR
                dur = lead + vdur + b.get('pausa', 0.35)
            else:
                fala, vdur, dur = None, 0.0, float(b['dur'])
            dur = math.ceil(dur * FPS) / FPS
            legs = []
            if fala is not None:
                pedacos = dividir(b['fala'])
                tot = sum(len(p) for p in pedacos)
                cur = lead
                for p in pedacos:
                    dd = vdur * len(p) / tot
                    legs.append((cur, cur + dd - 0.02, p))   # corte seco: a próxima legenda entra depois
                    srt.append((t0 + cur, t0 + cur + dd, p))
                    cur += dd
                trilha_voz.append((t0 + lead, fala))
            if b.get('carimbo'):
                b.setdefault('carimbo_em', max(0.3, dur - 1.7))
                eventos.append((t0 + b['carimbo_em'], 'carimbo'))
            for s in b.get('sfx', []):
                if s == 'chiado':
                    eventos.append((t0, 'chiado', dur))
                elif s == 'batida':
                    eventos.append((t0 + b.get('batida_em', 0.05), 'batida'))
                elif s == 'silencio':
                    silencios.append((t0, t0 + dur))
            render_bloco(pasta, i, rot, b, dur, legs, base_dir)
            blocos_ok.append(f'bloco{i:02d}.mp4')
            print(f'[bloco {i:02d}] {b["visual"]["tipo"]} {dur:.2f}s', flush=True)
            t0 += dur
        total = t0
        n = int(math.ceil(total * SR)) + SR
        mix_voz = np.zeros(n, np.float32)
        for ini, f in trilha_voz:
            s = int(ini * SR)
            mix_voz[s:s + len(f)] += f[: n - s]
        efeitos = np.zeros(n, np.float32)
        for ev in eventos:
            s = int(ev[0] * SR)
            x = sfx(ev[1], ev[2] if len(ev) > 2 else (0.6 if ev[1] == 'carimbo' else 2.4), rng)
            efeitos[s:s + len(x)] += x[: n - s]
        fundo = cama(n, rng)
        cs = np.cumsum(np.abs(mix_voz), dtype=np.float64); env = np.empty_like(mix_voz); w = 4800
        env[:] = np.interp(np.arange(n), np.arange(n), np.concatenate([np.zeros(w), (cs[w:] - cs[:-w]) / w])[:n])
        fundo *= np.where(env > 0.01, 0.55, 1.0).astype(np.float32)          # ducking simples sob a voz
        for a0, a1 in silencios:
            fundo[int(a0 * SR):int(a1 * SR)] *= 0.05
        mix = mix_voz * 1.0 + efeitos * 0.8 + fundo * 0.6
        mix = mix[: int(total * SR)]
        voz.escrever_wav(str(pasta / 'mix.wav'), mix / max(0.001, float(np.abs(mix).max())) * 0.95, sr=SR)
        (pasta / 'lista.txt').write_text(''.join(f"file '{x}'\n" for x in blocos_ok), encoding='utf-8')
        _ff(['-f', 'concat', '-safe', '0', '-i', 'lista.txt', '-c', 'copy', 'video_mudo.mp4'], pasta)
        med = subprocess.run(['ffmpeg', '-v', 'info', '-i', 'mix.wav', '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json',
                              '-f', 'null', '-'], cwd=pasta, capture_output=True, text=True).stderr
        m = json.loads(med[med.rindex('{'):med.rindex('}') + 1])
        ln = (f"loudnorm=I=-15:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
        _ff(['-i', 'video_mudo.mp4', '-i', 'mix.wav', '-map', '0:v', '-map', '1:a',
             '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.0', '-preset', 'medium', *ENC_FINAL, '-vf', 'scale=in_range=auto:out_range=tv,format=yuv420p', '-color_range', 'tv',
             '-af', ln, '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2',
             '-movflags', '+faststart', '-shortest', 'video_app.mp4'], pasta)
        _ff(['-v', 'error', '-xerror', '-i', 'video_app.mp4', '-f', 'null', '-'], pasta)
        fmt = lambda s: f'{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round(s * 1000)) % 1000:03d}'
        (pasta / 'subtitles.srt').write_text(''.join(f'{k}\n{fmt(x0)} --> {fmt(x1)}\n{tx}\n\n' for k, (x0, x1, tx) in enumerate(srt, 1)), encoding='utf-8')
        _ff(['-ss', '1.6', '-i', 'video_app.mp4', '-frames:v', '1', 'cover.png'], pasta)
        reg = {'id': rot['id'], 'motor': 'reel_leve', 'duracao_s': round(total, 3), 'blocos': len(blocos_ok),
               'vozes': presets, 'sha256': _sha(pasta / 'video_app.mp4'), 'roteiro': str(a.roteiro.resolve()),
               'arquivista': {'modo': 'performance_2_5d', 'planos': {str(j): bb['_atuacao'] for j, bb in
                                                                     enumerate(rot['blocos']) if bb.get('_atuacao')}}}
        (pasta / 'registro.json').write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding='utf-8')
        for nome in ('video_app.mp4', 'subtitles.srt', 'cover.png', 'registro.json'):
            (pasta / nome).replace(saida / nome)
    print(json.dumps(reg, ensure_ascii=False))


if __name__ == '__main__':
    main()
