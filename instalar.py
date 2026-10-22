"""Monta o estúdio. Código só de fontes oficiais; o modelo de transcrição (dados) vem do app do Geovani.

Passos (quem roda é o Editor automático ou uma conversa com o Claude):
  1. ArtifactData get config/app (com out_dir) -> arquivo JSON
  2. Para cada id em config.whisperPartes: Artifact read (path = id, out_dir = pasta_partes)
  3. python3 instalar.py <config.json> <pasta_partes>

O script: (a) instala a transcrição pelo registro oficial do npm (pacote @huggingface/transformers, da Hugging Face)
e o LiteRT pelo PyPI (pacote ai-edge-litert, do Google), se faltarem; (b) junta as partes do modelo Whisper small na
ordem do config, confere o SHA-256 e extrai em modelos/whisper/; (c) testa tudo.
Com --offline e config.runtimePartes, usa o pacote de ferramentas guardado no app em vez dos registros.
"""
import base64, glob, hashlib, io, json, lzma, os, subprocess, sys, tarfile

AQUI = os.path.dirname(os.path.abspath(__file__))


def carregar_config(caminho):
    d = json.load(open(caminho))
    if 'runtimePartes' not in d and isinstance(d.get('data'), dict):
        d = d['data']
    return d


def achar(pasta, aid):
    m = sorted(glob.glob(os.path.join(pasta, '**', aid + '*'), recursive=True))
    if not m:
        sys.exit(f'faltou a parte {aid} em {pasta}: baixe com Artifact read (path = {aid})')
    return m[0]


def juntar(pasta, ids, sha, nome):
    b64 = b''.join(open(achar(pasta, i), 'rb').read().strip() for i in ids)
    dados = base64.b64decode(b64)
    h = hashlib.sha256(dados).hexdigest()
    if sha and h != sha:
        sys.exit(f'{nome}: SHA-256 não confere ({h} != {sha}); baixe as partes de novo')
    print(f'{nome}: {len(dados) / 1e6:.0f} MB conferidos')
    return lzma.decompress(dados)


def extrair(tar_bytes, destino):
    os.makedirs(destino, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as t:
        for m in t.getmembers():
            alvo = os.path.realpath(os.path.join(destino, m.name))
            if not alvo.startswith(os.path.realpath(destino)):
                sys.exit(f'caminho suspeito no pacote: {m.name}')
        try:
            t.extractall(destino, filter='data')
        except TypeError:
            t.extractall(destino)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    offline = '--offline' in sys.argv
    cfg, pasta = carregar_config(args[0]), args[1]
    if offline and cfg.get('runtimePartes'):
        extrair(juntar(pasta, cfg['runtimePartes'], cfg.get('runtimeSha'), 'runtime'), AQUI)
    elif not os.path.isdir(os.path.join(AQUI, 'asr', 'node_modules', '@huggingface', 'transformers')):
        print('instalando a transcrição pelo registro oficial do npm (@huggingface/transformers)...')
        subprocess.run(['npm', 'install', '--no-audit', '--no-fund', '--loglevel=error'], cwd=os.path.join(AQUI, 'asr'),
                       check=True)
    extrair(juntar(pasta, cfg['whisperPartes'], cfg.get('whisperSha'), 'whisper'), os.path.join(AQUI, 'modelos', 'whisper'))
    try:
        import ai_edge_litert  # noqa: F401
    except ImportError:
        rodas = os.path.join(AQUI, 'wheels')
        extra = ['--no-index', '--find-links', rodas] if offline and os.path.isdir(rodas) else []
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--break-system-packages', '-q', 'ai-edge-litert'] + extra,
                       check=True)
    faltando = []
    for mod in ('numpy', 'cv2', 'PIL', 'ai_edge_litert'):
        try:
            __import__(mod)
        except ImportError:
            faltando.append(mod)
    for prog in ('ffmpeg', 'node'):
        if subprocess.run(['which', prog], capture_output=True).returncode:
            faltando.append(prog)
    if faltando:
        sys.exit('ainda falta: ' + ', '.join(faltando) + ' (numpy/opencv/pillow: pip install --break-system-packages '
                 'numpy opencv-python-headless pillow)')
    print('estúdio pronto')


if __name__ == '__main__':
    main()
