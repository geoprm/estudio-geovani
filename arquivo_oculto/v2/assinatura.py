"""Encaixa a abertura do Arquivista em um corte privado já aprovado pelo QA."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from . import perfil, voz


FRASE = 'Olá, criancinhas...'
FPS = 30
SR = voz.SR


def intervalo(ms, ass=False):
    horas, resto = divmod(ms, 3600000)
    minutos, resto = divmod(resto, 60000)
    segundos, milesimos = divmod(resto, 1000)
    if ass:
        return f'{horas}:{minutos:02d}:{segundos:02d}.{milesimos // 10:02d}'
    return f'{horas:02d}:{minutos:02d}:{segundos:02d},{milesimos:03d}'


def legendas(caminho, abertura, atraso):
    marcas = re.compile(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})')

    def deslocar(marca):
        h, m, s, ms = map(int, marca.groups())
        return intervalo(((h * 60 + m) * 60 + s) * 1000 + ms + atraso)

    blocos = [f'{intervalo(inicio)} --> {intervalo(fim)}\n{fala}' for inicio, fim, fala in abertura]
    originais = caminho.read_text(encoding='utf-8-sig').strip().split('\n\n')
    for bloco in originais:
        _, tempos, fala = bloco.split('\n', 2)
        blocos.append(marcas.sub(deslocar, tempos) + '\n' + fala)
    return '\n\n'.join(f'{i}\n{bloco}' for i, bloco in enumerate(blocos, start=1)) + '\n'


def criar_abertura(pasta, personagem, voz_id, gancho):
    narrador = voz.Voz(voz_id)
    partes = [narrador.sintetizar(fala) for fala in (FRASE, gancho)]
    inicio = int(0.18 * SR)
    segundo = inicio + len(partes[0]) + int(0.42 * SR)
    final = segundo + len(partes[1])
    quadros = (final + int(0.40 * SR) + SR // FPS - 1) // (SR // FPS)
    voz_abertura = np.zeros(quadros * (SR // FPS), dtype=np.float32)
    for onde, parte in zip((inicio, segundo), partes):
        voz_abertura[onde:onde + len(parte)] = parte
    voz.escrever_wav(str(pasta / 'fala.wav'), voz_abertura / max(0.001, np.abs(voz_abertura).max()) * 0.9)
    pista = [(round(i / SR * 1000), round((i + len(p)) / SR * 1000), f)
             for i, p, f in zip((inicio, segundo), partes, (FRASE, gancho))]
    ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Fala,Arial,56,&H00E4EAF2,&H000000FF,&H00150F0C,&H78000000,-1,0,0,0,100,100,0,0,1,5,0,2,118,118,365,1
Style: Selo,Arial,30,&H00E4EAF2,&H000000FF,&H00312A21,&H80000000,-1,0,0,0,100,100,2,0,3,8,0,7,104,104,190,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    ass += f'Dialogue: 0,0:00:00.00,{intervalo(round(quadros / FPS * 1000), True)},Selo,,0,0,0,,FICÇÃO\n'
    for ini, fim, fala in pista:
        ass += f'Dialogue: 0,{intervalo(ini, True)},{intervalo(fim, True)},Fala,,0,0,0,,{fala}\n'
    (pasta / 'abertura.ass').write_text(ass, encoding='utf-8')
    video = ("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
             "zoompan=z='1.035+min(0.045,on*0.00024)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30,"
             "eq=brightness=-0.035:saturation=0.82,ass=abertura.ass")
    filtro_voz = narrador.filtro_ffmpeg('1:a') + ';[v]loudnorm=I=-16:TP=-1.5[o]'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-framerate', '30', '-i', str(personagem),
                    '-i', 'fala.wav', '-filter_complex', filtro_voz, '-map', '0:v:0', '-map', '[o]', '-vf', video,
                    '-t', f'{quadros / FPS:.9f}', '-c:v', 'libx264', '-preset', 'fast', '-crf', '24', '-pix_fmt', 'yuv420p',
                    '-video_track_timescale', '15360', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2',
                    'abertura.mp4'], cwd=pasta, check=True)
    return pista, quadros


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifesto', type=Path)
    parser.add_argument('corte', type=Path)
    parser.add_argument('saida', type=Path)
    args = parser.parse_args()
    corte = args.corte.resolve()
    saida = args.saida.resolve()
    manifesto = json.loads(args.manifesto.read_text(encoding='utf-8'))
    gancho = manifesto['assinatura_abertura']['gancho']
    if not gancho.startswith('Hoje') or any(c in gancho for c in '\\{}\r\n'):
        parser.error('o gancho deve ser uma frase simples iniciada por Hoje')
    qa = json.loads((corte / 'qa.json').read_text(encoding='utf-8'))
    if qa['status'] not in ('pass', 'pass_with_warnings') or qa['modo'] != 'private_preview' or corte == saida:
        parser.error('use uma prévia privada aprovada e uma pasta de saída diferente')
    timeline = json.loads((corte / 'timeline.json').read_text(encoding='utf-8'))
    digest = hashlib.sha256((corte / 'video_app.mp4').read_bytes()).hexdigest()
    if timeline['episode_id'] != manifesto['episode_id'] or digest != qa['arquivos']['video_app.mp4']['sha256']:
        parser.error('o vídeo precisa corresponder ao episódio e ao arquivo conferido pelo QA')
    lock = perfil.carregar_lock()
    personagem = Path(perfil.RAIZ) / lock['character']['reference_image']
    saida.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=saida) as temp:
        pasta = Path(temp)
        pista, quadros = criar_abertura(pasta, personagem, lock['voice']['voice_id'], gancho)
        base = (corte / 'video_app.mp4').as_posix().replace("'", "'\\''")
        (pasta / 'cortes.txt').write_text(f"file 'abertura.mp4'\nfile '{base}'\n", encoding='utf-8')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'cortes.txt',
                        '-c', 'copy', '-movflags', '+faststart', 'video_app.mp4'], cwd=pasta, check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', 'video_app.mp4', '-f', 'null', '-'],
                       cwd=pasta, check=True)
        (pasta / 'subtitles.srt').write_text(
            legendas(corte / 'subtitles.srt', pista, round(quadros / FPS * 1000)), encoding='utf-8')
        entrega = {'episode_id': manifesto['episode_id'], 'modo': 'private_preview',
                   'abertura_s': quadros / FPS, 'frases': [FRASE, gancho],
                   'voice_id': lock['voice']['voice_id'], 'decodificado': True,
                   'sha256': hashlib.sha256((pasta / 'video_app.mp4').read_bytes()).hexdigest()}
        (pasta / 'assinatura.json').write_text(json.dumps(entrega, ensure_ascii=False, indent=2), encoding='utf-8')
        for nome in ('video_app.mp4', 'subtitles.srt', 'assinatura.json'):
            (pasta / nome).replace(saida / nome)
    print(json.dumps(entrega, ensure_ascii=False))


if __name__ == '__main__':
    main()
