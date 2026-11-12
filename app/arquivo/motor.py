#!/usr/bin/env python3
"""Motor Arquivo Oculto — gera um Reel vertical 1080x1920 do Arquivista a partir de um episódio em JSON.

Uso: python3 motor.py episodios.json NUM saida.mp4 [--capa capa.jpg]
Depende de: ffmpeg, pillow, numpy, kokoro-onnx (+ kokoro-v1.0.int8.onnx e voices-v1.0.bin em TTS_DIR).
"""
import json, math, os, random, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

AQUI = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get('AO_FONTS', os.path.join(AQUI, 'fonts'))
TTS_DIR = os.environ.get('AO_TTS', os.path.join(AQUI, 'tts'))
ARQ_IMG = os.environ.get('AO_ARQ', os.path.join(AQUI, 'assets', 'arquivista.png'))
W, H, FPS = 1080, 1920, 30
SR = 24000
OURO = (214, 168, 84)
OURO_CLARO = (238, 205, 140)
CREME = (241, 233, 214)
VERMELHO = (178, 42, 38)
VOZ = os.environ.get('AO_VOZ', 'pm_alex')


def fonte(nome, tam):
    mapa = {
        'anton': 'anton-latin-400-normal.woff', 'oswald': 'oswald-latin-700-normal.woff',
        'oswald4': 'oswald-latin-400-normal.woff', 'elite': 'special-elite-latin-400-normal.woff',
        'cinzel': 'cinzel-latin-700-normal.woff'}
    return ImageFont.truetype(os.path.join(FONT_DIR, mapa[nome]), tam)


# ------------------------------------------------------------------ áudio
def tts(cenas):
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(TTS_DIR, 'kokoro-v1.0.int8.onnx'), os.path.join(TTS_DIR, 'voices-v1.0.bin'))
    import hashlib
    cache = os.environ.get('AO_CACHE', os.path.join(os.path.expanduser('~'), '.cache', 'arquivo_oculto', 'tts'))
    os.makedirs(cache, exist_ok=True)
    out = []
    for c in cenas:
        txt = c.get('tts') or c['fala']
        key = hashlib.sha1(f"{VOZ}|{os.environ.get('AO_VEL', '1.0')}|{txt}".encode()).hexdigest()[:20]
        cp = os.path.join(cache, key + '.npy')
        if os.path.exists(cp):
            out.append(np.load(cp)); continue
        s, sr = k.create(c.get('tts') or c['fala'], voice=VOZ, speed=float(os.environ.get('AO_VEL', '1.0')), lang='pt-br')
        assert sr == SR
        # corta silêncio das pontas
        a = np.abs(s); idx = np.where(a > 0.01)[0]
        if len(idx):
            s = s[max(0, idx[0] - 600): idx[-1] + 1200]
        s = np.nan_to_num(s.astype(np.float32)); np.save(cp, s)
        out.append(s)
    return out


def escrever_wav(path, x, sr=SR):
    x = np.clip(x, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def trilha(dur, cortes, fim_fala):
    """Drone grave + pulso + impactos nos cortes + sting final. Tudo sintetizado aqui (sem direitos de terceiros)."""
    n = int(dur * SR); t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)
    drone = (0.5 * np.sin(2 * np.pi * 55 * t) + 0.3 * np.sin(2 * np.pi * 82.4 * t + 1) + 0.18 * np.sin(2 * np.pi * 110.3 * t)
             + 0.08 * np.sin(2 * np.pi * 164.8 * t * (1 + 0.002 * np.sin(2 * np.pi * 0.3 * t)))) * lfo
    ruido = rng.standard_normal(n)
    # ruído escuro (passa-baixa simples)
    k = np.exp(-np.arange(400) / 80.0); k /= k.sum()
    ruido = np.convolve(ruido, k, mode='same') * 0.6
    mus = 0.16 * drone + 0.05 * ruido
    # pulso de coração, 62 bpm, bem baixo
    bat = np.zeros(n)
    per = 60 / 62
    for b0 in np.arange(0.4, dur, per):
        for off, g in ((0, 1.0), (0.18, 0.6)):
            i0 = int((b0 + off) * SR); m = int(0.16 * SR)
            if i0 + m < n:
                tt = np.arange(m) / SR
                bat[i0:i0 + m] += g * np.sin(2 * np.pi * 48 * tt) * np.exp(-tt * 28)
    mus += 0.22 * bat
    # impactos nos cortes
    for c in cortes:
        i0 = int(c * SR); m = int(1.2 * SR)
        if i0 + m >= n: m = n - i0 - 1
        if m <= 0: continue
        tt = np.arange(m) / SR
        f = 70 * np.exp(-tt * 3) + 32
        boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2)
        hit = rng.standard_normal(m) * np.exp(-tt * 40) * 0.35
        mus[i0:i0 + m] += 0.55 * boom + hit
    # sobe tensão antes da pergunta final e sting no fim
    i_s = int(fim_fala * SR)
    if i_s < n:
        m = n - i_s; tt = np.arange(m) / SR
        sting = (np.sin(2 * np.pi * 41.2 * tt) + 0.5 * np.sin(2 * np.pi * 61.7 * tt) + 0.25 * np.sin(2 * np.pi * 329.6 * tt) * np.exp(-tt * 1.5)) * np.exp(-tt * 0.9)
        mus[i_s:] += 0.5 * sting
    # fade
    fi = int(0.05 * SR); fo = int(0.6 * SR)
    mus[:fi] *= np.linspace(0, 1, fi); mus[-fo:] *= np.linspace(1, 0, fo)
    return mus.astype(np.float32)


