#!/usr/bin/env python3
"""Fábrica do Arquivo Oculto: manifesto do episódio -> MP4 + SRT + capa PNG + production_manifest + QA.

Uso:
  python3 fabrica.py <manifesto_pacote.json> <producao.json> <pasta_saida>

- manifesto_pacote: formato do pacote ARQUIVO_OCULTO_CLAUDE_VIDEO_FACTORY_V1 (examples/EP0x_*.json): fatos, fontes, cenas planejadas.
- producao: como cada cena vira imagem nesta instância (narração por cena, tipo de cena, selo).
Modo visual desta instância: "animated_stills" (Arquivista animado por deformação + cenas desenhadas por código).
Não há gerador de imagem/vídeo por IA acessível daqui; o adapter fica registrado como indisponível no manifesto de produção.
"""
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import motor  # noqa: E402
import cenas_extra  # noqa: E402,F401  (registra os tipos de cena extras)
from PIL import Image, ImageDraw, ImageEnhance  # noqa: E402
import numpy as np  # noqa: E402

PROVEDORES = {
    'tts': {'id': 'kokoro-onnx', 'status': 'disponivel', 'custo': 0, 'licenca': 'Apache-2.0'},
    'imagem_ia': {'id': None, 'status': 'indisponivel', 'motivo': 'Canva, Gamma e Figma geram, mas os domínios de download estão bloqueados pela rede deste ambiente; Figma Weave sem conta vinculada; uso pago exige autorização'},
    'video_ia': {'id': None, 'status': 'indisponivel', 'motivo': 'nenhuma API de vídeo generativo (Veo/Flow, HeyGen etc.) configurada com credencial'},
    'musica': {'id': 'sintese-propria', 'status': 'disponivel', 'custo': 0, 'licenca': 'original (gerada pelo motor)'},
    'render': {'id': 'motor-arquivista (Python + FFmpeg)', 'status': 'disponivel'},
}


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def capa_png(ep_num, gancho, path):
    base = motor.Base()
    im = base.recorte(motor.REGIOES['close'], 1.0).resize((motor.W, motor.H))
    im = ImageEnhance.Brightness(im).enhance(0.9).convert('RGBA')
    g = np.zeros((motor.H, motor.W, 4), np.uint8); ys = np.arange(motor.H)
    g[..., 3] = (np.clip((ys - 1050) / 500, 0, 1) * 235).astype(np.uint8)[:, None]
    im.alpha_composite(Image.fromarray(g, 'RGBA'))
    d = ImageDraw.Draw(im)
    tam = 128
    while True:
        f = motor.fonte('anton', tam); ls = motor.quebrar(gancho, f, motor.W - 160)
        if len(ls) <= 3 or tam < 70: break
        tam -= 8
    y = 1330 - (len(ls) - 1) * tam * 0.55
    for i, l in enumerate(ls):
        motor.texto_centro(d, motor.W / 2, y + i * tam * 1.1, l, f, motor.OURO_CLARO + (255,), stroke=4, stroke_cor=(15, 10, 4))
    motor.texto_centro(d, motor.W / 2, 1700, f'ARQUIVO OCULTO · Nº {ep_num:02d}', motor.fonte('cinzel', 44), motor.CREME + (230,))
    im.convert('RGB').save(path)


