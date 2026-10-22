"""Recorte da pessoa, tratamento do rosto e composição sobre o fundo do perfil.

Novidade da v2: uma camada 'atras' (RGBA) entra ENTRE o fundo e a pessoa,
o que permite a palavra-carimbo atrás da cabeça.
"""
import os
import numpy as np
import cv2
import fundos
from perfis import RAIZ
from ai_edge_litert.interpreter import Interpreter

_it = Interpreter(model_path=os.path.join(RAIZ, 'modelos', 'selfie_segmentation.tflite'))
_it.allocate_tensors()
_ii = _it.get_input_details()[0]['index']
_oi = _it.get_output_details()[0]['index']


def sstep(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def guided(I, p, r, eps):
    bf = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp = bf(I), bf(p)
    a = (bf(I * p) - mI * mp) / (bf(I * I) - mI * mI + eps)
    b = mp - a * mI
    return bf(a) * I + bf(b)


def raw_mask(img):
    x = cv2.resize(img, (256, 256), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.
    _it.set_tensor(_ii, x[None]); _it.invoke()
    return _it.get_tensor(_oi)[0, :, :, 0]


class Matter:
    """Máscara com refinamento por guided filter e suavização temporal."""
    def __init__(self):
        self.prev = None

    def reset(self):
        self.prev = None

    def __call__(self, img, valid=None):
        h, w = img.shape[:2]
        m = raw_mask(img)
        if self.prev is not None:
            m = 0.55 * m + 0.45 * self.prev
        self.prev = m
        m = cv2.resize(m, (w // 2, h // 2), interpolation=cv2.INTER_LINEAR)
        g = cv2.cvtColor(cv2.resize(img, (w // 2, h // 2), interpolation=cv2.INTER_AREA),
                         cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
        m = guided(g, m, 6, 2e-3)
        m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
        a = sstep(m, 0.30, 0.70)
        if valid is not None:
            a = a * valid
        return cv2.GaussianBlur(a, (0, 0), 1.0)


_ell = {}


def ellipse(h, w, c, r, k=0.9, off=1.6, blur=0):
    q = lambda v: int(round(v / 6.0) * 6)
    c = (q(c[0]), q(c[1])); r = (max(6, q(r[0])), max(6, q(r[1])))
    key = (h, w, c[0], c[1], r[0], r[1], k, off, blur)
    if key not in _ell:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        e = ((xx - c[0]) / r[0]) ** 2 + ((yy - c[1]) / r[1]) ** 2
        v = np.clip(off - e * k, 0, 1).astype(np.float32)
        if blur:
            v = cv2.GaussianBlur(v, (0, 0), blur)
        if len(_ell) > 300:
            _ell.clear()
        _ell[key] = v
    return _ell[key]


def deshine(f, a, face_c, face_r):
    h, w = f.shape[:2]
    hs = cv2.resize(f, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    hsv_s = cv2.cvtColor((hs * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    Hh, Ss, Vs = hsv_s[..., 0], hsv_s[..., 1] / 255, hsv_s[..., 2] / 255
    ell = ellipse(h // 2, w // 2, (face_c[0] / 2, face_c[1] / 2), (face_r[0] / 2, face_r[1] / 2))
    skin = ((Hh < 22) | (Hh > 170)).astype(np.float32)
    hi = sstep(Vs, 0.60, 0.85) * np.clip((0.45 - Ss) / 0.25 + 0.5, 0, 1)
    a2 = cv2.resize(a, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    k = cv2.GaussianBlur(hi * skin * ell * a2, (0, 0), 3.5)
    k = cv2.resize(k, (w, h), interpolation=cv2.INTER_LINEAR)[..., None]
    V = f.max(axis=2, keepdims=True)
    target = V - k * (V - 0.58) * 0.55
    scale = np.where(V > 1e-3, target / np.maximum(V, 1e-3), 1.0)
    out = f * scale
    g = out.mean(axis=2, keepdims=True)
    return out + (out - g) * (k * 0.25)


def relight(f, a, face_c, face_r, gain=0.10):
    h, w = f.shape[:2]
    key = ellipse(h, w, (face_c[0] - 0.15 * face_r[0], face_c[1] - 0.1 * face_r[1]),
                  (face_r[0] * 2.2, face_r[1] * 2.0), k=0.55, off=1.0, blur=25)[..., None]
    warm = np.array([1.015, 1.0, 0.975], np.float32)
    f = f * (1 + gain * key) * (warm * key + (1 - key))
    body = ellipse(h, w, (face_c[0], face_c[1] + 2.4 * face_r[1]), (w * 0.9, h * 0.75), k=0.6, off=1.2)
    return f * (0.86 + 0.14 * body[..., None])


class Scene:
    """fundo: 'bandeira' | 'marinho' | 'real' (mantém o cenário gravado, levemente desfocado)."""
    def __init__(self, W, H, fundo='bandeira', rim=(1.0, 0.80, 0.45)):
        self.W, self.H, self.fundo = W, H, fundo
        self.bg = fundos.criar(fundo, W, H)
        self.matter = Matter()
        self.rim = np.array(rim, np.float32)

    def composite(self, panel, t, face_c, face_r, valid=None, atras=None):
        a = self.matter(panel, valid)
        f = panel.astype(np.float32) / 255
        f = deshine(f, a, face_c, face_r)
        f = relight(f, a, face_c, face_r)
        f = np.clip(f + (f - 0.5) * 0.10, 0, 1)
        f = np.clip((f - 0.02) / 0.98, 0, 1)
        g = f.mean(axis=2, keepdims=True)
        f = g + (f - g) * 0.97
        if self.bg is None:
            # cenário real: desfoque leve e um pouco mais escuro para destacar a pessoa
            bg = cv2.GaussianBlur(panel, (0, 0), 2.2).astype(np.float32) / 255 * 0.88
        else:
            bg = self.bg.frame(t)
        if atras is not None:
            al = atras[..., 3:4]
            bg = bg * (1 - al) + atras[..., :3] * al
        if self.bg is not None:
            outer = np.clip(cv2.GaussianBlur(a, (0, 0), 14) - a, 0, 1)
            bg = bg + self.rim * outer[..., None] * 0.22
            inner = np.clip(a - cv2.GaussianBlur(a, (0, 0), 5), 0, 1)
            f = f + self.rim * inner[..., None] * 0.30
        out = f * a[..., None] + bg * (1 - a[..., None])
        return (np.clip(out, 0, 1) * 255).astype(np.uint8)