def rms_envelope(x, dur):
    nf = int(math.ceil(dur * FPS)); env = np.zeros(nf)
    hop = SR // FPS
    for i in range(nf):
        seg = x[i * hop:(i + 1) * hop]
        env[i] = np.sqrt(np.mean(seg ** 2)) if len(seg) else 0
    if env.max() > 0: env = env / np.percentile(env[env > 0], 95)
    env = np.clip(env, 0, 1)
    # suaviza
    out = np.copy(env)
    for i in range(1, nf): out[i] = max(env[i], out[i - 1] * 0.8)
    return out


# ------------------------------------------------------------------ imagem base
def mascara_marfim(im):
    """Look canônico (arquivista-classico-v1): máscara de porcelana marfim/branca, mantendo sombras e rachaduras."""
    import cv2, json
    p = os.path.join(os.path.dirname(ARQ_IMG), 'arq_lmk106.json')
    if not os.path.exists(p):
        return im
    lm = np.array(json.load(open(p)), np.float32)
    a = np.asarray(im, np.float32)
    h, w = a.shape[:2]
    cont = lm[0:33]
    cx = lm[:, 0].mean()
    topo = lm[:, 1].min()
    # testa: espelha o contorno para cima até a borda do capuz
    alto = np.array([[x, topo - (cont[:, 1].max() - y) * 0.55] for x, y in cont[::2]], np.float32)
    hull = cv2.convexHull(np.vstack([cont, alto]).astype(np.int32))
    m = np.zeros((h, w), np.float32)
    cv2.fillConvexPoly(m, hull, 1.0)
    # só onde é máscara (claro), não a sombra do capuz
    lum = a.mean(axis=2)
    m *= np.clip((lum - 35) / 50, 0, 1)
    m = cv2.GaussianBlur(m, (0, 0), 4)[..., None]
    L = (lum / max(1.0, np.percentile(lum[m[..., 0] > 0.5], 97)))[..., None]
    marfim = np.array([246, 240, 226], np.float32) * np.clip(L, 0, 1.05) ** 0.85
    out = a * (1 - m) + marfim * m
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


class Base:
    def __init__(self):
        im = Image.open(ARQ_IMG).convert('RGB')
        self.src = im
        self.sw, self.sh = im.size
        if os.environ.get('AO_MASCARA', 'marfim') == 'marfim':
            im = mascara_marfim(im)
        g = ImageEnhance.Contrast(im).enhance(1.12)
        g = ImageEnhance.Brightness(g).enhance(0.92)
        self.grad = g
        self.desfocado = g.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
        self.desfocado = ImageEnhance.Brightness(self.desfocado).enhance(0.35)

    def recorte(self, box, escala=1.12):
        """recorta box (x0,y0,x1,y1) do original e devolve placa 9:16 maior que a tela (para movimento)."""
        x0, y0, x1, y1 = box
        bw, bh = x1 - x0, y1 - y0
        alvo = 9 / 16
        if bw / bh > alvo:
            nw = bh * alvo; cx = (x0 + x1) / 2; x0, x1 = cx - nw / 2, cx + nw / 2
        else:
            nh = bw / alvo; cy = (y0 + y1) / 2; y0, y1 = cy - nh / 2, cy + nh / 2
        x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(self.sw, x1), min(self.sh, y1)
        pw, ph = int(W * escala), int(H * escala)
        c = self.grad.crop((int(x0), int(y0), int(x1), int(y1))).resize((pw, ph), Image.LANCZOS)
        if (x1 - x0) < 600:
            c = c.filter(ImageFilter.UnsharpMask(radius=3, percent=90, threshold=2))
        return c


REGIOES = {
    'tudo': (0, 0, 941, 1672), 'close': (215, 170, 725, 1077), 'mascara': (300, 250, 640, 855),
    'mesa': (120, 1180, 941, 1672), 'ampulheta': (700, 1000, 941, 1480), 'globo': (0, 700, 300, 1250),
    'maos': (250, 520, 760, 1300), 'gavetas': (0, 120, 330, 760), 'lanterna': (40, 0, 330, 420), 'livros': (0, 1080, 380, 1520)
}
# olhos na imagem original (para o brilho que acompanha a voz)
OLHOS = [(426, 433), (531, 431)]
ALPHA_IMG = os.environ.get('AO_ALPHA', os.path.join(os.path.dirname(ARQ_IMG), 'arq_alpha.png'))


