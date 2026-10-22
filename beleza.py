"""Rosto: pontos do rosto (MediaPipe face landmark), pele suavizada de leve e dentes/aparelho mais claros.

Tudo é sutil de propósito: a pessoa tem que continuar parecendo ela mesma.
"""
import os
import numpy as np
import cv2
from perfis import RAIZ
from ai_edge_litert.interpreter import Interpreter

_it = Interpreter(model_path=os.path.join(RAIZ, 'modelos', 'face_landmark.tflite'))
_it.allocate_tensors()
_inp = _it.get_input_details()[0]['index']
_outs = {o['name']: o['index'] for o in _it.get_output_details()}
_O_LM = _outs.get('conv2d_21')
_O_SC = _outs.get('conv2d_31')

# contornos (índices do MediaPipe Face Mesh)
BOCA_INTERNA = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
LABIOS_EXT = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
OLHO_E = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
OLHO_D = [263, 466, 388, 387, 386, 385, 384, 398, 362, 382, 381, 380, 374, 373, 390, 249]
SOBR_E = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
SOBR_D = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]
OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176,
        149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]


def _rodar(img, cx, cy, lado):
    s = 192.0 / lado
    M = np.float32([[s, 0, 96 - s * cx], [0, s, 96 - s * cy]])
    crop = cv2.warpAffine(img, M, (192, 192), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    x = crop.astype(np.float32)[None] / 255.0
    _it.set_tensor(_inp, x)
    _it.invoke()
    lm = _it.get_tensor(_O_LM).reshape(468, 3)[:, :2]
    sc = float(_it.get_tensor(_O_SC).reshape(-1)[0]) if _O_SC is not None else 10.0
    pts = np.stack([(lm[:, 0] - (96 - s * cx)) / s, (lm[:, 1] - (96 - s * cy)) / s], 1)
    return pts, 1 / (1 + np.exp(-sc))


class Rosto:
    """Acha os 468 pontos do rosto. Começa por uma estimativa (centro e largura da cabeça) e se ajusta."""
    def __init__(self):
        self.prev = None

    def reset(self):
        self.prev = None

    def __call__(self, img_u8, cx, cy, largura):
        if self.prev is not None:
            p = self.prev
            cx, cy = p[:, 0].mean(), p[:, 1].mean()
            lado = max(np.ptp(p[:, 0]), np.ptp(p[:, 1])) * 1.6
        else:
            lado = largura * 1.7
        pts, conf = _rodar(img_u8, cx, cy, lado)
        # segunda passada, centrada nos pontos achados
        cx2, cy2 = pts[:, 0].mean(), pts[:, 1].mean()
        lado2 = max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1])) * 1.6
        pts, conf = _rodar(img_u8, cx2, cy2, lado2)
        if conf < 0.5:
            self.prev = None
            return None
        if self.prev is not None:
            pts = 0.5 * pts + 0.5 * self.prev      # suaviza tremor entre quadros
        self.prev = pts
        return pts


def _poly(shape, pts, idx, blur=0):
    m = np.zeros(shape[:2], np.float32)
    cv2.fillPoly(m, [np.round(pts[idx]).astype(np.int32)], 1.0, cv2.LINE_AA)
    if blur:
        m = cv2.GaussianBlur(m, (0, 0), blur)
    return m


def _caixa(pts, idx, margem, w, h):
    p = pts[idx]
    x0, y0 = np.floor(p.min(0)).astype(int) - margem
    x1, y1 = np.ceil(p.max(0)).astype(int) + margem
    return max(0, x0), max(0, y0), min(w, x1), min(h, y1)


