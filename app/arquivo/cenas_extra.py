"""Cenas animadas extras do Arquivo Oculto (todas desenhadas por código, sem imagem de terceiros).

Cada função recebe (base, v, rng, cena) e devolve {'plate': PIL (primeiro quadro), 'dyn': f(t_local) -> np.float32 RGB, 'zoom': (z0, z1)}.
São ILUSTRAÇÕES: nunca representam documento, foto ou carta real. O selo na tela deve dizer ILUSTRAÇÃO.
"""
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

import motor
from motor import W, H, fonte, OURO, OURO_CLARO, CREME, VERMELHO, REGIOES

PW, PH = int(W * 1.08), int(H * 1.08)


def _np(img):
    return np.asarray(img.convert('RGB'), np.float32)


def _fundo(base, alvo='tudo', brilho=0.28, blur=10):
    p = base.recorte(REGIOES[alvo], 1.08).filter(ImageFilter.GaussianBlur(blur))
    return ImageEnhance.Brightness(p).enhance(brilho).resize((PW, PH))


def _texto(d, cx, y, t, f, cor):
    w = f.getlength(t)
    d.text((cx - w / 2, y), t, font=f, fill=cor)


# ---------------------------------------------------------------- cartas genéricas sobre a mesa
def _carta(rng, simbolo, w=300, h=440):
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 18, fill=(22, 18, 16, 255), outline=OURO + (255,), width=6)
    d.rounded_rectangle((16, 16, w - 17, h - 17), 12, outline=(120, 92, 44, 255), width=2)
    cx, cy = w / 2, h / 2
    r = 70
    if simbolo == 0:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=OURO_CLARO + (255,), width=6)
        d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=OURO_CLARO + (255,))
    elif simbolo == 1:
        d.polygon([(cx, cy - r), (cx + r, cy + r * 0.8), (cx - r, cy + r * 0.8)], outline=OURO_CLARO + (255,), width=6)
    elif simbolo == 2:
        for k in range(8):
            a = k * math.pi / 4
            d.line((cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)), fill=OURO_CLARO + (255,), width=5)
    elif simbolo == 3:
        d.rectangle((cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7), outline=OURO_CLARO + (255,), width=6)
        d.line((cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7), fill=OURO_CLARO + (255,), width=4)
    else:
        d.arc((cx - r, cy - r, cx + r, cy + r), 200, 340, fill=OURO_CLARO + (255,), width=6)
        d.ellipse((cx - 10, cy + 10, cx + 10, cy + 30), fill=OURO_CLARO + (255,))
    # textura
    a = np.asarray(c, np.float32)
    a[..., :3] += rng.normal(0, 5, a[..., :3].shape)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def cena_cartas(base, v, rng, c):
    mesa = base.recorte(REGIOES['mesa'], 1.08).resize((PW, PH))
    mesa = ImageEnhance.Brightness(mesa).enhance(0.55)
    bg = _np(mesa)
    n = int(v.get('n', 7))
    cartas = []
    for i in range(n):
        im = _carta(rng, i % 5).rotate(rng.uniform(-28, 28), expand=True, resample=Image.BICUBIC)
        x = PW * 0.5 + rng.uniform(-330, 330) - im.width / 2
        y = PH * 0.48 + rng.uniform(-520, 420) - im.height / 2
        cartas.append((np.asarray(im, np.float32), x, y, 0.25 + i * 0.32))
    luz = np.zeros((PH, PW, 1), np.float32)
    yy, xx = np.mgrid[0:PH, 0:PW]

    def dyn(t):
        out = bg.copy()
        for arr, x, y, t0 in cartas:
            k = min(1.0, max(0.0, (t - t0) / 0.35))
            if k <= 0: continue
            k = 1 - (1 - k) ** 3
            dx = int(x + (1 - k) * -420); dy = int(y + (1 - k) * 180)
            h, w = arr.shape[:2]
            x0, y0 = max(0, dx), max(0, dy); x1, y1 = min(PW, dx + w), min(PH, dy + h)
            if x1 <= x0 or y1 <= y0: continue
            sub = arr[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
            al = sub[..., 3:4] / 255.0 * k
            # sombra
            sy0, sy1 = min(PH, y0 + 18), min(PH, y1 + 18)
            out[sy0:sy1, x0:x1] *= (1 - 0.45 * al[:sy1 - sy0])
            out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - al) + sub[..., :3] * al
        # feixe de luz que passa
        cx = PW * (0.2 + 0.6 * (0.5 + 0.5 * math.sin(t * 0.7)))
        g = np.exp(-((xx - cx) ** 2) / (2 * 260 ** 2))[..., None].astype(np.float32)
        return out * (0.75 + 0.45 * g)
    return {'plate': Image.fromarray(np.clip(dyn(5), 0, 255).astype(np.uint8)), 'dyn': dyn, 'zoom': (1.08, 1.0)}