class Animador:
    """Dá vida ao Arquivista parado: figura recortada sobre o cenário, cabeça que balança e acena com a voz,
    boca da máscara que abre com a fala, respiração, luz de lanterna tremendo e poeira no ar."""
    def __init__(self, base):
        import cv2
        self.cv2 = cv2
        src = np.asarray(base.grad, np.float32)
        h, w = src.shape[:2]
        a = cv2.imread(ALPHA_IMG, 0)
        a = cv2.resize(a, (w, h)).astype(np.float32) / 255.0
        a = cv2.GaussianBlur(np.clip((a - 0.35) / 0.3, 0, 1), (0, 0), 2.0)
        self.h, self.w = h, w
        self.fig = np.dstack([src, a[..., None] * 255]).astype(np.float32)
        # cenário sem a figura (preenche o buraco), mais escuro e suave
        small = cv2.resize(src.astype(np.uint8), (w // 3, h // 3))
        msk = (cv2.resize(a, (w // 3, h // 3)) > 0.15).astype(np.uint8) * 255
        msk = cv2.dilate(msk, np.ones((9, 9), np.uint8))
        bg = cv2.inpaint(small, msk, 7, cv2.INPAINT_TELEA)
        bg = cv2.GaussianBlur(cv2.resize(bg, (w, h)), (0, 0), 3)
        self.bg = bg.astype(np.float32) * 0.85
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        self.xx, self.yy = xx, yy
        g = lambda cx, cy, rx, ry: np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))
        self.w_head = g(470, 440, 250, 280)
        self.px, self.py = 472.0, 700.0
        self.w_jaw = g(476, 560, 38, 22) * (yy > 551)
        self.w_torso = g(470, 1050, 420, 420) * (yy > 640)
        self.w_lant = g(135, 120, 90, 120) * 1.0 + g(470, 150, 140, 110) * 0.7
        rng = np.random.default_rng(11)
        self.p = rng.uniform([0, 0, 0.6, 0], [w, h * 0.8, 2.4, 6.28], (70, 4))

    def cenario(self, t, w=None, h=None):
        """Só o cenário (sem a figura), com luz tremendo e poeira, já no tamanho pedido."""
        cv2 = self.cv2
        if w and not hasattr(self, '_bgW'):
            self._bgW = cv2.resize(self.bg, (w, h)); self._lW = cv2.resize(self.w_lant, (w, h))
        bg, wl = (self._bgW, self._lW) if w else (self.bg, self.w_lant)
        fl = 0.75 + 0.25 * math.sin(t * 7.3) * math.sin(t * 2.9 + 1)
        out = bg + wl[..., None] * np.array([60, 35, 10], np.float32) * fl
        sx = (w or self.w) / self.w; sy = (h or self.h) / self.h
        for (x, y, r, ph) in self.p:
            yy = (y - t * 14 * r) % (self.h * 0.85); xx = x + 18 * math.sin(t * 0.6 + ph)
            xi, yi = int(xx * sx), int(yy * sy)
            if 3 <= xi < out.shape[1] - 3 and 3 <= yi < out.shape[0] - 3:
                out[yi - 1:yi + 2, xi - 1:xi + 2] += np.array([90, 70, 40], np.float32) * (0.4 + 0.6 * math.sin(t * 2 + ph) ** 2)
        return out

    def quadro(self, t, e):
        cv2 = self.cv2
        e = float(e) if np.isfinite(e) else 0.0
        ang = math.radians(1.1 * math.sin(2 * math.pi * t / 5.7) + 0.5 * math.sin(2 * math.pi * t / 2.3) * e)
        nod = 4.0 * e
        dx = self.xx - self.px; dy = self.yy - self.py
        rx = dx * math.cos(ang) - dy * math.sin(ang) - dx
        ry = dx * math.sin(ang) + dy * math.cos(ang) - dy
        br = math.sin(2 * math.pi * t / 4.2)
        mx = self.xx - self.w_head * rx
        my = self.yy - self.w_head * (ry + nod) - self.w_jaw * (9.0 * e) + self.w_torso * (self.yy - 1500) * 0.006 * br
        fig = cv2.remap(self.fig, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        al = fig[..., 3:4] / 255.0
        fl = 0.75 + 0.25 * math.sin(t * 7.3) * math.sin(t * 2.9 + 1)
        bg = self.bg + self.w_lant[..., None] * np.array([60, 35, 10], np.float32) * fl
        out = bg * (1 - al) + fig[..., :3] * al
        # poeira em suspensão
        for (x, y, r, ph) in self.p:
            yy = (y - t * 14 * r) % (self.h * 0.85); xx = x + 18 * math.sin(t * 0.6 + ph)
            xi, yi = int(xx), int(yy)
            if 3 <= xi < self.w - 3 and 3 <= yi < self.h - 3:
                out[yi - 1:yi + 2, xi - 1:xi + 2] += np.array([90, 70, 40], np.float32) * (0.4 + 0.6 * math.sin(t * 2 + ph) ** 2)
        return out



def vinheta():
    y, x = np.ogrid[:H, :W]
    d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H * 0.47) / (H * 0.62)) ** 2)
    v = np.clip(1.05 - d ** 2 * 0.75, 0.22, 1.0)
    return v[..., None].astype(np.float32)


def graos(n=6):
    rng = np.random.default_rng(3)
    out = []
    for _ in range(n):
        g = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
        g = np.kron(g, np.ones((2, 2), np.float32))
        out.append(g[..., None] * 6.0)
    return out


def poeira(rng):
    lay = Image.new('L', (W, H), 0); d = ImageDraw.Draw(lay)
    for _ in range(rng.integers(2, 6)):
        x, y = rng.integers(0, W), rng.integers(0, H); r = rng.integers(1, 3)
        d.ellipse((x - r, y - r, x + r, y + r), fill=int(rng.integers(60, 140)))
    if rng.random() < 0.3:
        x = rng.integers(0, W); d.line((x, 0, x + rng.integers(-20, 20), H), fill=40, width=1)
    return np.asarray(lay, np.float32)[..., None]


# ------------------------------------------------------------------ texto
def quebrar(txt, f, larg):
    pal = txt.split(); linhas = []; cur = ''
    for p in pal:
        t = (cur + ' ' + p).strip()
        if f.getlength(t) <= larg: cur = t
        else:
            if cur: linhas.append(cur)
            cur = p
    if cur: linhas.append(cur)
    return linhas


def texto_centro(d, cx, y, txt, f, cor, sombra=True, stroke=0, stroke_cor=(0, 0, 0)):
    w = f.getlength(txt)
    if sombra:
        d.text((cx - w / 2 + 3, y + 4), txt, font=f, fill=(0, 0, 0, 170))
    d.text((cx - w / 2, y), txt, font=f, fill=cor, stroke_width=stroke, stroke_fill=stroke_cor)


def camada_titulo(txt, y=250):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    tam = 118
    while True:
        f = fonte('anton', tam); ls = quebrar(txt, f, W - 140)
        if len(ls) <= 2 or tam < 70: break
        tam -= 8
    alt = tam * 1.12
    for i, l in enumerate(ls):
        texto_centro(d, W / 2, y + i * alt, l, f, OURO_CLARO, stroke=3, stroke_cor=(20, 12, 4))
    # filete abaixo da última linha
    bb = d.textbbox((0, y + (len(ls) - 1) * alt), ls[-1], font=f)
    yb = bb[3] + 26
    d.line((W / 2 - 70, yb, W / 2 + 70, yb), fill=OURO + (220,), width=4)
    return lay


def camada_selo(txt):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = fonte('oswald', 34)
    cor = {'DOCUMENTADO': (46, 140, 88), 'ILUSTRAÇÃO': (150, 120, 60), 'RECONSTITUIÇÃO IA': (150, 120, 60)}.get(txt, (120, 120, 120))
    w = f.getlength(txt)
    x, y = 56, 120
    d.rounded_rectangle((x, y, x + w + 40, y + 58), 8, fill=(10, 8, 6, 200), outline=cor + (255,), width=3)
    d.text((x + 20, y + 6), txt, font=f, fill=cor + (255,) if txt == 'DOCUMENTADO' else CREME + (255,))
    return lay


def camada_marca(num):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = fonte('cinzel', 30)
    t = f'ARQUIVO OCULTO · Nº {num:02d}'
    w = f.getlength(t)
    d.text((W - 56 - w, 132), t, font=f, fill=OURO + (200,))
    return lay


def blocos_legenda(fala):
    f = fonte('oswald', 62)
    pal = fala.split(); blocos = []; cur = []
    for p in pal:
        t = ' '.join(cur + [p])
        if len(quebrar(t, f, W - 160)) <= 2 and len(t) <= 46: cur.append(p)
        else:
            blocos.append(' '.join(cur)); cur = [p]
        if p.endswith(('.', '?', '!')) and len(' '.join(cur)) > 18:
            blocos.append(' '.join(cur)); cur = []
    if cur: blocos.append(' '.join(cur))
    return [b for b in blocos if b]


def camada_legenda(txt):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = fonte('oswald', 62)
    ls = quebrar(txt, f, W - 160)
    y0 = 1450
    for i, l in enumerate(ls):
        texto_centro(d, W / 2, y0 + i * 80, l, f, CREME + (255,), sombra=False, stroke=5, stroke_cor=(0, 0, 0))
    return lay


def faixa_inferior():
    a = np.zeros((H, W), np.float32)
    ys = np.arange(H)
    g = np.clip((ys - 1250) / 500, 0, 1) * 0.75
    a[:] = g[:, None]
    lay = np.zeros((H, W, 4), np.uint8); lay[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(lay, 'RGBA')


# ------------------------------------------------------------------ cenas
def fundo_escuro(base, rng):
    alvo = ['gavetas', 'lanterna', 'livros', 'globo', 'tudo'][int(rng.integers(0, 5))]
    p = base.recorte(REGIOES[alvo], 1.08).filter(ImageFilter.GaussianBlur(9))
    return ImageEnhance.Brightness(p).enhance(0.30)


def placa_data(base, v, rng):
    p = fundo_escuro(base, rng)
    d = ImageDraw.Draw(p, 'RGBA')
    pw, ph = p.size
    f = fonte('anton', 230 if len(v['texto']) <= 5 else 150)
    texto_centro(d, pw / 2, ph * 0.40, v['texto'], f, OURO_CLARO + (255,), stroke=4, stroke_cor=(25, 15, 5))
    if v.get('sub'):
        texto_centro(d, pw / 2, ph * 0.40 + f.size * 1.25, v['sub'], fonte('oswald', 52), CREME + (235,))
    for i in range(3):
        y = ph * 0.38 - 30 - i * 14
        d.line((pw * 0.3, y, pw * 0.7, y), fill=OURO + (70 - i * 20,), width=2)
    return p


def placa_doc(base, v, rng):
    p = fundo_escuro(base, rng)
    pw, ph = p.size
    papel = Image.new('RGBA', (860, 1000), (0, 0, 0, 0))
    arr = np.zeros((1000, 860, 4), np.uint8)
    noise = rng.normal(0, 1, (1000, 860))
    base_c = np.array([214, 196, 160], np.float32)
    tex = base_c[None, None, :] + noise[..., None] * 10 - np.linspace(0, 30, 1000)[:, None, None]
    # manchas
    yy, xx = np.mgrid[:1000, :860]
    for _ in range(6):
        cx, cy, r = rng.integers(0, 860), rng.integers(0, 1000), rng.integers(80, 260)
        m = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))
        tex -= m[..., None] * rng.integers(10, 35)
    arr[..., :3] = np.clip(tex, 0, 255).astype(np.uint8); arr[..., 3] = 255
    papel = Image.fromarray(arr, 'RGBA')
    d = ImageDraw.Draw(papel)
    fe = fonte('elite', 46); fl = fonte('elite', 40)
    d.text((60, 70), v.get('cabecalho', 'ARQUIVO'), font=fe, fill=(40, 30, 22))
    d.line((60, 140, 800, 140), fill=(60, 45, 30), width=3)
    y = 200
    for l in v.get('linhas', []):
        for sub in quebrar(l, fl, 740):
            d.text((60, y), sub, font=fl, fill=(45, 35, 25)); y += 62
        y += 18
    # linhas tarjadas
    for i in range(4):
        yy0 = y + 40 + i * 70
        if yy0 > 860: break
        x1 = 60 + rng.integers(300, 740)
        d.rectangle((60, yy0, x1, yy0 + 34), fill=(18, 14, 12))
    if v.get('carimbo'):
        st = Image.new('RGBA', (760, 200), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        fc = fonte('anton', 96)
        tw = fc.getlength(v['carimbo'])
        sd.rounded_rectangle((380 - tw / 2 - 30, 30, 380 + tw / 2 + 30, 170), 10, outline=VERMELHO + (230,), width=8)
        sd.text((380 - tw / 2, 40), v['carimbo'], font=fc, fill=VERMELHO + (220,))
        st = st.rotate(-12, expand=True, resample=Image.BICUBIC)
        papel.alpha_composite(st, (40, 560))
    papel = papel.rotate(rng.uniform(-3, 3), expand=True, resample=Image.BICUBIC)
    sombra = Image.new('RGBA', papel.size, (0, 0, 0, 0))
    sombra.paste((0, 0, 0, 160), mask=papel.split()[3])
    sombra = sombra.filter(ImageFilter.GaussianBlur(24))
    x0 = (pw - papel.width) // 2; y0 = int(ph * 0.58 - papel.height / 2)
    p = p.convert('RGBA')
    p.alpha_composite(sombra, (x0 + 16, y0 + 30)); p.alpha_composite(papel, (x0, y0))
    return p.convert('RGB')


def placa_split(base, v, rng):
    p = fundo_escuro(base, rng).convert('RGBA')
    pw, ph = p.size
    d = ImageDraw.Draw(p)
    d.rectangle((0, 0, pw / 2 - 3, ph), fill=(0, 0, 0, 90))
    d.line((pw / 2, ph * 0.33, pw / 2, ph * 0.72), fill=OURO + (230,), width=4)
    fa = fonte('anton', 150); fs = fonte('oswald', 50)
    for i, (lado, cx) in enumerate(((v['a'], pw * 0.27), (v['b'], pw * 0.73))):
        a, b = lado
        fa2 = fa if fa.getlength(a) < pw * 0.42 else fonte('anton', int(150 * pw * 0.42 / fa.getlength(a)))
        texto_centro(d, cx, ph * 0.43, a, fa2, (OURO_CLARO if i == 0 else CREME) + (255,), stroke=3, stroke_cor=(20, 12, 4))
        texto_centro(d, cx, ph * 0.43 + 190, b, fs, CREME + (220,))
    if v.get('riscar') == 'b':
        d.line((pw * 0.55, ph * 0.47, pw * 0.92, ph * 0.52), fill=VERMELHO + (255,), width=16)
    return p.convert('RGB')


def placa_timeline(base, v, rng):
    p = fundo_escuro(base, rng).convert('RGBA')
    pw, ph = p.size
    d = ImageDraw.Draw(p)
    pts = v['pontos']; n = len(pts)
    y = ph * 0.5
    x0, x1 = pw * 0.22, pw * 0.78
    d.line((x0, y, x1, y), fill=OURO + (200,), width=5)
    fa = fonte('anton', 92); fs = fonte('oswald', 40)
    for i, (ano, rot) in enumerate(pts):
        x = x0 + (x1 - x0) * i / (n - 1)
        d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=(20, 14, 8, 255), outline=OURO_CLARO + (255,), width=6)
        up = i % 2 == 0
        texto_centro(d, x, y - 170 if up else y + 50, ano, fa, OURO_CLARO + (255,), stroke=2, stroke_cor=(20, 12, 4))
        for j, l in enumerate(quebrar(rot, fs, 300)):
            texto_centro(d, x, (y - 60 if up else y + 160) + j * 48 - (len(quebrar(rot, fs, 300)) - 1) * 48 * (1 if up else 0), l, fs, CREME + (230,))
    return p.convert('RGB')


