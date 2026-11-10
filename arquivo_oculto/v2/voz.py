"""Adapter de TTS do Arquivo Oculto V2 (Kokoro ONNX, local, gratuito, Apache-2.0).

- Presets fixos e versionados: a mesma voz/versão em todos os episódios (perfil voice.tts_policy).
- Cache por hash (texto + preset + versão do modelo): re-render não regrava a voz.
- Cada fala é sintetizada isolada: a duração REAL de cada trecho vira o voice_span da timeline.
- Pós-processamento por FFmpeg (tom, timbre, sala), aplicado à pista inteira para manter a voz idêntica entre cenas.

Uso:  python -m arquivo_oculto.v2.voz amostras <pasta>   -> 3 amostras de ~10 s + métricas + comparativo
"""
import hashlib
import json
import os
import subprocess
import sys
import wave

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
AO = os.path.dirname(AQUI)
TTS_DIR = os.environ.get('AO_TTS', os.path.join(AO, 'tts'))
CACHE = os.environ.get('AO_CACHE', os.path.join(AO, 'cache', 'tts_v2'))
SR = 24000
MODELO = 'kokoro-v1.0.int8'

# Cada preset: vozes Kokoro (mistura de estilos), velocidade e cadeia de pós-processamento.
# 'tom' < 1 deixa a voz mais grave (asetrate) sem mudar a duração (atempo compensa).
PRESETS = {
    'arquivista-voz-01': {  # legado V1 (preservado para comparação; é o que está nos MP4 atuais)
        'vozes': {'pm_alex': 1.0}, 'velocidade': 1.0, 'tom': 0.90,
        'cadeia': 'equalizer=f=120:t=q:w=1:g=4,equalizer=f=3500:t=q:w=1:g=2,highpass=f=60,aecho=0.8:0.6:45|90:0.18|0.10',
        'descricao': 'V1: pm_alex, tom 0,90, eco de sala largo'},
    'arquivista-v2-a': {
        'vozes': {'pm_alex': 1.0}, 'velocidade': 0.82, 'tom': 0.86,
        'cadeia': ('highpass=f=55,equalizer=f=110:t=q:w=1.1:g=4,equalizer=f=450:t=q:w=1.2:g=-2,'
                   'equalizer=f=3200:t=q:w=1:g=2.5,asoftclip=type=tanh:threshold=0.6:output=0.95,'
                   'aecho=0.85:0.35:28|61:0.10|0.05'),
        'descricao': 'Grave-média íntima: pm_alex, velocidade 0,82, tom 0,86, presença em 3,2 kHz, leve aspereza (saturação), sala curta'},
    'arquivista-v2-b': {
        'vozes': {'pm_santa': 1.0}, 'velocidade': 0.82, 'tom': 0.87,
        'cadeia': ('highpass=f=60,equalizer=f=130:t=q:w=1:g=3,equalizer=f=2600:t=q:w=1.2:g=3,'
                   'aecho=0.9:0.5:7|13:0.22|0.12,aecho=0.85:0.3:33:0.08'),
        'descricao': 'Ressonante e metálica: pm_santa, velocidade 0,82, tom 0,87, filtro de pente curto (metal), sala curta'},
    'arquivista-v2-c': {
        'vozes': {'pm_alex': 0.6, 'pm_santa': 0.4}, 'velocidade': 0.81, 'tom': 0.85,
        'cadeia': ('highpass=f=55,equalizer=f=105:t=q:w=1:g=4.5,equalizer=f=500:t=q:w=1.2:g=-2.5,'
                   'equalizer=f=2900:t=q:w=1:g=2.5,aecho=0.9:0.45:6|11:0.16|0.08,'
                   'asoftclip=type=tanh:threshold=0.65:output=0.95,aecho=0.85:0.32:30|64:0.09|0.05'),
        'descricao': 'Mistura 60% pm_alex + 40% pm_santa, velocidade 0,81, tom 0,85, metal discreto + aspereza + sala curta'},
}
TEXTO_AMOSTRA = ('Este baralho foi lançado em dezembro de mil novecentos e noventa e quatro. '
                 'Décadas depois... há quem jure que ele previu o futuro. '
                 'Eu guardo as datas. E as datas contam outra história.')


