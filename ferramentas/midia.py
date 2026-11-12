"""Mídia: leitura com ffprobe, QA técnico, exportação por plataforma, versão do app (<= limite) e capa.

Tudo via FFmpeg (testado com 9.0.2 gyan.dev). Nenhuma dependência Python além da biblioteca padrão.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

from comum import config_app

# Threads do x264: esta máquina tem 8 GB e outros agentes renderizam ao mesmo tempo. Menos threads, menos memória.
THREADS = os.environ.get('ESTUDIO_THREADS', '4')

PRESETS = {
    # alvo: (largura, altura). Specs conferidas em 11/11/2026; plataformas mudam: confira antes de publicar.
    'reels': {'w': 1080, 'h': 1920, 'crf': 19, 'fps_max': 60, 'audio_k': 192, 'lufs': -14.0},
    'tiktok': {'w': 1080, 'h': 1920, 'crf': 19, 'fps_max': 60, 'audio_k': 192, 'lufs': -14.0},
    'shorts': {'w': 1080, 'h': 1920, 'crf': 19, 'fps_max': 60, 'audio_k': 192, 'lufs': -14.0},
    'youtube': {'w': 1920, 'h': 1080, 'crf': 18, 'fps_max': 60, 'audio_k': 256, 'lufs': -14.0},
    'master': {'w': None, 'h': None, 'crf': 16, 'fps_max': 60, 'audio_k': 320, 'lufs': None},
}


def ffmpeg_ok():
    return bool(shutil.which('ffmpeg') and shutil.which('ffprobe'))


def _rodar(cmd, timeout=3600):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def sondar(caminho):
    """Resumo do ffprobe: duração, vídeo (codec, dimensões, fps, pix_fmt) e áudio (codec, taxa, canais)."""
    code, out, err = _rodar(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', caminho], 120)
    if code != 0:
        raise ValueError(f'ffprobe não leu {os.path.basename(caminho)}: {err.strip()[:300]}')
    d = json.loads(out)
    v = next((s for s in d.get('streams', []) if s.get('codec_type') == 'video' and not s.get('disposition', {}).get('attached_pic')), None)
    a = next((s for s in d.get('streams', []) if s.get('codec_type') == 'audio'), None)
    fmt = d.get('format', {})

    def fps(s):
        try:
            n, m = s.get('avg_frame_rate', '0/1').split('/')
            return round(float(n) / float(m), 3) if float(m) else 0.0
        except (ValueError, ZeroDivisionError):
            return 0.0

    info = {'duracao_s': round(float(fmt.get('duration') or 0), 3), 'bytes': int(fmt.get('size') or os.path.getsize(caminho)),
            'container': fmt.get('format_name', ''), 'bitrate': int(fmt.get('bit_rate') or 0), 'video': None, 'audio': None}
    if v:
        w, h = int(v.get('width') or 0), int(v.get('height') or 0)
        rot = 0
        for sd in v.get('side_data_list', []) or []:
            if 'rotation' in sd:
                rot = int(float(sd['rotation']))
        if abs(rot) in (90, 270):
            w, h = h, w
        info['video'] = {'codec': v.get('codec_name'), 'largura': w, 'altura': h, 'fps': fps(v), 'pix_fmt': v.get('pix_fmt'),
                         'perfil': v.get('profile'), 'rotacao': rot}
    if a:
        info['audio'] = {'codec': a.get('codec_name'), 'taxa': int(a.get('sample_rate') or 0), 'canais': int(a.get('channels') or 0)}
    return info


def faststart(caminho):
    """True se o átomo moov vem antes do mdat (o vídeo começa a tocar antes de baixar inteiro)."""
    try:
        with open(caminho, 'rb') as f:
            pos, fim = 0, os.path.getsize(caminho)
            while pos < fim:
                f.seek(pos)
                cab = f.read(16)
                if len(cab) < 8:
                    return None
                tam = int.from_bytes(cab[:4], 'big')
                tipo = cab[4:8].decode('latin-1')
                if tam == 1:
                    tam = int.from_bytes(cab[8:16], 'big')
                elif tam == 0:
                    tam = fim - pos
                if tipo == 'moov':
                    return True
                if tipo == 'mdat':
                    return False
                if tam < 8:
                    return None
                pos += tam
    except OSError:
        return None
    return None


# ------------------------------------------------------------------ QA técnico
def _medir(caminho, tem_audio):
    """Uma passada do FFmpeg: blackdetect + freezedetect no vídeo; silencedetect + ebur128 no áudio."""
    cmd = ['ffmpeg', '-hide_banner', '-nostats', '-i', caminho, '-vf', 'blackdetect=d=0.5:pix_th=0.10,freezedetect=n=-60dB:d=3']
    if tem_audio:
        cmd += ['-af', 'silencedetect=noise=-45dB:d=1.5,ebur128=peak=true']
    else:
        cmd += ['-an']
    cmd += ['-f', 'null', '-']
    _, _, err = _rodar(cmd, 3600)
    pretos = [(float(a), float(b)) for a, b in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', err)]
    congel = [float(x) for x in re.findall(r'freeze_duration: ([\d.]+)', err)]
    silencios = [float(x) for x in re.findall(r'silence_duration: ([\d.]+)', err)]
    lufs = tp = None
    resumo = err[err.rfind('Summary:'):] if 'Summary:' in err else ''
    m = re.search(r'I:\s+(-?[\d.]+) LUFS', resumo)
    if m:
        lufs = float(m.group(1))
    m = re.search(r'True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS', resumo)
    if m and m.group(1) != '-inf':
        tp = float(m.group(1))
    return {'pretos': pretos, 'congelados_s': congel, 'silencios_s': silencios, 'lufs_integrado': lufs, 'true_peak_dbtp': tp}


def qa_tecnico(caminho, vertical=True, duracao_max=None):
    """QA técnico. status: pass | pass_with_warnings | fail. Não julga conteúdo: isso é da skill video-qa."""
    checks = []

    def chk(nome, ok, info, nivel='aviso'):
        checks.append({'check': nome, 'ok': bool(ok), 'nivel': nivel, 'info': info})

    try:
        s = sondar(caminho)
    except ValueError as e:
        return {'status': 'fail', 'checks': [{'check': 'legivel', 'ok': False, 'nivel': 'erro', 'info': str(e)}], 'medido': {}}
    v, a = s['video'], s['audio']
    chk('tem_video', v is not None, 'faixa de vídeo presente' if v else 'sem faixa de vídeo', 'erro')
    if not v:
        return {'status': 'fail', 'checks': checks, 'medido': s}
    chk('duracao', s['duracao_s'] >= 1, f"{s['duracao_s']} s", 'erro')
    chk('tem_audio', a is not None, f"{a['codec']} {a['taxa']} Hz {a['canais']} canais" if a else 'vídeo mudo')
    chk('codec_video', v['codec'] in ('h264',), f"{v['codec']} (h264 toca em todo navegador e rede)")
    chk('pix_fmt', v['pix_fmt'] == 'yuv420p', f"{v['pix_fmt']} (yuv420p é o compatível)")
    if a:
        chk('codec_audio', a['codec'] == 'aac', f"{a['codec']}")
    w, h = v['largura'], v['altura']
    if vertical:
        chk('proporcao_9x16', h > w and abs(w / h - 9 / 16) < 0.02, f'{w}x{h}')
        chk('resolucao', w >= 1080, f'{w}x{h} (alvo 1080x1920)')
    else:
        chk('resolucao', min(w, h) >= 720, f'{w}x{h}')
    chk('fps', 23.9 <= v['fps'] <= 60.1, f"{v['fps']} fps")
    if duracao_max:
        chk('duracao_formato', s['duracao_s'] <= duracao_max, f"{s['duracao_s']} s (máximo do formato: {duracao_max} s)")
    fs = faststart(caminho)
    if fs is not None:
        chk('faststart', fs, 'moov no início' if fs else 'moov no fim: exporte com -movflags +faststart')

    m = _medir(caminho, a is not None)
    total_preto = sum(b - a_ for a_, b in m['pretos'])
    inicio_preto = any(a_ < 0.3 and (b - a_) >= 0.5 for a_, b in m['pretos'])
    chk('tela_preta', total_preto < s['duracao_s'] * 0.9, f'{total_preto:.1f} s de tela preta no total', 'erro')
    chk('preto_no_inicio', not inicio_preto, 'começa com tela preta (mata a retenção)' if inicio_preto else 'abre com imagem')
    chk('trechos_pretos', total_preto <= 1.0, f'{len(m["pretos"])} trecho(s), {total_preto:.1f} s')
    maior_cong = max(m['congelados_s'] or [0])
    chk('imagem_congelada', maior_cong < 3.0, f'maior trecho parado: {maior_cong:.1f} s' if maior_cong else 'sem trecho parado >= 3 s')
    if a:
        maior_sil = max(m['silencios_s'] or [0])
        chk('silencio', maior_sil < 2.0, f'maior silêncio: {maior_sil:.1f} s' if maior_sil else 'sem silêncio >= 1,5 s')
        if m['lufs_integrado'] is not None:
            chk('loudness', -17.0 <= m['lufs_integrado'] <= -11.0, f"{m['lufs_integrado']} LUFS (alvo -14, faixa -17 a -11)")
        if m['true_peak_dbtp'] is not None:
            chk('true_peak', m['true_peak_dbtp'] <= -1.0, f"{m['true_peak_dbtp']} dBTP (máximo -1)")

    erros = [c for c in checks if not c['ok'] and c['nivel'] == 'erro']
    avisos = [c for c in checks if not c['ok'] and c['nivel'] != 'erro']
    status = 'fail' if erros else 'pass_with_warnings' if avisos else 'pass'
    return {'status': status, 'checks': checks, 'medido': {**s, **m}}


# ------------------------------------------------------------------ exportação
def _filtro_enquadramento(w_in, h_in, w, h, modo):
    if not w or not h:
        return None
    if abs(w_in / h_in - w / h) < 0.01:
        return f'scale={w}:{h}:flags=lanczos,setsar=1'
    if modo == 'crop':
        return f'scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h},setsar=1'
    if modo == 'pad':
        return f'scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1'
    # blur: fundo desfocado da própria imagem, quadro inteiro por cima (padrão para 16:9 -> 9:16)
    return (f'split[bg][fg];[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=24:2,eq=brightness=-0.08[bgb];'
            f'[fg]scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos[fgs];[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1')


def medir_loudnorm(caminho, alvo, tp=-1.5, lra=11):
    _, _, err = _rodar(['ffmpeg', '-hide_banner', '-nostats', '-i', caminho, '-vn', '-af',
                        f'loudnorm=I={alvo}:TP={tp}:LRA={lra}:print_format=json', '-f', 'null', '-'], 1800)
    bloco = err[err.rfind('{'):err.rfind('}') + 1]
    return json.loads(bloco)


def filtro_loudnorm(caminho, alvo, tp=-1.5, lra=11):
    """Loudnorm em duas passadas: mede e aplica com os valores medidos (linear quando possível)."""
    m = medir_loudnorm(caminho, alvo, tp, lra)
    return (f"loudnorm=I={alvo}:TP={tp}:LRA={lra}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")


def exportar(entrada, saida, preset='reels', enquadrar='blur', lufs=None, fps=None):
    """Exporta com preset de plataforma. Devolve o resumo do ffprobe da saída."""
    if preset == 'app':
        return exportar_app(entrada, saida)
    p = PRESETS[preset]
    s = sondar(entrada)
    v = s['video']
    vf = _filtro_enquadramento(v['largura'], v['altura'], p['w'], p['h'], enquadrar)
    fps_alvo = fps or (min(v['fps'], p['fps_max']) if v['fps'] else 30)
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', entrada]
    filtros_v = [vf] if vf else []
    filtros_v.append(f'fps={fps_alvo}')
    filtros_v.append('format=yuv420p')
    complexo = vf and ';' in vf
    if complexo:
        cmd += ['-filter_complex', f'[0:v]{",".join(filtros_v)}[v]', '-map', '[v]', '-map', '0:a?']
    else:
        cmd += ['-vf', ','.join(filtros_v)]
    alvo_lufs = lufs if lufs is not None else p['lufs']
    if s['audio'] and alvo_lufs is not None:
        cmd += ['-af', filtro_loudnorm(entrada, alvo_lufs)]
    cmd += ['-c:v', 'libx264', '-threads', THREADS, '-preset', 'slow', '-crf', str(p['crf']), '-profile:v', 'high', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', f"{p['audio_k']}k", '-ar', '48000', '-movflags', '+faststart', saida]
    code, _, err = _rodar(cmd)
    if code != 0:
        raise RuntimeError(f'FFmpeg falhou: {err.strip()[-600:]}')
    return sondar(saida)


def _compativel_app(s, limite):
    v, a = s['video'], s['audio']
    return (s['bytes'] <= limite and v and v['codec'] == 'h264' and v['pix_fmt'] == 'yuv420p'
            and (a is None or a['codec'] == 'aac') and max(v['largura'], v['altura']) <= 1920)


def exportar_app(entrada, saida, limite=None):
    """Versão para o app: H.264/AAC, faststart, até o limite de bytes (19 MiB por padrão), duas passadas."""
    limite = limite or config_app()['limite_video_app_bytes']
    s = sondar(entrada)
    if _compativel_app(s, limite) and faststart(entrada):
        shutil.copyfile(entrada, saida)
        return sondar(saida)
    dur = max(s['duracao_s'], 1.0)
    audio_bps = 128_000 if s['audio'] else 0
    v = s['video']
    escala = "scale='min(1080,iw)':-2" if v['altura'] >= v['largura'] else "scale=-2:'min(1080,ih)'"
    fator = 0.94
    with tempfile.TemporaryDirectory() as tmp:
        log = os.path.join(tmp, 'passlog')
        for _ in range(3):
            video_bps = int(limite * 8 * fator / dur) - audio_bps
            video_bps = max(250_000, min(video_bps, 8_000_000))
            comum = ['-vf', f'{escala},format=yuv420p', '-c:v', 'libx264', '-threads', THREADS, '-preset', 'medium', '-b:v', str(video_bps),
                     '-maxrate', str(int(video_bps * 1.4)), '-bufsize', str(int(video_bps * 2)), '-profile:v', 'high',
                     '-passlogfile', log]
            code, _, err = _rodar(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', entrada, *comum, '-pass', '1',
                                   '-an', '-f', 'mp4', os.devnull])
            if code != 0:
                raise RuntimeError(f'FFmpeg (passada 1) falhou: {err.strip()[-600:]}')
            audio = ['-c:a', 'aac', '-b:a', '128k', '-ar', '48000'] if s['audio'] else ['-an']
            code, _, err = _rodar(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', entrada, *comum, '-pass', '2',
                                   *audio, '-movflags', '+faststart', saida])
            if code != 0:
                raise RuntimeError(f'FFmpeg (passada 2) falhou: {err.strip()[-600:]}')
            if os.path.getsize(saida) <= limite:
                out = sondar(saida)
                out['video_bps_alvo'] = video_bps
                return out
            fator *= 0.88
    raise RuntimeError(f'Não coube em {limite} bytes depois de 3 tentativas: o vídeo é longo demais para o app.')


def extrair_capa(video, saida_jpg, segundo=None):
    """Capa JPG. Sem segundo definido, o filtro thumbnail escolhe o quadro mais representativo dos primeiros ~10 s."""
    if segundo is not None:
        cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-ss', str(segundo), '-i', video, '-frames:v', '1', '-q:v', '3', saida_jpg]
    else:
        cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', video, '-vf', 'thumbnail=240', '-frames:v', '1', '-q:v', '3', saida_jpg]
    code, _, err = _rodar(cmd, 300)
    if code != 0 or not os.path.exists(saida_jpg):
        raise RuntimeError(f'Capa não gerada: {err.strip()[-300:]}')
    return saida_jpg


def capa_para_jpg(imagem, saida_jpg, largura_max=1080):
    """Converte a capa enviada (png/webp/jpg) para JPG leve, sem aumentar."""
    code, _, err = _rodar(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', imagem, '-vf',
                           f"scale='min({largura_max},iw)':-2", '-frames:v', '1', '-q:v', '3', saida_jpg], 120)
    if code != 0:
        raise RuntimeError(f'Capa não convertida: {err.strip()[-300:]}')
    return saida_jpg
