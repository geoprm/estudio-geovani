"""O Arquivista como ATOR (perfil V2): atuação 2,5D em camadas a partir da referência canônica.

Camadas com profundidade própria: fundo do arquivo (inpaint, lanternas), personagem (recortado por arq_alpha.png)
e objetos da mesa (globo, livros, ampulheta) à frente. A câmera desloca cada camada com paralaxe real.
O corpo atua por transformações rígidas e deformações suaves: caminhar com balanço de passo, inclinar-se,
girar a cabeça (giro 3D aproximado por elipsoide), baixar o olhar, sair para a sombra.
Nos planos com autorização de fala, a boca da máscara se articula pela energia da voz.

Planos (gramática do GUIA_DE_CENAS_E_MOVIMENTOS): aparicao (A1), corredor (A2), olhar_camera, virar_cabeca,
ombro (A3/A4 sobre o ombro com foco seletivo), debrucar (A5/A4), silencio (A7), encerramento (A8).
Não é vídeo generativo: o modo é registrado como performance_2_5d.
"""
import json
import math
import os

import cv2
import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
AO = os.path.dirname(AQUI)
REF = os.environ.get('AO_ARQ', os.path.join(AO, 'assets', 'arquivista.png'))
ALPHA = os.environ.get('AO_ALPHA', os.path.join(AO, 'assets', 'arq_alpha.png'))
LMK = os.environ.get('AO_LMK', os.path.join(AO, 'assets', 'arq_lmk106.json'))

CABECA = (472.0, 430.0)          # centro do rosto na referência (pixels da imagem 941x1672)
GANHO_TELA = 1.14                # +14% de exposição nos planos do personagem (QA 04/11: escuros demais para celular)
OLHOS = [(426, 433), (531, 431)]


def ease(k):
    k = min(1.0, max(0.0, k))
    return k * k * (3 - 2 * k)


def janela(k, a, b):
    """0 antes de a, 1 depois de b, suave no meio."""
    return ease((k - a) / max(1e-6, b - a))


def mascara_marfim_ouro(rgb):
    """Máscara marfim envelhecida mantendo os veios e reflexos dourados da referência premium."""
    a = rgb.astype(np.float32)
    h, w = a.shape[:2]
    if not os.path.exists(LMK):
        return a
    lm = np.array(json.load(open(LMK)), np.float32)
    cont = lm[0:33]; topo = lm[:, 1].min()
    alto = np.array([[x, topo - (cont[:, 1].max() - y) * 0.55] for x, y in cont[::2]], np.float32)
    hull = cv2.convexHull(np.vstack([cont, alto]).astype(np.int32))
    m = np.zeros((h, w), np.float32)
    cv2.fillConvexPoly(m, hull, 1.0)
    lum = a.mean(axis=2)
    m *= np.clip((lum - 35) / 50, 0, 1)
    m = cv2.GaussianBlur(m, (0, 0), 4)[..., None]
    ref = max(1.0, float(np.percentile(lum[m[..., 0] > 0.5], 97)))
    L = np.clip(lum / ref, 0, 1.05)[..., None]
    marfim = np.array([236, 226, 204], np.float32) * L ** 0.82          # marfim quente, envelhecido
    # veios e bordas douradas: alta frequência + saturação da referência
    sat = (a.max(axis=2) - a.min(axis=2))[..., None] / 255.0
    det = np.abs(lum - cv2.GaussianBlur(lum, (0, 0), 3))[..., None] / 40.0
    ouro = np.clip(sat * 1.6 + det * 0.8, 0, 1) * 0.55
    pele = marfim * (1 - ouro) + a * 1.08 * ouro
    # pátina: sombra levemente esverdeada/sépia nas reentrâncias
    pele *= (0.92 + 0.08 * L)
    return a * (1 - m) + pele * m