class Voz:
    def __init__(self, preset):
        if preset not in PRESETS:
            raise KeyError(f'preset de voz desconhecido: {preset}')
        self.nome = preset
        self.cfg = PRESETS[preset]
        self._k = None

    def _kokoro(self):
        if self._k is None:
            from kokoro_onnx import Kokoro
            self._k = Kokoro(os.path.join(TTS_DIR, 'kokoro-v1.0.int8.onnx'), os.path.join(TTS_DIR, 'voices-v1.0.bin'))
        return self._k

    def estilo(self):
        vozes = self.cfg['vozes']
        if len(vozes) == 1:
            return next(iter(vozes))
        k = self._kokoro()
        return sum(k.get_voice_style(n) * w for n, w in vozes.items())

    def chave(self, texto):
        h = json.dumps({'m': MODELO, 'v': self.cfg['vozes'], 's': self.cfg['velocidade'], 't': texto}, sort_keys=True)
        return hashlib.sha256(h.encode()).hexdigest()[:24]

    def sintetizar(self, texto):
        """Fala crua (antes do pós-processamento), 24 kHz mono float32, com cache por hash."""
        os.makedirs(CACHE, exist_ok=True)
        cp = os.path.join(CACHE, self.chave(texto) + '.npy')
        if os.path.exists(cp):
            return np.load(cp)
        s, sr = self._kokoro().create(texto, voice=self.estilo(), speed=self.cfg['velocidade'], lang='pt-br')
        assert sr == SR, sr
        a = np.abs(s); idx = np.where(a > 0.01)[0]
        if len(idx):
            s = s[max(0, idx[0] - 480): idx[-1] + 960]
        s = np.nan_to_num(s.astype(np.float32))
        np.save(cp, s)
        return s

    def filtro_ffmpeg(self, rotulo_in='0:a', rotulo_out='v'):
        t = self.cfg['tom']
        return (f'[{rotulo_in}]asetrate={SR}*{t},aresample=48000,atempo={1 / t:.5f},{self.cfg["cadeia"]},'
                f'acompressor=threshold=-20dB:ratio=3:attack=5:release=140[{rotulo_out}]')

    def config_registro(self):
        return {'provider': 'kokoro-onnx (local)', 'voice_model': MODELO, 'voice_id': self.nome,
                'vozes_base': self.cfg['vozes'], 'locale': 'pt-BR', 'rate': self.cfg['velocidade'],
                'pitch': self.cfg['tom'], 'style': self.cfg['descricao'], 'pos_processamento': self.cfg['cadeia'],
                'version': f'{self.nome}@{MODELO}', 'licenca': 'Apache-2.0', 'custo_brl': 0}


def escrever_wav(path, x, sr=SR):
    x = np.clip(np.nan_to_num(x), -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def ler_wav(path):
    with wave.open(path, 'rb') as w:
        sr = w.getframerate(); n = w.getnframes(); ch = w.getnchannels()
        x = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, sr


def processar(voz, cru_wav, saida_wav):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', cru_wav, '-filter_complex',
                    voz.filtro_ffmpeg() + ';[v]loudnorm=I=-16:TP=-1.5[o]', '-map', '[o]', '-ar', '48000', '-ac', '1', saida_wav],
                   check=True)


