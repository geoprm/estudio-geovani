"""Motor horizontal (16:9, 1920x1080) para os vídeos longos do Arquivo Oculto no YouTube.

Reaproveita todo o `reel_leve` (roteiro JSON, vozes Kokoro, carimbos, televisor, placar, Arquivista em atuação 2,5D),
trocando só o layout: legenda embaixo, título no alto, Arquivista centralizado sobre o próprio fundo desfocado e
exportação com mais qualidade (crf 19, até 9 Mb/s). Duração livre: o YouTube aceita até 15 min sem verificação do canal.

Uso (na raiz do estúdio):  python -m arquivo_oculto.v2.reel_longo <roteiro.json> <pasta de saída>
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import fundo_motor as fm
from . import reel_leve as rl

W, H = 1920, 1080


def _gradiente(lay):
    ys = np.arange(H, dtype=np.float32)
    a = np.clip((230 - ys) / 230, 0, 1) * 0.60 + np.clip((ys - 760) / 320, 0, 1) * 0.85
    g = np.zeros((H, W, 4), np.uint8)
    g[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)[:, None]
    lay.alpha_composite(Image.fromarray(g, 'RGBA'))


def camada_bloco(caminho, rot, b):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    _gradiente(lay)
    d = ImageDraw.Draw(lay)
    f = fm.fonte('cinzel', 28)
    t = rot['serie']
    d.text((W - 70 - f.getlength(t), 44), t, font=f, fill=fm.OURO + (210,))
    if b.get('credito'):
        fc = fm.fonte('oswald4', 22)
        linha = fm.quebrar(b['credito'], fc, 760)[:2]
        for i, l in enumerate(linha):
            d.text((W - 70 - fc.getlength(l), 86 + i * 28), l, font=fc, fill=fm.CREME + (205,))
    y = 40
    for s in [s for s in (rot.get('selo_fixo'), b.get('selo')) if s]:
        fs = fm.fonte('oswald', 28)
        cor = next((c for k, c in rl.SELO_COR.items() if s.startswith(k)), (150, 120, 70))
        w = fs.getlength(s)
        d.rounded_rectangle((70, y, 70 + w + 32, y + 48), 8, fill=(10, 8, 6, 210), outline=cor + (255,), width=3)
        d.text((86, y + 5), s, font=fs, fill=fm.CREME + (255,))
        y += 58
    if b.get('tela'):
        tam = 92
        while True:
            ft = fm.fonte('anton', tam)
            ls = fm.quebrar(b['tela'], ft, W - 560)
            if len(ls) <= 2 or tam < 60:
                break
            tam -= 6
        for i, linha in enumerate(ls):
            fm.texto_centro(d, W / 2, 140 + i * tam * 1.08, linha, ft, fm.OURO_CLARO + (255,), stroke=3,
                            stroke_cor=(20, 12, 4))
    lay.save(caminho)


def camada_legenda(caminho, txt):
    lay = Image.new('RGBA', (W, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tam = 54
    while True:
        f = fm.fonte('oswald', tam)
        ls = fm.quebrar(txt, f, W - 520)
        if len(ls) <= 2 or tam <= 40:
            break
        tam -= 4
    alt = int(tam * 1.3)
    for i, linha in enumerate(ls):
        wl = f.getlength(linha)
        d.rounded_rectangle((W / 2 - wl / 2 - 24, 10 + i * alt, W / 2 + wl / 2 + 24, 10 + i * alt + tam + 20), 12,
                            fill=(6, 5, 4, 120))
    for i, linha in enumerate(ls):
        fm.texto_centro(d, W / 2, 16 + i * alt, linha, f, fm.CREME + (255,), sombra=False, stroke=5, stroke_cor=(0, 0, 0))
    lay.save(caminho)


def camada_carimbo(caminho, txt):
    tmp = Image.new('RGBA', (1, 1))
    rl_W, rl_H = rl.W, rl.H
    # gera o carimbo com a função original num quadro vertical e reposiciona no horizontal
    rl.W, rl.H = 1080, 1920
    try:
        _carimbo_orig(caminho, txt)
    finally:
        rl.W, rl.H = rl_W, rl_H
    v = Image.open(caminho)
    caixa = v.getbbox() or (0, 0, 1, 1)
    peca = v.crop(caixa)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay.alpha_composite(peca, (W - peca.width - 140, 330))
    lay.save(caminho)
    del tmp


def cartao(caminho, linhas, sub=None, papel=False):
    base = Image.new('RGB', (W, H), (14, 11, 8))
    if papel:
        rng = np.random.default_rng(7)
        ruido = (rng.normal(0, 9, (H, W, 1)) + np.array([[[42, 34, 24]]])).clip(0, 255).astype(np.uint8)
        base = Image.fromarray(ruido).filter(ImageFilter.GaussianBlur(1.2))
    d = ImageDraw.Draw(base)
    f = fm.fonte('anton', 100)
    ls = [l2 for linha in linhas for l2 in fm.quebrar(linha, f, W - 420)]
    y = 470 - len(ls) * 58
    for l2 in ls:
        fm.texto_centro(d, W / 2, y, l2, f, fm.OURO_CLARO, stroke=3, stroke_cor=(20, 12, 4))
        y += 116
    if sub:
        f2 = fm.fonte('oswald4', 40)
        for l2 in fm.quebrar(sub, f2, W - 520):
            fm.texto_centro(d, W / 2, y + 24, l2, f2, fm.CREME)
            y += 52
    base.save(caminho)


def placar(caminho, contagem, titulo):
    base = Image.new('RGB', (W, H), (12, 10, 8))
    d = ImageDraw.Draw(base)
    fm.texto_centro(d, W / 2, 170, titulo, fm.fonte('anton', 84), fm.OURO_CLARO, stroke=3, stroke_cor=(20, 12, 4))
    y = 330
    for nome, n in contagem:
        cor = rl.CARIMBO_COR.get(nome, (150, 120, 70))
        d.rounded_rectangle((520, y, W - 520, y + 110), 14, fill=(22, 18, 14), outline=cor, width=5)
        d.text((560, y + 20), nome, font=fm.fonte('anton', 60), fill=cor)
        fn = fm.fonte('anton', 78)
        d.text((W - 560 - fn.getlength(str(n)), y + 8), str(n), font=fn, fill=fm.CREME)
        y += 136
    base.save(caminho)


def televisor(caminho):
    (tw, th), (tx, ty) = rl.CRT_TELA, rl.CRT_POS
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((tx - 60, ty - 50, tx + tw + 60, ty + th + 110), 60, fill=(28, 22, 18, 255),
                        outline=(70, 56, 40, 255), width=6)
    d.rounded_rectangle((tx - 30, ty - 22, tx + tw + 30, ty + th + 80), 50, fill=(12, 10, 9, 255))
    d.rounded_rectangle((tx, ty, tx + tw, ty + th), 70, fill=(0, 0, 0, 0))
    for x in (tx + tw - 140, tx + tw - 70):
        d.ellipse((x, ty + th + 30, x + 40, ty + th + 60), fill=(60, 48, 34, 255))
    lay.save(caminho)


_carimbo_orig = rl.camada_carimbo


def configurar():
    rl.W, rl.H, rl.LY = W, H, 872
    rl.FG_BOX, rl.FG_DY = (1500, 760), -20
    rl.CRT_TELA, rl.CRT_POS = (1000, 750), ((W - 1000) // 2, 90)
    rl.ATOR_X = (W - 608) // 2
    rl.ENC_FINAL = ['-crf', '19', '-maxrate', '9000k', '-bufsize', '18000k']
    rl._gradiente, rl.camada_bloco, rl.camada_legenda = _gradiente, camada_bloco, camada_legenda
    rl.camada_carimbo, rl.cartao, rl.placar, rl.televisor = camada_carimbo, cartao, placar, televisor


if __name__ == '__main__':
    configurar()
    rl.main()