def qa(mp4, srt_path, capa, alvo, prod, man, inicios=None):
    r = {'checks': [], 'status': 'pass'}

    def add(nome, ok, info, grave=True):
        r['checks'].append({'check': nome, 'ok': bool(ok), 'info': info})
        if not ok:
            r['status'] = 'fail' if grave else ('pass_with_warnings' if r['status'] == 'pass' else r['status'])
    pr = json.loads(sh(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', mp4]).stdout or '{}')
    v = next((s for s in pr.get('streams', []) if s['codec_type'] == 'video'), {})
    a = next((s for s in pr.get('streams', []) if s['codec_type'] == 'audio'), {})
    dur = float(pr.get('format', {}).get('duration', 0))
    add('video_1080x1920_h264', v.get('width') == 1080 and v.get('height') == 1920 and v.get('codec_name') == 'h264', f"{v.get('width')}x{v.get('height')} {v.get('codec_name')} {v.get('r_frame_rate')} {v.get('pix_fmt')}")
    add('audio_aac', a.get('codec_name') == 'aac', f"{a.get('codec_name')} {a.get('sample_rate')} Hz {a.get('channels')} canais")
    add('duracao_meta', abs(dur - alvo) <= 6, f'{dur:.2f} s (meta {alvo} s)', grave=False)
    add('tamanho_upload_app', os.path.getsize(mp4) < 20 * 1024 * 1024, f'{os.path.getsize(mp4) / 1048576:.1f} MiB', grave=False)
    head = open(mp4, 'rb').read(64 * 1024)
    add('faststart_moov', b'moov' in head, 'moov no início do arquivo' if b'moov' in head else 'moov no fim')
    # quadros não pretos
    lums = []
    # meio de cada cena (longe dos cortes, onde há um escurecimento proposital de 0,1 s) + 0,3 s
    if inicios:
        fins = list(inicios[1:]) + [dur - 2.4]
        pontos = [0.3] + [(a + b) / 2 for a, b in zip(inicios, fins)]
    else:
        pontos = [0.3] + [dur * k / 8 for k in range(1, 8)]
    for t in pontos:
        out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', mp4, '-frames:v', '1', '-vf', 'scale=108:192', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
                             capture_output=True).stdout
        lums.append(round(float(np.frombuffer(out, np.uint8).mean()) if out else 0, 1))
    add('quadros_nao_pretos', min(lums) > 6, f'luminância média no meio de cada cena: {lums}')
    # loudness
    lo = sh(['ffmpeg', '-v', 'info', '-i', mp4, '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
    import re
    I = re.findall(r'I:\s+(-?[\d.]+) LUFS', lo); TP = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', lo)
    li = float(I[-1]) if I else None; tp = float(TP[-1]) if TP else None
    add('loudness', li is not None and -18 <= li <= -12 and (tp is None or tp <= -0.5), f'integrado {li} LUFS, pico {tp} dBTP (alvo -16±2 / ≤ -1)', grave=False)
    # legendas
    blocos = open(srt_path, encoding='utf-8').read().strip().split('\n\n')
    tempos = []
    for b in blocos:
        ln = b.split('\n')
        if len(ln) >= 2 and '-->' in ln[1]:
            def s2(x):
                h, m, rest = x.strip().split(':'); s_, ms = rest.split(',')
                return int(h) * 3600 + int(m) * 60 + int(s_) + int(ms) / 1000
            a_, b_ = ln[1].split('-->'); tempos.append((s2(a_), s2(b_)))
    mono = all(tempos[i][0] <= tempos[i + 1][0] and tempos[i][0] < tempos[i][1] for i in range(len(tempos) - 1))
    add('srt_monotonico', mono and len(tempos) > 3, f'{len(tempos)} legendas, última termina em {tempos[-1][1] if tempos else 0:.2f} s')
    txt_srt = ' '.join(b.split('\n', 2)[2] for b in blocos if b.count('\n') >= 2)
    falas = ' '.join(c['fala'] for c in prod['cenas'])
    add('legenda_igual_narracao', ''.join(txt_srt.split()) == ''.join(falas.split()), 'texto das legendas = texto narrado')
    add('capa_png', os.path.exists(capa) and Image.open(capa).size == (1080, 1920), 'capa 1080x1920')
    # editorial
    rec = [s['scene_id'] for s in man.get('scenes', []) if s.get('reconstruction_label_required')]
    sem_selo = [c['scene_id'] for c in prod['cenas'] if c['scene_id'] in rec and not c.get('selo')]
    add('selos_reconstituicao', not sem_selo, f'cenas que pedem rótulo: {rec}; sem selo: {sem_selo}')
    add('claims_com_fonte', all(c.get('sources') or c['status'] in ('interpretation', 'allegation') for c in man.get('claims', [])),
        ', '.join(f"{c['id']}:{c['status']}" for c in man.get('claims', [])))
    arq = [c['scene_id'] for c in prod['cenas'] if c['v']['tipo'] == 'arq']
    add('arquivista_presente', len(arq) >= 2, f'cenas com o Arquivista: {arq}')
    r['duracao'] = dur
    return r


def main():
    man_path, prod_path, saida = sys.argv[1:4]
    man = json.load(open(man_path, encoding='utf-8'))
    prod = json.load(open(prod_path, encoding='utf-8'))
    os.makedirs(saida, exist_ok=True)
    eid = man['episode_id']
    mp4 = os.path.join(saida, f'{eid}.mp4'); srt_p = os.path.join(saida, f'{eid}.srt')
    capa = os.path.join(saida, f'{eid}_cover.png'); capa_jpg = os.path.join(saida, f'{eid}_frame.jpg')
    estado = {'episode_id': eid, 'status': 'rendering', 'inicio': dt.datetime.now().isoformat()}
    json.dump(estado, open(os.path.join(saida, f'{eid}_status.json'), 'w'), ensure_ascii=False)
    ep = {'num': prod['num'], 'titulo': man['title'], 'serie': man.get('format'), 'cenas': prod['cenas']}
    dur = motor.render(ep, mp4, capa_jpg)
    motor.srt(motor.ULTIMO['legendas'], srt_p)
    capa_png(prod['num'], man.get('hook') or man['title'], capa)
    rel = qa(mp4, srt_p, capa, man.get('target_duration_sec', 38), prod, man, motor.ULTIMO['inicio'])
    pm = {
        'episode_id': eid, 'brand_id': man['brand_id'], 'character_id': man['character_id'], 'title': man['title'],
        'gerado_em': dt.datetime.now().isoformat(), 'modo_visual': 'animated_stills',
        'aviso_modo': 'Arquivista animado por deformação da imagem de referência (cabeça, máscara, respiração, luz e poeira) e cenas desenhadas por código. Não é vídeo generativo.',
        'personagem': {'referencia': 'assets/arquivista_conceito_premium.png (máscara convertida para marfim, look canônico provisório)',
                       'referencia_canonica_privada': 'assets/arquivista_legado_referencia_privada.png (só referência interna, não publicada)'},
        'voz': motor.ULTIMO['voz_cfg'], 'provedores': PROVEDORES, 'custo_estimado_brl': 0,
        'manifesto_origem': os.path.basename(man_path), 'producao': os.path.basename(prod_path),
        'claims': man.get('claims', []), 'fontes': man.get('source_urls', []),
        'cenas': [{'scene_id': c['scene_id'], 'inicio_s': round(motor.ULTIMO['inicio'][i], 2), 'tipo': c['v']['tipo'], 'tela': c.get('tela', ''),
                   'selo': c.get('selo'), 'fala': c['fala'],
                   'asset_class': next((s['asset_class'] for s in man['scenes'] if s['scene_id'] == c['scene_id']), None),
                   'origem_visual': 'personagem (imagem de referência do proprietário, animada)' if c['v']['tipo'] == 'arq' else 'gerado por código (ilustração original)'}
                  for i, c in enumerate(prod['cenas'])],
        'musica_sfx': 'sintetizados pelo motor (drone, pulso, impactos, sting): sem direitos de terceiros',
        'arquivos': {k: {'path': os.path.basename(p), 'sha256': sha(p), 'bytes': os.path.getsize(p)} for k, p in [('mp4', mp4), ('srt', srt_p), ('cover', capa)]},
        'duracao_s': round(dur, 2), 'qa_status': rel['status'], 'publicacao_aprovada': False,
    }
    json.dump(pm, open(os.path.join(saida, f'{eid}_manifest.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(rel, open(os.path.join(saida, f'{eid}_qa.json'), 'w'), ensure_ascii=False, indent=1)
    estado.update(status='completed' if rel['status'] in ('pass', 'pass_with_warnings') else 'failed', fim=dt.datetime.now().isoformat(), qa=rel['status'])
    json.dump(estado, open(os.path.join(saida, f'{eid}_status.json'), 'w'), ensure_ascii=False)
    print(json.dumps({'mp4': mp4, 'dur': round(dur, 2), 'qa': rel['status'], 'falhas': [c for c in rel['checks'] if not c['ok']]}, ensure_ascii=False, indent=1))


def so_qa(man_path, prod_path, saida):
    """Refaz só o QA de um episódio já renderizado (sem gastar render)."""
    man = json.load(open(man_path, encoding='utf-8')); prod = json.load(open(prod_path, encoding='utf-8'))
    eid = man['episode_id']; j = lambda x: os.path.join(saida, f'{eid}{x}')
    pm = json.load(open(j('_manifest.json'), encoding='utf-8'))
    rel = qa(j('.mp4'), j('.srt'), j('_cover.png'), man.get('target_duration_sec', 38), prod, man, [c['inicio_s'] for c in pm['cenas']])
    json.dump(rel, open(j('_qa.json'), 'w'), ensure_ascii=False, indent=1)
    pm['qa_status'] = rel['status']; json.dump(pm, open(j('_manifest.json'), 'w'), ensure_ascii=False, indent=1)
    st = json.load(open(j('_status.json'))); st.update(status='completed' if rel['status'] in ('pass', 'pass_with_warnings') else 'failed', qa=rel['status'])
    json.dump(st, open(j('_status.json'), 'w'), ensure_ascii=False)
    print(rel['status'], [c for c in rel['checks'] if not c['ok']])


if __name__ == '__main__':
    if '--so-qa' in sys.argv:
        a = [x for x in sys.argv[1:] if x != '--so-qa']; so_qa(*a)
    else:
        main()
