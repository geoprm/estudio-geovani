"""Motor de edição v2 — Estúdio de Reels.

Dois perfis de marca (perfis.py) e dois layouts:
  'dividida'   — prova em cima, pessoa embaixo, legenda na divisão (modelo atual)
  'depoimento' — pessoa em tela cheia, palavra-carimbo atrás da cabeça, legenda discreta

Regras do Manual v2 já embutidas: gancho sozinho na tela nos primeiros segundos, zoom de abertura
100→110% em 1,5 s, lower third de 2,5 a 5 s, palavra-chave em destaque, legenda de tela cheia em
y = 1380 (área segura), selo de fonte, versão B (prova em tela cheia na abertura) e capa.
"""
import json, math, os, subprocess, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from perfis import PERFIS, RAIZ, fonte
import fundos
import pessoa
import beleza

FPS, W, H = 30, 1080, 1920
SPF = 48000 // FPS
SEAM = 900
BOT_H = H - SEAM
SUB_Y_CHEIA = 1380     # legenda em tela cheia e no depoimento (acima da área coberta pelo app)
LOWER_Y = 1470         # centro do lower third (1420 a 1520 px)
SUB_Y_DEP = 1320       # legenda do depoimento: acima do lower third
TOPO_K = 0.80            # topo da cabeça = centro do rosto - 0.80 x largura da cabeça (preparar.py usa 0.775)
SELO_Y = 180           # selo de fonte (150 a 210 px)
TRABALHO = os.environ.get('ESTUDIO_TRABALHO', os.path.join(RAIZ, 'trabalho'))

F_BL = fonte('Montserrat_900Black.ttf')
F_XB = fonte('Montserrat_800ExtraBold.ttf')
F_BD = fonte('Montserrat_700Bold.ttf')
F_SB = fonte('Montserrat_600SemiBold.ttf')
F_SERIF = fonte('Merriweather_700Bold.ttf')
F_ANTON = fonte('Anton_400Regular.ttf')

WHITE = (255, 255, 255)
GOLD = (236, 190, 90)
GOLD2 = (255, 214, 120)
YELLOW = (255, 212, 0)
RED = (214, 48, 49)
RED2 = (255, 82, 82)
GREEN = (40, 200, 110)
INK = (20, 20, 22)
GREY = (170, 176, 190)


# ------------------------------------------------------------------ utilidades
def clamp01(x):
    return min(1.0, max(0.0, x))


def smooth(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_out_back(x, s=1.6):
    x = clamp01(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


_fc = {}


def font(p, s):
    k = (p, int(s))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]


def blend(frame, im, cx, cy, alpha=1.0, y0=0, y1=None):
    if alpha <= 0.003:
        return
    a = np.asarray(im)
    h, w = a.shape[:2]
    y1 = frame.shape[0] if y1 is None else y1
    x0, yy0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya = max(0, x0), max(y0, yy0)
    xb, yb = min(W, x0 + w), min(y1, yy0 + h)
    if xb <= xa or yb <= ya:
        return
    sub = a[ya - yy0:yb - yy0, xa - x0:xb - x0].astype(np.float32)
    al = sub[..., 3:4] / 255.0 * alpha
    roi = frame[ya:yb, xa:xb].astype(np.float32)
    frame[ya:yb, xa:xb] = (sub[..., :3] * al + roi * (1 - al)).astype(np.uint8)


def scaled(im, s):
    if abs(s - 1) < 1e-3:
        return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


def text_layer(lines, width=W, pad=60, shadow=True, spacing=1.06, stroke=0):
    """lines: [(texto, fonte, tamanho, cor)] centralizadas."""
    hgt = int(sum(s * spacing for _, _, s, _ in lines)) + pad * 2
    txt = Image.new('RGBA', (width, hgt), (0, 0, 0, 0))
    shd = Image.new('RGBA', (width, hgt), (0, 0, 0, 0))
    dt, ds = ImageDraw.Draw(txt), ImageDraw.Draw(shd)
    y = pad
    for text, fp, size, color in lines:
        f = font(fp, size)
        base = y + int(size * 0.86)
        sw = int(size * stroke)
        if shadow:
            ds.text((width / 2 + 3, base + 8), text, font=f, anchor='ms', fill=(0, 0, 0, 200),
                    stroke_width=sw, stroke_fill=(0, 0, 0, 200))
        dt.text((width / 2, base), text, font=f, anchor='ms', fill=color + (255,), stroke_width=sw,
                stroke_fill=(0, 0, 0, 255))
        y += int(size * spacing)
    out = shd.filter(ImageFilter.GaussianBlur(10)) if shadow else Image.new('RGBA', txt.size)
    out.alpha_composite(txt)
    return out


def pill(text, icon=None, fsize=38, bg=(12, 16, 26, 225), border=GOLD, fg=WHITE, pad=34, h=86):
    f = font(F_XB, fsize)
    tw = f.getlength(text)
    iw = 54 if icon else 0
    w = int(tw + pad * 2 + iw)
    S = 3
    im = Image.new('RGBA', ((w + 40) * S, (h + 44) * S), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20 * S, 28 * S, (20 + w) * S, (28 + h) * S], radius=h * S // 2,
                                         fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * S)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20 * S, 20 * S, (20 + w) * S, (20 + h) * S], radius=h * S // 2, fill=bg,
                        outline=border + (255,), width=3 * S)
    cy = 20 + h / 2
    ix = 20 + pad - 6
    if icon == 'mute':
        c = border + (255,)
        d.polygon([(ix * S, (cy - 8) * S), ((ix + 9) * S, (cy - 8) * S), ((ix + 22) * S, (cy - 19) * S),
                   ((ix + 22) * S, (cy + 19) * S), ((ix + 9) * S, (cy + 8) * S), (ix * S, (cy + 8) * S)], fill=c)
        d.line([((ix + 29) * S, (cy - 10) * S), ((ix + 43) * S, (cy + 10) * S)], fill=RED2 + (255,), width=5 * S)
        d.line([((ix + 43) * S, (cy - 10) * S), ((ix + 29) * S, (cy + 10) * S)], fill=RED2 + (255,), width=5 * S)
    elif icon == 'dot':
        d.ellipse([(ix + 6) * S, (cy - 11) * S, (ix + 28) * S, (cy + 11) * S], fill=RED + (255,))
    im = im.resize((w + 40, h + 44), Image.LANCZOS)
    ImageDraw.Draw(im).text((20 + pad + iw, cy), text, font=f, anchor='lm', fill=fg + (255,))
    return im