def placa_grade(base, v, rng):
    p = fundo_escuro(base, rng).convert('RGBA')
    pw, ph = p.size
    d = ImageDraw.Draw(p)
    # 17 círculos dourados
    cx0, cy0 = pw / 2, ph * 0.42
    for i in range(17):
        a = 2 * math.pi * i / 17 - math.pi / 2
        x, y = cx0 + 300 * math.cos(a), cy0 + 300 * math.sin(a)
        d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=OURO + (230,))
    # 169 traços em anel interno
    for i in range(169):
        a = 2 * math.pi * i / 169
        r0, r1 = 200, 240
        d.line((cx0 + r0 * math.cos(a), cy0 + r0 * math.sin(a), cx0 + r1 * math.cos(a), cy0 + r1 * math.sin(a)), fill=CREME + (200,), width=3)
    texto_centro(d, cx0, cy0 - 70, '17', fonte('anton', 120), OURO_CLARO + (255,))
    texto_centro(d, cx0, cy0 + 60, '169', fonte('oswald', 60), CREME + (255,))
    return p.convert('RGB')


def placa_pergunta(base, v, rng, txt):
    p = Image.new('RGB', (int(W * 1.06), int(H * 1.06)), (6, 5, 4))
    m = base.recorte(REGIOES['mascara'], 0.55)
    m = ImageEnhance.Brightness(m).enhance(0.28)
    pw, ph = p.size
    p.paste(m, ((pw - m.width) // 2, int(ph * 0.12)))
    p = p.filter(ImageFilter.GaussianBlur(2))
    d = ImageDraw.Draw(p, 'RGBA')
    tam = 130
    while True:
        f = fonte('anton', tam); ls = quebrar(txt, f, pw - 180)
        if len(ls) <= 3 or tam < 70: break
        tam -= 10
    y0 = ph * 0.55 - len(ls) * tam * 0.56
    for i, l in enumerate(ls):
        texto_centro(d, pw / 2, y0 + i * tam * 1.12, l, f, CREME + (255,), stroke=3, stroke_cor=(0, 0, 0))
    return p


def placa_outro(base, num):
    p = Image.new('RGB', (W, H), (5, 4, 3))
    m = base.recorte(REGIOES['mascara'], 0.62)
    m = ImageEnhance.Brightness(m).enhance(0.5)
    p.paste(m, ((W - m.width) // 2, 230))
    d = ImageDraw.Draw(p, 'RGBA')
    g = np.zeros((H, W, 4), np.uint8); ys = np.arange(H)
    g[..., 3] = (np.clip((ys - 700) / 500, 0, 1) * 255).astype(np.uint8)[:, None]
    p = p.convert('RGBA'); p.alpha_composite(Image.fromarray(g, 'RGBA'))
    d = ImageDraw.Draw(p)
    texto_centro(d, W / 2, 1300, 'ARQUIVO OCULTO', fonte('cinzel', 96), OURO_CLARO + (255,))
    d.line((W / 2 - 160, 1430, W / 2 + 160, 1430), fill=OURO + (255,), width=3)
    texto_centro(d, W / 2, 1460, 'O passado deixa pistas.', fonte('oswald4', 52), CREME + (235,))
    texto_centro(d, W / 2, 1530, 'O futuro exige estratégia.', fonte('oswald4', 52), CREME + (235,))
    texto_centro(d, W / 2, 1680, f'ARQUIVO Nº {num:02d}', fonte('oswald', 38), OURO + (220,))
    return p.convert('RGB')


# ------------------------------------------------------------------ montagem
EXTRA_CENAS = {}   # tipo -> função(base, v, rng, cena) -> {'plate': PIL, 'dyn': f(t_local)->np.float32 (opcional), 'zoom': (z0, z1)}


def preparar_cena(base, c, rng):
    v = c['v']; tipo = v['tipo']
    info = {'tipo': tipo, 'olhos': None}
    if tipo == 'arq':
        box = REGIOES['close' if v.get('close') else 'tudo']
        plate = base.recorte(box, 1.10 if v.get('close') else 1.08)
        info['zoom'] = (1.0, 1.07) if not v.get('close') else (1.02, 1.12)
        # posição dos olhos na placa
        x0, y0, x1, y1 = box
        bw, bh = x1 - x0, y1 - y0
        alvo = 9 / 16
        if bw / bh > alvo:
            nw = bh * alvo; cx = (x0 + x1) / 2; x0 = cx - nw / 2; bw = nw
        else:
            nh = bw / alvo; cy = (y0 + y1) / 2; y0 = cy - nh / 2; bh = nh
        # animado: recorte direto da imagem original (x0, y0, largura, altura)
        info['anim_box'] = (x0, y0, bw, bh)
        info['olhos'] = [(ox, oy, 46) for ox, oy in OLHOS]
    elif tipo == 'crop':
        plate = base.recorte(REGIOES[v.get('alvo', 'mesa')], 1.12)
        info['zoom'] = (1.12, 1.0)
    elif tipo == 'data':
        plate = placa_data(base, v, rng); info['zoom'] = (1.0, 1.06)
    elif tipo == 'doc':
        plate = placa_doc(base, v, rng); info['zoom'] = (1.0, 1.05)
    elif tipo == 'split':
        plate = placa_split(base, v, rng); info['zoom'] = (1.04, 1.0)
    elif tipo == 'timeline':
        plate = placa_timeline(base, v, rng); info['zoom'] = (1.0, 1.04)
    elif tipo == 'grade':
        plate = placa_grade(base, v, rng); info['zoom'] = (1.0, 1.06)
    elif tipo == 'pergunta':
        plate = placa_pergunta(base, v, rng, c['tela']); info['zoom'] = (1.0, 1.04)
    elif tipo in EXTRA_CENAS:
        ext = EXTRA_CENAS[tipo](base, v, rng, c)
        plate = ext.pop('plate'); info.update(ext)
    else:
        raise ValueError(tipo)
    if v.get('zoom'): info['zoom'] = tuple(v['zoom'])
    info['surgir'] = float(v.get('surgir', 0))
    info['plate'] = plate
    info['pan'] = (rng.uniform(-0.25, 0.25), rng.uniform(-0.15, 0.15))
    info['titulo'] = None if (tipo in ('data', 'pergunta', 'grade', 'tipo') or v.get('sem_titulo') or not c.get('tela')) else camada_titulo(c['tela'])
    info['selo'] = camada_selo(c['selo']) if c.get('selo') else None
    return info


def enquadrar(plate, z, pan, k):
    pw, ph = plate.size
    # janela de tamanho W/z x H/z dentro da placa (placa pode ser maior que a tela)
    cw, ch = pw / z, ph / z
    cw = min(cw, pw); ch = min(ch, ph)
    # aspecto 9:16
    if cw / ch > W / H: cw = ch * W / H
    else: ch = cw * H / W
    mx, my = (pw - cw) / 2, (ph - ch) / 2
    cx = pw / 2 + pan[0] * mx * (2 * k - 1)
    cy = ph / 2 + pan[1] * my * (2 * k - 1)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return plate.resize((W, H), Image.BILINEAR, box=box), box


LEG_TXT = []
ULTIMO = {}


def srt(itens, path):
    def ts(x):
        ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s_, ms = divmod(ms, 1000)
        return f'{h:02d}:{m:02d}:{s_:02d},{ms:03d}'
    with open(path, 'w', encoding='utf-8') as f:
        for i, (a, b, t) in enumerate(itens, 1):
            f.write(f'{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n')


def render(ep, saida, capa=None):
    LEG_TXT.clear()
    rng = np.random.default_rng(ep['num'] * 101)
    base = Base()
    cenas = ep['cenas']
    print('voz…', flush=True)
    vozes = tts(cenas)
    pausa = 0.26
    inicio = []; t = 0.0
    for i, s in enumerate(vozes):
        inicio.append(t)
        t += len(s) / SR + (0.55 if i == len(vozes) - 2 else pausa)
    fim_fala = t
    outro = 2.4
    dur = fim_fala + outro
    nvoz = int(dur * SR)
    voz = np.zeros(nvoz, np.float32)
    for st, s in zip(inicio, vozes):
        i0 = int(st * SR); voz[i0:i0 + len(s)] += s
    voz = np.nan_to_num(voz)
    env = np.nan_to_num(rms_envelope(voz, dur))
    cortes = inicio[1:] + [fim_fala]
    mus = trilha(dur, cortes, fim_fala)

    tmp = tempfile.mkdtemp()
    escrever_wav(os.path.join(tmp, 'voz.wav'), voz / max(1e-6, np.abs(voz).max()) * 0.9)
    escrever_wav(os.path.join(tmp, 'mus.wav'), mus / max(1e-6, np.abs(mus).max()) * 0.9)
    # voz mais grave e escura + reverb de sala de arquivo; trilha abaixada sob a voz
    filtro = ("[0:a]asetrate=24000*0.9,aresample=48000,atempo=1.1111,"
              "equalizer=f=120:t=q:w=1:g=4,equalizer=f=3500:t=q:w=1:g=2,highpass=f=60,"
              "aecho=0.8:0.6:45|90:0.18|0.10,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,asplit=2[v][vsc];"
              "[1:a]aresample=48000,volume=0.30[m];"
              "[m][vsc]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=350[md];"
              "[v][md]amix=inputs=2:weights=1 0.9:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[a]")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(tmp, 'voz.wav'), '-i', os.path.join(tmp, 'mus.wav'),
                    '-filter_complex', filtro, '-map', '[a]', '-ar', '48000', '-ac', '2', os.path.join(tmp, 'mix.wav')], check=True)

    print('cenas…', flush=True)
    infos = [preparar_cena(base, c, rng) for c in cenas]
    legs = []
    for i, c in enumerate(cenas):
        bl = blocos_legenda(c['fala'])
        dur_c = len(vozes[i]) / SR
        tot = sum(len(b) for b in bl)
        tt = inicio[i]
        for b in bl:
            d = dur_c * len(b) / tot
            legs.append((tt, tt + d + (pausa if b == bl[-1] else 0), camada_legenda(b)))
            LEG_TXT.append((tt, tt + d + (pausa if b == bl[-1] else 0), b))
            tt += d
    import cv2
    marca = camada_marca(ep['num'])
    faixa = faixa_inferior()
    outro_img = np.asarray(placa_outro(base, ep['num']), np.float32)
    vin = vinheta(); gr = graos()

    def pre(lay):
        """RGBA PIL -> (rgb*alpha, 1-alpha) em float32 para mistura rápida."""
        a = np.asarray(lay, np.float32)
        al = a[..., 3:4] / 255.0
        return a[..., :3] * al, 1.0 - al

    # camada fixa por cena (faixa + título + selo + marca) e legendas recortadas na faixa de baixo
    for inf in infos:
        lay = faixa.copy()
        if inf['titulo'] is not None: lay.alpha_composite(inf['titulo'])
        if inf['selo'] is not None: lay.alpha_composite(inf['selo'])
        lay.alpha_composite(marca)
        inf['ov'] = pre(lay)
        inf['plate_np'] = np.asarray(inf['plate'].convert('RGB'))
    LY0, LY1 = 1400, 1700
    legs = [(a, b, pre(l.crop((0, LY0, W, LY1)))) for (a, b, l) in legs]
    # brilho dos olhos: sprite radial
    def sprite(r):
        r = max(4, int(r)); y, x = np.ogrid[-r:r + 1, -r:r + 1]
        g = np.exp(-((x / r) ** 2 + (y / (r * 0.6)) ** 2) * 2.2).astype(np.float32)
        return g[..., None] * np.array([255, 170, 60], np.float32)[None, None, :]

    anim = Animador(base)
    nf = int(round(dur * FPS))
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', os.path.join(tmp, 'mix.wav'), '-c:v', 'libx264', '-preset', 'faster', '-crf', '23', '-maxrate', '3000k', '-bufsize', '6000k', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', saida]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    print('quadros…', nf, flush=True)
    capa_frame = None
    pz = poeira(rng)
    for fi in range(nf):
        t = fi / FPS
        if t >= fim_fala:
            k = (t - fim_fala) / outro
            m = int(W * 0.02 * k); mh = int(H * 0.02 * k)
            a = cv2.resize(outro_img[mh:H - mh, m:W - m], (W, H), interpolation=cv2.INTER_LINEAR) if m else outro_img.copy()
            a *= min(1, (t - fim_fala) / 0.35) * min(1, max(0.0, (dur - t) / 0.5))
        else:
            ci = max(i for i in range(len(cenas)) if inicio[i] <= t)
            inf = infos[ci]
            t0 = inicio[ci]; t1 = inicio[ci + 1] if ci + 1 < len(cenas) else fim_fala
            k = (t - t0) / max(0.01, t1 - t0)
            z0, z1 = inf['zoom']
            ke = 0.5 - 0.5 * math.cos(math.pi * k)
            z = z0 + (z1 - z0) * ke
            if inf.get('anim_box'):
                bx, by, pw, ph = inf['anim_box']
                P = anim.quadro(t, env[min(fi, len(env) - 1)])
            elif inf.get('dyn'):
                bx = by = 0
                P = inf['dyn'](t - t0); ph, pw = P.shape[:2]
            else:
                bx = by = 0
                P = inf['plate_np']; ph, pw = P.shape[:2]
            cw, ch = pw / z, ph / z
            if cw / ch > W / H: cw = ch * W / H
            else: ch = cw * H / W
            mx, my = (pw - cw) / 2, (ph - ch) / 2
            cx = pw / 2 + inf['pan'][0] * mx * (2 * ke - 1); cy = ph / 2 + inf['pan'][1] * my * (2 * ke - 1)
            x0, y0 = bx + cx - cw / 2, by + cy - ch / 2
            sx, sy = W / cw, H / ch
            M = np.array([[sx, 0, -x0 * sx], [0, sy, -y0 * sy]], np.float32)
            a = cv2.warpAffine(P, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            a = a.astype(np.float32) if a.dtype != np.float32 else a
            if inf['olhos']:
                e = env[min(fi, len(env) - 1)]
                for ox, oy, r in inf['olhos']:
                    px, py = (ox - x0) * sx, (oy - y0) * sy; rr = r * sx * 0.55
                    sp = sprite(rr) * (0.18 + 0.62 * e)
                    hh2, ww2 = sp.shape[:2]
                    ya, xa = int(py - hh2 // 2), int(px - ww2 // 2)
                    if 0 <= ya and ya + hh2 <= H and 0 <= xa and xa + ww2 <= W:
                        reg = a[ya:ya + hh2, xa:xa + ww2]
                        a[ya:ya + hh2, xa:xa + ww2] = reg + sp * (1 - reg / 300.0)
            if inf.get('surgir') and (t - t0) < inf['surgir']:
                a = a * ((t - t0) / inf['surgir']) ** 1.6
            pre_rgb, inv = inf['ov']
            if ci > 0 and (t - t0) < 0.18 and inf['titulo'] is not None:
                ap = (t - t0) / 0.18
                a = a * (1 - (1 - inv) * ap) + pre_rgb * ap
            else:
                a = a * inv + pre_rgb
            for (la, lb, (lr, li)) in legs:
                if la <= t < lb:
                    a[LY0:LY1] = a[LY0:LY1] * li + lr; break
            dt = t - t0
            if ci > 0 and dt < 0.10:
                a *= (0.35 + 6.5 * dt)
        fl = 1.0 + 0.035 * math.sin(fi * 0.9) * rng.random()
        a *= vin * fl
        a += gr[fi % len(gr)]
        if fi % 3 == 0: pz = poeira(rng)
        a += pz * 0.35
        a[..., 2] *= 0.93
        a = np.clip(a, 0, 255).astype(np.uint8)
        if capa_frame is None and fi == int(0.6 * FPS): capa_frame = a.copy()
        proc.stdin.write(a.tobytes())
        if fi % 300 == 0: print(f'  {fi}/{nf}', flush=True)
    proc.stdin.close(); proc.wait()
    if capa and capa_frame is not None:
        Image.fromarray(capa_frame).save(capa, quality=90)
    ULTIMO.clear()
    ULTIMO.update(inicio=list(inicio), fim_fala=fim_fala, dur=dur, legendas=list(LEG_TXT), mix=os.path.join(tmp, 'mix.wav'),
                  voz=os.path.join(tmp, 'voz.wav'), voz_cfg={'engine': 'kokoro-onnx', 'model': 'kokoro-v1.0.int8', 'voice': VOZ,
                  'speed': float(os.environ.get('AO_VEL', '1.0')), 'pos': 'pitch 0.9 + eq + eco de sala', 'versao': 'arquivista-voz-01'})
    return dur


if __name__ == '__main__':
    eps = json.load(open(sys.argv[1]))
    num = int(sys.argv[2])
    ep = next(e for e in eps if e['num'] == num)
    capa = sys.argv[sys.argv.index('--capa') + 1] if '--capa' in sys.argv else None
    d = render(ep, sys.argv[3], capa)
    print('ok', round(d, 1), 's')
