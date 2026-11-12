"""Base comum da Central do Estúdio: caminhos, perfis, registro (livro de entregas) e utilidades.

Só biblioteca padrão do Python. FFmpeg/ffprobe são chamados por midia.py.
"""
import hashlib
import json
import os
import re
import unicodedata
from datetime import datetime, timedelta, timezone

RAIZ = os.environ.get('ESTUDIO_CENTRAL', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = os.path.join(RAIZ, 'config')
ENTRADA = os.path.join(RAIZ, 'entrada')
ENTREGAS = os.path.join(RAIZ, 'entregas')
REGISTRO = os.path.join(RAIZ, 'registro', 'entregas.jsonl')
ORIENTACOES = os.path.join(RAIZ, 'orientacoes')
BRT = timezone(timedelta(hours=-3))

PACOTE_ID = 'estudio-geovani/entrega@1'
TIPOS = ('video_pronto', 'pauta', 'material_bruto', 'orientacao')
AGENTES = ('claude-code', 'codex', 'chatgpt', 'claude-chat', 'geovani', 'outro')
EXT_VIDEO = ('.mp4', '.mov', '.m4v', '.mkv', '.webm')
EXT_IMAGEM = ('.jpg', '.jpeg', '.png', '.webp')


def agora_iso():
    return datetime.now(BRT).isoformat(timespec='seconds')


def hoje_iso():
    return datetime.now(BRT).date().isoformat()


def ler_json(caminho):
    with open(caminho, encoding='utf-8-sig') as f:
        return json.load(f)


def gravar_json(caminho, dados):
    os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
    tmp = caminho + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp, caminho)


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def slug(texto, limite=48):
    t = unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode('ascii').lower()
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')
    return (t[:limite].rstrip('-')) or 'sem-titulo'


# ------------------------------------------------------------------ perfis
def perfis():
    """Todos os perfis de config/perfis/*.json, por id."""
    pasta = os.path.join(CONFIG, 'perfis')
    out = {}
    for nome in sorted(os.listdir(pasta)):
        if nome.endswith('.json'):
            p = ler_json(os.path.join(pasta, nome))
            out[p['id']] = p
    return out


def resolver_perfil(valor):
    """Aceita id ou apelido ('arquivo-oculto', 'Dr. Geovani', '@direitaxx') e devolve o id canônico, ou None."""
    if not valor:
        return None
    alvo = slug(str(valor).lstrip('@'))
    for pid, p in perfis().items():
        nomes = {pid, slug(p.get('nome', '')), slug(p.get('nome_completo', ''))} | {slug(a) for a in p.get('apelidos', [])}
        if alvo in nomes:
            return pid
    return None


def config_app():
    return ler_json(os.path.join(CONFIG, 'app.json'))


# ------------------------------------------------------------------ registro (livro de entregas, só acrescenta)
def registrar_evento(evento):
    """Acrescenta uma linha ao livro. Cada linha é um evento; o estado atual de uma entrega é o último evento dela."""
    os.makedirs(os.path.dirname(REGISTRO), exist_ok=True)
    evento = dict(evento)
    evento.setdefault('em', agora_iso())
    with open(REGISTRO, 'a', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(evento, ensure_ascii=False) + '\n')
    return evento


def eventos():
    if not os.path.exists(REGISTRO):
        return []
    with open(REGISTRO, encoding='utf-8') as f:
        return [json.loads(linha) for linha in f if linha.strip()]


def estado_atual():
    """id -> último evento (com os campos de eventos anteriores preservados quando o último não os repete)."""
    atual = {}
    for ev in eventos():
        base = atual.get(ev['id'], {})
        base = {**base, **ev}
        atual[ev['id']] = base
    return atual


def caminho_entrega(pid, entrega_id, quando=None):
    mes = (quando or hoje_iso())[:7]
    return os.path.join(ENTREGAS, pid, mes, entrega_id)


def localizar_entrega(entrega_id):
    est = estado_atual().get(entrega_id)
    if est and est.get('caminho'):
        p = os.path.join(RAIZ, est['caminho'])
        if os.path.isdir(p):
            return p
    raise SystemExit(f'Entrega {entrega_id} não encontrada no registro (rode: python ferramentas/estudio.py status)')


def rel(caminho):
    return os.path.relpath(caminho, RAIZ).replace('\\', '/')