# ---------------------------------------------------------------- dossiês carimbados
def cena_dossies(base, v, rng, c):
    bg = _np(_fundo(base, 'maos', 0.35, 6))
    rot = v.get('rotulos', ['POLÍTICA', 'PODER', 'CRISES'])
    pastas = []
    fa = fonte('anton', 86); fe = fonte('elite', 40)
    for i, r in enumerate(rot):
        p = Image.new('RGBA', (820, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(p)
        cor = [(92, 70, 40), (78, 58, 34), (104, 80, 46)][i % 3]
        d.rounded_rectangle((0, 40, 819, 559), 14, fill=cor + (255,))
        d.rounded_rectangle((40, 0, 330, 70), 12, fill=cor + (255,))
        d.text((70, 12), f'DOSSIÊ {i + 1:02d}', font=fe, fill=(30, 22, 14, 255))
        tw = fa.getlength(r)
        d.rounded_rectangle((410 - tw / 2 - 30, 230, 410 + tw / 2 + 30, 360), 10, outline=VERMELHO + (230,), width=8)
        d.text((410 - tw / 2, 238), r, font=fa, fill=VERMELHO + (230,))
        a = np.asarray(p, np.float32); a[..., :3] += rng.normal(0, 7, a[..., :3].shape)
        pastas.append(np.clip(a, 0, 255))
    n = len(pastas)

    def dyn(t):
        out = bg.copy()
        dur = max(0.6, float(v.get('dur', 4.0)))
        for i, arr in enumerate(pastas):
            t0 = i * dur / n
            k = min(1.0, max(0.0, (t - t0) / 0.45)); k = 1 - (1 - k) ** 3
            if k <= 0: continue
            h, w = arr.shape[:2]
            dx = int((PW - w) / 2 + (1 - k) * PW * 0.9 + (i - 1) * 40); dy = int(PH * 0.30 + i * 150)
            x0, x1 = max(0, dx), min(PW, dx + w); y0, y1 = max(0, dy), min(PH, dy + h)
            if x1 <= x0: continue
            sub = arr[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
            al = sub[..., 3:4] / 255.0
            out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - al) + sub[..., :3] * al
        return out
    return {'plate': Image.fromarray(np.clip(dyn(9), 0, 255).astype(np.uint8)), 'dyn': dyn, 'zoom': (1.0, 1.06)}


# ---------------------------------------------------------------- parede de monitores
def cena_telas(base, v, rng, c):
    bg = np.zeros((PH, PW, 3), np.float32) + np.array([10, 8, 7], np.float32)
    cols, rows = 3, 4
    mw, mh = 300, 250
    gx, gy = (PW - cols * mw) // (cols + 1), 120
    pos = [(gx + i * (mw + gx), 330 + j * (mh + 70)) for j in range(rows) for i in range(cols)]
    pontos = rng.uniform(0, 1, (220, 2))
    anos = v.get('anos', [1994, 2026])
    fa = fonte('anton', 96); fs = fonte('oswald', 30)
    base_img = Image.new('RGB', (PW, PH), (10, 8, 7)); d = ImageDraw.Draw(base_img)
    for (x, y) in pos:
        d.rounded_rectangle((x - 16, y - 16, x + mw + 16, y + mh + 16), 22, fill=(46, 40, 34))
        d.rounded_rectangle((x, y, x + mw, y + mh), 30, fill=(4, 10, 8))
    bg = _np(base_img)
    scan = (0.82 + 0.18 * (np.arange(PH) % 4 < 2))[:, None, None].astype(np.float32)

    def dyn(t):
        img = Image.fromarray(bg.astype(np.uint8)); d = ImageDraw.Draw(img)
        ano = int(anos[0] + (anos[1] - anos[0]) * min(1, max(0, (t - 0.15) / 1.3)))
        for k, (x, y) in enumerate(pos):
            on = (t * 3 + k * 0.37) % 1.0 > 0.04
            if not on: continue
            cor = (70, 200, 140) if k % 3 else (220, 170, 70)
            if k % 4 == 1:
                tw = fa.getlength(str(ano)); d.text((x + mw / 2 - tw / 2, y + 60), str(ano), font=fa, fill=cor)
            elif k % 4 == 2:
                for i in range(0, mw, 6):
                    yy = y + mh / 2 + 50 * math.sin(i * 0.05 + t * 4 + k) * math.sin(t + k)
                    d.point((x + i, yy), fill=cor)
                    d.point((x + i, yy + 1), fill=cor)
            else:
                for (px, py) in pontos[k * 15:(k * 15) + 60]:
                    if (px * 7 + t * 0.4 + k) % 1 < 0.7:
                        d.ellipse((x + 20 + px * (mw - 40) - 2, y + 20 + py * (mh - 40) - 2, x + 22 + px * (mw - 40), y + 22 + py * (mh - 40)), fill=cor)
            d.text((x + 14, y + mh - 42), f'ARQ {k + 1:02d}', font=fs, fill=(cor[0] // 2, cor[1] // 2, cor[2] // 2))
        a = np.asarray(img, np.float32) * scan
        glow = cv2.GaussianBlur(a, (0, 0), 14)
        return a + glow * 0.5
    return {'plate': Image.fromarray(np.clip(dyn(3), 0, 255).astype(np.uint8)), 'dyn': dyn, 'zoom': (1.02, 1.1)}


# ---------------------------------------------------------------- escritório de 1990 à noite, lanterna
def cena_escritorio(base, v, rng, c):
    img = Image.new('RGB', (PW, PH), (12, 10, 9)); d = ImageDraw.Draw(img)
    d.rectangle((0, int(PH * 0.62), PW, PH), fill=(24, 19, 15))           # piso
    d.rectangle((0, int(PH * 0.50), PW, int(PH * 0.62)), fill=(34, 27, 21))  # mesas
    for i, x in enumerate([60, 420, 780]):
        y = int(PH * 0.36)
        d.rounded_rectangle((x, y, x + 300, y + 250), 14, fill=(150, 138, 112))      # monitor bege
        d.rounded_rectangle((x + 28, y + 26, x + 272, y + 200), 18, fill=(20, 26, 22))
        d.rectangle((x + 110, y + 250, x + 190, y + 290), fill=(120, 110, 90))
        d.rectangle((x - 10, y + 290, x + 310, y + 330), fill=(130, 120, 98))        # gabinete
        for k in range(3):
            d.rectangle((x + 20 + k * 60, int(PH * 0.555), x + 70 + k * 60, int(PH * 0.585)), fill=(40, 40, 46))  # disquetes
    for i in range(5):
        x = 80 + i * 210; y = int(PH * 0.66) + (i % 2) * 90
        d.rectangle((x, y, x + 180, y + 140), fill=(70, 54, 36)); d.line((x, y + 40, x + 180, y + 40), fill=(50, 38, 26), width=4)
    bg = _np(img.filter(ImageFilter.GaussianBlur(1.5)))
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)

    def dyn(t):
        cx = PW * (0.15 + 0.7 * (0.5 + 0.5 * math.sin(t * 0.9 - 1)))
        cy = PH * 0.45 + 120 * math.sin(t * 1.3)
        # cone da lanterna vindo do canto superior esquerdo
        ang = np.arctan2(yy - (-200), xx - (-100)); ang0 = math.atan2(cy + 200, cx + 100)
        cone = np.exp(-((ang - ang0) ** 2) / (2 * 0.06 ** 2))
        spot = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * 230 ** 2)))
        luz = (0.12 + 1.6 * spot + 0.35 * cone)[..., None].astype(np.float32)
        out = bg * luz + np.array([40, 30, 14], np.float32) * (0.35 * cone)[..., None]
        return out
    return {'plate': Image.fromarray(np.clip(dyn(1), 0, 255).astype(np.uint8)), 'dyn': dyn, 'zoom': (1.0, 1.07)}


