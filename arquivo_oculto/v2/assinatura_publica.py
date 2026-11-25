"""Abertura "Olá, criancinhas..." para um corte já aprovado pelo QA, sem re-renderizar o episódio.

Regra do canal (Geovani, 10/11/2026): a primeira fala do Arquivista em todo vídeo narrado por ele começa com
"Olá, criancinhas..."; o complemento muda a cada vídeo e começa com "Hoje".

Diferente de `assinatura.py` (prévias de ficção, selo FICÇÃO), esta versão serve aos episódios factuais e aceita
`public_release`. Gera ~4 s com o retrato canônico (aparição da sombra, push-in lento, luz de lanterna), o mesmo
cabeçalho, o mesmo título e as mesmas legendas da fábrica V2, a voz aprovada com a mesma cadeia e uma cama grave.
Depois emenda no corte por concat, sem recodificar o episódio. Leve em memória: só o ffmpeg toca nos quadros.

Uso (na raiz do estúdio):
  python -m arquivo_oculto.v2.assinatura_publica <pasta do corte> <pasta de saída> --num 1 \
      --gancho "Hoje vou te contar a história de um baralho." --tela "UM JOGO PREVIU O FUTURO?"
"""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image, ImageDraw

from . import fundo_motor as fm
from . import perfil, voz
from .assinatura import FRASE, legendas

W, H, FPS = 1080, 1920, 30
SR = voz.SR
LY = 1380                      # topo da faixa de legenda na fábrica V2


def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def _recortar_srt(caminho, inicio, fim):
    """Mantém só as legendas dentro do trecho e as traz para o tempo zero do corte."""
    import re
    marca = re.compile(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})')

    def ms(txt):
        h, m, s, x = map(int, marca.match(txt).groups())
        return ((h * 60 + m) * 60 + s) * 1000 + x

    def fmt(v):
        v = max(0, v)
        h, r = divmod(v, 3600000); m, r = divmod(r, 60000); s, x = divmod(r, 1000)
        return f'{h:02d}:{m:02d}:{s:02d},{x:03d}'

    a0, a1 = round(inicio * 1000), round(fim * 1000)
    blocos = []
    for bloco in caminho.read_text(encoding='utf-8-sig').strip().split('\n\n'):
        _, tempos, fala = bloco.split('\n', 2)
        ini, fin = (ms(t.strip()) for t in tempos.split('-->'))
        if fin <= a0 or ini >= a1:
            continue
        blocos.append(f'{fmt(max(ini, a0) - a0)} --> {fmt(min(fin, a1) - a0)}\n{fala}')
    return '\n\n'.join(f'{i}\n{b}' for i, b in enumerate(blocos, start=1)) + '\n'


