#!/usr/bin/env python3
"""Filtro do Arquivista: põe a máscara e o capuz do Arquivista no rosto de quem gravou e troca o fundo
pelo cenário do Arquivista (biblioteca com lanternas e poeira). Mantém a fala original; por padrão deixa a
voz um pouco mais grave e com eco de sala de arquivo.

Uso: python3 filtro.py entrada.mp4 saida.mp4 [--capa capa.jpg] [--num 11] [--sem-voz-sombria]
Precisa: ffmpeg, numpy, opencv, onnxruntime, insightface (buffalo_s em ~/.insightface/models) e
u2net_human_seg.onnx (AO_SEG ou ao lado deste arquivo em modelos/).
"""
import math, os, subprocess, sys, tempfile
import numpy as np
import cv2

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import motor  # noqa: E402

W, H, FPS = motor.W, motor.H, 30
SEG = os.environ.get('AO_SEG', os.path.join(AQUI, 'modelos', 'u2net_human_seg.onnx'))
LMK = os.environ.get('AO_LMK', os.path.join(os.path.dirname(motor.ARQ_IMG), 'arq_lmk106.json'))


class Segmentador:
    def __init__(self):
        import onnxruntime as ort
        self.s = ort.InferenceSession(SEG, providers=['CPUExecutionProvider'])
        self.n = self.s.get_inputs()[0].name

    def __call__(self, rgb):
        x = cv2.resize(rgb, (320, 320)).astype(np.float32) / 255.0
        x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        o = self.s.run(None, {self.n: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
        o = (o - o.min()) / max(1e-6, o.max() - o.min())
        return cv2.resize(o, (rgb.shape[1], rgb.shape[0]))


def ler_video(path):
    pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height:stream_side_data=rotation',
                         '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip().split('\n')[0].split(',')
    # ffmpeg já aplica a rotação do celular; recorta para 9:16 e escala para 1080x1920
    vf = f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', path, '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)


def main():
    a = sys.argv
    ent, sai = a[1], a[2]
    capa = a[a.index('--capa') + 1] if '--capa' in a else None
    num = int(a[a.index('--num') + 1]) if '--num' in a else 0
    sombria = '--sem-voz-sombria' not in a

    from insightface.app import FaceAnalysis
    fa = FaceAnalysis(name='buffalo_s', allowed_modules=['detection', 'landmark_2d_106'], providers=['CPUExecutionProvider'])
    fa.prepare(ctx_id=-1, det_size=(384, 384), det_thresh=0.35)
    seg = Segmentador()
    base = motor.Base()
    anim = motor.Animador(base)
    import json
    ref = np.array(json.load(open(LMK)), np.float32)  # 106 pontos do rosto da máscara na imagem original

    # peça da cabeça: capuz + máscara (sem as mãos), com borda suave
    fig = anim.fig.copy()
    yy = anim.yy
    corte = np.clip((610 - yy) / 40, 0, 1)
    fig[..., 3] *= corte
    # cenário do Arquivista em 9:16 (o próprio cenário sem a figura)
    bx0, by0, bx1, by1 = 0, 0, anim.w, anim.h

    tmp = tempfile.mkdtemp()
    # áudio
    aud = os.path.join(tmp, 'a.wav')
    filtro_voz = ("asetrate=48000*0.93,aresample=48000,atempo=1.0753,equalizer=f=120:t=q:w=1:g=3,"
                  "aecho=0.8:0.55:40|85:0.15|0.08,loudnorm=I=-14:TP=-1.5") if sombria else "loudnorm=I=-14:TP=-1.5"
    tem_audio = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', ent],
                               capture_output=True, text=True).stdout.strip() != ''
    if tem_audio:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', ent, '-vn', '-ac', '2', '-ar', '48000', '-af', filtro_voz, aud], check=True)

    vin = motor.vinheta(); gr = motor.graos()
    marca = np.asarray(motor.camada_marca(num) if num else motor.Image.new('RGBA', (W, H)), np.float32)
    m_al = marca[..., 3:4] / 255.0; m_rgb = marca[..., :3] * m_al

    sov = os.path.join(tmp, 'v.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'faster', '-crf', '22', '-maxrate', '3500k', '-bufsize', '7000k', '-pix_fmt', 'yuv420p', sov]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    lm_s = None; mask = None; boca0 = None; perdeu = 0; capa_ok = False; rng = np.random.default_rng(5)
    abert = 0.0
    for fi, fr in enumerate(ler_video(ent)):
        t = fi / FPS
        bgr = cv2.cvtColor(fr, cv2.COLOR_RGB2BGR)
        faces = fa.get(bgr)
        if faces:
            f = max(faces, key=lambda z: (z.bbox[2] - z.bbox[0]) * (z.bbox[3] - z.bbox[1]))
            lm = f.landmark_2d_106.astype(np.float32)
            lm_s = lm if lm_s is None else lm_s * 0.55 + lm * 0.45
            perdeu = 0
        else:
            perdeu += 1
        if fi % 3 == 0 or mask is None:
            mask = seg(fr)
        # abertura da boca (pontos internos dos lábios no modelo de 106 pontos)
        if lm_s is not None:
            boca = lm_s[52:72]
            alt = (boca[:, 1].max() - boca[:, 1].min()) / max(1.0, lm_s[:, 1].max() - lm_s[:, 1].min())
            boca0 = alt if boca0 is None else min(boca0 * 1.002, alt)
            abert = abert * 0.5 + 0.5 * float(np.clip((alt - boca0) * 12, 0, 1))
        # cenário animado (fundo sem a figura, com luz tremendo e poeira)
        cen = anim.cenario(t, W, H)
        # pessoa: escurecida, tons âmbar
        p = fr.astype(np.float32)
        lum = p.mean(axis=2, keepdims=True)
        p = (p * 0.35 + lum * 0.65) * np.array([1.0, 0.86, 0.66], np.float32) * 0.72
        m = cv2.GaussianBlur(np.clip((mask - 0.3) / 0.4, 0, 1), (0, 0), 3)[..., None]
        out = cen * (1 - m) + p * m
        # cabeça do Arquivista sobre o rosto
        if lm_s is not None and perdeu < 15:
            idx = list(range(0, 33, 2)) + list(range(33, 106))
            M, _ = cv2.estimateAffinePartial2D(ref[idx], lm_s[idx], method=cv2.LMEDS)
            if M is not None:
                # boca da máscara acompanha a boca de quem fala
                peca = fig
                if abert > 0.05:
                    my = anim.yy - anim.w_jaw * (12.0 * abert)
                    peca = cv2.remap(fig, anim.xx, my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                # o capuz é um pouco maior que a cabeça: amplia 6% em torno do nariz
                c = lm_s[86] if len(lm_s) > 86 else lm_s.mean(0)
                S = np.array([[1.06, 0, -0.06 * c[0]], [0, 1.06, -0.06 * c[1]], [0, 0, 1]], np.float32)
                M2 = (S @ np.vstack([M, [0, 0, 1]]))[:2]
                warp = cv2.warpAffine(peca, M2, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
                al = warp[..., 3:4] / 255.0
                out = out * (1 - al) + warp[..., :3] * al
                # brilho dos olhos com a fala
                for k, (ox, oy) in enumerate(motor.OLHOS):
                    q = M2 @ np.array([ox, oy, 1.0], np.float32)
                    r = int(max(6, 26 * math.sqrt(abs(np.linalg.det(M2[:, :2])))))
                    x0, y0 = int(q[0]) - r, int(q[1]) - r
                    if 0 <= x0 and x0 + 2 * r + 1 <= W and 0 <= y0 and y0 + 2 * r + 1 <= H:
                        yv, xv = np.ogrid[-r:r + 1, -r:r + 1]
                        g = np.exp(-((xv / r) ** 2 + (yv / (r * 0.6)) ** 2) * 2.2)[..., None]
                        out[y0:y0 + 2 * r + 1, x0:x0 + 2 * r + 1] += g * np.array([255, 170, 60], np.float32) * (0.15 + 0.5 * abert)
        fl = 1.0 + 0.03 * math.sin(fi * 0.9) * rng.random()
        out = out * vin * fl + gr[fi % len(gr)]
        out = out * (1 - m_al) + m_rgb
        out[..., 2] *= 0.93
        o8 = np.clip(out, 0, 255).astype(np.uint8)
        if capa and not capa_ok and fi >= 15 and lm_s is not None:
            motor.Image.fromarray(o8).save(capa, quality=90); capa_ok = True
        proc.stdin.write(o8.tobytes())
        if fi % 150 == 0: print('  quadro', fi, flush=True)
    proc.stdin.close(); proc.wait()
    m = ['ffmpeg', '-y', '-loglevel', 'error', '-i', sov]
    if tem_audio: m += ['-i', aud, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k']
    subprocess.run(m + ['-c:v', 'copy', '-movflags', '+faststart', sai], check=True)
    print('ok')


if __name__ == '__main__':
    main()
