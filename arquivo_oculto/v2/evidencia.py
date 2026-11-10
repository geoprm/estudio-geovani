"""Planos de evidência do Arquivo Oculto V2 (documento, carta, dado, grade, leituras), todos com movimento.

Regra: material autêntico só entra com registro de fonte e direitos (manifesto `assets`). Quando o filtro de direitos
do modo de render barra o asset, o plano usa a variante honesta (placeholder ou paráfrase com fonte) — nunca um
desenho fingindo ser o original. Ilustrações feitas aqui são ILUSTRAÇÃO e nunca imitam carta, foto ou documento real.

Cada função recebe (ctx, p) e devolve {'dyn': f(tl, dur) -> RGB float32 (PH, PW), 'zoom': (z0, z1), 'pan': ((x0,y0),(x1,y1))}.
"""
import math
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

from . import fundo_motor as fm

W, H = 1080, 1920
PW, PH = int(W * 1.08), int(H * 1.08)
OURO, OURO_CLARO, CREME, VERMELHO = fm.OURO, fm.OURO_CLARO, fm.CREME, fm.VERMELHO
TINTA = (38, 30, 22)


def ease(k):
    k = min(1.0, max(0.0, k)); return k * k * (3 - 2 * k)


def janela(k, a, b):
    return ease((k - a) / max(1e-6, b - a))


def _np(im):
    return np.asarray(im.convert('RGB'), np.float32)


def mesa(ctx, brilho=0.42, blur=3, alvo='mesa'):
    p = ctx['base'].recorte(fm.REGIOES[alvo], 1.08).filter(ImageFilter.GaussianBlur(blur))
    return ImageEnhance.Brightness(p).enhance(brilho).resize((PW, PH))


def papel(w, h, rng, tom=(214, 198, 164)):
    noise = rng.normal(0, 1, (h, w))
    tex = np.array(tom, np.float32)[None, None, :] + noise[..., None] * 9 - np.linspace(0, 26, h)[:, None, None]
    yy, xx = np.mgrid[:h, :w]
    for _ in range(5):
        cx, cy, r = rng.integers(0, w), rng.integers(0, h), rng.integers(60, 220)
        tex -= np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))[..., None] * rng.integers(8, 26)
    borda = np.clip(np.minimum.reduce([xx, yy, w - 1 - xx, h - 1 - yy]) / 18.0, 0, 1)[..., None]
    tex = tex * (0.82 + 0.18 * borda)
    arr = np.zeros((h, w, 4), np.uint8); arr[..., :3] = np.clip(tex, 0, 255); arr[..., 3] = 255
    return Image.fromarray(arr, 'RGBA')


def colar(fundo, peca, x, y, ang=0.0, sombra=26):
    peca = peca.rotate(ang, expand=True, resample=Image.BICUBIC) if ang else peca
    sm = Image.new('RGBA', peca.size, (0, 0, 0, 0)); sm.paste((0, 0, 0, 170), mask=peca.split()[3])
    sm = sm.filter(ImageFilter.GaussianBlur(sombra))
    fundo.alpha_composite(sm, (int(x + 14), int(y + 26))); fundo.alpha_composite(peca, (int(x), int(y)))
    return fundo


def circulo_tinta(arr, cx, cy, rx, ry, k, cor=(150, 28, 24), esp=7, semente=0):
    """Desenha (até k ∈ [0,1]) um círculo à mão de lápis vermelho sobre arr (RGB float32)."""
    if k <= 0: return arr
    rng = np.random.default_rng(semente)
    n = 90; ts = np.linspace(-0.3, 2 * math.pi * 1.08, n)
    jit = rng.normal(0, 0.035, n).cumsum() * 0.3
    pts = [(cx + rx * (1 + jit[i]) * math.cos(a), cy + ry * (1 + jit[i]) * math.sin(a)) for i, a in enumerate(ts)]
    m = max(2, int(n * min(1.0, k)))
    lay = np.zeros(arr.shape[:2], np.float32)
    cv2.polylines(lay, [np.array(pts[:m], np.int32)], False, 1.0, esp, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 1.1)[..., None]
    return arr * (1 - 0.85 * lay) + np.array(cor, np.float32) * 0.85 * lay


def feixe(arr, k, larg=260, ganho=0.55):
    """Feixe de lanterna que atravessa a placa (luz que 'lê' o documento)."""
    ph, pw = arr.shape[:2]
    cx = pw * (-0.2 + 1.4 * k)
    xs = np.arange(pw, dtype=np.float32)[None, :]
    ys = np.arange(ph, dtype=np.float32)[:, None]
    g = np.exp(-((xs - cx - (ys - ph / 2) * 0.35) / larg) ** 2)[..., None]
    return arr * (0.78 + ganho * g)


# ---------------------------------------------------------------- abertura: cartas caindo (ILUSTRAÇÃO)
def _verso(rng, w=250, h=360):
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 16, fill=(16, 14, 18, 255), outline=OURO + (255,), width=5)
    d.rounded_rectangle((14, 14, w - 15, h - 15), 10, outline=(110, 84, 40, 255), width=2)
    cx, cy = w / 2, h / 2
    for r in (78, 58):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=OURO_CLARO + (230,), width=3)
    f = fm.fonte('cinzel', 54); tw = f.getlength('AO'); d.text((cx - tw / 2, cy - 36), 'AO', font=f, fill=OURO_CLARO + (255,))
    for i in range(12):
        a = i * math.pi / 6
        d.line((cx + 84 * math.cos(a), cy + 84 * math.sin(a), cx + 104 * math.cos(a), cy + 104 * math.sin(a)), fill=OURO + (200,), width=3)
    a = np.asarray(c, np.float32); a[..., :3] += rng.normal(0, 4, a[..., :3].shape)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def cartas_caem(ctx, p):
    rng = np.random.default_rng(p.get('semente', 3))
    base = mesa(ctx, 0.30, 4)
    n = int(p.get('n', 9))
    cartas = []
    for i in range(n):
        im = _verso(rng).rotate(rng.uniform(-35, 35), expand=True, resample=Image.BICUBIC)
        x = PW * 0.5 + rng.uniform(-300, 300) - im.width / 2
        y = PH * 0.50 + rng.uniform(-430, 380) - im.height / 2
        cartas.append((np.asarray(im, np.float32), x, y, 0.05 + i * 0.16, rng.uniform(-1, 1)))
    bg = _np(base)

    def dyn(tl, dur):
        out = bg.copy()
        flash = 0.0
        for arr, x, y, t0, giro in cartas:
            k = (tl - t0) / 0.28
            if k <= 0: continue
            kk = min(1.0, k); e = 1 - (1 - kk) ** 3
            esc = 1.6 - 0.6 * e                                # vem de cima (mais perto da câmera) e assenta
            h0, w0 = arr.shape[:2]
            jan = int(max(w0, h0) * 1.9)                       # janela local (evita processar a placa inteira)
            cxw = x + w0 / 2 - (1 - e) * 120 * giro; cyw = y + h0 / 2 - (1 - e) * 160
            jx, jy = int(cxw - jan / 2), int(cyw - jan / 2)
            M = cv2.getRotationMatrix2D((w0 / 2, h0 / 2), giro * 40 * (1 - e), esc)
            M[0, 2] += jan / 2 - w0 / 2; M[1, 2] += jan / 2 - h0 / 2
            pc = cv2.warpAffine(arr, M, (jan, jan), flags=cv2.INTER_LINEAR, borderValue=0)
            x0c, y0c, x1c, y1c = max(0, jx), max(0, jy), min(PW, jx + jan), min(PH, jy + jan)
            if x1c <= x0c or y1c <= y0c: continue
            pc = pc[y0c - jy:y1c - jy, x0c - jx:x1c - jx]
            al = pc[..., 3:4] / 255.0
            sh = cv2.GaussianBlur(al[..., 0], (0, 0), 12)[..., None]
            reg = out[y0c:y1c, x0c:x1c]
            reg *= 1 - 0.5 * np.roll(np.roll(sh, 20, 0), 10, 1) * e
            out[y0c:y1c, x0c:x1c] = reg * (1 - al) + pc[..., :3] * al
            if 0.9 < k < 1.6: flash = max(flash, 0.18 * (1.6 - k))
        return feixe(out, 0.5 + 0.35 * math.sin(tl * 0.8), 420, 0.35) * (1 + flash)
    return {'dyn': dyn, 'zoom': (1.0, 1.07), 'pan': ((0, 0.02), (0, -0.02))}