def metricas(wav_path, palavras):
    x, sr = ler_wav(wav_path)
    dur = len(x) / sr
    # F0 por autocorrelação em janelas sonoras (50–300 Hz)
    win = int(0.04 * sr); hop = int(0.01 * sr); f0 = []
    for i in range(0, len(x) - win, hop):
        seg = x[i:i + win] * np.hanning(win)
        if np.sqrt(np.mean(seg ** 2)) < 0.02:
            continue
        ac = np.correlate(seg, seg, 'full')[win - 1:]
        lo, hi = int(sr / 300), int(sr / 50)
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] > 0.35 * ac[0]:
            f0.append(sr / k)
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    fr = np.fft.rfftfreq(len(x), 1 / sr)
    centroide = float((spec * fr).sum() / max(1e-9, spec.sum()))
    env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    silencio = env < 0.01
    pausas = []; run = 0
    for s in silencio:
        if s: run += 1
        else:
            if run * 10 >= 200: pausas.append(run * 10)
            run = 0
    return {'duracao_s': round(dur, 2), 'wpm': round(palavras / dur * 60, 1),
            'f0_mediana_hz': round(float(np.median(f0)), 1) if f0 else None,
            'centroide_espectral_hz': round(centroide), 'pausas_ms': pausas}


def pontuar(m):
    """Distância ao perfil-alvo descrito no V2 (sem a referência sonora antiga, que não está no disco)."""
    pen = 0.0
    f0 = m['f0_mediana_hz'] or 200
    pen += max(0, f0 - 115) / 10 + max(0, 85 - f0) / 10      # grave-média masculina
    pen += max(0, m['wpm'] - 155) / 5 + max(0, 135 - m['wpm']) / 5
    pen += max(0, m['centroide_espectral_hz'] - 2200) / 400   # escura, mas inteligível
    pen += max(0, 900 - m['centroide_espectral_hz']) / 200
    return round(pen, 2)


def amostras(pasta, presets=('arquivista-voz-01', 'arquivista-v2-a', 'arquivista-v2-b', 'arquivista-v2-c')):
    pasta = os.path.abspath(pasta)
    os.makedirs(pasta, exist_ok=True)
    palavras = len(TEXTO_AMOSTRA.replace('...', ' ').split())
    out = {'texto': TEXTO_AMOSTRA, 'referencia_sonora_antiga': 'AUSENTE (video_antigo_kwai_1202.mp4 não está no disco)',
           'amostras': []}
    for p in presets:
        v = Voz(p)
        cru = os.path.join(pasta, f'{p}_cru.wav'); fin = os.path.join(pasta, f'{p}.wav')
        escrever_wav(cru, v.sintetizar(TEXTO_AMOSTRA))
        processar(v, cru, fin)
        m = metricas(fin, palavras)
        out['amostras'].append({'preset': p, 'arquivo': os.path.basename(fin), **m, 'distancia_alvo': pontuar(m),
                                'config': v.config_registro()})
        os.remove(cru)
    # comparativo único para escuta: anúncio por bip, amostra, silêncio
    lista = os.path.join(pasta, 'lista.txt')
    sil = os.path.join(pasta, '_sil.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=mono', '-t', '1.2', sil], check=True)
    with open(lista, 'w') as f:
        for a in out['amostras']:
            f.write(f"file '{a['arquivo']}'\nfile '_sil.wav'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lista, '-c:a', 'libmp3lame',
                    '-q:a', '3', os.path.join(pasta, 'comparativo_vozes.mp3')], cwd=pasta, check=True)
    os.remove(lista); os.remove(sil)
    cand = [a for a in out['amostras'] if a['preset'] != 'arquivista-voz-01']
    out['escolha_provisoria'] = min(cand, key=lambda a: a['distancia_alvo'])['preset']
    out['criterio'] = ('Menor distância ao alvo do V2 (F0 85–115 Hz, 135–155 palavras/min, timbre escuro e inteligível). '
                       'Provisória: a comparação com a voz do vídeo antigo depende do arquivo de referência.')
    with open(os.path.join(pasta, 'amostras_voz.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return out


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'amostras':
        r = amostras(sys.argv[2])
        for a in r['amostras']:
            print(f"{a['preset']:20s} {a['duracao_s']:5.2f}s {a['wpm']:6.1f} wpm F0 {a['f0_mediana_hz']} Hz "
                  f"centróide {a['centroide_espectral_hz']} Hz pausas {a['pausas_ms']} -> distância {a['distancia_alvo']}")
        print('escolha provisória:', r['escolha_provisoria'])
    else:
        print(__doc__)
