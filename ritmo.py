"""Passo 2: corte de ritmo. Tira pausas e respiros, acelera 6% e alterna o enquadramento (jump cuts).

    python3 ritmo.py trabalho/meu_video                 # usa o vídeo inteiro
    python3 ritmo.py trabalho/meu_video frases.json     # só os trechos escolhidos: [[ini, fim], ...]
    python3 ritmo.py trabalho/meu_video frases.json 1.06 0.8   # velocidade e cauda muda (s) para cartela final

Gera mix.mov, mix_segs.json e mix_track.npy na mesma pasta.
"""
import json, os, subprocess, sys
import numpy as np

FPS = 30
MIN_GAP, KEEP = 0.17, 0.045            # pausa mínima cortada e respiro mantido em cada lado
ZPAT = [1.00, 1.13, 1.05, 1.18, 1.02, 1.10]


def main():
    pasta = os.path.abspath(sys.argv[1])
    src = os.path.join(pasta, 'original.mp4')
    db = np.load(os.path.join(pasta, 'env_db.npy'))
    dur = len(db) / 100
    if len(sys.argv) > 2 and sys.argv[2].endswith('.json'):
        frases = json.load(open(sys.argv[2]))
    else:
        voz = np.where(db > np.percentile(db, 10) + 6)[0]
        frases = [[max(0.0, voz[0] / 100 - 0.08), min(dur, voz[-1] / 100 + 0.25)]]
    speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.06
    tail = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    thr = np.percentile(db, 10) + 6

    micro = []
    for a, b in frases:
        i0, i1 = int(a * 100), int(b * 100)
        low = db[i0:i1] < thr
        cur, j = a, 0
        while j < len(low):
            if low[j]:
                k = j
                while k < len(low) and low[k]:
                    k += 1
                g0, g1 = (i0 + j) / 100, (i0 + k) / 100
                if g1 - g0 >= MIN_GAP and g0 > a + 0.05 and g1 < b - 0.05:
                    micro.append((cur, g0 + KEEP))
                    cur = g1 - KEEP
                j = k
            else:
                j += 1
        micro.append((cur, b))
    micro = [(s, e) for s, e in micro if e - s >= 0.25]

    tr = np.load(os.path.join(pasta, 'track.npy')).astype(np.float64)
    med = np.median(tr, axis=0)
    bad = (tr[:, 2] < med[2] * 0.75) | (np.abs(tr[:, 0] - med[0]) > 200)
    tr[bad] = np.nan
    for c in range(3):
        col = tr[:, c]; idx = np.arange(len(col)); ok = ~np.isnan(col)
        tr[:, c] = np.interp(idx, idx[ok], col[ok])
    win = 31
    pad = np.pad(tr, ((win // 2, win // 2), (0, 0)), mode='edge')
    trs = np.stack([np.convolve(pad[:, c], np.ones(win) / win, mode='valid') for c in range(3)], 1)
    trs[:, 2] = med[2]

    parts = os.path.join(pasta, 'mparts')
    os.makedirs(parts, exist_ok=True)
    lst, segs, track_out, off = [], [], [], 0
    cor = ['-colorspace', 'bt470bg', '-color_primaries', 'bt470bg', '-color_trc', 'smpte170m', '-color_range', 'tv']
    for i, (a, b) in enumerate(micro):
        f0, f1 = round(a * FPS), round(b * FPS)
        n_out = max(1, round((f1 - f0) / speed))
        out = os.path.join(parts, f'm{i:03d}.mov')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{f0 / FPS:.4f}', '-i', src,
                        '-vf', f'setpts=PTS/{speed},fps=30', '-frames:v', str(n_out),
                        '-af', f'atempo={speed},apad,atrim=0:{n_out / FPS:.5f},afade=t=in:d=0.006,'
                               f'afade=t=out:st={n_out / FPS - 0.008:.4f}:d=0.008',
                        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '12', '-pix_fmt', 'yuv420p'] + cor +
                       ['-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '2', out], check=True)
        lst.append(f"file '{out}'")
        z = ZPAT[i % len(ZPAT)]
        segs.append({'src0': f0 / FPS, 'src1': f1 / FPS, 'off': off / FPS, 'n': n_out, 'z0': z, 'z1': z * 1.02})
        for j in range(n_out):
            track_out.append(trs[min(f0 + int(round(j * speed)), len(trs) - 1)])
        off += n_out
    if tail > 0:
        n_out = round(tail * FPS)
        out = os.path.join(parts, 'tail.mov')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.0', '-i', src, '-frames:v', str(n_out),
                        '-af', f'volume=0,apad,atrim=0:{n_out / FPS:.5f}', '-c:v', 'libx264', '-preset',
                        'ultrafast', '-crf', '12', '-pix_fmt', 'yuv420p', '-r', '30'] + cor +
                       ['-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '2', out], check=True)
        lst.append(f"file '{out}'")
        segs.append({'src0': 9000.0, 'src1': 9000.0 + tail, 'off': off / FPS, 'n': n_out, 'z0': 1.0, 'z1': 1.0,
                     'tail': True})
        track_out += [trs[30 + j] for j in range(n_out)]
        off += n_out
    open(os.path.join(parts, 'list.txt'), 'w').write('\n'.join(lst) + '\n')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i',
                    os.path.join(parts, 'list.txt'), '-c', 'copy', os.path.join(pasta, 'mix.mov')], check=True)
    np.save(os.path.join(pasta, 'mix_track.npy'), np.array(track_out, np.float32))
    json.dump({'speed': speed, 'segs': segs}, open(os.path.join(pasta, 'mix_segs.json'), 'w'), indent=1)
    orig = sum(b - a for a, b in frases)
    print(f'{len(frases)} trechos -> {len(micro)} cortes; {orig:.1f}s -> {off / FPS:.1f}s')


if __name__ == '__main__':
    main()
