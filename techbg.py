"""Fundo 'Brasil + IA': bandeira em painel de LED digital, ondulando, com HUD sutil."""
import numpy as np, cv2, math


def flag_texture(w=1500, h=1050):
    img = np.zeros((h, w, 3), np.float32)
    img[:] = np.array([0, 156, 59]) / 255
    cx, cy = w / 2, h / 2
    m = 0.083 * h * 1.0
    rh = np.array([[cx, m], [w - m * 1.0, cy], [cx, h - m], [m * 1.0, cy]], np.int32)
    cv2.fillPoly(img, [rh], (1.0, 223 / 255, 0), lineType=cv2.LINE_AA)
    R = 0.25 * h * 1.4
    cv2.circle(img, (int(cx), int(cy)), int(R), (0, 39 / 255, 118 / 255), -1, lineType=cv2.LINE_AA)
    # faixa branca curva
    band = np.zeros((h, w), np.float32)
    cv2.ellipse(band, (int(cx - R * 0.15), int(cy + R * 2.2)), (int(R * 2.45), int(R * 2.45)), 0, 0, 360, 1.0,
                int(R * 0.17), lineType=cv2.LINE_AA)
    circ = np.zeros((h, w), np.float32)
    cv2.circle(circ, (int(cx), int(cy)), int(R), 1.0, -1, lineType=cv2.LINE_AA)
    band *= circ
    img = img * (1 - band[..., None]) + band[..., None]
    rng = np.random.default_rng(5)
    for _ in range(27):
        a = rng.uniform(0, 2 * math.pi); r = R * math.sqrt(rng.uniform(0.0, 0.8))
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * 0.9 + R * 0.25
        if (x - cx) ** 2 + (y - cy) ** 2 < (R * 0.92) ** 2:
            cv2.circle(img, (int(x), int(y)), int(rng.uniform(3, 7)), (1, 1, 1), -1, lineType=cv2.LINE_AA)
    return img


class TechFlag:
    def __init__(self, W, H, strength=0.62, spacing=10, seed=1):
        self.W, self.H, self.strength = W, H, strength
        self.tex = flag_texture()
        th, tw = self.tex.shape[:2]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        # mapeia o painel para a textura (bandeira levemente inclinada / perspectiva)
        sx = 1.0 * th / H  # escala uniforme (sem distorcer o círculo)
        self.u = tw / 2 + (xx - W / 2) * sx
        self.v = th / 2 + (yy - H * 0.43) * sx + (xx / W - 0.5) * 30
        self.xx, self.yy = xx, yy
        # máscara de pontos de LED
        gy = (yy % spacing) - spacing / 2 + 0.5
        gx = (xx % spacing) - spacing / 2 + 0.5
        d = np.sqrt(gx ** 2 + gy ** 2)
        self.dots = np.clip(1.35 - d / (spacing * 0.36), 0, 1).astype(np.float32)[..., None]
        # vinheta e base
        v = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.42) / (H * 0.70)) ** 2)
        t = np.clip((v - 0.45) / 0.9, 0, 1)
        self.vig = (1 - 0.82 * t * t * (3 - 2 * t))[..., None].astype(np.float32)
        ds = np.sqrt(((xx - W / 2) / 360.) ** 2 + ((yy - H * 0.40) / 430.) ** 2)
        self.spot = (0.62 + 0.38 * np.clip(ds - 0.25, 0, 1) ** 0.8)[..., None].astype(np.float32) if H > 950 else 1.0
        self.base = np.zeros((H, W, 3), np.float32) + np.array([4, 7, 15], np.float32) / 255
        # HUD: grade hexagonal fina + linhas de circuito nas bordas
        hud = np.zeros((H, W), np.float32)
        s = 46
        for row in range(-1, H // int(s * 0.866) + 2):
            for col in range(-1, W // s + 2):
                cx = col * s + (s / 2 if row % 2 else 0); cy = row * s * 0.866
                pts = np.array([[cx + 15 * math.cos(math.pi / 3 * k + math.pi / 6),
                                 cy + 15 * math.sin(math.pi / 3 * k + math.pi / 6)] for k in range(6)], np.int32)
                cv2.polylines(hud, [pts], True, 1.0, 1, lineType=cv2.LINE_AA)
        edge = np.clip((np.abs(xx - W / 2) / (W / 2) - 0.55) / 0.45, 0, 1)
        self.hud = (hud * edge * 0.35)[..., None] * np.array([0.25, 0.8, 1.0], np.float32)
        rng = np.random.default_rng(seed)
        self.circ = np.zeros((H, W), np.float32)
        for _ in range(14):
            x = int(rng.choice([rng.uniform(0, W * 0.16), rng.uniform(W * 0.84, W)]))
            y = int(rng.uniform(0, H))
            pts = [(x, y)]
            for _ in range(3):
                x2 = x + int(rng.choice([-1, 1]) * rng.uniform(30, 90)); y2 = y + int(rng.uniform(40, 140))
                pts.append((x2, y)); pts.append((x2, y2)); x, y = x2, y2
            cv2.polylines(self.circ, [np.array(pts, np.int32)], False, 1.0, 2, lineType=cv2.LINE_AA)
            cv2.circle(self.circ, pts[-1], 5, 1.0, -1, lineType=cv2.LINE_AA)
        self.grain = rng.normal(0, 1.4, (H, W, 1)).astype(np.float32) / 255

    def frame(self, t):
        if not hasattr(self, '_x1'):
            self._x1 = self.xx[0:1, :]          # (1, W)
            self._y1 = self.yy[:, 0:1]          # (H, 1)
            self._cb = np.cos(self._y1 * 0.0021); self._sb = np.sin(self._y1 * 0.0021)
            self._scancol = np.array([0.25, 0.7, 1.0], np.float32) * 0.10
            self._circcol = (self.circ[..., None] * np.array([0.2, 0.75, 1.0], np.float32) * 0.22).astype(np.float32)
            self._base_hud = (self.base + self.hud).astype(np.float32)
        ph = t * 1.6
        ax = self._x1 * 0.0085 - ph
        sa, ca = np.sin(ax), np.cos(ax)
        s1 = sa * self._cb + ca * self._sb            # sin(ax + by)
        c1 = ca * self._cb - sa * self._sb            # cos(ax + by)
        wave = s1 + 0.5 * np.sin(self._x1 * 0.017 - ph * 1.7 + 1.3)
        du = (6 * wave).astype(np.float32); dv = (16 * wave).astype(np.float32)
        flag = cv2.remap(self.tex, self.u + du, self.v + dv, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        shade = (0.78 + 0.22 * c1).astype(np.float32)[..., None]
        led = flag * self.dots * shade
        small = cv2.resize(led, (self.W // 2, self.H // 2), interpolation=cv2.INTER_AREA)
        glow = cv2.resize(cv2.GaussianBlur(small, (0, 0), 3.5), (self.W, self.H), interpolation=cv2.INTER_LINEAR)
        spot = self.spot if isinstance(self.spot, np.ndarray) else 1.0
        img = self._base_hud + (led * 0.95 + glow * 0.9) * (self.strength * spot)
        sy = (t * 140) % (self.H + 300) - 150
        scan = np.exp(-((self._y1 - sy) / 40) ** 2).astype(np.float32)[..., None]
        pulse = 0.6 + 0.4 * math.sin(t * 2.2)
        img = img + scan * self._scancol + self._circcol * pulse
        img = img * self.vig + self.grain
        return np.clip(img, 0, 1)