def _camada_fixa(caminho, num):
    """Gradientes de leitura e cabeçalho, idênticos aos de `fabrica_v2._overlays`."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ys = np.arange(H, dtype=np.float32)
    a = np.clip((380 - ys) / 380, 0, 1) * 0.55 + np.clip((ys - 1180) / 520, 0, 1) * 0.80
    g = np.zeros((H, W, 4), np.uint8)
    g[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)[:, None]
    lay.alpha_composite(Image.fromarray(g, 'RGBA'))
    del g
    d = ImageDraw.Draw(lay)
    f = fm.fonte('cinzel', 30)
    t = f'ARQUIVO OCULTO · Nº {num:02d}'
    d.text((W - 100 - f.getlength(t), 196), t, font=f, fill=fm.OURO + (210,))
    lay.save(caminho)


def _camada_tela(caminho, tela):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tam = 104
    while True:
        f = fm.fonte('anton', tam)
        linhas = fm.quebrar(tela, f, W - 220)
        if len(linhas) <= 2 or tam < 64:
            break
        tam -= 6
    for i, linha in enumerate(linhas):
        fm.texto_centro(d, W / 2, 290 + i * tam * 1.1, linha, f, fm.OURO_CLARO + (255,), stroke=3, stroke_cor=(20, 12, 4))
    lay.save(caminho)


def _camada_legenda(caminho, txt):
    """Mesma tarja e tipografia de `fabrica_v2._legenda_img`."""
    lay = Image.new('RGBA', (W, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tam = 64
    while True:
        f = fm.fonte('oswald', tam)
        linhas = fm.quebrar(txt, f, W - 220)
        if len(linhas) <= 2 or tam <= 44:
            break
        tam -= 4
    alt = int(tam * 1.31)
    for i, linha in enumerate(linhas):
        wl = f.getlength(linha)
        d.rounded_rectangle((W / 2 - wl / 2 - 26, 14 + i * alt, W / 2 + wl / 2 + 26, 14 + i * alt + tam + 22), 14,
                            fill=(6, 5, 4, 120))
    for i, linha in enumerate(linhas):
        fm.texto_centro(d, W / 2, 20 + i * alt, linha, f, fm.CREME + (255,), sombra=False, stroke=5, stroke_cor=(0, 0, 0))
    lay.save(caminho)


def criar_abertura(pasta, gancho, tela, num):
    lock = perfil.carregar_lock()
    retrato = Path(perfil.RAIZ) / lock['character']['reference_image']
    narrador = voz.Voz(lock['voice']['voice_id'])
    partes = [narrador.sintetizar(FRASE), narrador.sintetizar(gancho)]
    inicio = int(0.30 * SR)
    segundo = inicio + len(partes[0]) + int(0.42 * SR)
    final = segundo + len(partes[1])
    quadros = (final + int(0.38 * SR) + SR // FPS - 1) // (SR // FPS)
    dur = quadros / FPS
    trilha = np.zeros(quadros * (SR // FPS), dtype=np.float32)
    for onde, parte in zip((inicio, segundo), partes):
        trilha[onde:onde + len(parte)] = parte
    voz.escrever_wav(str(pasta / 'fala.wav'), trilha / max(0.001, float(np.abs(trilha).max())) * 0.9)
    pista = [(round(i / SR * 1000), round((i + len(p)) / SR * 1000), f)
             for i, p, f in zip((inicio, segundo), partes, (FRASE, gancho))]

    _camada_fixa(pasta / 'fixa.png', num)
    _camada_tela(pasta / 'tela.png', tela)
    for n, (_, _, txt) in enumerate(pista):
        _camada_legenda(pasta / f'leg{n}.png', txt)

    (a0, b0, _), (a1, b1, _) = pista
    video = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
        "zoompan=z='1.03+on*0.00045':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2+on*0.25':d=1:s=1080x1920:fps=30,"
        "eq=brightness='-0.05+0.022*sin(2*PI*t*1.7)+0.012*sin(2*PI*t*4.3)':saturation=0.84:eval=frame,"
        "vignette=angle=PI/4.6,fade=t=in:st=0:d=0.9[base];"
        "[base][1:v]overlay=0:0:format=auto[v1];"
        "[2:v]format=rgba,fade=t=in:st=0.55:d=0.45:alpha=1[t];"
        "[v1][t]overlay=0:0:format=auto[v2];"
        f"[v2][3:v]overlay=0:{LY}:enable='between(t,{a0 / 1000:.3f},{b0 / 1000 + 0.12:.3f})'[v3];"
        f"[v3][4:v]overlay=0:{LY}:enable='between(t,{a1 / 1000:.3f},{b1 / 1000 + 0.25:.3f})',format=yuv420p[vo]"
    )
    cama = (f"aevalsrc='0.055*sin(2*PI*55*t)+0.035*sin(2*PI*82.41*t)+0.02*sin(2*PI*110*t)*(0.6+0.4*sin(2*PI*0.35*t))'"
            f":s=48000:d={dur:.3f},lowpass=f=420,afade=t=in:st=0:d=0.8,afade=t=out:st={max(0.0, dur - 0.5):.3f}:d=0.5[c]")
    audio = (narrador.filtro_ffmpeg('5:a', 'v') + ';' + cama + ';'
             "[v][c]amix=inputs=2:weights=1 0.45:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=9,"
             "aresample=48000,aformat=channel_layouts=stereo[ao]")
    cmd = ['ffmpeg', '-y', '-v', 'error',
           '-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.6f}', '-i', str(retrato),
           '-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.6f}', '-i', 'fixa.png',
           '-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.6f}', '-i', 'tela.png',
           '-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.6f}', '-i', 'leg0.png',
           '-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.6f}', '-i', 'leg1.png',
           '-i', 'fala.wav',
           '-filter_complex', video + ';' + audio, '-map', '[vo]', '-map', '[ao]', '-t', f'{dur:.6f}',
           '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.0', '-preset', 'medium', '-crf', '20',
           '-pix_fmt', 'yuv420p', '-r', str(FPS), '-video_track_timescale', '15360',
           '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-ac', '2', 'abertura.mp4']
    subprocess.run(cmd, cwd=pasta, check=True)
    return pista, dur


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('corte', type=Path)
    ap.add_argument('saida', type=Path)
    ap.add_argument('--num', type=int, required=True)
    ap.add_argument('--gancho', required=True)
    ap.add_argument('--tela', required=True)
    ap.add_argument('--inicio', type=float, default=None, help='corte curto: início do trecho no episódio (s)')
    ap.add_argument('--fim', type=float, default=None, help='corte curto: fim do trecho no episódio (s)')
    a = ap.parse_args()
    if (a.inicio is None) != (a.fim is None) or (a.inicio is not None and not 8 <= a.fim - a.inicio <= 60):
        ap.error('--inicio e --fim vão juntos e o trecho deve ter entre 8 e 60 s')
    corte, saida = a.corte.resolve(), a.saida.resolve()
    if not a.gancho.startswith('Hoje') or any(c in a.gancho for c in '\\{}\r\n\''):
        ap.error('o complemento deve ser uma frase simples iniciada por "Hoje"')
    if not a.tela.strip() or len(a.tela) > 48:
        ap.error('o título de tela precisa ter entre 1 e 48 caracteres')
    if corte == saida:
        ap.error('use uma pasta de saída diferente da do corte')
    qa = json.loads((corte / 'qa.json').read_text(encoding='utf-8'))
    base = corte / 'video_app.mp4'
    sha_base = _sha(base)
    if qa['status'] not in ('pass', 'pass_with_warnings') or sha_base != qa['arquivos']['video_app.mp4']['sha256']:
        ap.error('o corte precisa estar aprovado pelo QA e o vídeo tem de ser o mesmo arquivo conferido')
    saida.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=saida) as temp:
        pasta = Path(temp)
        pista, dur = criar_abertura(pasta, a.gancho, a.tela, a.num)
        caminho = base.as_posix().replace("'", "'\\''")
        srt_base = corte / 'subtitles.srt'
        if a.inicio is not None:
            # corte curto: recorta o trecho do episódio aprovado com os mesmos parâmetros e fecha em fade
            d = a.fim - a.inicio
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{a.inicio:.3f}', '-i', str(base), '-t', f'{d:.3f}',
                            '-vf', f'fade=t=out:st={d - 0.45:.3f}:d=0.45', '-af', f'afade=t=out:st={d - 0.45:.3f}:d=0.45',
                            '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.0', '-preset', 'medium', '-crf', '20',
                            '-pix_fmt', 'yuv420p', '-r', str(FPS), '-video_track_timescale', '15360',
                            '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-ac', '2', 'trecho.mp4'], cwd=pasta, check=True)
            caminho = 'trecho.mp4'
            srt_base = pasta / 'trecho.srt'
            srt_base.write_text(_recortar_srt(corte / 'subtitles.srt', a.inicio, a.fim), encoding='utf-8')
        (pasta / 'cortes.txt').write_text(f"file 'abertura.mp4'\nfile '{caminho}'\n", encoding='utf-8')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'cortes.txt',
                        '-c', 'copy', '-movflags', '+faststart', 'video_app.mp4'], cwd=pasta, check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', 'video_app.mp4', '-f', 'null', '-'], cwd=pasta, check=True)
        info = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_name,width,height',
                                          '-of', 'json', 'video_app.mp4'], cwd=pasta, check=True,
                                         capture_output=True, text=True).stdout)
        (pasta / 'subtitles.srt').write_text(legendas(srt_base, pista, round(dur * 1000)), encoding='utf-8')
        registro = {
            'episode_id': qa.get('episode_id') or json.loads((corte / 'status.json').read_text(encoding='utf-8'))['episode_id'],
            'modo': qa['modo'], 'regra': 'primeira fala do Arquivista começa com "Olá, criancinhas..."',
            'frases': [FRASE, a.gancho], 'tela': a.tela, 'abertura_s': round(dur, 3),
            'duracao_total_s': round(float(info['format']['duration']), 3),
            'corte_base': {'pasta': corte.name, 'sha256': sha_base, 'qa': qa['status']},
            'trecho_s': None if a.inicio is None else [a.inicio, a.fim],
            'decodificado_sem_erro': True, 'sha256': _sha(pasta / 'video_app.mp4'),
        }
        (pasta / 'assinatura.json').write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding='utf-8')
        for nome in ('video_app.mp4', 'subtitles.srt', 'assinatura.json', 'abertura.mp4'):
            (pasta / nome).replace(saida / nome)
    if (corte / 'cover.png').exists():
        shutil.copy2(corte / 'cover.png', saida / 'cover.png')
    print(json.dumps(registro, ensure_ascii=False))


if __name__ == '__main__':
    main()