def embelezar(img, pts, forca=0.35):
    """Pele mais lisa e uniforme, sem apagar textura de barba, olhos, sobrancelhas e boca.
    img: uint8 RGB (alterada no lugar)."""
    if pts is None or forca <= 0:
        return img
    h, w = img.shape[:2]
    x0, y0, x1, y1 = _caixa(pts, OVAL, 12, w, h)
    if x1 - x0 < 40 or y1 - y0 < 40:
        return img
    u8 = img[y0:y1, x0:x1]
    p = pts - [x0, y0]
    face = _poly(u8.shape, p, OVAL, blur=5)
    keep = np.clip(_poly(u8.shape, p, OLHO_E, 3) + _poly(u8.shape, p, OLHO_D, 3) + _poly(u8.shape, p, SOBR_E, 3)
                   + _poly(u8.shape, p, SOBR_D, 3) + _poly(u8.shape, p, LABIOS_EXT, 2), 0, 1)
    ycc = cv2.cvtColor(u8, cv2.COLOR_RGB2YCrCb).astype(np.float32)
    cr, cb = ycc[..., 1], ycc[..., 2]
    pele = np.clip(1 - (np.abs(cr - 150) / 24) ** 2, 0, 1) * np.clip(1 - (np.abs(cb - 112) / 24) ** 2, 0, 1)
    pele = pele * np.clip((ycc[..., 0] / 255 - 0.24) / 0.14, 0, 1)    # barba e sombras escuras ficam de fora
    pele = cv2.GaussianBlur(pele, (0, 0), 2)
    m = (face * (1 - keep) * pele)[..., None] * forca
    esc = max(1.0, (x1 - x0) / 300)                                    # proporcional ao tamanho do rosto
    lisa = cv2.bilateralFilter(u8, int(9 * esc) | 1, 26, 6 * esc).astype(np.float32)
    lisa = lisa * 1.015 + 1.5                                          # leve viço
    img[y0:y1, x0:x1] = np.clip(u8 * (1 - m) + lisa * m, 0, 255).astype(np.uint8)
    return img


def dentes(img, pts, forca=0.85):
    """Aparelho e sombra escura nos dentes: tapa os pontos escuros pequenos (bráquetes, fio) com a cor dos
    dentes ao redor, tira o tom cinza e clareia para um marfim natural (nada de branco de comercial).
    Boca fechada não muda; lábio não é tocado (o vermelho do lábio fica de fora)."""
    if pts is None or forca <= 0:
        return img
    h, w = img.shape[:2]
    bx = pts[BOCA_INTERNA]
    larg = np.ptp(bx[:, 0])
    abertura = pts[14, 1] - pts[13, 1]
    if larg < 20 or abertura < larg * 0.035:
        return img
    x0, y0 = np.floor(bx.min(0)).astype(int) - 4
    x1, y1 = np.ceil(bx.max(0)).astype(int) + 4
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    u8 = img[y0:y1, x0:x1]
    boca = _poly(u8.shape, bx - [x0, y0], list(range(len(BOCA_INTERNA))))
    boca = cv2.erode(boca, np.ones((3, 3), np.uint8))
    if (boca > 0.5).sum() < 40:
        return img
    k = max(3, int(round(larg / 16)) | 1)
    el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    fechado = cv2.morphologyEx(u8, cv2.MORPH_CLOSE, el)                 # some bráquete e fio escuros
    k2 = int(k * 1.6) | 1
    fechado = cv2.morphologyEx(fechado, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k2, k2)))  # brilho do metal
    fechado = cv2.medianBlur(fechado, 3)
    lab = cv2.cvtColor(fechado, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    dentro = boca > 0.5
    ref = np.percentile(L[dentro], 75)
    dente = np.clip((L - ref * 0.6) / (ref * 0.22 + 1), 0, 1)          # claro em relação à própria boca
    dente *= np.clip((160 - A) / 12, 0, 1)                              # lábio (bem vermelho) fica de fora
    dente = cv2.GaussianBlur(dente * boca, (0, 0), 1.0)
    alvo = 178.0
    novoL = L + max(0.0, alvo - ref) * 0.75
    novoL = np.minimum(novoL, alvo + 18)                                # brilho do metal não estoura
    novo = np.stack([novoL, 128 + (A - 128) * 0.45 + 2, 128 + (B - 128) * 0.55 + 6], -1)
    rgb = cv2.cvtColor(np.clip(novo, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)
    m = (dente * forca)[..., None]
    img[y0:y1, x0:x1] = np.clip(u8 * (1 - m) + rgb * m, 0, 255).astype(np.uint8)
    return img


class Retoque:
    """Uso no motor: r = Retoque(pele=0.40, dentes=0.85); frame = r(frame, x, y, largura_cabeca)."""
    def __init__(self, pele=0.40, dentes=0.85):
        self.pele, self.forca_dentes = pele, dentes
        self.rosto = Rosto()

    def reset(self):
        self.rosto.reset()

    def __call__(self, frame, cx, cy, largura):
        if self.pele <= 0 and self.forca_dentes <= 0:
            return frame
        pts = self.rosto(frame, cx, cy, largura)
        if pts is None:
            return frame
        img = frame.copy()
        embelezar(img, pts, self.pele)
        dentes(img, pts, self.forca_dentes)
        return img