# ---------------------------------------------------------------- terminal verde de BBS
def cena_terminal(base, v, rng, c):
    linhas = v.get('linhas', ['ATDT 555-0190', 'CONNECT 2400', '', 'BBS · AUSTIN, TEXAS', 'USUARIOS ONLINE: 3', '', '> ARQUIVOS', '> MENSAGENS', '> SAIR', '', 'CARREGANDO_'])
    f = fonte('elite', 50)
    bg = np.zeros((PH, PW, 3), np.float32) + np.array([4, 12, 7], np.float32)
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    vin = np.clip(1.15 - (((xx - PW / 2) / (PW * 0.6)) ** 2 + ((yy - PH / 2) / (PH * 0.55)) ** 2), 0, 1)[..., None]
    scan = (0.75 + 0.25 * (np.arange(PH) % 4 < 2))[:, None, None].astype(np.float32)
    total = sum(len(l) for l in linhas)
    vel = float(v.get('cps', 28))

    def dyn(t):
        img = Image.new('RGB', (PW, PH), (0, 0, 0)); d = ImageDraw.Draw(img)
        n = int(t * vel); y = 380
        for l in linhas:
            s = l[:max(0, n)]; n -= len(l)
            d.text((120, y), s, font=f, fill=(90, 255, 150))
            y += 74
            if n < 0: break
        if int(t * 2) % 2 == 0:
            d.rectangle((120 + f.getlength(s), y - 74, 150 + f.getlength(s), y - 22), fill=(90, 255, 150))
        a = np.asarray(img, np.float32)
        glow = cv2.GaussianBlur(a, (0, 0), 6)
        return (bg + a * 0.9 + glow * 0.8) * scan * vin
    return {'plate': Image.fromarray(np.clip(dyn(9), 0, 255).astype(np.uint8)), 'dyn': dyn, 'zoom': (1.0, 1.05)}


