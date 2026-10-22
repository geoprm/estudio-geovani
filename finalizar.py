"""Passo final: renderiza as versões A e B e a capa, já no tamanho certo para enviar.

    python3 finalizar.py videos/<nome>.py pasta_saida [tempo_capa] ["PALAVRA|PALAVRA|PALAVRA"] [DESTAQUE]

A versão B só difere na abertura: o motor renderiza a abertura das duas, o resto uma vez só
(em dois processos paralelos), e emenda. Cada vídeo sai com no máximo ~14 MB.
"""
import importlib.util, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
LIMITE_MB = 14.0


def carregar(cfg):
    spec = importlib.util.spec_from_file_location('cfg_video', cfg)
    mod = importlib.util.module_from_spec(spec)
    sys.argv = [cfg, 'noop']
    spec.loader.exec_module(mod)
    return mod


def roda(args):
    print(' '.join(args), flush=True)
    subprocess.run(args, check=True)


def concat(partes, saida, pasta):
    lista = os.path.join(pasta, os.path.basename(saida) + '.txt')
    open(lista, 'w').write(''.join(f"file '{os.path.abspath(p)}'\n" for p in partes))
    roda(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lista, '-c', 'copy', saida])


def comprimir(video, audio, saida, dur):
    kbps = int(LIMITE_MB * 8 * 1024 / dur) - 200
    kbps = max(1800, min(kbps, 9000))
    base = ['ffmpeg', '-v', 'error', '-y', '-i', video, '-c:v', 'libx264', '-preset', 'medium', '-b:v', f'{kbps}k',
            '-maxrate', f'{int(kbps * 1.3)}k', '-bufsize', f'{kbps * 2}k', '-pix_fmt', 'yuv420p',
            '-colorspace', 'bt470bg', '-color_primaries', 'bt470bg', '-color_trc', 'smpte170m', '-color_range', 'tv']
    log = saida + '.2pass'
    roda(base + ['-pass', '1', '-passlogfile', log, '-an', '-f', 'null', '/dev/null'])
    roda(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', audio] + base[6:] + ['-pass', '2', '-passlogfile', log,
         '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', saida])


def main():
    argv = list(sys.argv)          # carregar() troca o sys.argv; guarde os argumentos antes
    cfg, saida = os.path.abspath(argv[1]), os.path.abspath(argv[2])
    os.makedirs(saida, exist_ok=True)
    mod = carregar(cfg)
    R = mod.R
    total = R.TOTAL
    n = min(total, round((R.fim_gancho() + 0.5) * 30)) if R.gancho else 0
    meio = n + (total - n) // 2
    py = [sys.executable, cfg]
    pasta = os.path.join(saida, 'partes')
    os.makedirs(pasta, exist_ok=True)
    roda(py + ['audio'])
    from motor import TRABALHO
    wav = os.path.join(TRABALHO, mod.NOME, 'work_final.wav')
    jobs = [py + ['part', f'{pasta}/a1.mp4', str(n), str(meio)], py + ['part', f'{pasta}/a2.mp4', str(meio), str(total)]]
    if n:
        jobs += [py + ['part', f'{pasta}/a0.mp4', '0', str(n)], py + ['part', f'{pasta}/b0.mp4', '0', str(n), '--B']]
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(roda, jobs))
    a_partes = ([f'{pasta}/a0.mp4'] if n else []) + [f'{pasta}/a1.mp4', f'{pasta}/a2.mp4']
    concat(a_partes, f'{pasta}/A_bruto.mp4', pasta)
    dur = total / 30
    comprimir(f'{pasta}/A_bruto.mp4', wav, os.path.join(saida, 'versao_A.mp4'), dur)
    if n:
        concat([f'{pasta}/b0.mp4', f'{pasta}/a1.mp4', f'{pasta}/a2.mp4'], f'{pasta}/B_bruto.mp4', pasta)
        comprimir(f'{pasta}/B_bruto.mp4', wav, os.path.join(saida, 'versao_B.mp4'), dur)
    if len(argv) > 4:
        t = argv[3]
        dest = argv[5] if len(argv) > 5 else ''
        png = os.path.join(pasta, 'capa.png')
        roda(py + ['capa', t, argv[4], dest or 'X', png])
        roda(['ffmpeg', '-v', 'error', '-y', '-i', png, '-q:v', '3', os.path.join(saida, 'capa.jpg')])
    for f in sorted(os.listdir(saida)):
        p = os.path.join(saida, f)
        if os.path.isfile(p):
            print(f'{f}: {os.path.getsize(p) / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
