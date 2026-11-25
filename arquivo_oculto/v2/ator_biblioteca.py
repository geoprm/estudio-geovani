"""Biblioteca de planos de atuação do Arquivista (2,5D) para o motor leve de reels.

A atuação quadro a quadro (`ator.py`) custa ~1,3 s por quadro e não cabe dentro de cada render com a memória atual.
Aqui cada plano é renderizado UMA vez (4 s, 1080x1920, 30 fps) e o `reel_leve` monta as aparições do Arquivista
cortando entre esses planos, sem nenhum plano dele passar de 4 s (regra do perfil V2).

Uso (na raiz do estúdio):  python -m arquivo_oculto.v2.ator_biblioteca [plano ...]
Saída: arquivo_oculto/saida_v2/ator_clipes/<plano>.mp4 + biblioteca.json. Modo declarado: performance_2_5d.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from .ator import Atores

W, H, FPS, DUR = 1080, 1920, 30, 4.0
PASTA = Path(__file__).resolve().parents[1] / 'saida_v2' / 'ator_clipes'
PLANOS = {
    'aparicao': {},                 # sai da sombra e olha para a lente
    'olhar_camera': {},             # vira da prova para a lente, micro push-in
    'silencio': {},                 # close do rosto numa pausa dramática
    'debrucar': {},                 # inclina-se sobre a mesa
    'virar_cabeca': {'lado': -1},   # reage a uma prova, gira a cabeça
    'encerramento': {},             # recua e some na sombra
}


def render(ator, plano, params):
    saida = PASTA / f'{plano}.mp4'
    n = int(DUR * FPS)
    proc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                             '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16',
                             '-pix_fmt', 'yuv420p', str(saida)], stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(n):
        q = ator.quadro(plano, f / (n - 1), f / FPS, DUR, dict(params), 0.0)
        proc.stdin.write(np.clip(q, 0, 255).astype(np.uint8).tobytes())
    proc.stdin.close()
    proc.wait()
    print(f'{plano}: {n} quadros em {time.time() - t0:.0f}s -> {saida.name}', flush=True)
    return saida


def main():
    PASTA.mkdir(parents=True, exist_ok=True)
    pedidos = sys.argv[1:] or list(PLANOS)
    ator = Atores(W, H)
    reg_p = PASTA / 'biblioteca.json'
    reg = json.loads(reg_p.read_text(encoding='utf-8')) if reg_p.exists() else {'modo': 'performance_2_5d', 'planos': {}}
    for p in pedidos:
        render(ator, p, PLANOS[p])
        reg['planos'][p] = {'arquivo': f'{p}.mp4', 'dur_s': DUR, 'fps': FPS, 'params': PLANOS[p]}
        reg_p.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