# ---------------------------------------------------------------- relógio
def cena_relogio(base, v, rng, c):
    bg = _np(_fundo(base, 'ampulheta', 0.32, 7))
    cx, cy, R = PW / 2, PH * 0.46, 380
    face = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(face)
    d.ellipse((cx - R - 30, cy - R - 30, cx + R + 30, cy + R + 30), fill=(70, 54, 26, 255))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(226, 214, 186, 255))
    fr = fonte('cinzel', 70)
    nums = ['XII', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']
    for i, nlab in enumerate(nums):
        a = i * math.pi / 6 - math.pi / 2
        x, y = cx + (R - 80) * math.cos(a), cy + (R - 80) * math.sin(a)
        w = fr.getlength(nlab); d.text((x - w / 2, y - 40), nlab, font=fr, fill=(40, 30, 20, 255))
    for i in range(60):
        a = i * math.pi / 30
        r0 = R - (30 if i % 5 == 0 else 16)
        d.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + (R - 6) * math.cos(a), cy + (R - 6) * math.sin(a)), fill=(40, 30, 20, 255), width=4 if i % 5 == 0 else 2)
    fa = np.asarray(face, np.float32)
    al = fa[..., 3:4] / 255.0
    base_np = bg * (1 - al) + fa[..., :3] * al

    def dyn(t):
        img = Image.fromarray(np.clip(base_np, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
        seg = int(t * 1.0)  # tique por segundo
        for ang, L, wdt, cor in [((11 + t / 3600) / 12 * 2 * math.pi, R * 0.5, 14, (30, 22, 14)),
                                 ((58 + t / 60) / 60 * 2 * math.pi, R * 0.75, 10, (30, 22, 14)),
                                 ((seg % 60) / 60 * 2 * math.pi, R * 0.85, 4, VERMELHO)]:
            a = ang - math.pi / 2
            d.line((cx, cy, cx + L * math.cos(a), cy + L * math.sin(a)), fill=cor, width=wdt)
        d.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=(60, 44, 20))
        return np.asarray(img, np.float32)
    return {'plate': Image.fromarray(np.clip(dyn(0), 0, 255).astype(np.uint8)), 'dyn': dyn, 'zoom': (1.0, 1.15)}


# ---------------------------------------------------------------- linha do tempo animada (o salto entre datas)
def cena_salto(base, v, rng, c):
    bg = _np(_fundo(base, 'gavetas', 0.25, 8))
    a0, a1 = v.get('de', '1990'), v.get('ate', '1994')
    r0, r1 = v.get('rot_de', 'A BUSCA'), v.get('rot_ate', 'AS CARTAS')
    fa = fonte('anton', 150); fs = fonte('oswald', 44); fg = fonte('oswald', 52)
    y = PH * 0.50; x0, x1 = PW * 0.22, PW * 0.78

    def dyn(t):
        img = Image.fromarray(bg.astype(np.uint8)); d = ImageDraw.Draw(img)
        k = min(1.0, max(0.0, (t - 0.5) / 1.8)); k = 1 - (1 - k) ** 2
        xm = x0 + (x1 - x0) * k
        d.line((x0, y, x1, y), fill=(80, 64, 36), width=6)
        d.line((x0, y, xm, y), fill=VERMELHO, width=10)
        for (x, ano, rot, on) in [(x0, a0, r0, True), (x1, a1, r1, k >= 1)]:
            col = OURO_CLARO if on else (90, 76, 50)
            d.ellipse((x - 24, y - 24, x + 24, y + 24), fill=(20, 14, 8), outline=col, width=7)
            _texto(d, x, y - 230, ano, fa, col)
            _texto(d, x, y + 50, rot, fs, CREME if on else (110, 100, 80))
        if k >= 1:
            gap = v.get('gap', '4 ANOS E 9 MESES')
            _texto(d, PW / 2, y + 170, gap, fg, VERMELHO)
        return np.asarray(img, np.float32)
    return {'plate': Image.fromarray(np.clip(dyn(5), 0, 255).astype(np.uint8)), 'dyn': dyn, 'zoom': (1.0, 1.04)}


# ---------------------------------------------------------------- tipografia cinética
def cena_tipo(base, v, rng, c):
    bg = _np(_fundo(base, v.get('fundo', 'livros'), 0.22, 9))
    linhas = v.get('linhas', [c.get('tela', '')])
    fa = fonte('anton', int(v.get('tam', 130))); fs = fonte('oswald', 48)
    sub = v.get('sub', '')

    def dyn(t):
        img = Image.fromarray(bg.astype(np.uint8)).convert('RGBA')
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        y = PH * 0.40 - len(linhas) * fa.size * 0.6
        for i, l in enumerate(linhas):
            k = min(1.0, max(0.0, (t - 0.25 - i * 0.45) / 0.35))
            if k <= 0: continue
            al = int(255 * k)
            off = (1 - k) * 60
            w = fa.getlength(l)
            d.text((PW / 2 - w / 2, y + i * fa.size * 1.15 + off), l, font=fa, fill=OURO_CLARO + (al,), stroke_width=3, stroke_fill=(20, 12, 4, al))
        if sub and t > 0.25 + len(linhas) * 0.45:
            for j, sl in enumerate(motor.quebrar(sub, fs, PW - 220)):
                w = fs.getlength(sl); d.text((PW / 2 - w / 2, y + len(linhas) * fa.size * 1.15 + 30 + j * 62), sl, font=fs, fill=CREME + (230,))
        img.alpha_composite(lay)
        return np.asarray(img.convert('RGB'), np.float32)
    return {'plate': Image.fromarray(np.clip(dyn(9), 0, 255).astype(np.uint8)), 'dyn': dyn, 'zoom': (1.0, 1.05)}


motor.EXTRA_CENAS.update({'cartas': cena_cartas, 'dossies': cena_dossies, 'telas': cena_telas, 'escritorio': cena_escritorio,
                          'terminal': cena_terminal, 'relogio': cena_relogio, 'salto': cena_salto, 'tipo': cena_tipo})