# ------------------------------------------------------------------ cards de manchete
class Card:
    def __init__(self, outlet, date, headline, mark, fsize=50, width=920):
        self.outlet, self.date, self.headline, self.mark = outlet, date, headline, mark
        self.w = width
        self.fh = font(F_SERIF, fsize)
        self.lh = int(fsize * 1.48)
        words = headline.split(' ')
        lines, cur = [], ''
        for wd in words:
            cand = (cur + ' ' + wd).strip()
            if self.fh.getlength(cand) > self.w - 110 and cur:
                lines.append(cur); cur = wd
            else:
                cur = cand
        lines.append(cur)
        self.lines = lines
        self.top = 112
        self.h = self.top + self.lh * len(lines) + 46
        ms = headline.find(mark); me = ms + len(mark)
        boxes, pos = {}, 0
        for li, line in enumerate(lines):
            x = 55
            for wd in line.split(' '):
                i0 = headline.find(wd, pos); i1 = i0 + len(wd); pos = i1
                wl = self.fh.getlength(wd)
                if ms >= 0 and i0 >= ms and i1 <= me + 1:
                    a, b = boxes.get(li, (x, x + wl))
                    boxes[li] = (min(a, x), max(b, x + wl))
                x += wl + self.fh.getlength(' ')
        self.mboxes = [(li, a, b) for li, (a, b) in sorted(boxes.items())]
        self.total = sum(b - a for _, a, b in self.mboxes) or 1
        self._cache = {}

    def render(self, mprog):
        key = round(mprog, 2)
        if key in self._cache:
            return self._cache[key]
        pad = 50
        im = Image.new('RGBA', (self.w + pad * 2, self.h + pad * 2), (0, 0, 0, 0))
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 16, pad + self.w, pad + self.h + 16], radius=26,
                                             fill=(0, 0, 0, 170))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([pad, pad, pad + self.w, pad + self.h], radius=26, fill=(248, 246, 241, 255))
        fo, fd = font(F_XB, 30), font(F_SB, 28)
        d.rectangle([pad + 55, pad + 44, pad + 67, pad + 76], fill=RED + (255,))
        d.text((pad + 84, pad + 60), self.outlet.upper(), font=fo, anchor='lm', fill=RED + (255,))
        ow = fo.getlength(self.outlet.upper())
        d.text((pad + 84 + ow + 22, pad + 60), '•  ' + self.date, font=fd, anchor='lm', fill=(110, 110, 110, 255))
        d.line([pad + 55, pad + 96, pad + self.w - 55, pad + 96], fill=(222, 218, 210, 255), width=2)
        rem = mprog * self.total
        for li, a, b in self.mboxes:
            if rem <= 0:
                break
            seg = min(b - a, rem); rem -= seg
            y = pad + self.top + li * self.lh
            d.rectangle([pad + a - 6, y + 10, pad + a + seg + 6, y + self.lh - 6], fill=(255, 210, 70, 255))
        for li, line in enumerate(self.lines):
            d.text((pad + 55, pad + self.top + li * self.lh + int(self.lh * 0.73)), line, font=self.fh, anchor='ls',
                   fill=INK + (255,))
        self._cache[key] = im
        return im


def label_img(txt='NA IMPRENSA'):
    f = font(F_XB, 30)
    w = int(f.getlength(txt)) + 70
    im = Image.new('RGBA', (w, 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([8, 18, 32, 42], fill=RED + (255,))
    d.text((46, 31), txt, font=f, anchor='lm', fill=GOLD2 + (255,))
    return im


LABEL = label_img()


def draw_card(frame, card, t, t_in, y, dim=0.0, lift=0.0):
    if t < t_in:
        return
    p = ease_out((t - t_in) / 0.35)
    mp = smooth((t - t_in - 0.45) / 0.55)
    im = scaled(card.render(mp), (0.94 + 0.06 * p) * (1 - 0.07 * dim))
    x = W / 2 + 160 * (1 - p)
    a = min(1.0, (t - t_in) / 0.18) * (1 - 0.55 * dim)
    blend(frame, im, x, y - lift, a, 0, SEAM)


def pop_in(frame, im, t, t0, cx, cy, dur=0.22, alpha=1.0, y1=SEAM):
    if t < t0:
        return
    p = (t - t0) / dur
    s = 0.72 + 0.28 * ease_out_back(p) if p < 1 else 1.0
    a = min(1.0, (t - t0) / 0.09 + 0.1) * alpha
    blend(frame, scaled(im, s), cx, cy, a, 0, y1)


def slide_in(frame, im, t, t0, cx, cy, dx=80, dur=0.3, alpha=1.0):
    if t < t0:
        return
    p = ease_out((t - t0) / dur)
    blend(frame, im, cx + dx * (1 - p), cy, min(1.0, (t - t0) / 0.15) * alpha, 0, SEAM)


_num_cache = {}


def number_img(txt, size, color, fp=F_BL):
    k = (txt, size, color, fp)
    if k not in _num_cache:
        _num_cache[k] = text_layer([(txt, fp, size, color)])
        if len(_num_cache) > 400:
            _num_cache.clear()
    return _num_cache[k]


def fmt_br(v, dec=0):
    s = f'{v:,.{dec}f}'
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')


def counter(frame, t, t0, dur, v0, v1, cx, cy, size, color, dec=0, suffix='', prefix='', alpha=1.0):
    if t < t0:
        return
    p = ease_out((t - t0) / dur)
    v = v0 + (v1 - v0) * p
    if dec == 0:
        v = round(v)
    im = number_img(prefix + fmt_br(v, dec) + suffix, size, color)
    pop_in(frame, im, t, t0, cx, cy, 0.25, alpha)


def check_row(label, prog, size=58, mark='check'):
    f = font(F_BL, size)
    w = int(f.getlength(label) + 140)
    im = Image.new('RGBA', (w, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = GOLD if mark == 'check' else RED2
    d.rounded_rectangle([10, 22, 74, 86], radius=12, outline=col + (255,), width=6)
    if prog > 0:
        if mark == 'check':
            pts = [(24, 54), (38, 70), (64, 34)]
        else:
            pts = [(26, 38), (58, 70)]
        L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        dl = prog * sum(L); seg = [pts[0]]
        for i, l in enumerate(L):
            if dl >= l:
                seg.append(pts[i + 1]); dl -= l
            else:
                q = dl / l
                seg.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * q, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * q))
                break
        d.line(seg, fill=(GOLD2 if mark == 'check' else RED2) + (255,), width=10, joint='curve')
        if mark == 'x' and prog > 0.5:
            q = (prog - 0.5) * 2
            d.line([(58, 38), (58 - 32 * q, 38 + 32 * q)], fill=RED2 + (255,), width=10)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((106, 60), label, font=f, anchor='lm', fill=(0, 0, 0, 180))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6))); out.alpha_composite(im)
    ImageDraw.Draw(out).text((102, 54), label, font=f, anchor='lm', fill=WHITE + (255,))
    return out


