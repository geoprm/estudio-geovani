"""Adereços de "Carta Sem Remetente" (Arquivo Morto, E01): envelope, carta, porta fechada/aberta, calendário, carimbo.

Tudo desenhado aqui (ficção). Uso, na raiz do estúdio:
  python arquivo_oculto/producao/arquivo_morto/AM-E01/aderecos.py
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
FONTES = AQUI.parents[2] / 'fonts'
MAO = ImageFont.truetype(str(AQUI / 'HomemadeApple-Regular.ttf'), 64)
MAO_P = ImageFont.truetype(str(AQUI / 'HomemadeApple-Regular.ttf'), 48)
ELITE = ImageFont.truetype(str(FONTES / 'special-elite-latin-400-normal.woff'), 46)
ELITE_P = ImageFont.truetype(str(FONTES / 'special-elite-latin-400-normal.woff'), 34)
ANTON = ImageFont.truetype(str(FONTES / 'anton-latin-400-normal.woff'), 120)
rng = np.random.default_rng(1979)


def papel(w, h, base=(214, 196, 160), manchas=14):
    a = np.ones((h, w, 3), np.float32) * np.array(base, np.float32)
    a += rng.normal(0, 7, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    for _ in range(manchas):                                  # manchas de umidade e dedos
        cx, cy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(40, 220)
        a -= (np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))) * rng.uniform(8, 30))[..., None]
    borda = np.minimum(np.minimum(xx, w - xx), np.minimum(yy, h - yy)) / 60.0
    a *= (0.78 + 0.22 * np.clip(borda, 0, 1))[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))


def tremer(d, xy, txt, fonte, cor, ang=0.0):
    """Escrita à mão com leve tremor por letra."""
    x, y = xy
    for ch in txt:
        dy = rng.normal(0, 1.6) + math.sin(x / 90) * 2
        d.text((x, y + dy), ch, font=fonte, fill=cor)
        x += fonte.getlength(ch) * rng.uniform(0.96, 1.04)
    return x


def carimbo_postal(tam, data):
    img = Image.new('RGBA', (tam, tam), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cor = (40, 30, 60, 220)
    d.ellipse((10, 10, tam - 10, tam - 10), outline=cor, width=8)
    d.ellipse((40, 40, tam - 40, tam - 40), outline=cor, width=4)
    f = ImageFont.truetype(str(FONTES / 'oswald-latin-700-normal.woff'), int(tam * 0.13))
    for txt, y in (('SERTÃO · BA', tam * 0.26), (data, tam * 0.44), ('AG. CENTRAL', tam * 0.62)):
        w = f.getlength(txt)
        d.text(((tam - w) / 2, y), txt, font=f, fill=cor)
    a = np.asarray(img).copy()
    a[..., 3] = np.where(rng.random(a.shape[:2]) < 0.22, (a[..., 3] * 0.3).astype(np.uint8), a[..., 3])
    return Image.fromarray(a, 'RGBA').rotate(14, resample=Image.BICUBIC)


def envelope():
    w, h = 1500, 900
    img = papel(w, h, (206, 190, 150)).convert('RGBA')
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (w / 2, h * 0.48), (w, 0)], outline=(150, 130, 95, 255), width=4)
    tremer(d, (380, 470), 'Para: Maria das Dores', MAO, (30, 30, 55, 255))
    tremer(d, (420, 580), 'Rua da Matriz, 41', MAO_P, (30, 30, 55, 255))
    tremer(d, (420, 660), 'Sertão da Bahia', MAO_P, (30, 30, 55, 255))
    d.rectangle((1230, 60, 1420, 270), fill=(170, 60, 50, 255), outline=(240, 230, 210, 255), width=8)
    d.text((1262, 120), '1,50', font=ELITE, fill=(240, 230, 210, 255))
    img.alpha_composite(carimbo_postal(330, '12 NOV 2026'), (1040, 40))
    return img


def verso():
    w, h = 1500, 900
    img = papel(w, h, (200, 184, 146)).convert('RGBA')
    d = ImageDraw.Draw(img)
    d.polygon([(0, h * 0.35), (w / 2, h), (w, h * 0.35)], outline=(150, 130, 95, 255), width=4)
    d.text((90, 110), 'REMETENTE:', font=ELITE, fill=(60, 50, 40, 255))
    d.line((380, 160, 1300, 160), fill=(90, 80, 60, 255), width=3)
    return img


def carta():
    w, h = 1200, 1600
    img = papel(w, h, (226, 214, 184), manchas=18).convert('RGBA')
    d = ImageDraw.Draw(img)
    for y in range(260, h - 120, 92):
        d.line((90, y, w - 90, y), fill=(150, 170, 190, 120), width=2)
    linhas = ['Filha,', 'me perdoa.', '', 'Eu deixei a porta', 'da cozinha aberta.', '', '', '            Mãe']
    y = 175
    for linha in linhas:
        if linha:
            tremer(d, (130, y), linha, MAO, (25, 25, 60, 255))
        y += 92
    return img


def porta(aberta):
    w, h = 1080, 1920
    a = np.ones((h, w, 3), np.float32) * np.array([24, 21, 19], np.float32)
    a += rng.normal(0, 4, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    x0, x1, y0, y1 = 300, 780, 520, 1640
    madeira = (rng.normal(0, 1, (1, x1 - x0)).repeat(y1 - y0, 0) * 9
               + np.sin(np.arange(y1 - y0)[:, None] / 7.0 + np.arange(x1 - x0)[None, :] / 40.0) * 4)
    porta_rgb = np.stack([44 + madeira, 31 + madeira * 0.8, 22 + madeira * 0.6], -1)
    if aberta:
        # a folha gira para dentro: fica estreita e escura; o vão vira um retângulo preto profundo
        fol = int((x1 - x0) * 0.42)
        a[y0:y1, x0:x1] = np.array([3, 3, 4])
        a[y0:y1, x0:x0 + fol] = porta_rgb[:, :fol] * 0.55
        frio = np.exp(-((xx - (x0 + fol + 30)) ** 2) / (2 * 30 ** 2)) * ((yy > y0) & (yy < y1))
        a += (frio * 70)[..., None] * np.array([0.7, 0.8, 1.0])
        chao = np.clip((yy - y1) / 280, 0, 1) * np.exp(-((xx - 560) ** 2) / (2 * 160 ** 2)) * (yy > y1)
        a += (chao * 80)[..., None] * np.array([0.7, 0.8, 1.0])
    else:
        a[y0:y1, x0:x1] = porta_rgb
        a[y0 + 6:y1 - 6, x0 + 30:x0 + 32] *= 0.5
        cy = (y0 + y1) // 2
        a[cy - 14:cy + 14, x1 - 60:x1 - 34] = np.array([120, 104, 70])
    a[y0 - 24:y0, x0 - 24:x1 + 24] = np.array([30, 24, 18])
    a[y0 - 24:y1, x0 - 24:x0] = np.array([30, 24, 18])
    a[y0 - 24:y1, x1:x1 + 24] = np.array([30, 24, 18])
    luz = np.exp(-(((xx - 540) ** 2) / (2 * 420 ** 2) + ((yy - 1300) ** 2) / (2 * 700 ** 2)))
    a *= (0.9 + 0.9 * luz)[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))


def calendario():
    w, h = 1000, 1300
    img = papel(w, h, (232, 226, 210), manchas=8).convert('RGBA')
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w, 210), fill=(150, 40, 36, 255))
    f = ImageFont.truetype(str(FONTES / 'oswald-latin-700-normal.woff'), 110)
    d.text((70, 40), 'NOVEMBRO 2026', font=f, fill=(245, 236, 220, 255))
    fd = ImageFont.truetype(str(FONTES / 'oswald-latin-700-normal.woff'), 64)
    dias = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S']
    for i, dd in enumerate(dias):
        d.text((70 + i * 128, 250), dd, font=fd, fill=(120, 40, 36, 255))
    dia = 1
    for semana in range(5):
        for col in range(7):
            if semana == 0 and col < 0:
                continue
            if dia > 30:
                break
            x, y = 70 + col * 128, 350 + semana * 170
            d.text((x, y), str(dia), font=fd, fill=(50, 45, 40, 255))
            if dia == 11:
                d.ellipse((x - 30, y - 18, x + 110, y + 100), outline=(170, 30, 30, 255), width=7)
            if dia < 11:
                d.line((x - 10, y + 10, x + 70, y + 80), fill=(60, 60, 60, 200), width=5)
                d.line((x + 70, y + 10, x - 10, y + 80), fill=(60, 60, 60, 200), width=5)
            dia += 1
    return img


def carimbo_close():
    img = papel(1080, 1080, (206, 190, 150)).convert('RGBA')
    img.alpha_composite(carimbo_postal(900, '12 NOV 2026'), (90, 90))
    return img


if __name__ == '__main__':
    for nome, im in (('envelope.png', envelope()), ('verso.png', verso()), ('carta.png', carta()),
                     ('porta_fechada.png', porta(False)), ('porta_aberta.png', porta(True)),
                     ('calendario.png', calendario()), ('carimbo_close.png', carimbo_close())):
        im.convert('RGB').save(AQUI / nome)
        print(nome, im.size)
