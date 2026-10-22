"""Passo 1 de todo vídeo novo: prepara a gravação bruta.

    python3 preparar.py gravacao.mp4 trabalho/meu_video

Gera na pasta:
  original.mp4    cópia normalizada (1080x1920, 30 fps)
  audio16k.f32    áudio para a transcrição
  palavras.json   transcrição palavra a palavra (Whisper small, roda local)
  env_db.npy      energia do áudio a cada 10 ms (para achar pausas)
  track.npy       posição da cabeça quadro a quadro (para enquadrar)
"""
import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from perfis import RAIZ
import pessoa


def normalizar(src, pasta):
    out = os.path.join(pasta, 'original.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf',
                    'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30',
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '14', '-pix_fmt', 'yuv420p',
                    '-colorspace', 'bt470bg', '-color_primaries', 'bt470bg', '-color_trc', 'smpte170m',
                    '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', out], check=True)
    return out


def audio(src, pasta):
    out = os.path.join(pasta, 'audio16k.f32')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ac', '1', '-ar', '16000', '-f', 'f32le', out],
                   check=True)
    return out


def envelope(f32, pasta):
    x = np.fromfile(f32, dtype=np.float32)
    fr = x[: len(x) // 160 * 160].reshape(-1, 160)          # 10 ms
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    np.save(os.path.join(pasta, 'env_db.npy'), db.astype(np.float32))


def transcrever(f32, pasta):
    out = os.path.join(pasta, 'palavras.json')
    script = os.path.join(RAIZ, 'asr', 'transcribe.mjs')
    subprocess.run(['node', script, os.path.abspath(f32), os.path.abspath(out), 'word'], check=True,
                   cwd=os.path.join(RAIZ, 'asr'))
    return out


def rastrear(src, pasta):
    w, h = 270, 480
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-vf', f'scale={w}:{h}', '-f', 'rawvideo',
                          '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, bufsize=10 ** 7)
    res = []
    while True:
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        img = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        m = pessoa.cv2.resize(pessoa.raw_mask(img), (w, h)) > 0.5
        rows = np.where(m.any(axis=1))[0]
        if len(rows) == 0:
            res.append(res[-1] if res else (w / 2 * 4, h / 3 * 4, 240))
            continue
        top_ = rows[0]
        band = m[top_: top_ + int(h * 0.22)]
        cols = np.where(band.any(axis=0))[0]
        widths = band.sum(axis=1)
        hw = np.median(widths[len(widths) // 3: 2 * len(widths) // 3]) if len(widths) > 6 else 60
        cx = cols.mean() if len(cols) else w / 2
        cy = top_ + 0.62 * hw * 1.25
        res.append((cx * 4, cy * 4, hw * 4))
    np.save(os.path.join(pasta, 'track.npy'), np.array(res, np.float32))


if __name__ == '__main__':
    src, pasta = sys.argv[1], sys.argv[2]
    os.makedirs(pasta, exist_ok=True)
    orig = normalizar(src, pasta)
    f32 = audio(orig, pasta)
    envelope(f32, pasta)
    rastrear(orig, pasta)
    transcrever(f32, pasta)
    d = json.load(open(os.path.join(pasta, 'palavras.json')))
    print('\nTRANSCRIÇÃO (revise nomes, números e acentos):\n' + d.get('text', ''))