# ---------------------------------------------------------------- documento de 1995 (trecho) com data circulada
def documento_1995(ctx, p):
    rng = np.random.default_rng(5)
    modo_ok = p.get('_gate_ok', False)
    fundo = mesa(ctx, 0.36, 2).convert('RGBA')
    FW, FH = 980, 1180
    folha = papel(FW, FH, rng, (222, 214, 190))
    d = ImageDraw.Draw(folha)
    fm_ = fm.fonte('elite', 46); ft = fm.fonte('elite', 54); fp = fm.fonte('oswald4', 32)
    y = 70; larg = FW - 120
    if modo_ok:      # transcrição curta (citação com crédito) — só na prévia privada até revisão humana
        for l in fm.quebrar('The Official INWO Card List - April 18, 1995', ft, larg):
            d.text((60, y), l, font=ft, fill=TINTA); y += 68
        y += 10; d.line((60, y, FW - 60, y), fill=(90, 70, 50), width=2); y += 34
        frase = ('(We saw the first post listing every card in the original release only 4 days after the Dec. 16 release.)')
        alvo = None
        for l in fm.quebrar(frase, fm_, larg):
            if 'Dec. 16' in l:
                xa = 60 + fm_.getlength(l.split('Dec. 16')[0]); alvo = (xa, y, fm_.getlength('Dec. 16'))
            d.text((60, y), l, font=fm_, fill=TINTA); y += 64
        y += 30
        d.text((60, y), 'Copyright © 1995 Steve Jackson Games Incorporated.', font=fm.fonte('elite', 30), fill=(70, 58, 44))
        rodape = 'TRANSCRIÇÃO DE TRECHO · sjgames.com/inwo/lists/ill.html'
    else:            # paráfrase com fonte (dado factual) — liberada para uso público
        for l in ['LISTA OFICIAL DO INWO', 'Steve Jackson Games · 18/04/1995']:
            d.text((60, y), l, font=ft, fill=TINTA); y += 70
        y += 20; d.line((60, y, FW - 60, y), fill=(90, 70, 50), width=2); y += 40
        alvo = None
        for l in fm.quebrar('A própria editora registra a data de lançamento do jogo: 16 de dezembro de 1994.', fm_, larg):
            if '16 de dezembro' in l:
                xa = 60 + fm_.getlength(l.split('16 de dezembro')[0]); alvo = (xa, y, fm_.getlength('16 de dezembro'))
            d.text((60, y), l, font=fm_, fill=TINTA); y += 64
        rodape = 'PARÁFRASE COM FONTE · sjgames.com/inwo/lists/ill.html'
    d.text((60, FH - 74), rodape, font=fp, fill=(96, 78, 58))
    x0, y0 = (PW - FW) // 2, int(PH * 0.14)
    colar(fundo, folha, x0, y0, 0)
    data = Image.new('RGBA', (PW, 300), (0, 0, 0, 0)); dd = ImageDraw.Draw(data)
    fm.texto_centro(dd, PW / 2, 40, '16 · 12 · 1994', fm.fonte('anton', 170), OURO_CLARO + (255,), stroke=4, stroke_cor=(20, 12, 4))
    base = _np(fundo)
    data_np = np.asarray(data, np.float32)
    if alvo:
        ax, ay, aw = alvo
        cxa, cya = x0 + ax + aw / 2, y0 + ay + 30
    else:
        cxa, cya, aw = PW / 2, PH * 0.45, 260

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        out = feixe(base.copy(), 0.15 + 0.7 * k, 300, 0.5)
        out = circulo_tinta(out, cxa, cya, aw / 2 + 36, 48, janela(k, 0.25, 0.6), semente=2)
        e = janela(k, 0.55, 0.8)
        if e > 0:
            y = int(PH * 0.66)
            al = data_np[..., 3:4] / 255.0 * e
            reg = out[y:y + 300]
            out[y:y + 300] = reg * (1 - al) + data_np[..., :3] * al
        return out
    return {'dyn': dyn, 'zoom': (1.18, 1.0), 'pan': ((-0.2, -0.35), (0, 0.05)), 'foco_ponto': (cxa / PW, cya / PH)}


# ---------------------------------------------------------------- título da obra (fato: nome, editora, data)
def titulo_obra(ctx, p):
    base = _np(mesa(ctx, 0.20, 9, 'livros'))
    linhas = p.get('linhas', ['ILLUMINATI:', 'NEW WORLD ORDER'])
    sub = p.get('sub', 'STEVE JACKSON GAMES · TEXAS · DEZ/1994')
    lay = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    fa = fm.fonte('anton', 150)
    y = PH * 0.36
    for i, l in enumerate(linhas):
        tam = 150
        while fm.fonte('anton', tam).getlength(l) > PW - 160: tam -= 6
        fm.texto_centro(d, PW / 2, y + i * 175, l, fm.fonte('anton', tam), OURO_CLARO + (255,), stroke=3, stroke_cor=(20, 12, 4))
    # subtítulo cabe na área segura: diminui até 38 px e, se ainda for largo, quebra em até 2 linhas (o S14 do EP05 vazava da tela)
    larg_max, tam = 860, 46
    while fm.fonte('oswald', tam).getlength(sub) > larg_max and tam > 38: tam -= 2
    fs = fm.fonte('oswald', tam)
    if fs.getlength(sub) > larg_max:
        tam = 44; fs = fm.fonte('oswald', tam)
    partes = [sub] if fs.getlength(sub) <= larg_max else fm.quebrar(sub, fs, larg_max)[:2]
    for j, parte in enumerate(partes):
        fm.texto_centro(d, PW / 2, y + len(linhas) * 175 + 40 + j * (tam + 16), parte, fs, CREME + (235,))
    d.line((PW / 2 - 200, y - 50, PW / 2 + 200, y - 50), fill=OURO + (200,), width=3)
    tx = np.asarray(lay, np.float32)
    al = tx[..., 3:4] / 255.0; rgb = tx[..., :3]
    xs = np.arange(PW, dtype=np.float32)[None, :, None]

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        frente = PW * (-0.1 + 1.5 * janela(k, 0.0, 0.55))
        rev = np.clip((frente - xs) / 140, 0, 1)                    # revelação da esquerda para a direita
        brilho = np.exp(-((xs - frente) / 70) ** 2) * 0.9
        out = base * (0.8 + 0.3 * math.sin(tl * 1.3) ** 2)
        a = al * rev
        out = out * (1 - a) + rgb * a * (1 + brilho)
        return out
    return {'dyn': dyn, 'zoom': (1.0, 1.06), 'pan': ((0.1, 0), (-0.1, 0))}