def arrow_img(color=GOLD2):
    im = Image.new('RGBA', (160, 120), (0, 0, 0, 0))
    ImageDraw.Draw(im).line([(30, 30), (80, 85), (130, 30)], fill=color + (255,), width=18, joint='curve')
    return im


ARROW = arrow_img()


def credit_img(text, size=26):
    f = font(F_BD, size)
    l, tp, r, b = f.getbbox(text)
    im = Image.new('RGBA', (r - l + 40, b - tp + 30), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((20 - l + 2, 15 - tp + 3), text, font=f, fill=(0, 0, 0, 220))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    ImageDraw.Draw(im).text((20 - l, 15 - tp), text, font=f, fill=(255, 255, 255, 235))
    return im


def scene_alpha(t, a, b, end, fin=0.0, fout=0.22):
    if t < a or t >= b:
        return 0.0
    al = 1.0
    if fin > 0:
        al = min(al, (t - a) / fin)
    if fout > 0 and b < end - 0.01:
        al = min(al, (b - t) / fout)
    return max(0.0, min(1.0, al))


# ------------------------------------------------------------------ leitor de vídeo para o painel de cima
class ClipReader:
    """Lê um vídeo externo já recortado para 1080x900, sequencialmente."""
    def __init__(self, path, y0=250, start=0.0, src_w=720, src_h=1280):
        self.path, self.y0, self.start = path, y0, start
        self.p = None; self.idx = -1; self.last = None
        self._open(start)

    def _open(self, t0):
        if self.p:
            self.p.kill()
        vf = f'scale=1080:1920:flags=lanczos,crop=1080:{SEAM}:0:{self.y0},fps=30'
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-i', self.path, '-an', '-vf', vf,
                                   '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE,
                                  bufsize=10 ** 8)
        self.base = t0; self.idx = -1; self.last = None

    def frame(self, t):
        want = int(round((t - self.base) * FPS))
        if want < self.idx or want - self.idx > 600:
            self._open(t); want = 0
        n = W * SEAM * 3
        while self.idx < want:
            buf = self.p.stdout.read(n)
            if len(buf) < n:
                break
            self.last = np.frombuffer(buf, np.uint8).reshape(SEAM, W, 3); self.idx += 1
        return self.last


# ------------------------------------------------------------------ SFX sintetizados
def sfx_whoosh(dur=0.42, sr=48000, up=True):
    n = int(dur * sr); rng = np.random.default_rng(1)
    x = rng.normal(0, 1, n).astype(np.float32)
    t = np.linspace(0, 1, n)
    fc = (300 + 3200 * t ** 1.5) if up else (3200 - 2900 * t)
    y = np.zeros(n, np.float32); lp = 0.0; hp_prev = 0.0; hp = 0.0
    for i in range(n):
        a = 1 - math.exp(-2 * math.pi * fc[i] / sr)
        lp += a * (x[i] - lp)
        hp = 0.97 * (hp + lp - hp_prev); hp_prev = lp
        y[i] = hp
    env = np.sin(np.pi * np.clip(t * 1.15, 0, 1)) ** 1.6
    y *= env
    return y / (np.abs(y).max() + 1e-9)


def sfx_hit(dur=0.9, sr=48000):
    n = int(dur * sr); t = np.arange(n) / sr
    f = 58 * np.exp(-t * 1.5) + 36
    ph = 2 * np.pi * np.cumsum(f) / sr
    y = np.sin(ph) * np.exp(-t * 4.5)
    click = np.random.default_rng(2).normal(0, 1, n) * np.exp(-t * 90)
    k = np.ones(12) / 12
    click = np.convolve(click, k, 'same')
    y = y + 0.35 * click
    return (y / np.abs(y).max()).astype(np.float32)


def sfx_pop(dur=0.09, sr=48000):
    n = int(dur * sr); t = np.arange(n) / sr
    f = 1100 - 500 * t / dur
    y = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 55)
    return (y / np.abs(y).max()).astype(np.float32)


def sfx_tick(sr=48000):
    n = int(0.03 * sr); t = np.arange(n) / sr
    y = np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 260)
    return (y / np.abs(y).max()).astype(np.float32)


SFX = {'whoosh': sfx_whoosh(), 'hit': sfx_hit(), 'pop': sfx_pop(), 'tick': sfx_tick()}
SFX_DB = {'whoosh': -27, 'hit': -17, 'pop': -30, 'tick': -32}




# ------------------------------------------------------------------ peças novas da v2
def _chave(w):
    return w.strip('.,!?:;…"\'()').upper()


def texto_palavras(linhas, fp, size, cor, cor_destaque, destaque=(), contorno=0.08, max_w=980,
                   espaco=1.04, sombra=200):
    """Texto centralizado em várias linhas; palavras em `destaque` ganham a cor de destaque."""
    destaque = {_chave(d) for d in destaque}
    f = font(fp, size)
    while max(f.getlength(l) for l in linhas) > max_w and size > 30:
        size -= 4
        f = font(fp, size)
    lh = int(size * espaco)
    hgt = lh * len(linhas) + 120
    txt = Image.new('RGBA', (W, hgt), (0, 0, 0, 0))
    shd = Image.new('RGBA', (W, hgt), (0, 0, 0, 0))
    dt, ds = ImageDraw.Draw(txt), ImageDraw.Draw(shd)
    sw = int(size * contorno)
    sp = f.getlength(' ')
    for li, linha in enumerate(linhas):
        x = (W - f.getlength(linha)) / 2
        base = 60 + li * lh + int(size * 0.86)
        for w_ in linha.split(' '):
            col = cor_destaque if _chave(w_) in destaque else cor
            ds.text((x + 3, base + 8), w_, font=f, anchor='ls', fill=(0, 0, 0, sombra), stroke_width=sw,
                    stroke_fill=(0, 0, 0, sombra))
            dt.text((x, base), w_, font=f, anchor='ls', fill=col + (255,), stroke_width=sw,
                    stroke_fill=(0, 0, 0, 255))
            x += f.getlength(w_) + sp
    out = shd.filter(ImageFilter.GaussianBlur(10))
    out.alpha_composite(txt)
    return out


