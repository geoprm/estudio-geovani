"""Fundos animados: bandeira LED (techbg) e estúdio azul-marinho com brilho dourado."""
import math
import numpy as np
import cv2
import techbg


class Marinho:
    """Azul-marinho profundo, luz suave atrás da pessoa e bokeh dourado que deriva devagar."""
    def __init__(self, W, H, seed=3, n=16):
        self.W, self.H = W, H
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        top = np.array([3, 11, 30], np.float32) / 255      # #030B1E
        mid = np.array([12, 30, 66], np.float32) / 255
        g = np.clip(1 - np.abs(yy / H - 0.42) * 1.6, 0, 1)[..., None]
        base = top * (1 - g) + mid * g
        # luz de recorte atrás da cabeça
        cx, cy = W * 0.5, H * 0.36
        d = np.sqrt(((xx - cx) / (W * 0.55)) ** 2 + ((yy - cy) / (H * 0.42)) ** 2)
        glow = np.clip(1 - d, 0, 1) ** 2 * 0.22
        base = base + np.array([0.20, 0.28, 0.45], np.float32) * glow[..., None]
        vig = np.clip(1 - (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.8)) ** 2) * 0.55, 0.45, 1)
        self.base = (base * vig[..., None]).astype(np.float32)
        rng = np.random.default_rng(seed)
        self.dots = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(14, 46), rng.uniform(0.15, 0.55),
                      rng.uniform(0, 2 * math.pi), rng.uniform(6, 18)) for _ in range(n)]

    def frame(self, t):
        h2, w2 = self.H // 4, self.W // 4
        layer = np.zeros((h2, w2), np.float32)
        for x, y, r, a, ph, sp in self.dots:
            xx = (x + sp * t * 2.0 + 18 * math.sin(t * 0.4 + ph)) % self.W
            yy = (y - sp * t * 1.2) % self.H
            cv2.circle(layer, (int(xx / 4), int(yy / 4)), max(2, int(r / 4)),
                       a * (0.75 + 0.25 * math.sin(t * 1.3 + ph)), -1, cv2.LINE_AA)
        layer = cv2.GaussianBlur(layer, (0, 0), 3.0)
        layer = cv2.resize(layer, (self.W, self.H), interpolation=cv2.INTER_LINEAR)
        gold = np.array([0.90, 0.66, 0.24], np.float32)
        return np.clip(self.base + layer[..., None] * gold * 0.35, 0, 1)


def criar(tipo, W, H, **kw):
    if tipo == 'bandeira':
        return techbg.TechFlag(W, H, strength=kw.get('strength', 0.58), seed=kw.get('seed', 1))
    if tipo == 'marinho':
        return Marinho(W, H)
    return None  # 'real': mantém o cenário gravado