# ---------------------------------------------------------------- arte original (recorte oficial) — filtro de direitos
def arte_original(ctx, p):
    rng = np.random.default_rng(9)
    fundo = mesa(ctx, 0.34, 2).convert('RGBA')
    folha = papel(860, 1120, rng, (196, 182, 150))
    d = ImageDraw.Draw(folha)
    if p.get('_gate_ok'):
        art = Image.open(p['arquivo']).convert('RGB')
        lw = 700; lh = int(art.height * lw / art.width)
        art = art.resize((lw, lh), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
        foto = Image.new('RGBA', (lw + 40, lh + 40), (238, 232, 216, 255)); foto.paste(art, (20, 20))
        folha.alpha_composite(foto, (80, 120))
        topo_txt = 120 + lh + 80
        legenda = [p.get('titulo', ''), p.get('credito', ''), 'RECORTE DA ARTE · NÃO É A CARTA COMPLETA']
    else:
        lw, lh = 700, 480
        slip = Image.new('RGBA', (lw + 40, lh + 40), (24, 20, 18, 255)); sd = ImageDraw.Draw(slip)
        sd.rectangle((10, 10, lw + 29, lh + 29), outline=(120, 96, 60), width=3)
        fm.texto_centro(sd, (lw + 40) / 2, lh / 2 - 60, 'ARTE ORIGINAL RETIDA', fm.fonte('anton', 64), CREME + (255,), sombra=False)
        fm.texto_centro(sd, (lw + 40) / 2, lh / 2 + 30, 'aguardando licença do titular', fm.fonte('oswald4', 40), (190, 170, 130, 255), sombra=False)
        folha.alpha_composite(slip, (80, 120))
        topo_txt = 120 + lh + 80
        legenda = [p.get('titulo', ''), p.get('credito', ''), 'IMAGEM BLOQUEADA NO MODO PÚBLICO']
    fe = fm.fonte('elite', 34)
    y = topo_txt
    for l in legenda:
        for s in fm.quebrar(l, fe, 720):
            d.text((80, y), s, font=fe, fill=TINTA); y += 46
        y += 8
    # clipe
    clip = Image.new('RGBA', (60, 170), (0, 0, 0, 0)); cd = ImageDraw.Draw(clip)
    cd.rounded_rectangle((8, 4, 52, 166), 22, outline=(170, 170, 176, 255), width=7)
    cd.rounded_rectangle((20, 30, 40, 140), 12, outline=(140, 140, 146, 255), width=5)
    folha.alpha_composite(clip, (380, 40))
    x0, y0 = (PW - 860) // 2, int(PH * 0.16)
    colar(fundo, folha, x0, y0, 1.6)
    base = _np(fundo)

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        out = feixe(base.copy(), 0.1 + 0.8 * k, 340, 0.55)
        sig = 6 * (1 - janela(k, 0.0, 0.35))
        return cv2.GaussianBlur(out, (0, 0), sig) if sig > 0.4 else out
    return {'dyn': dyn, 'zoom': (1.12, 1.0), 'pan': ((0.0, -0.25), (0.0, 0.1))}


# ---------------------------------------------------------------- lista oficial: três linhas destacadas em sincronia
def lista_oficial(ctx, p):
    rng = np.random.default_rng(13)
    fundo = mesa(ctx, 0.34, 2).convert('RGBA')
    FW, FH = 1000, 1300
    folha = papel(FW, FH, rng, (220, 210, 184))
    d = ImageDraw.Draw(folha)
    fh = fm.fonte('elite', 54); fr = fm.fonte('elite', 46); fc = fm.fonte('oswald', 30); fa = fm.fonte('elite', 32)
    d.text((50, 50), 'LISTA OFICIAL INWO', font=fh, fill=TINTA)
    d.text((50, 118), 'Steve Jackson Games · 18/04/1995', font=fm.fonte('elite', 40), fill=(70, 58, 44))
    d.line((50, 180, FW - 50, 180), fill=(90, 70, 50), width=2)
    cols = [50, 470, 560, 700]
    for x, c in zip(cols, ['CARTA', 'FREQ.', 'TIPO', 'ARTE / CORES']):
        d.text((x, 200), c, font=fc, fill=(96, 78, 58))
    linhas = p['linhas']               # [[nome, freq, tipo, arte_cores, destaque?], ...] ('…' para trecho omitido)
    y = 268; alvos = []
    for ln in linhas:
        if ln[0] == '…':
            d.text((50, y), '· · ·', font=fr, fill=(110, 96, 76)); y += 70; continue
        for x, v in zip(cols, ln[:4]):
            f = fr if x != 700 else fa
            d.text((x, y + (8 if x == 700 else 0)), v, font=f, fill=TINTA)
        if len(ln) > 4 and ln[4]:
            alvos.append((50 + fr.getlength(ln[0]) / 2, y + 28, fr.getlength(ln[0]) / 2 + 30))
        y += 82
    d.text((50, FH - 74), 'Dados transcritos da lista publicada pela editora', font=fm.fonte('oswald4', 32), fill=(96, 78, 58))
    x0, y0 = (PW - FW) // 2, int(PH * 0.12)
    colar(fundo, folha, x0, y0, -0.8)
    base = _np(fundo)
    sync = p.get('sync', [0.08, 0.38, 0.68])

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        out = feixe(base.copy(), 0.2 + 0.6 * k, 380, 0.45)
        for i, (ax, ay, rx) in enumerate(alvos):
            t0 = sync[i] if i < len(sync) else 0.8
            out = circulo_tinta(out, x0 + ax, y0 + ay, rx, 40, (k - t0) / 0.18, semente=i + 7)
        return out
    if p.get('camera') == 'geral':      # do cabeçalho para as linhas
        return {'dyn': dyn, 'zoom': (1.0, 1.10), 'pan': ((0, -0.6), (0, 0.1))}
    # macro com tilt (A5): a câmera desce acompanhando as linhas destacadas
    return {'dyn': dyn, 'zoom': (1.38, 1.26), 'pan': ((-0.6, -0.15), (-0.45, 0.55))}


# ---------------------------------------------------------------- 412 cartas na lista (contagem e viés de seleção)
def grade_cartas(ctx, p):
    n = int(p.get('n', 412)); fase = p.get('fase', 'contagem')
    cols = 22; rows = math.ceil(n / cols)
    cw, ch = 34, 48; gx, gy = 7, 8
    gw = cols * (cw + gx) - gx; gh = rows * (ch + gy) - gy
    ox, oy = (PW - gw) / 2, PH * 0.36
    bg = np.zeros((PH, PW, 3), np.float32) + _np(mesa(ctx, 0.16, 12, 'gavetas')) * 0.6
    rng = np.random.default_rng(21)
    ordem = rng.permutation(n)
    destaques = set(p.get('destaques', [37, 205, 330]))
    fa = fm.fonte('anton', 210); fs = fm.fonte('oswald', 46)

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
        vis = n if fase != 'contagem' else int(n * janela(k, 0.0, 0.75))
        for j in range(vis):
            i = ordem[j] if fase == 'contagem' else j
            r, c = divmod(i, cols)
            x, y = ox + c * (cw + gx), oy + r * (ch + gy)
            if fase == 'selecao':
                dest = i in destaques
                amb = 1 - 0.85 * janela(k, 0.15, 0.55)
                cor = OURO_CLARO if dest else tuple(int(v * amb) for v in (120, 96, 60))
                larg = 4 if dest else 2
            else:
                cor = (150, 120, 70); larg = 2
            d.rounded_rectangle((x, y, x + cw, y + ch), 6, outline=cor, width=larg, fill=(20, 16, 12))
        num = vis if fase == 'contagem' else n
        fm.texto_centro(d, PW / 2, oy - 330, str(num), fa, OURO_CLARO + (255,), stroke=3, stroke_cor=(20, 12, 4))
        fm.texto_centro(d, PW / 2, oy - 80, 'CARTAS NA LISTA DE 1995', fs, CREME + (230,))
        out = np.asarray(img, np.float32)
        if fase == 'selecao':
            glow = cv2.GaussianBlur(out, (0, 0), 10) * janela(k, 0.3, 0.7) * 0.8
            out = out + glow
        return out
    return {'dyn': dyn, 'zoom': (1.0, 1.07) if fase == 'contagem' else (1.06, 1.18), 'pan': ((0, 0), (0, 0.05))}


# ---------------------------------------------------------------- duas leituras (INTERPRETAÇÃO)
def leituras(ctx, p):
    base = _np(mesa(ctx, p.get('brilho_fundo', 0.34), 10, 'tudo'))   # QA 04/11: fundo a 0,16 virava tela quase preta
    a, b = p.get('a', ['PREVISÃO?', 'alguém sabia']), p.get('b', ['MEDOS DOS ANOS 90', 'terrorismo · epidemias · poder'])
    sync_b = p.get('sync_b', 0.45)

    def lado(txt, sub, cor):
        lay = Image.new('RGBA', (PW // 2, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        tam = 120
        larg = PW // 2 - 200                     # margem lateral segura (>= 100 px após o enquadramento)
        while max(fm.fonte('anton', tam).getlength(x) for x in fm.quebrar(txt, fm.fonte('anton', tam), larg)) > larg and tam > 60:
            tam -= 6
        f = fm.fonte('anton', tam); ls = fm.quebrar(txt, f, larg)
        y = PH * 0.42 - len(ls) * tam * 0.55
        for i, l in enumerate(ls):
            fm.texto_centro(d, PW / 4, y + i * tam * 1.08, l, f, cor + (255,), stroke=3, stroke_cor=(16, 10, 4))
        for i, l in enumerate(fm.quebrar(sub, fm.fonte('oswald4', 40), PW // 2 - 110)):
            fm.texto_centro(d, PW / 4, y + len(ls) * tam * 1.08 + 30 + i * 52, l, fm.fonte('oswald4', 40), CREME + (220,))
        return np.asarray(lay, np.float32)
    L = lado(a[0], a[1], OURO_CLARO); R = lado(b[0], b[1], CREME)

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        out = base.copy()
        ea = janela(k, 0.0, 0.18); eb = janela(k, sync_b, sync_b + 0.15)
        half = PW // 2
        # a metade ativa recebe luz; a outra escurece
        out[:, :half] *= 0.65 + 0.5 * ea * (1 - 0.5 * eb)
        out[:, half:] *= 0.55 + 0.6 * eb
        for arr, x0, e, dx in ((L, 0, ea * (1 - 0.45 * eb), -40), (R, half, eb, 40)):
            if e <= 0: continue
            al = arr[..., 3:4] / 255.0 * e
            sh = int(dx * (1 - e))
            reg = out[:, x0:x0 + half]
            src = np.roll(arr, sh, axis=1); als = np.roll(al, sh, axis=1)
            out[:, x0:x0 + half] = reg * (1 - als) + src[..., :3] * als
        x = half; out[int(PH * 0.28):int(PH * 0.72), x - 2:x + 2] = np.array(OURO, np.float32) * (0.4 + 0.6 * ea)
        return out
    return {'dyn': dyn, 'zoom': (1.02, 1.08), 'pan': ((0, 0), (0, 0))}


# ---------------------------------------------------------------- dossiê que se abre (A4) — ILUSTRAÇÃO
def dossie_abre(ctx, p):
    rng = np.random.default_rng(17)
    fundo = mesa(ctx, 0.34, 2).convert('RGBA')
    fw, fh = 860, 1180
    pagina = papel(fw - 40, fh - 40, rng, (220, 210, 184)); d = ImageDraw.Draw(pagina)
    d.text((50, 60), p.get('cabecalho', 'ARQUIVO Nº 01 · PÁGINA SOLTA'), font=fm.fonte('elite', 40), fill=TINTA)
    d.line((50, 120, fw - 90, 120), fill=(90, 70, 50), width=2)
    y = 170
    for l in p.get('linhas', []):
        for s in fm.quebrar(l, fm.fonte('elite', 38), fw - 140):
            d.text((50, y), s, font=fm.fonte('elite', 38), fill=TINTA); y += 54
        y += 16
    if p.get('data'):
        fm.texto_centro(d, (fw - 40) / 2, y + 60, p['data'], fm.fonte('anton', 150), (120, 30, 26, 255), sombra=False)
    capa = Image.new('RGBA', (fw, fh), (0, 0, 0, 0)); cd = ImageDraw.Draw(capa)
    cd.rounded_rectangle((0, 30, fw - 1, fh - 1), 16, fill=(78, 60, 36, 255))
    cd.rounded_rectangle((40, 0, 330, 70), 12, fill=(78, 60, 36, 255))
    cd.text((70, 12), 'DOSSIÊ', font=fm.fonte('elite', 40), fill=(30, 22, 14, 255))
    fm.texto_centro(cd, fw / 2, fh * 0.45, p.get('rotulo', 'STEVE JACKSON GAMES'), fm.fonte('anton', 70), (40, 28, 16, 255), sombra=False)
    capa_np = np.asarray(capa, np.float32)
    x0, y0 = (PW - fw) // 2, int(PH * 0.16)
    base_img = fundo.copy()
    colar(base_img, pagina, x0 + 20, y0 + 50, 0)
    base = _np(base_img)

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        e = janela(k, 0.12, 0.55)
        out = feixe(base.copy(), 0.3 + 0.5 * k, 360, 0.5)
        larg = max(1, int(fw * (1 - e)))                      # a capa gira sobre a lombada esquerda
        if larg > 4:
            c = cv2.resize(capa_np, (larg, fh), interpolation=cv2.INTER_AREA)
            sombra = 1 - 0.45 * e
            al = c[..., 3:4] / 255.0
            reg = out[y0:y0 + fh, x0:x0 + larg]
            out[y0:y0 + fh, x0:x0 + larg] = reg * (1 - al) + c[..., :3] * sombra * al
        return out
    return {'dyn': dyn, 'zoom': (1.0, 1.12), 'pan': ((0, 0.15), (0, -0.05))}


# ---------------------------------------------------------------- escritório de época, 1950–1979 (RECONSTITUIÇÃO ILUSTRADA)
def escritorio_epoca(ctx, p):
    """Repartição dos anos 1960–70 desenhada por código: arquivos de aço, máquina de escrever, luminária de mesa, pastas
    e persiana. Sem monitor nem disquete (a cena 'escritorio' da V1 é de 1990 e vira anacronismo antes de 1980).
    Nada de logotipo, nome de órgão ou papel legível: é ambientação rotulada, não documento.
    p: acao 'lanterna' (feixe varre os arquivos à noite e uma gaveta se abre) | 'gaveta' (uma gaveta de aço se abre sob
    a luz) | 'luminaria' (a luz da mesa acende e a câmera se aproxima das pastas); semente."""
    rng = np.random.default_rng(p.get('semente', 7))
    acao = p.get('acao', 'lanterna')
    img = Image.new('RGB', (PW, PH), (14, 12, 10)); d = ImageDraw.Draw(img)
    yp = int(PH * 0.62)
    for y in range(yp):                                                   # parede: reboco escuro com leve gradiente
        c = 20 + 16 * y / yp
        d.line((0, y, PW, y), fill=(int(c + 7), int(c + 3), int(c - 1)))
    # janela com persiana (luz fria da rua)
    jx0, jy0, jx1, jy1 = int(PW * 0.07), int(PH * 0.03), int(PW * 0.47), int(PH * 0.145)
    d.rectangle((jx0 - 14, jy0 - 14, jx1 + 14, jy1 + 14), fill=(44, 37, 30))
    d.rectangle((jx0, jy0, jx1, jy1), fill=(26, 30, 38))
    for y in range(jy0 + 4, jy1, 22):
        d.rectangle((jx0, y, jx1, y + 12), fill=(78, 84, 96))
    d.line((jx0 + (jx1 - jx0) * 0.72, jy0, jx0 + (jx1 - jx0) * 0.72, jy1), fill=(40, 36, 32), width=3)   # cordão
    # arquivos de aço de 4 gavetas (verde-oliva acinzentado), com puxador e porta-etiqueta em branco
    gav = {}
    n_arq, gap = 3, 24
    ax0, ax1 = int(PW * 0.05), int(PW * 0.95)
    aw = (ax1 - ax0 - gap * (n_arq - 1)) // n_arq
    at, ab = int(PH * 0.175), int(PH * 0.63)
    for i in range(n_arq):
        x0 = ax0 + i * (aw + gap); tom = np.array((70, 76, 66)) + rng.integers(-6, 7, 3)
        d.rectangle((x0, at, x0 + aw, ab), fill=tuple(int(v) for v in tom * 0.82))
        d.rectangle((x0, at, x0 + aw, at + 14), fill=tuple(int(v) for v in tom * 1.15))           # tampo
        gh = (ab - at - 30) // 4
        for j in range(4):
            y0 = at + 22 + j * gh
            r = (x0 + 12, y0, x0 + aw - 12, y0 + gh - 10)
            d.rectangle(r, fill=tuple(int(v) for v in tom))
            d.line((r[0], r[1], r[2], r[1]), fill=tuple(int(min(255, v * 1.35)) for v in tom), width=3)   # chanfro claro
            d.line((r[0], r[3], r[2], r[3]), fill=tuple(int(v * 0.6) for v in tom), width=4)
            cx = (r[0] + r[2]) // 2
            d.rounded_rectangle((cx - 72, y0 + int(gh * 0.34), cx + 72, y0 + int(gh * 0.34) + 20), 9, fill=(150, 148, 136))
            d.rectangle((cx - 52, y0 + int(gh * 0.13), cx + 52, y0 + int(gh * 0.13) + 22), fill=(120, 116, 100))
            d.rectangle((cx - 46, y0 + int(gh * 0.13) + 3, cx + 46, y0 + int(gh * 0.13) + 18), fill=(196, 184, 150))
            gav[(i, j)] = r
    # mesa em perspectiva: tampo do fundo (0,60) até a borda da frente (0,78), painel escuro abaixo
    mb, mf = int(PH * 0.60), int(PH * 0.78)
    for y in range(mb, mf):
        c = (y - mb) / (mf - mb)
        d.line((0, y, PW, y), fill=(int(46 + 22 * c), int(31 + 15 * c), int(20 + 9 * c)))
    for i in range(9):                                                    # veio da madeira, convergindo ao fundo
        x = int(-150 + i * 180)
        d.line((PW / 2 + (x - PW / 2) * 0.55, mb, x, mf), fill=(40, 27, 17), width=2)
    d.rectangle((0, mf, PW, mf + 16), fill=(78, 54, 34))                   # quina da frente
    d.rectangle((0, mf + 16, PW, PH), fill=(30, 20, 13))
    # máquina de escrever (silhueta, sem marca), um pouco à esquerda
    s = 1.28; tx, ty = int(PW * 0.33), int(PH * 0.735)
    S = lambda v: int(v * s)
    d.polygon([(tx - S(210), ty + S(40)), (tx + S(210), ty + S(40)), (tx + S(170), ty - S(120)), (tx - S(170), ty - S(120))], fill=(28, 28, 30))
    folha = papel(S(250), S(170), rng, (196, 186, 160)); fd = ImageDraw.Draw(folha)
    for k in range(4):                                                    # linhas datilografadas ilegíveis
        yk = S(40) + k * S(24)
        fd.line((S(24), yk, S(24) + int(rng.integers(S(110), S(210))), yk), fill=(92, 82, 68, 255), width=4)
    rgba = img.convert('RGBA'); rgba.alpha_composite(folha, (tx - S(125), ty - S(150) - folha.height + S(20)))
    img = rgba.convert('RGB'); d = ImageDraw.Draw(img)
    d.rounded_rectangle((tx - S(245), ty - S(175), tx + S(245), ty - S(122)), S(22), fill=(36, 36, 38))   # carro
    d.rounded_rectangle((tx - S(228), ty - S(166), tx + S(228), ty - S(130)), S(16), fill=(16, 16, 16))   # rolo
    d.ellipse((tx - S(268), ty - S(170), tx - S(236), ty - S(128)), fill=(70, 66, 58))                    # botão do rolo
    for row in range(4):                                                  # teclas
        for k in range(10 - (row % 2)):
            kx = tx - S(165) + k * S(36) + (row % 2) * S(18) + row * S(4); ky = ty - S(92) + row * S(30)
            d.ellipse((kx - S(11), ky - S(10), kx + S(11), ky + S(10)), fill=(58, 56, 52))
            d.ellipse((kx - S(7), ky - S(7), kx + S(7), ky + S(5)), fill=(96, 92, 84))
    # pastas de papel pardo empilhadas sob a luminária
    px_, py_ = int(PW * 0.69), int(PH * 0.745)
    for k in range(5):
        d.polygon([(px_ - 190 + k * 7, py_ - k * 17), (px_ + 190 + k * 5, py_ - k * 17), (px_ + 165 + k * 5, py_ - 34 - k * 17),
                   (px_ - 165 + k * 7, py_ - 34 - k * 17)], fill=(176 - k * 7, 146 - k * 7, 98 - k * 5))
        d.line((px_ - 190 + k * 7, py_ - k * 17, px_ + 190 + k * 5, py_ - k * 17), fill=(120 - k * 6, 96 - k * 6, 60), width=2)
    # luminária de latão com abajur verde
    lx, lb = int(PW * 0.84), int(PH * 0.70)
    ly = lb - 300
    d.rectangle((lx - 78, lb - 26, lx + 78, lb + 4), fill=(84, 70, 40))
    d.rectangle((lx - 9, ly + 44, lx + 9, lb - 24), fill=(110, 92, 52))
    d.polygon([(lx - 150, ly + 76), (lx + 150, ly + 76), (lx + 106, ly), (lx - 106, ly)], fill=(22, 64, 44))
    d.line((lx - 150, ly + 76, lx + 150, ly + 76), fill=(150, 120, 60), width=5)
    base = _np(img.filter(ImageFilter.GaussianBlur(1.1)))
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    poca = np.exp(-(((xx - lx + 230) ** 2) / (2 * 380 ** 2) + ((yy - PH * 0.71) ** 2) / (2 * 170 ** 2)))   # luz na mesa
    poca += 0.5 * np.exp(-(((xx - lx + 60) ** 2) / (2 * 260 ** 2) + ((yy - PH * 0.50) ** 2) / (2 * 240 ** 2)))  # respingo nos arquivos
    cupula = np.exp(-(((xx - lx) ** 2) / (2 * 160 ** 2) + ((yy - (ly + 84)) ** 2) / (2 * 50 ** 2)))
    rua = np.zeros((PH, PW), np.float32)                                  # listras da persiana projetadas na parede
    for y in range(jy0 + 4, jy1, 22):
        dy = (y - jy0) * 2.2
        cv2.fillConvexPoly(rua, np.array([(jx0 + 240, int(PH * 0.20 + dy)), (jx1 + 540, int(PH * 0.25 + dy)),
                                         (jx1 + 540, int(PH * 0.25 + dy + 22)), (jx0 + 240, int(PH * 0.20 + dy + 20))], np.int32), 1.0)
    rua = cv2.GaussianBlur(rua, (0, 0), 9) * (yy < mb)
    gx0, gy0, gx1, gy1 = gav[(1, 1)]                                     # a gaveta que se abre
    frente = base[gy0 - 4:gy1 + 6, gx0 - 4:gx1 + 4].copy()
    hgt, wid = frente.shape[:2]
    miolo = np.zeros_like(frente) + np.array([10, 9, 8], np.float32)
    for k in range(9):                                                    # abas de pastas dentro da gaveta
        fx = 18 + k * (wid - 40) // 9
        cv2.rectangle(miolo, (fx, 18 + (k % 3) * 9), (fx + 62, 74), (150 - k * 4, 124 - k * 4, 84), -1)
    cv2.rectangle(miolo, (8, 64), (wid - 8, hgt - 6), (120, 98, 66), -1)
    foco_gav = np.exp(-(((xx - (gx0 + gx1) / 2) ** 2) / (2 * 230 ** 2) + ((yy - (gy0 + gy1) / 2 - 60) ** 2) / (2 * 200 ** 2)))

    def acesa(k):
        if acao != 'luminaria':
            return 1.0
        if k < 0.10: return 0.0
        if k < 0.17: return 0.6 * (1 + math.sin(k * 420)) / 2           # tremida do acender
        return 1.0

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        a = acesa(k)
        out = base.copy()
        if acao in ('gaveta', 'lanterna'):
            e = janela(k, 0.15, 0.65) if acao == 'gaveta' else janela(k, 0.50, 0.88)
            out[gy0 - 4:gy1 + 6, gx0 - 4:gx1 + 4] = miolo
            sc = 1.0 + 0.12 * e; nw, nh = int(wid * sc), int(hgt * sc)
            fr = cv2.resize(frente, (nw, nh), interpolation=cv2.INTER_LINEAR)
            x = (gx0 + gx1) // 2 - nw // 2; y = gy0 - 4 + int(110 * e) - (nh - hgt) // 2
            out[max(0, y - 22):y, x:x + nw] *= 0.45                       # sombra da frente puxada
            out[y:y + nh, x:x + nw] = fr
        if acao == 'lanterna':
            cx = PW * (0.10 + 0.62 * ease(min(1.0, k * 1.6))); cy = PH * (0.40 + 0.04 * math.sin(tl * 1.7))
            if k > 0.62:                                                  # o feixe pousa na gaveta aberta
                q = janela(k, 0.62, 0.8); cx = cx * (1 - q) + (gx0 + gx1) / 2 * q; cy = cy * (1 - q) + (gy0 + gy1) / 2 * q + 60 * q
            ang = np.arctan2(yy + 260, xx + 140); ang0 = math.atan2(cy + 260, cx + 140)
            cone = np.exp(-((ang - ang0) ** 2) / (2 * 0.05 ** 2))
            spot = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * 215 ** 2)))
            luz = 0.13 + 0.45 * rua + 0.25 * (poca + cupula) + 1.7 * spot + 0.30 * cone
            return out * luz[..., None] + np.array([36, 30, 18], np.float32) * (0.4 * cone)[..., None]
        luz = 0.20 + 0.55 * rua + a * (1.05 * poca + 0.9 * cupula)
        if acao == 'gaveta':
            luz = luz + 0.9 * foco_gav
        return out * luz[..., None] + np.array([46, 32, 12], np.float32) * (a * 0.5 * poca)[..., None]
    if acao == 'luminaria':
        return {'dyn': dyn, 'zoom': (1.0, 1.15), 'pan': ((0.0, -0.1), (0.5, 0.5))}
    return {'dyn': dyn, 'zoom': (1.0, 1.08), 'pan': ((0.0, -0.05), (0.0, 0.08))}


# ---------------------------------------------------------------- linha do tempo 1990 → 1994 (fato com fonte)
def salto_datas(ctx, p):
    bg = _np(mesa(ctx, 0.20, 9, 'gavetas'))
    a0, a1 = p.get('de', '01·03·1990'), p.get('ate', '16·12·1994')
    r0, r1 = p.get('rot_de', 'BUSCA FEDERAL NA EDITORA'), p.get('rot_ate', 'INWO NAS LOJAS')
    gap = p.get('gap', '4 ANOS E 9 MESES')
    fa = fm.fonte('anton', 104); fs = fm.fonte('oswald', 40); fg = fm.fonte('anton', 70)
    y = PH * 0.52; x0, x1 = PW * 0.24, PW * 0.76

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
        e = janela(k, 0.15, 0.6)
        xm = x0 + (x1 - x0) * e
        d.line((x0, y, x1, y), fill=(80, 64, 36), width=6)
        d.line((x0, y, xm, y), fill=VERMELHO, width=10)
        for (x, ano, rot, on, cima) in [(x0, a0, r0, True, True), (x1, a1, r1, e >= 0.98, False)]:
            col = OURO_CLARO if on else (90, 76, 50)
            d.ellipse((x - 24, y - 24, x + 24, y + 24), fill=(20, 14, 8), outline=col, width=7)
            yt = y - 270 if cima else y + 60
            fm.texto_centro(d, x, yt, ano, fa, col)
            for i, l in enumerate(fm.quebrar(rot, fs, 420)):
                fm.texto_centro(d, x, yt + (125 if cima else 130) + i * 48, l, fs, CREME if on else (110, 100, 80))
        if e >= 0.98:
            fm.texto_centro(d, PW / 2, y + 380, gap, fg, VERMELHO + (255,))
        return np.asarray(img, np.float32)
    return {'dyn': dyn, 'zoom': (1.0, 1.05), 'pan': ((0, 0), (0, 0))}


# ---------------------------------------------------------------- trecho de documento genérico (EP02 em diante)
def trecho_documento(ctx, p):
    """Trecho de documento com variante privada (transcrição literal, quotation_excerpt) e pública (paráfrase com fonte).
    p: {'privado': {cabecalho, texto, destaque, rodape}, 'publico': {...}, 'data': 'opcional'}; usa a variante pública
    quando o filtro de direitos barra o trecho literal ou quando só ela existe."""
    rng = np.random.default_rng(p.get('semente', 23))
    v = p.get('privado') if (p.get('_gate_ok') and p.get('privado')) else (p.get('publico') or p.get('privado'))
    fundo = mesa(ctx, 0.36, 2).convert('RGBA')
    FW, FH = 980, 1180
    folha = papel(FW, FH, rng, (222, 214, 190))
    d = ImageDraw.Draw(folha)
    fb = fm.fonte('elite', 46); ft = fm.fonte('elite', 52); fp = fm.fonte('oswald4', 32)
    y = 70; larg = FW - 120
    for l in fm.quebrar(v.get('cabecalho', ''), ft, larg):
        d.text((60, y), l, font=ft, fill=TINTA); y += 66
    y += 10; d.line((60, y, FW - 60, y), fill=(90, 70, 50), width=2); y += 36
    alvo = None; dest = v.get('destaque', '')
    linhas_txt = fm.quebrar(v.get('texto', ''), fb, larg)
    # o destaque pode quebrar entre linhas: circula o maior trecho contínuo dele que coube numa linha só
    cands = []
    if dest:
        ws = dest.split()
        cands = [' '.join(ws[i:j]) for n in range(len(ws), 0, -1) for i in range(len(ws) - n + 1) for j in [i + n]]
    escolha = next(((c, i) for c in sorted(cands, key=len, reverse=True) if len(c) >= 3
                    for i, l in enumerate(linhas_txt) if c in l), None)
    for i, l in enumerate(linhas_txt):
        if escolha and i == escolha[1]:
            c = escolha[0]; xa = 60 + fb.getlength(l.split(c)[0]); alvo = (xa, y, fb.getlength(c))
        d.text((60, y), l, font=fb, fill=TINTA); y += 64
    d.text((60, FH - 74), v.get('rodape', ''), font=fp, fill=(96, 78, 58))
    x0, y0 = (PW - FW) // 2, int(PH * 0.14)
    colar(fundo, folha, x0, y0, 0)
    base = _np(fundo)
    data_np = None
    if p.get('data'):
        data = Image.new('RGBA', (PW, 300), (0, 0, 0, 0)); dd = ImageDraw.Draw(data)
        fm.texto_centro(dd, PW / 2, 40, p['data'], fm.fonte('anton', 160), OURO_CLARO + (255,), stroke=4, stroke_cor=(20, 12, 4))
        data_np = np.asarray(data, np.float32)
    if alvo:
        ax, ay, aw = alvo; cxa, cya = x0 + ax + aw / 2, y0 + ay + 30
    else:
        cxa, cya, aw = PW / 2, PH * 0.4, 0

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        out = feixe(base.copy(), 0.15 + 0.7 * k, 300, 0.5)
        if alvo:
            out = circulo_tinta(out, cxa, cya, aw / 2 + 36, 48, janela(k, 0.25, 0.6), semente=5)
        if data_np is not None:
            e = janela(k, 0.55, 0.8)
            if e > 0:
                yy = int(PH * 0.66); al = data_np[..., 3:4] / 255.0 * e
                out[yy:yy + 300] = out[yy:yy + 300] * (1 - al) + data_np[..., :3] * al
        return out
    return {'dyn': dyn, 'zoom': (1.16, 1.0), 'pan': ((-0.15, -0.35), (0, 0.05))}


# ---------------------------------------------------------------- página real de documento (PDF) — domínio público ou acervo
def _foco_camera(foco_plate, z_max=2.4):
    """Converte uma região (x0, y0, x1, y1) em pixels da placa em (zoom, pan) do enquadramento 9:16 da fábrica."""
    x0, y0, x1, y1 = foco_plate
    rw, rh = max(40, x1 - x0), max(40, y1 - y0)
    z = min(z_max, max(1.0, min(0.86 * PW / rw, 0.86 * PH / rh)))
    cw, ch = PW / z, PH / z
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    px = 0.0 if PW - cw < 1 else max(-1.0, min(1.0, (cx - PW / 2) / ((PW - cw) / 2)))
    py = 0.0 if PH - ch < 1 else max(-1.0, min(1.0, (cy - PH / 2) / ((PH - ch) / 2)))
    return z, (px, py)


def pagina_documento(ctx, p):
    """p: arquivo (PDF), pagina (0 = primeira), foco [x0,y0,x1,y1] normalizado na página (opcional), circular (bool),
    inverter (começa no detalhe e abre para a página), dpi, rodape (texto pequeno abaixo da página)."""
    import pymupdf
    doc = pymupdf.open(p['arquivo'])
    pg = doc[int(p.get('pagina', 0))]
    pix = pg.get_pixmap(dpi=int(p.get('dpi', 130)))
    img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    doc.close()
    larg = int(p.get('largura', 1000))
    alt = int(img.height * larg / img.width)
    if alt > PH - 140:
        alt = PH - 140; larg = int(img.width * alt / img.height)
    img = img.resize((larg, alt), Image.LANCZOS)
    a = np.asarray(img, np.float32)
    a = a * np.array([1.0, 0.97, 0.90], np.float32) + np.array([6, 4, 0], np.float32)      # papel envelhecido, sem alterar o conteúdo
    folha = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    fundo = mesa(ctx, 0.30, 3).convert('RGBA')
    x0, y0 = (PW - larg) // 2, max(60, (PH - alt) // 2 - 40)
    colar(fundo, folha, x0, y0, 0)
    if p.get('rodape'):
        d = ImageDraw.Draw(fundo); f = fm.fonte('oswald4', 30)
        for i, l in enumerate(fm.quebrar(p['rodape'], f, PW - 220)[:2]):
            d.text((x0, y0 + alt + 24 + i * 38), l, font=f, fill=CREME + (200,))
    base = _np(fundo)
    foco = p.get('foco')
    if foco:
        fx0, fy0, fx1, fy1 = foco
        reg = (x0 + fx0 * larg, y0 + fy0 * alt, x0 + fx1 * larg, y0 + fy1 * alt)
        z_det, pan_det = _foco_camera(reg)
    else:
        reg = None; z_det, pan_det = 1.12, (0.0, -0.2)

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        out = feixe(base.copy(), 0.1 + 0.8 * k, 360, 0.42)
        if reg is not None and p.get('circular', True):
            out = circulo_tinta(out, (reg[0] + reg[2]) / 2, (reg[1] + reg[3]) / 2, (reg[2] - reg[0]) / 2 + 22,
                                (reg[3] - reg[1]) / 2 + 18, janela(k, 0.55, 0.85), esp=6, semente=11)
        return out
    ida = ((1.0, (0.0, 0.0)), (z_det, pan_det))
    if p.get('inverter'):
        ida = ida[::-1]
    return {'dyn': dyn, 'zoom': (ida[0][0], ida[1][0]), 'pan': (ida[0][1], ida[1][1])}


# ---------------------------------------------------------------- carta ou fotografia de arquivo
def imagem_arquivo(ctx, p):
    """p: arquivo, moldura 'carta' | 'foto' | 'cheia', foco [x0,y0,x1,y1] normalizado (opcional), legenda (texto curto
    sob a imagem), inclinacao (graus). Placeholder honesto quando o filtro de direitos barra o arquivo."""
    rng = np.random.default_rng(p.get('semente', 31))
    fundo = mesa(ctx, 0.30, 3).convert('RGBA')
    mold = p.get('moldura', 'carta')
    if p.get('_gate_ok') and p.get('arquivo'):
        im = Image.open(p['arquivo']).convert('RGB')
    else:
        im = Image.new('RGB', (600, 840), (24, 20, 18)); d0 = ImageDraw.Draw(im)
        d0.rectangle((14, 14, 585, 825), outline=(120, 96, 60), width=4)
        fm.texto_centro(d0, 300, 330, 'IMAGEM RETIDA', fm.fonte('anton', 70), CREME, sombra=False)
        fm.texto_centro(d0, 300, 430, 'aguardando licença', fm.fonte('oswald4', 40), (190, 170, 130), sombra=False)
    if mold == 'cheia':
        esc = max(PW / im.width, PH / im.height)
        im = im.resize((int(im.width * esc) + 1, int(im.height * esc) + 1), Image.LANCZOS)
        fundo = im.crop(((im.width - PW) // 2, (im.height - PH) // 2, (im.width - PW) // 2 + PW, (im.height - PH) // 2 + PH)).convert('RGBA')
        x0 = y0 = 0; larg, alt = PW, PH
    else:
        larg = int(p.get('largura', 720 if mold == 'carta' else 940))
        alt = int(im.height * larg / im.width)
        if alt > PH * 0.62:
            alt = int(PH * 0.62); larg = int(im.width * alt / im.height)
        im = im.resize((larg, alt), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 50, 2))
        if mold == 'carta':
            m = Image.new('L', (larg, alt), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, larg - 1, alt - 1), int(larg * 0.05), fill=255)
            peca = Image.new('RGBA', (larg, alt), (0, 0, 0, 0)); peca.paste(im, (0, 0), m)
        else:
            peca = Image.new('RGBA', (larg + 36, alt + 36), (236, 230, 214, 255)); peca.paste(im, (18, 18))
            larg, alt = larg + 36, alt + 36
        x0, y0 = (PW - larg) // 2, int(PH * 0.40 - alt / 2)
        colar(fundo, peca, x0, y0, float(p.get('inclinacao', rng.uniform(-3, 3))))
    if p.get('legenda') and mold != 'cheia':
        d = ImageDraw.Draw(fundo); f = fm.fonte('elite', 36)
        for i, l in enumerate(fm.quebrar(p['legenda'], f, PW - 200)[:2]):
            fm.texto_centro(d, PW / 2, y0 + alt + 50 + i * 48, l, f, CREME + (230,), sombra=True)
    base = _np(fundo)
    foco = p.get('foco')
    if foco and mold != 'cheia':
        fx0, fy0, fx1, fy1 = foco
        z_det, pan_det = _foco_camera((x0 + fx0 * larg, y0 + fy0 * alt, x0 + fx1 * larg, y0 + fy1 * alt))
    else:
        z_det, pan_det = (1.10, (0.0, -0.1))

    def dyn(tl, dur):
        k = tl / max(0.1, dur)
        out = feixe(base.copy(), 0.05 + 0.9 * k, 330, 0.5)
        sig = 5 * (1 - janela(k, 0.0, 0.3))
        return cv2.GaussianBlur(out, (0, 0), sig) if sig > 0.4 else out
    return {'dyn': dyn, 'zoom': (1.0, z_det), 'pan': ((0.0, 0.0), pan_det)}


# ---------------------------------------------------------------- trecho de vídeo de arquivo (cinejornal etc.)
def video_arquivo(ctx, p):
    """p: arquivo (mp4), inicio (s), velocidade, pb (preto e branco), enquadramento 'faixa' (largura inteira com fundo
    desfocado) | 'cheio' (corta para 9:16). Lê os quadros em ordem; o áudio do arquivo não é usado."""
    cap = cv2.VideoCapture(p['arquivo'])
    fps = cap.get(cv2.CAP_PROP_FPS) or 29.97
    ini = float(p.get('inicio', 0.0)); vel = float(p.get('velocidade', 1.0))
    cap.set(cv2.CAP_PROP_POS_MSEC, ini * 1000)
    estado = {'t': ini - 1 / fps, 'q': None}
    yy = np.arange(PH, dtype=np.float32)[:, None, None]

    def ler(t):
        while estado['t'] + 1e-6 < t or estado['q'] is None:
            ok, q = cap.read()
            if not ok:
                break
            estado['q'] = q; estado['t'] = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        return estado['q']

    def dyn(tl, dur):
        q = ler(ini + tl * vel)
        if q is None:
            return np.zeros((PH, PW, 3), np.float32)
        q = cv2.cvtColor(q, cv2.COLOR_BGR2RGB).astype(np.float32)
        if p.get('pb', True):
            g = q.mean(axis=2, keepdims=True); q = g * np.array([1.04, 0.98, 0.86], np.float32)
        h, w = q.shape[:2]
        if p.get('enquadramento', 'faixa') == 'cheio':
            esc = PH / h; q2 = cv2.resize(q, (int(w * esc), PH)); x = (q2.shape[1] - PW) // 2
            out = q2[:, x:x + PW].copy()
        else:
            esc = PW / w; fh = int(h * esc); q2 = cv2.resize(q, (PW, fh), interpolation=cv2.INTER_CUBIC)
            bgh = cv2.resize(q, (int(w * PH / h), PH)); bx = (bgh.shape[1] - PW) // 2
            out = cv2.GaussianBlur(bgh[:, bx:bx + PW], (0, 0), 22) * 0.32
            y0 = int(PH * 0.42 - fh / 2)
            out[y0:y0 + fh] = q2
            out[y0 - 6:y0] = 0; out[y0 + fh:y0 + fh + 6] = 0          # bordas de película
        flick = 1.0 + 0.04 * math.sin(tl * 23.0) * math.sin(tl * 7.0)
        return out * flick
    return {'dyn': dyn, 'zoom': (1.0, 1.05), 'pan': ((0, 0), (0, 0))}


def adaptar_extra(nome):
    """Usa uma cena de cenas_extra.py (V1) como plano de evidência, sem alterá-la."""
    def f(ctx, p):
        import cenas_extra  # noqa: F401  (registra em motor.EXTRA_CENAS)
        import motor
        ext = motor.EXTRA_CENAS[nome](ctx['base'], p, np.random.default_rng(p.get('semente', 4)), {'tela': ''})
        dyn0 = ext['dyn']
        return {'dyn': lambda tl, dur: dyn0(tl), 'zoom': ext.get('zoom', (1.0, 1.05)), 'pan': ((0, 0), (0, 0))}
    return f


def quadro_cinema(ctx, p):
    """Adereços originais do microdrama O Índice Cego, em quatro enquadramentos."""
    modo = p['modo']
    base = mesa(ctx, brilho=0.56 if modo == 'pelicula' else 0.38).convert('RGB')
    luz = Image.new('RGB', base.size)
    d = ImageDraw.Draw(luz)
    cx, cy = PW // 2, int(PH * 0.45)
    bronze, âmbar, cobre, preto = (74, 49, 30), (199, 156, 98), (130, 69, 46), (17, 13, 12)
    d.ellipse((cx - 490, cy - 690, cx + 490, cy + 640), fill=(42, 25, 15))
    base = Image.blend(base, luz.filter(ImageFilter.GaussianBlur(125)), 0.58)
    d = ImageDraw.Draw(base)

    if modo == 'pelicula':
        # A janela principal é cercada pelos dentes da película e dois fotogramas cortados.
        x, y = cx - 340, cy - 334
        d.rounded_rectangle((x - 24, y - 234, x + 704, y + 812), 19, fill=(28, 21, 17), outline=bronze, width=6)
        for yy in range(y - 205, y + 794, 71):
            for xx in (x + 5, x + 630):
                d.rounded_rectangle((xx, yy, xx + 45, yy + 32), 7, fill=bronze, outline=âmbar, width=2)
        for yy in (y - 240, y + 35, y + 593):
            d.rounded_rectangle((x + 80, yy, x + 604, yy + 510), 8, outline=bronze, width=5)
        d.rectangle((x + 84, y + 39, x + 600, y + 540), fill=(93, 61, 37))
        d.polygon([(x + 84, y + 520), (cx - 89, y + 276), (cx + 87, y + 276), (x + 600, y + 520)], fill=(49, 31, 24))
        d.rectangle((cx - 76, y + 96, cx + 76, y + 315), fill=preto, outline=âmbar, width=3)
        d.line((x + 84, y + 565, x + 603, y + 565), fill=cobre, width=4)
        d.text((x + 90, y + 609), p.get('inscricao', '32'), font=fm.fonte('oswald', 56), fill=CREME)
        d.line((x + 593, y + 56, x + 114, y + 501), fill=(178, 111, 61), width=1)
    elif modo == 'porta':
        d.polygon([(cx - 545, cy + 610), (cx - 218, cy - 277), (cx + 218, cy - 277), (cx + 545, cy + 610)], fill=(53, 33, 24))
        d.polygon([(0, cy + 568), (cx - 199, cy + 198), (cx - 199, cy - 275), (20, cy - 549)], fill=(35, 26, 22))
        d.polygon([(PW, cy + 568), (cx + 199, cy + 198), (cx + 199, cy - 275), (PW - 20, cy - 549)], fill=(42, 27, 22))
        for f in (0.2, 0.45, 0.75, 1):
            d.line((cx - int(541 * f), cy + 610, cx - int(198 * f), cy + 198), fill=bronze, width=2)
            d.line((cx + int(541 * f), cy + 610, cx + int(198 * f), cy + 198), fill=bronze, width=2)
        d.rectangle((cx - 172, cy - 278, cx + 172, cy + 270), fill=preto, outline=bronze, width=10)
        d.rectangle((cx - 134, cy - 240, cx + 134, cy + 268), fill=(25, 19, 17), outline=cobre, width=4)
        d.line((cx + 133, cy - 239, cx + 133, cy + 267), fill=âmbar, width=5)
        d.ellipse((cx + 75, cy + 7, cx + 96, cy + 28), fill=âmbar)
    elif modo == 'plateia':
        d.rounded_rectangle((cx - 401, cy - 420, cx + 401, cy + 410), 13, fill=(34, 29, 23), outline=bronze, width=5)
        d.arc((cx - 289, cy - 356, cx + 289, cy - 196), 195, 345, fill=âmbar, width=3)
        d.text((cx, cy - 367), 'CABINE', anchor='mt', font=fm.fonte('oswald', 35), fill=CREME)
        for row in range(4):
            for col in range(7):
                x, y = cx + (col - 3) * 93, cy - 155 + row * 111
                alvo = row == 2 and col == 3
                d.rounded_rectangle((x - 33, y - 33, x + 33, y + 33), 11, fill=(114, 46, 35) if alvo else (57, 43, 33), outline=âmbar if alvo else bronze, width=4)
                if alvo:
                    d.text((x, y), '33', anchor='mm', font=fm.fonte('oswald', 37), fill=CREME)
        d.line((cx, cy - 254, cx, cy + 32), fill=cobre, width=4)
    else:
        # Close da lente apontada para a poltrona, sem representação de câmera histórica.
        for raio, borda, fundo in ((400, bronze, (35, 28, 23)), (325, cobre, (24, 20, 19)),
                                   (255, bronze, (13, 23, 23)), (176, (60, 99, 88), (10, 16, 17))):
            d.ellipse((cx - raio, cy - raio, cx + raio, cy + raio), fill=fundo, outline=borda, width=9)
        d.arc((cx - 223, cy - 223, cx + 223, cy + 223), 195, 291, fill=(76, 123, 107), width=6)
        d.ellipse((cx + 84, cy - 111, cx + 102, cy - 93), fill=(187, 69, 43))
        d.line((cx - 96, cy + 34, cx + 80, cy - 78), fill=(41, 70, 65), width=8)

    arr = _np(base)
    xs = np.arange(PW, dtype=np.float32)[None, :]
    ys = np.arange(PH, dtype=np.float32)[:, None]
    ganho = 0.55 if modo == 'pelicula' else 0.43

    def dyn(tl, dur):
        k = ease(tl / max(dur, 0.01))
        eixo = PW * (0.22 + k * 0.56) + (ys - cy) * 0.12
        brilho = np.exp(-((xs - eixo) / 265) ** 2)
        return arr * (0.88 + ganho * brilho[..., None])

    zoom = (1.19, 1.03) if modo == 'plateia' else (1.02, 1.12)
    return {'dyn': dyn, 'zoom': zoom, 'pan': ((-0.18, -0.07), (0.13, -0.12))}


def lata_cinema(ctx, p):
    """Verso da lata da bobina com a etiqueta da poltrona."""
    base = mesa(ctx, brilho=0.56).convert('RGB')
    d = ImageDraw.Draw(base)
    cx, cy = PW // 2, int(PH * 0.44)
    for raio, borda, fundo in (
        (411, (121, 86, 51), (48, 36, 29)),
        (389, (70, 54, 41), (83, 61, 42)),
        (348, (116, 83, 53), (51, 39, 33)),
    ):
        d.ellipse((cx - raio, cy - raio, cx + raio, cy + raio), fill=fundo, outline=borda, width=8)
    rng = np.random.default_rng(33)
    for _ in range(185):
        a, r = rng.uniform(0, math.tau), rng.uniform(245, 348)
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        d.line((x, y, x + rng.uniform(2, 32), y + 1), fill=(82, 62, 47), width=1)
    d.rounded_rectangle((cx - 193, cy - 91, cx + 194, cy + 92), 7, fill=(162, 134, 91), outline=(207, 170, 110), width=4)
    d.text((cx, cy), p['inscricao'], anchor='mm', font=fm.fonte('anton', 119), fill=(75, 24, 21))
    arr = _np(base)
    return {
        'dyn': lambda tl, dur: feixe(arr, 0.26 + 0.53 * ease(tl / max(0.01, dur)), 290, 0.46),
        'zoom': (1.0, 1.17), 'pan': ((0.09, -0.16), (-0.03, -0.22)),
    }


def bilhete_indice(ctx, p):
    """Adereço ficcional. O papel do Arquivista entra sob um feixe de luz."""
    rng = np.random.default_rng(701)
    fundo = mesa(ctx, brilho=0.47, blur=4).convert('RGBA')
    envelope = papel(850, 548, rng, (125, 91, 60))
    contorno = ImageDraw.Draw(envelope)
    contorno.line([(8, 23), (427, 356), (843, 23)], fill=(69, 45, 32), width=4)
    contorno.line([(7, 535), (318, 263)], fill=(78, 53, 37), width=3)
    contorno.line([(843, 535), (533, 263)], fill=(78, 53, 37), width=3)
    contorno.ellipse((395, 319, 461, 380), fill=(85, 35, 31), outline=(123, 59, 42), width=3)
    colar(fundo, envelope, 148, 530, ang=7)
    bilhete = papel(710, 412, rng, (194, 165, 120))
    tinta = ImageDraw.Draw(bilhete)
    fonte = fm.fonte('elite', 57)
    texto = p['linhas']
    for idx, linha in enumerate(texto):
        tinta.text((355, 206 + (idx - (len(texto) - 1) / 2) * 75), linha,
                   font=fonte, anchor='mm', fill=(65, 34, 26))
    colar(fundo, bilhete, 228, 805, ang=-6)
    arr = _np(fundo)
    return {
        'dyn': lambda tl, dur: feixe(arr, 0.19 + 0.63 * ease(tl / max(0.01, dur)), 305, 0.48),
        'zoom': (1.0, 1.19), 'pan': ((-0.08, -0.08), (0.08, 0.04)),
    }


PLANOS = {'cartas_caem': cartas_caem, 'documento_1995': documento_1995, 'titulo_obra': titulo_obra,
          'arte_original': arte_original, 'lista_oficial': lista_oficial, 'grade_cartas': grade_cartas,
          'leituras': leituras, 'dossie_abre': dossie_abre, 'salto_datas': salto_datas,
          'telas': adaptar_extra('telas'), 'escritorio': adaptar_extra('escritorio'), 'dossies': adaptar_extra('dossies'),
          'terminal': adaptar_extra('terminal'), 'trecho_documento': trecho_documento,
          'pagina_documento': pagina_documento, 'imagem_arquivo': imagem_arquivo, 'video_arquivo': video_arquivo,
          'escritorio_epoca': escritorio_epoca, 'quadro_cinema': quadro_cinema, 'lata_cinema': lata_cinema,
          'bilhete_indice': bilhete_indice}