def lower_img(P):
    l1, l2 = P['lower']
    f1, f2 = font(P['fonte_lower'], 42), font(P['fonte_lower2'], 28)
    w = int(max(f1.getlength(l1), f2.getlength(l2))) + 78
    h = 120
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 28, 20 + w, 28 + h], radius=16, fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    bg = P['marinho'] + (232,) if 'marinho' in P else (12, 16, 26, 222)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=16, fill=bg)
    d.rounded_rectangle([20, 20, 32, 20 + h], radius=6, fill=P['destaque'] + (255,))
    d.text((56, 20 + 50), l1, font=f1, anchor='ls', fill=WHITE + (255,))
    d.text((56, 20 + 94), l2, font=f2, anchor='ls', fill=P['moldura'] + (255,))
    return im


def selo_img(texto, P, size=28):
    f = font(P['fonte_selo'], size)
    w = int(f.getlength(texto)) + 56
    h = 56
    im = Image.new('RGBA', (w + 30, h + 30), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([15, 19, 15 + w, 19 + h], radius=10, fill=(0, 0, 0, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    bg = P['marinho'] + (225,) if 'marinho' in P else (10, 12, 18, 215)
    d.rounded_rectangle([15, 15, 15 + w, 15 + h], radius=10, fill=bg, outline=P['moldura'] + (255,), width=2)
    d.text((15 + 28, 15 + h / 2 + 1), texto, font=f, anchor='lm', fill=WHITE + (255,))
    return im


def carimbo_img(texto, P, max_w=1040, size=290):
    """Palavra grande que fica ATRÁS da cabeça (vermelha na @direitaxx, dourada no Dr. Geovani)."""
    fp = P['fonte_carimbo']
    cor = P[P['carimbo_cor']]
    linhas = texto.upper().split('\n') if P['carimbo_cor'] == 'alerta' else texto.split('\n')
    size = int(size if len(linhas) == 1 else size * 0.72)
    f = font(fp, size)
    while max(f.getlength(l) for l in linhas) > max_w and size > 60:
        size -= 6
        f = font(fp, size)
    lh = int(size * 0.98)
    hgt = lh * len(linhas) + 80
    txt = Image.new('RGBA', (W, hgt), (0, 0, 0, 0))
    shd = Image.new('RGBA', (W, hgt), (0, 0, 0, 0))
    dt, ds = ImageDraw.Draw(txt), ImageDraw.Draw(shd)
    for li, l in enumerate(linhas):
        base = 40 + li * lh + int(size * 0.88)
        ds.text((W / 2 + 4, base + 10), l, font=f, anchor='ms', fill=(0, 0, 0, 120))
        dt.text((W / 2, base), l, font=f, anchor='ms', fill=cor + (255,))
    out = shd.filter(ImageFilter.GaussianBlur(14))
    out.alpha_composite(txt)
    return out


def place_rgba(canvas, im, cx, cy, alpha=1.0):
    """Cola uma imagem RGBA (PIL) numa camada float RGBA (alfa direto)."""
    a = np.asarray(im).astype(np.float32) / 255
    h, w = a.shape[:2]
    Hc, Wc = canvas.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(Wc, x0 + w), min(Hc, y0 + h)
    if xb <= xa or yb <= ya:
        return
    sub = a[ya - y0:yb - y0, xa - x0:xb - x0]
    al = sub[..., 3:4] * alpha
    roi = canvas[ya:yb, xa:xb]
    roi[..., :3] = sub[..., :3] * al + roi[..., :3] * (1 - al)
    roi[..., 3:4] = al + roi[..., 3:4] * (1 - al)


# ------------------------------------------------------------------ o reel
class Reel:
    def __init__(self, src, segs, face_src, zbase=1.18, face_panel=None, face_r=(170, 215),
                 grade='eq=contrast=1.03:saturation=1.0', perfil='direitaxx', layout='dividida', fundo=None):
        self.P = PERFIS[perfil] if isinstance(perfil, str) else perfil
        self.layout = layout
        self.src, self.face_src, self.zbase, self.face_r, self.grade = src, face_src, zbase, face_r, grade
        self.SEGF = []
        off = 0
        for s, e, z0, z1 in segs:
            f0, f1 = round(s * FPS), round(e * FPS)
            self.SEGF.append((f0, f1, z0, z1, off))
            off += f1 - f0
        self.TOTAL = off
        self.END = off / FPS
        self.groups = []
        self.sfx = []
        P = self.P
        tipo = P['fundo'] if P['fundo'] != 'real' else 'bandeira'
        if layout == 'dividida':
            self.PH = BOT_H
            self.face_panel = face_panel or (540, 370)
            self.top_bg = fundos.criar(tipo, W, SEAM, strength=0.16, seed=4)
            self.scene = pessoa.Scene(W, BOT_H, fundo or P['fundo'], P['rim'])
            self.sub_y = SEAM + 5
            self.sizes = P['legenda']
        else:
            self.PH = H
            self.face_panel = face_panel or (540, 640)
            self.scene = pessoa.Scene(W, H, fundo or 'real', P['rim'])
            self.sub_y = SUB_Y_DEP
            self.sizes = P['legenda_cheia']
        self._full_bg = fundos.criar(tipo, W, H, strength=0.20, seed=4)
        # recursos do Manual v2
        self.gancho = None          # {'linhas': [...], 'destaque': [...], 'ate': 2.5}
        self.lower = True           # lower third de 2,5 a 5 s
        self.selos = []             # [(t0, t1, 'FONTE: ...')]
        self.carimbos = []          # [(t0, t1, 'TEXTO')]  — atrás da cabeça
        self.cutaways = []          # [(t0, t1)] — prova em tela cheia, rosto some
        self.variante = 'A'         # 'B' = prova em tela cheia durante o gancho
        self.zoom_abertura = True
        # retoque leve do rosto: pele (0 a 1) e dentes/aparelho (0 a 1). R.retoque = None desliga.
        rt = P.get('retoque', {'pele': 0.40, 'dentes': 0.85})
        self.retoque = beleza.Retoque(**rt) if rt else None
        self._cache = {}

    def T(self, t):
        f = t * FPS
        for f0, f1, _a, _b, o in self.SEGF:
            if f < f0:
                return o / FPS
            if f < f1:
                return (o + f - f0) / FPS
        return self.END

    # ---------------- legendas
    def set_groups(self, groups, sizes=None, sub_y=None, max_w=940):
        if sizes:
            self.sizes = sizes
        if sub_y:
            self.sub_y = sub_y
        self.max_w = max_w
        for g in groups:
            g['ws'] = [self.T(t) for _, t in g['w']]
            g['t0'] = g['ws'][0]
        for i, g in enumerate(groups):
            nxt = groups[i + 1]['t0'] if i + 1 < len(groups) else self.END
            g['t1'] = min(nxt, g['ws'][-1] + 0.8) if i + 1 < len(groups) else self.END
        self.groups = groups
        self._gc = {}

    def group_img(self, gi, active):
        k = (gi, active)
        if k in self._gc:
            return self._gc[k]
        P = self.P
        g = self.groups[gi]
        size = self.sizes[g['st']]
        fp = P['fonte_legenda']
        f = font(fp, size)
        space = int(size * 0.40)
        words = [w for w, _ in g['w']]
        wl = [f.getlength(w) for w in words]
        width = lambda a, b: sum(wl[a:b]) + space * (b - a - 1)
        if g.get('br'):
            lines = [list(range(0, g['br'])), list(range(g['br'], len(words)))]
        elif width(0, len(words)) <= self.max_w or len(words) == 1:
            lines = [list(range(len(words)))]
        else:
            k2 = min(range(1, len(words)), key=lambda k: max(width(0, k), width(k, len(words))))
            lines = [list(range(0, k2)), list(range(k2, len(words)))]
        lh = int(size * 1.16)
        ch = lh * len(lines) + 120
        txt = Image.new('RGBA', (W, ch), (0, 0, 0, 0))
        shd = Image.new('RGBA', (W, ch), (0, 0, 0, 0))
        dt, ds = ImageDraw.Draw(txt), ImageDraw.Draw(shd)
        cont = self.sizes.get('contorno', 0.11)
        for li, line in enumerate(lines):
            x = (W - width(line[0], line[-1] + 1)) / 2
            base = 60 + li * lh + int(size * 0.86)
            for i in line:
                color = P['destaque'] if i == active else g['col'].get(i, WHITE)
                if i in g['col'] and i != active:
                    color = g['col'][i]
                sc = 1.05 if i == active else 1.0
                fi = font(fp, int(size * sc))
                sw = int(size * sc * cont)
                cx = x + wl[i] / 2
                if sw > 0:
                    ds.text((cx + 3, base + 8), words[i], font=fi, anchor='ms', fill=(0, 0, 0, 170),
                            stroke_width=sw, stroke_fill=(0, 0, 0, 170))
                else:
                    ds.text((cx + 2, base + 5), words[i], font=fi, anchor='ms', fill=(0, 0, 0, 235))
                dt.text((cx, base), words[i], font=fi, anchor='ms', fill=color + (255,), stroke_width=sw,
                        stroke_fill=(0, 0, 0, 255))
                x += wl[i] + space
        out = shd.filter(ImageFilter.GaussianBlur(8 if cont > 0 else 5))
        if cont <= 0:  # sem contorno: sombra dupla para ler sobre qualquer fundo
            out.alpha_composite(shd.filter(ImageFilter.GaussianBlur(14)))
        out.alpha_composite(txt)
        self._gc[k] = out
        return out

    def draw_subs(self, frame, t, hide_until=-1, y=None):
        if t < hide_until:
            return
        sy = self.sub_y if y is None else y
        for gi, g in enumerate(self.groups):
            if g['t0'] <= t < g['t1']:
                active = 0
                for i, ws in enumerate(g['ws']):
                    if t >= ws - 0.02:
                        active = i
                im = self.group_img(gi, active)
                dt = t - g['t0']
                al = 1.0
                if dt < 0.18:
                    im = scaled(im, 0.78 + 0.22 * ease_out_back(dt / 0.18))
                    al = min(1.0, dt / 0.07 + 0.15)
                blend(frame, im, W / 2, sy, al)
                return

    # ---------------- camadas do Manual v2
    def fim_gancho(self):
        return self.gancho['ate'] if self.gancho else 0.0

    def _img(self, key, fn):
        if key not in self._cache:
            self._cache[key] = fn()
        return self._cache[key]

    def draw_gancho(self, frame, t, y, size=96):
        g = self.gancho
        if not g or t >= g['ate']:
            return False
        P = self.P
        im = self._img(('gancho', size), lambda: texto_palavras(
            g['linhas'], P['fonte_gancho'], size, P['texto'], P['destaque'], g.get('destaque', ()),
            contorno=0.07 if P['legenda']['contorno'] > 0 else 0.0))
        s = 1.06 - 0.06 * ease_out(t / 0.25)          # já aparece no frame 0 e assenta
        al = clamp01((g['ate'] - t) / 0.12)
        blend(frame, scaled(im, s), W / 2, y, al)
        return True

    def draw_texto(self, frame, t, hide_until, y, hook_y):
        if not self.draw_gancho(frame, t, hook_y):
            self.draw_subs(frame, t, max(hide_until, self.fim_gancho()), y)

    def draw_lower(self, frame, t):
        if not self.lower:
            return
        t0 = max(2.5, self.fim_gancho())
        t1 = t0 + 2.5
        if not (t0 <= t < t1):
            return
        im = self._img('lower', lambda: lower_img(self.P))
        p = ease_out((t - t0) / 0.3)
        al = min(1.0, (t - t0) / 0.15) * clamp01((t1 - t) / 0.25)
        cx = 28 + im.width / 2 - 70 * (1 - p)
        blend(frame, im, cx, LOWER_Y, al)

    def draw_selos(self, frame, t):
        for t0, t1, texto in self.selos:
            if t0 <= t < t1:
                im = self._img(('selo', texto), lambda: selo_img(texto, self.P))
                al = min(1.0, (t - t0) / 0.15) * clamp01((t1 - t) / 0.2)
                blend(frame, im, 33 + im.width / 2, SELO_Y, al)

    def _caixa_carimbo(self, tx):
        """Linhas (topo, base) das letras dentro da imagem do carimbo, sem a sombra."""
        def f():
            im = self._img(('carimbo', tx), lambda: carimbo_img(tx, self.P))
            a = np.asarray(im)[..., 3]
            rows = np.where((a > 200).any(1))[0]
            return (int(rows[0]), int(rows[-1]), im.height) if len(rows) else (0, im.height, im.height)
        return self._img(('carimbo_caixa', tx), f)

    def camada_carimbos(self, t, face_c, face_r, topo=None):
        """Palavra grande atrás da cabeça. A base da palavra encosta no topo da cabeça e só uma faixa
        pequena (P['carimbo_sob']) passa por trás, para a palavra ser lida inteira. Sem espaço acima da
        cabeça, a palavra encolhe (até 62%) e o enquadramento abre um pouco (ver _z_carimbo)."""
        ativos = [(t0, t1, tx) for t0, t1, tx in self.carimbos if t0 <= t < t1]
        if not ativos:
            return None
        if topo is None:
            topo = face_c[1] - face_r[1] * (TOPO_K / 0.55)
        canvas = np.zeros((self.PH, W, 4), np.float32)
        lim = self._lim_carimbo()
        sob = self.P.get('carimbo_sob', 0.18)
        for t0, t1, tx in ativos:
            im = self._img(('carimbo', tx), lambda: carimbo_img(tx, self.P))
            r0, r1, hh = self._caixa_carimbo(tx)
            th = r1 - r0
            k = float(np.clip((topo - lim) / max(1.0, (1 - sob) * th), 0.62, 1.0))
            cy = topo + sob * th * k - (r1 - hh / 2) * k
            cy = max(cy, lim + (hh / 2 - r0) * k)
            q = (t - t0) / 0.14
            s = 1.30 - 0.30 * ease_out(q)
            al = min(1.0, q * 1.6) * clamp01((t1 - t) / 0.10)
            place_rgba(canvas, scaled(im, s * k), W / 2, cy, al)
        return canvas

    def _lim_carimbo(self):
        return 215 if self.layout == 'depoimento' else 30

    def _z_carimbo(self, t, z, fi, fp, src_h):
        """Enquanto um carimbo aparece, abre o enquadramento só o necessário para caber a palavra acima
        da cabeça (entra junto com o impacto sonoro, como um corte)."""
        ativos = [tx for t0, t1, tx in self.carimbos if t0 <= t < t1]
        if not ativos or self.layout != 'depoimento':
            return z
        th = max(r1 - r0 for r0, r1, _ in (self._caixa_carimbo(tx) for tx in ativos))
        need = self._lim_carimbo() + (1 - self.P.get('carimbo_sob', 0.18)) * th * 0.80
        x, y, _ = self.track[min(fi, len(self.track) - 1)]
        topo_src = y - TOPO_K * self._hw_suave(fi)

        def topo(zz):
            top_ = min(max(y - fp[1] / zz, 0), src_h - self.PH / zz)
            return (topo_src - top_) * zz

        zz = z
        while zz > 1.0 and topo(zz) < need:
            zz -= 0.01
        return max(1.0, zz)

    def cortes(self):
        cuts = list(self.cutaways)
        if self.variante == 'B' and self.gancho:
            cuts = [(0.0, self.gancho['ate'])] + cuts
        return cuts

    # ---------------- áudio (igual à v1)
    def add_sfx(self, kind, t_out, db=None):
        self.sfx.append((kind, t_out, db))

    def build_audio(self, prefix):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', self.src, '-vn', '-ac', '1', '-ar', '48000',
                        '-f', 'f32le', f'{prefix}_a48.f32'], check=True)
        a = np.fromfile(f'{prefix}_a48.f32', dtype=np.float32)
        parts, fade, prev = [], int(0.010 * 48000), None
        for f0, f1, *_ in self.SEGF:
            seg = a[f0 * SPF:f1 * SPF].copy()
            if prev != f0:
                seg[:fade] *= np.linspace(0, 1, fade)
                if parts:
                    parts[-1][-fade:] *= np.linspace(1, 0, fade)
            parts.append(seg)
            prev = f1
        out = np.concatenate(parts)
        n = int(0.3 * 48000)
        out[-n:] *= np.linspace(1, 0, n)
        out.astype(np.float32).tofile(f'{prefix}_cut.f32')
        chain = ('highpass=f=80,afftdn=nr=12:nf=-42:tn=1,'
                 'equalizer=f=170:t=q:w=1.0:g=1.8,equalizer=f=400:t=q:w=1.2:g=-2.0,'
                 'equalizer=f=3300:t=q:w=1.1:g=2.4,equalizer=f=9500:t=q:w=1.0:g=1.2,deesser=i=0.35,'
                 'acompressor=threshold=0.08:ratio=3.2:attack=5:release=110:makeup=1.7')
        r = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'f32le', '-ar', '48000', '-ac', '1', '-i',
                            f'{prefix}_cut.f32', '-af', chain + ',loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json',
                            '-f', 'null', '-'], capture_output=True, text=True)
        m = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
        ln = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', '48000', '-ac', '1', '-i',
                        f'{prefix}_cut.f32', '-af', chain + ',' + ln + ',aresample=48000', '-f', 'f32le',
                        f'{prefix}_voice.f32'], check=True)
        v = np.fromfile(f'{prefix}_voice.f32', dtype=np.float32)
        fx = np.zeros_like(v)
        sfx = list(self.sfx)
        if self.gancho:
            sfx.append(('hit', 0.02, -19))                 # impacto no frame 0
        for t0, _t1, _tx in self.carimbos:
            sfx.append(('hit', t0, -21))
        for kind, t0, db in sfx:
            s = SFX[kind] * (10 ** ((db if db is not None else SFX_DB[kind]) / 20))
            i0 = int(t0 * 48000)
            if kind == 'whoosh':
                i0 -= int(0.30 * 48000)
            i0 = max(0, i0)
            i1 = min(len(fx), i0 + len(s))
            fx[i0:i1] += s[:i1 - i0]
        (v + fx).astype(np.float32).tofile(f'{prefix}_mix.f32')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', '48000', '-ac', '1', '-i',
                        f'{prefix}_mix.f32', '-af', 'alimiter=limit=0.84:attack=3:release=50:level=false',
                        '-ac', '2', '-c:a', 'pcm_s16le', f'{prefix}_final.wav'], check=True)
        print('audio ok', m['input_i'])

    # ---------------- imagem
    def zoom_at(self, seg, fi):
        f0, f1, z0, z1, _ = seg
        if z0 == z1:
            return z0
        p = (fi - f0) / max(1, f1 - f0 - 1)
        return z0 + (z1 - z0) * (p * p * (3 - 2 * p))

    def _hw_suave(self, fi):
        if getattr(self, '_hws', None) is None:
            hw = np.asarray(self.track, np.float32)[:, 2]
            k = 21
            pad = np.pad(hw, (k // 2, k // 2), mode='edge')
            self._hws = np.convolve(pad, np.ones(k) / k, mode='valid')
        return float(self._hws[min(fi, len(self._hws) - 1)])

    def pessoa_painel(self, frame, seg, fi, t, scene=None, PH=None, fp=None, zmul=1.0, carimbos=True):
        scene = scene or self.scene
        PH = PH or self.PH
        fp = fp or self.face_panel
        z = self.zbase * self.zoom_at(seg, fi) * zmul
        if self.zoom_abertura and seg is self.SEGF[0]:
            z *= 1 + 0.10 * smooth(min(t, 1.5) / 1.5)
        track = getattr(self, 'track', None)
        if track is not None and carimbos and self.carimbos:
            z = self._z_carimbo(t, z, fi, fp, frame.shape[0])
        fs = self.face_src
        fr = (self.face_r[0] * z, self.face_r[1] * z)
        if track is not None:
            x, y, hw = track[min(fi, len(track) - 1)]
            if self.retoque is not None:
                frame = self.retoque(frame, x, y, hw)
            sw, shh = frame.shape[1], frame.shape[0]
            left = min(max(x - fp[0] / z, 0), sw - W / z)
            top_ = min(max(y - fp[1] / z, 0), shh - PH / z)
            fs = (left + fp[0] / z, top_ + fp[1] / z)
            fr = (hw * 0.43 * z, hw * 0.55 * z)
        M = np.float32([[z, 0, fp[0] - z * fs[0]], [0, z, fp[1] - z * fs[1]]])
        p = cv2.warpAffine(frame, M, (W, PH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT,
                           borderValue=(200, 200, 205))
        valid = cv2.warpAffine(self._ones, M, (W, PH), flags=cv2.INTER_LINEAR)
        fpp = (fp[0], fp[1])
        topo = None
        if track is not None:
            fpp = (fp[0] + (x - fs[0]) * z, fp[1] + (y - fs[1]) * z)
            topo = fpp[1] - TOPO_K * self._hw_suave(fi) * z     # topo da cabeça (sem tremer)
        atras = self.camada_carimbos(t, fpp, fr, topo) if carimbos and PH == self.PH else None
        out = scene.composite(p, t, fpp, fr, valid, atras)
        b = cv2.GaussianBlur(out, (0, 0), 1.2)
        return cv2.addWeighted(out, 1.35, b, -0.35, 0)

    def draw_seam(self, frame):
        c = self.P['moldura']
        g = np.array(c, np.float32)
        frame[SEAM - 2:SEAM + 2] = c
        for k, a in enumerate((0.45, 0.25, 0.12)):
            for y in (SEAM - 3 - k, SEAM + 2 + k):
                frame[y] = (frame[y].astype(np.float32) * (1 - a) + g * a).astype(np.uint8)

    def compor(self, frame, seg, fi, t, oi, draw_top, hide_subs_until, top_source):
        cuts = self.cortes()
        if cuts and any(a <= t < b for a, b in cuts):
            out = (self._full_bg.frame(t + 3.0) * 255).astype(np.uint8)
            CY = 420
            draw_top(out[CY:CY + SEAM], t)
            a0 = max(a for a, b in cuts if a <= t < b)
            q = ease_out((t - a0) / 0.22) if t - a0 < 0.22 else 1.0
            sc = 1.15 * (1.06 - 0.06 * q)
            cyc = CY + 430
            M_ = np.float32([[sc, 0, 540 * (1 - sc)], [0, sc, cyc * (1 - sc)]])
            out = cv2.warpAffine(out, M_, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            if not self.draw_gancho(out, t, SUB_Y_CHEIA, size=84):
                self.draw_subs(out, t, max(hide_subs_until, self.fim_gancho()), y=SUB_Y_CHEIA)
            self.scene.matter.reset()
            return out, True
        if self.layout == 'depoimento':
            # no depoimento, draw_top é a PROVA: só aparece em tela cheia (versão B e cutaways).
            # Enfeites por cima da pessoa (selos extras, ícones) vão em R.extra(frame, t).
            out = self.pessoa_painel(frame, seg, fi, t)
            extra = getattr(self, 'extra', None)
            if extra:
                extra(out, t)
            self.draw_texto(out, t, hide_subs_until, self.sub_y, 1290)
            return out, False
        out = np.empty((H, W, 3), np.uint8)
        top = top_source(t) if top_source is not None else None
        out[:SEAM] = top if top is not None else (self.top_bg.frame(t + 3.0) * 255).astype(np.uint8)
        draw_top(out, t)
        out[SEAM:] = self.pessoa_painel(frame, seg, fi, t)
        self.draw_seam(out)
        self.draw_texto(out, t, hide_subs_until, self.sub_y, SEAM)
        return out, False

    def render(self, out_path, draw_top, prefix, preview=None, hide_subs_until=-1, top_source=None, part=None):
        plan = [(fi, seg) for seg in self.SEGF for fi in range(seg[0], seg[1])]
        vf = self.grade + ',scale=in_color_matrix=bt601:in_range=tv,format=rgb24'
        dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', self.src, '-vf', vf, '-f', 'rawvideo', '-pix_fmt',
                                'rgb24', '-'], stdout=subprocess.PIPE, bufsize=10 ** 8)
        enc = None
        venc = ['-vf', 'scale=out_color_matrix=bt601:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset',
                'medium', '-crf', '19', '-maxrate', '11M', '-bufsize', '22M', '-profile:v', 'high', '-colorspace',
                'bt470bg', '-color_primaries', 'bt470bg', '-color_trc', 'smpte170m', '-color_range', 'tv']
        raw = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r',
               str(FPS), '-i', '-']
        if preview is None and part is not None:
            enc = subprocess.Popen(raw + venc + [out_path], stdin=subprocess.PIPE)
        elif preview is None:
            enc = subprocess.Popen(raw + ['-i', f'{prefix}_final.wav'] + venc +
                                   ['-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', out_path],
                                   stdin=subprocess.PIPE)
        fsize = W * H * 3
        src_idx, frame = -1, None
        self._ones = None
        want = set(preview or [])
        prev_seg = None
        for oi, (fi, seg) in enumerate(plan):
            while src_idx < fi:
                buf = dec.stdout.read(fsize)
                if len(buf) < fsize:
                    break
                frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
                src_idx += 1
            if self._ones is None:
                self._ones = np.ones(frame.shape[:2], np.float32)
            if preview is not None and oi not in want:
                continue
            if part is not None:
                if oi < part[0]:
                    continue
                if oi >= part[1]:
                    break
                if oi == part[0]:
                    self.scene.matter.reset()
            if seg is not prev_seg:
                self.scene.matter.reset()
                if self.retoque is not None:
                    self.retoque.reset()
            prev_seg = seg
            t = oi / FPS
            out, cut = self.compor(frame, seg, fi, t, oi, draw_top, hide_subs_until, top_source)
            if cut:
                prev_seg = None
            self.draw_lower(out, t)
            self.draw_selos(out, t)
            if enc:
                enc.stdin.write(out.tobytes())
            else:
                Image.fromarray(out).save(f'{prefix}_p_{oi:04d}.jpg', quality=90)
                if oi >= max(want):
                    break
            if oi % 150 == 0:
                print(f'frame {oi}/{len(plan)}', flush=True)
        dec.stdout.close()
        dec.kill()
        if enc:
            enc.stdin.close()
            enc.wait()

    # ---------------- capa
    def capa(self, t, palavras, destaque, out_png):
        """Capa 1080x1920: você em tela cheia sobre o fundo do perfil + 3 palavras na faixa segura (384–1536)."""
        oi = int(round(t * FPS))
        plan = [(fi, seg) for seg in self.SEGF for fi in range(seg[0], seg[1])]
        fi, seg = plan[min(oi, len(plan) - 1)]
        r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{fi / FPS:.3f}', '-i', self.src, '-frames:v', '1',
                            '-vf', self.grade + ',scale=in_color_matrix=bt601:in_range=tv,format=rgb24',
                            '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True)
        frame = np.frombuffer(r.stdout[:W * H * 3], np.uint8).reshape(H, W, 3)
        self._ones = np.ones(frame.shape[:2], np.float32)
        if self.retoque is not None:
            self.retoque.reset()
        P = self.P
        cena = pessoa.Scene(W, H, P['fundo'] if self.layout == 'dividida' else 'real', P['rim'])
        zb = self.zbase
        if self.layout == 'dividida':
            self.zbase = zb * 1.10
        out = self.pessoa_painel(frame, seg, fi, 2.0, scene=cena, PH=H, fp=(540, 600), carimbos=False)
        self.zbase = zb
        g = np.clip((np.arange(H, dtype=np.float32) - 980) / 700, 0, 1) ** 1.3 * 0.82
        out = (out.astype(np.float32) * (1 - g[:, None, None])).astype(np.uint8)
        fp = P['fonte_carimbo'] if P['carimbo_cor'] == 'alerta' else P['fonte_gancho']
        im = texto_palavras(palavras, fp, 190, WHITE, P['destaque'], destaque,
                            contorno=0.0, max_w=960, espaco=1.12, sombra=230)
        cy = 1490 - im.height / 2 + 40
        blend(out, im, W / 2, cy)
        Image.fromarray(out).save(out_png)
        return out_png


def G(ws, st='n', col=None, br=None):
    d = {'w': ws, 'st': st, 'col': col or {}}
    if br:
        d['br'] = br
    return d


def main(R, draw_top, name, top_source=None, hide_subs_until=-1):
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--B' in sys.argv:
        R.variante = 'B'
    cmd = args[0]
    pasta = os.path.join(TRABALHO, name)
    os.makedirs(pasta, exist_ok=True)
    prefix = os.path.join(pasta, 'work')
    print('duração: %.2fs (%d frames) · perfil %s · layout %s · versão %s'
          % (R.END, R.TOTAL, R.P['nome'], R.layout, R.variante))
    if cmd == 'audio':
        R.build_audio(prefix)
    elif cmd == 'preview':
        p = prefix + ('_B' if R.variante == 'B' else '')
        R.render(None, draw_top, p, [int(x) for x in args[1].split(',')], hide_subs_until, top_source)
    elif cmd == 'times':
        for x in args[1].split(','):
            print(x, round(R.T(float(x)) * FPS))
    elif cmd == 'render':
        R.render(args[1], draw_top, prefix, None, hide_subs_until, top_source)
    elif cmd == 'part':
        R.render(args[1], draw_top, prefix, None, hide_subs_until, top_source, part=(int(args[2]), int(args[3])))
    elif cmd == 'capa':
        palavras = args[2].split('|')
        destaque = args[3].split(',') if len(args) > 4 else ()
        R.capa(float(args[1]), palavras, destaque, args[-1])


# ------------------------------------------------------------------ extras
def chip(text, color=GREEN, fsize=40):
    return pill(text, icon=None, fsize=fsize, bg=(10, 22, 18, 215), border=color, h=82)


def tint_flash(frame, t, t0, color=(220, 30, 30), dur=0.45, strength=0.38, y1=SEAM):
    if not (t0 <= t < t0 + dur):
        return
    a = strength * (1 - (t - t0) / dur) ** 2
    roi = frame[:y1].astype(np.float32)
    frame[:y1] = (roi * (1 - a) + np.array(color, np.float32) * a).astype(np.uint8)


def hbar(frame, x, y, w_full, h, prog, color, label, value, alpha=1.0, label_size=40, value_size=46):
    """Barra horizontal com rótulo à esquerda (acima) e valor na ponta."""
    if alpha <= 0:
        return
    w = int(w_full * clamp01(prog))
    roi = frame[y:y + h, x:x + w_full].astype(np.float32)
    track = np.array([40, 46, 60], np.float32)
    roi[:] = roi * (1 - 0.55 * alpha) + track * 0.55 * alpha
    if w > 0:
        roi[:, :w] = roi[:, :w] * (1 - alpha) + np.array(color, np.float32) * alpha
    frame[y:y + h, x:x + w_full] = roi.astype(np.uint8)
    lab = number_img(label, label_size, WHITE, F_XB)
    blend(frame, lab, x + lab.width / 2 - 60, y - 36, alpha, 0, SEAM)
    if value:
        val = number_img(value, value_size, WHITE, F_BL)
        blend(frame, val, min(x + w + val.width / 2 - 40, x + w_full - val.width / 2 + 70), y + h / 2 + 2,
              alpha * clamp01(prog * 3), 0, SEAM)


def pin_row(text, idx, size=54):
    f = font(F_BL, size)
    w = int(f.getlength(text)) + 190
    im = Image.new('RGBA', (w, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 14, 84, 86], radius=16, fill=RED + (255,))
    d.text((45, 51), str(idx), font=font(F_BL, 44), anchor='mm', fill=WHITE + (255,))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((112, 54), text, font=f, anchor='lm', fill=(0, 0, 0, 200))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6))); out.alpha_composite(im)
    ImageDraw.Draw(out).text((108, 50), text, font=f, anchor='lm', fill=WHITE + (255,))
    return out