class Atores:
    """Prepara as camadas uma vez; render_quadro(plano, k, t) devolve um quadro RGB float32 na resolução pedida."""

    def __init__(self, W=1080, H=1920, mascara='marfim_ouro'):
        self.W, self.H = W, H
        src = np.asarray(Image.open(REF).convert('RGB'), np.float32)
        if mascara == 'marfim_ouro':
            src = mascara_marfim_ouro(src)
        # leve correção de contraste do cânone (mesma do motor V1)
        src = np.clip((src - 128) * 1.10 + 128 - 6, 0, 255)
        h, w = src.shape[:2]
        self.h, self.w = h, w
        a = cv2.imread(ALPHA, 0)
        a = cv2.resize(a, (w, h)).astype(np.float32) / 255.0
        a = cv2.GaussianBlur(np.clip((a - 0.35) / 0.3, 0, 1), (0, 0), 1.6)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        self.xx, self.yy = xx, yy
        # contraluz (rim): borda externa superior/lateral da silhueta
        borda = np.clip(a - cv2.GaussianBlur(a, (0, 0), 7), 0, 1)
        rim = cv2.GaussianBlur(borda, (0, 0), 2.5) * np.clip((1250 - yy) / 600, 0, 1)
        self.fig = np.dstack([src, a * 255, rim * 255]).astype(np.float32)   # RGB + alfa + rim
        # objetos da mesa à frente da figura
        zona = np.zeros((h, w), np.float32)
        zona[yy > 1290] = 1
        zona[(xx < 160) & (yy > 700)] = 1
        zona[(xx > 740) & (yy > 1020)] = 1
        zona[(yy > 1020) & (yy <= 1290) & ((xx < 260) | (xx > 700))] = 1
        zona = cv2.GaussianBlur(zona, (0, 0), 6)
        fg_a = np.clip(zona * (1 - a) * 1.4, 0, 1)
        self.fg = np.dstack([src, fg_a * 255]).astype(np.float32)
        # fundo sem a figura (inpaint em 1/3, suavizado)
        small = cv2.resize(src.astype(np.uint8), (w // 3, h // 3))
        msk = (cv2.resize(a, (w // 3, h // 3)) > 0.12).astype(np.uint8) * 255
        msk = cv2.dilate(msk, np.ones((11, 11), np.uint8))
        bg = cv2.inpaint(small, msk, 9, cv2.INPAINT_TELEA)
        bg = cv2.GaussianBlur(cv2.resize(bg, (w, h), interpolation=cv2.INTER_CUBIC), (0, 0), 2.5).astype(np.float32)
        g = lambda cx, cy, rx, ry: np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))
        self.bg = bg * 0.88
        self.bg_luz = (g(135, 120, 90, 130) + g(470, 150, 150, 120) * 0.8 + g(820, 420, 70, 90) * 0.5)[..., None]
        # pesos da cabeça (capuz + máscara), sem arrastar mãos e tronco
        cx, cy = CABECA
        r2 = ((xx - cx) / 235) ** 2 + ((yy - (cy - 30)) / 330) ** 2
        self.w_cab = (np.clip(1.35 - r2, 0, 1) * np.clip((655 - yy) / 95, 0, 1)).astype(np.float32)
        self.prof = (175 * np.sqrt(np.clip(1 - ((xx - cx) / 190) ** 2 - ((yy - cy) / 260) ** 2, 0, 1))).astype(np.float32)
        self.junta_boca = ((yy - 546) * np.clip(1 - ((xx - 483) / 47) ** 2 - ((yy - 546) / 24) ** 2,
                                                0, 1)).astype(np.float32)
        rng = np.random.default_rng(11)
        self.poeira = rng.uniform([0, 0, 0.6, 0], [w, h * 0.85, 2.4, 6.28], (90, 4))
        # pilares escuros de estante para travelling (camada mais próxima que a figura)
        self.pilares = rng.uniform(0, 1, 7)

    # ------------------------------------------------------------------ deformação da cabeça (rígida)
    def cabeca(self, yaw_deg=0.0, pitch_deg=0.0, roll_deg=0.0, fala=0.0):
        fig = self.fig
        if abs(yaw_deg) < 0.05 and abs(pitch_deg) < 0.05 and abs(roll_deg) < 0.05 and fala == 0:
            return fig
        th, ph, ro = math.radians(yaw_deg), math.radians(pitch_deg), math.radians(roll_deg)
        cx, cy = CABECA
        dx = self.xx - cx; dy = self.yy - cy; z = self.prof
        # deslocamento direto (aprox. pequena rotação de um elipsoide) aplicado como mapa inverso
        fx = dx * (math.cos(th) - 1) + z * math.sin(th) - dy * math.sin(ro)
        fy = dy * (math.cos(ph) - 1) + z * math.sin(ph) * 0.7 + dx * math.sin(ro)
        mx = (self.xx - self.w_cab * fx).astype(np.float32)
        my = (self.yy - self.w_cab * fy).astype(np.float32)
        if fala > 0:
            my -= self.junta_boca * (0.74 * fala)
        out = cv2.remap(fig, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        # sombreamento: rosto entra no capuz ao baixar a cabeça; lado oposto à lanterna escurece ao girar
        sh = 1 - self.w_cab * (0.30 * max(0.0, math.sin(ph)) - 0.22 * math.sin(th) * np.clip(dx / 200, -1, 1))
        out[..., :3] *= np.clip(sh, 0.55, 1.2)[..., None]
        return out

    # ------------------------------------------------------------------ composição de um quadro
    def compor(self, cam, corpo, luz, t):
        """cam: centro (cx, cy) em pixels da referência, escala s (px de tela por px de referência), deslocamentos
        de câmera para paralaxe (tx, ty) e zoom relativo dz. corpo: dx, dy, escala, rot, yaw, pitch, roll.
        luz: exposicao, figura (0 silhueta..1), rim, lanterna, spot (x, y, raio, ganho) em px de tela."""
        W, H = self.W, self.H
        cx, cy, s = cam['cx'], cam['cy'], cam['s']
        tx, ty, dz = cam.get('tx', 0.0), cam.get('ty', 0.0), cam.get('dz', 0.0)

        def M(par, extra=None):
            sc = s * (1 + dz * par)
            ox = cx + tx * par; oy = cy + ty * par
            A = np.array([[sc, 0, W / 2 - ox * sc], [0, sc, H / 2 - oy * sc]], np.float32)
            if extra is not None:
                A = A @ np.vstack([extra, [0, 0, 1]])
            return A

        # fundo
        fl = 0.78 + 0.22 * math.sin(t * 7.3) * math.sin(t * 2.9 + 1)
        bg = self.bg * luz.get('fundo', 1.0) + self.bg_luz * np.array([70, 40, 12], np.float32) * fl * luz.get('lanterna', 1.0)
        out = cv2.warpAffine(bg, M(0.55), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # figura: cabeça + corpo
        if luz.get('figura', 1.0) > 0.001 or luz.get('rim', 0) > 0.001:
            fig = self.cabeca(corpo.get('yaw', 0), corpo.get('pitch', 0), corpo.get('roll', 0), corpo.get('fala', 0))
            ax, ay = 470.0, 1300.0                      # âncora do corpo (cintura atrás da mesa)
            rot = math.radians(corpo.get('rot', 0)); e = corpo.get('escala', 1.0)
            B = np.array([[e * math.cos(rot), -e * math.sin(rot), 0], [e * math.sin(rot), e * math.cos(rot), 0]], np.float32)
            B[:, 2] = [ax + corpo.get('dx', 0) - (B[0, 0] * ax + B[0, 1] * ay), ay + corpo.get('dy', 0) - (B[1, 0] * ax + B[1, 1] * ay)]
            f = cv2.warpAffine(fig, M(1.0, B), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            al = f[..., 3:4] / 255.0
            rgb = f[..., :3] * luz.get('figura', 1.0)
            rim = f[..., 4:5] / 255.0 * luz.get('rim', 0.35)
            rgb = rgb + rim * np.array([255, 178, 92], np.float32) * 1.6
            out = out * (1 - al) + rgb * al
        # objetos da mesa
        if luz.get('mesa', 1.0) > 0.001:
            g = cv2.warpAffine(self.fg, M(1.35), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            al = g[..., 3:4] / 255.0 * luz.get('mesa', 1.0)
            out = out * (1 - al) + g[..., :3] * luz.get('mesa_luz', 1.0) * al
        # poeira na luz
        for (x, y, r, ph) in self.poeira:
            yy = (y - t * 14 * r) % (self.h * 0.85); xx = x + 18 * math.sin(t * 0.6 + ph)
            A = M(0.8)
            px = A[0, 0] * xx + A[0, 2]; py = A[1, 1] * yy + A[1, 2]
            xi, yi = int(px), int(py)
            if 3 <= xi < W - 3 and 3 <= yi < H - 3:
                out[yi - 1:yi + 2, xi - 1:xi + 2] += np.array([90, 70, 40], np.float32) * (0.4 + 0.6 * math.sin(t * 2 + ph) ** 2)
        # montantes de estante em primeiro plano (travelling): faixas escuras de borda suave, com fio de luz
        if cam.get('pilares') is not None:
            xs = np.arange(W, dtype=np.float32)
            perfil = np.ones(W, np.float32); brilho = np.zeros(W, np.float32)
            for i in range(3):
                xc = ((self.pilares[i] * 1.7 + i * 0.85 - cam['pilares'] * 0.9) % 2.4 - 0.7) * W
                larg = 70 + 40 * i
                perfil *= 1 - 0.88 * np.exp(-((xs - xc) / larg) ** 4)
                brilho += np.exp(-((xs - (xc - larg * 1.05)) / 9) ** 2) * 0.5
            out = out * perfil[None, :, None] + brilho[None, :, None] * np.array([120, 80, 35], np.float32)
        # luz de destaque
        if luz.get('spot'):
            sx, sy, sr, sg = luz['spot']
            yy, xx = np.ogrid[:H, :W]
            g = np.exp(-(((xx - sx) ** 2 + (yy - sy) ** 2) / (2 * sr * sr))).astype(np.float32)
            out = out * (1 - 0.55 * sg + 0.55 * sg * (0.35 + 1.25 * g[..., None]))
        return out * luz.get('exposicao', 1.0) * GANHO_TELA

    # ------------------------------------------------------------------ planos de atuação
    def plano(self, tipo, k, t, dur, p=None):
        """Parâmetros de câmera/corpo/luz do plano `tipo` no progresso k (0..1)."""
        p = p or {}
        hz = self.H
        br = math.sin(2 * math.pi * t / 4.2)               # respiração
        sw = math.sin(2 * math.pi * t / 6.1)               # balanço lento
        corpo = {'dx': 0, 'dy': 1.5 * br, 'escala': 1 + 0.004 * br, 'rot': 0.25 * sw, 'yaw': 0, 'pitch': 0, 'roll': 0.4 * sw}
        luz = {'exposicao': 1.0, 'figura': 1.0, 'rim': 0.35, 'lanterna': 1.0, 'mesa': 1.0}
        if tipo == 'aparicao':          # A1: sai da sombra, para e olha para a lente; dolly-in discreto
            altura = p.get('altura', 980)
            s = hz / altura * (1 + 0.10 * ease(k))
            cam = {'cx': 472, 'cy': 560 - 40 * ease(k), 's': s, 'dz': 0.06 * ease(k)}
            e = janela(k, 0.05, 0.62)
            luz.update(figura=0.06 + 0.94 * e, rim=1.0 - 0.6 * e, lanterna=0.25 + 0.75 * e, fundo=0.45 + 0.55 * e,
                       exposicao=0.35 + 0.65 * janela(k, 0, 0.25))
            corpo.update(dy=40 * (1 - e), escala=0.97 + 0.03 * e, pitch=11 * (1 - janela(k, 0.45, 0.85)),
                         yaw=-7 * (1 - janela(k, 0.4, 0.9)))
        elif tipo == 'corredor':        # A2: caminha entre fichários; travelling lateral com pilares
            altura = p.get('altura', 1050)
            s = hz / altura
            d = p.get('direcao', 1)
            cam = {'cx': 470 + d * 160 * (k - 0.5), 'cy': 560, 's': s, 'tx': d * 220 * (k - 0.5), 'pilares': d * k * dur / 3.0}
            passo = abs(math.sin(math.pi * 1.8 * t))
            corpo.update(dx=d * 330 * (k - 0.5), dy=-9 * passo + 4, rot=1.1 * math.sin(math.pi * 1.8 * t),
                         yaw=-d * 9 * (1 - janela(k, 0.55, 0.95)), pitch=4, roll=0.8 * math.sin(math.pi * 1.8 * t))
            pos = 0.5 + 0.5 * math.cos(2 * math.pi * (k * 1.3 + 0.2))
            luz.update(figura=0.78 + 0.27 * pos, rim=0.7, mesa=0.0, lanterna=0.8 + 0.4 * pos)
        elif tipo == 'olhar_camera':    # vira da prova para a lente; micro push-in
            altura = p.get('altura', 640)
            s = hz / altura * (1 + 0.06 * ease(k))
            cam = {'cx': 474, 'cy': 470, 's': s, 'dz': 0.03 * k}
            v = janela(k, 0.12, 0.6)
            corpo.update(yaw=p.get('de_yaw', 13) * (1 - v), pitch=9 * (1 - v), roll=1.2 * (1 - v) + 0.3 * sw)
            luz.update(rim=0.45, mesa=0.0)
        elif tipo == 'virar_cabeca':    # reage a uma prova: gira a cabeça e baixa o olhar; câmera orbita
            altura = p.get('altura', 1150)
            s = hz / altura * (1 + 0.05 * ease(k))
            d = p.get('lado', -1)
            cam = {'cx': 470 - d * 60 * ease(k), 'cy': 700, 's': s, 'tx': -d * 120 * ease(k), 'dz': 0.04 * ease(k)}
            v = janela(k, 0.15, 0.55)
            corpo.update(yaw=d * 15 * v, pitch=8 * v, roll=-d * 1.5 * v, dx=d * 12 * v, rot=-d * 0.8 * v)
            luz.update(spot=(self.W * (0.5 + d * 0.32), self.H * 0.62, 380, 0.7 * v))
        elif tipo == 'debrucar':        # inclina-se sobre a mesa; tilt da máscara para a mesa; luz revela a prova
            altura = p.get('altura', 1300)
            s = hz / altura * (1 + 0.08 * ease(k))
            cam = {'cx': 470, 'cy': 640 + 320 * ease(k), 's': s, 'ty': 90 * ease(k), 'dz': 0.05 * ease(k)}
            v = janela(k, 0.05, 0.7)
            corpo.update(escala=1 + 0.05 * v, dy=24 * v, pitch=14 * v, yaw=-3 * v)
            luz.update(spot=(self.W * 0.5, self.H * (0.80 - 0.18 * v), 420, 0.85 * v), mesa_luz=1.0 + 0.5 * v)
        elif tipo == 'silencio':        # A7: rosto imóvel numa batida dramática; push-in micro
            altura = p.get('altura', 420)
            s = hz / altura * (1 + 0.035 * k)
            cam = {'cx': 478, 'cy': 448, 's': s}
            corpo.update(yaw=0.6 * sw, pitch=1.0, roll=0.2 * sw, dy=0.8 * br)
            luz.update(lanterna=0.7 + 0.3 * math.sin(t * 1.7) ** 2, rim=0.3, mesa=0.0)
        elif tipo == 'encerramento':    # A8: recua, a luz apaga, ele some na sombra; pull-back
            altura = p.get('altura', 1100)
            s = hz / altura * (1.10 - 0.16 * ease(k))
            cam = {'cx': 470, 'cy': 650, 's': s, 'dz': -0.05 * ease(k)}
            v = janela(k, 0.25, 0.95)
            corpo.update(dy=-10 * v + 1.5 * br, escala=1 - 0.05 * v, pitch=-3 * v)
            luz.update(figura=1 - 0.95 * v, rim=0.35 + 0.65 * janela(k, 0.2, 0.5) - 0.9 * janela(k, 0.7, 1.0),
                       lanterna=1 - 0.9 * janela(k, 0.35, 0.8), fundo=1 - 0.75 * v, exposicao=1 - 0.55 * janela(k, 0.8, 1.0))
        elif tipo == 'ombro':           # base do over-the-shoulder (o renderer compõe a prova ao fundo)
            altura = p.get('altura', 900)
            s = hz / altura
            cam = {'cx': 470 + p.get('lado', 1) * -330, 'cy': 470, 's': s * 1.0}
            corpo.update(yaw=p.get('lado', 1) * 18, pitch=12)
            luz.update(rim=0.8, mesa=0.0, figura=0.7)
        else:
            raise ValueError(f'plano de atuação desconhecido: {tipo}')
        return cam, corpo, luz

    def quadro(self, tipo, k, t, dur, p=None, fala=0.0):
        cam, corpo, luz = self.plano(tipo, k, t, dur, p)
        if fala > 0:
            corpo['fala'] = fala
            corpo['pitch'] += 1.6 * fala
            corpo['roll'] += 0.4 * fala
        return self.compor(cam, corpo, luz, t)

    def ombro(self, k, t, prova, p=None):
        """Over-the-shoulder com foco seletivo: capuz desfocado em primeiro plano, prova (RGB float32 WxH) ao fundo."""
        p = p or {}
        W, H = self.W, self.H
        lado = p.get('lado', 1)
        foco = janela(k, 0.12, 0.5)                       # 0 = foco no capuz, 1 = foco na prova
        fundo = prova.copy()
        sig = 9 * (1 - foco) + 0.01
        if sig > 0.5:
            fundo = cv2.GaussianBlur(fundo, (0, 0), sig)
        cam, corpo, luz = self.plano('ombro', k, t, 1.0, p)
        s = H / p.get('altura', 1000) * (1.0 + 0.05 * ease(k))
        fig = self.cabeca(corpo['yaw'], corpo['pitch'], 0)
        # centro da cabeça na borda do quadro (lado = 1: direita; -1: esquerda), um pouco abaixo do meio
        alvo_x = W * (0.5 + lado * (0.47 - 0.03 * ease(k))); alvo_y = H * 0.46
        A = np.array([[s, 0, alvo_x - CABECA[0] * s], [0, s, alvo_y - CABECA[1] * s]], np.float32)
        f = cv2.warpAffine(fig, A, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        sb = 2 + 14 * foco
        f = cv2.GaussianBlur(f, (0, 0), sb)
        al = np.clip(f[..., 3:4] / 255.0 * 1.15, 0, 1)
        rgb = f[..., :3] * 0.45 + f[..., 4:5] / 255.0 * np.array([255, 170, 80], np.float32) * 0.9
        return fundo * (1 - al) + rgb * al
