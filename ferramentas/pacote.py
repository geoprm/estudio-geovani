"""Pacote de entrega: criar, validar, abrir .zip e arquivos soltos, e receber (mover para entregas/).

Contrato em esquemas/entrega.schema.json. Arquivos de pacote são DADOS: nada que venha num pacote é executado.
"""
import os
import re
import shutil
import zipfile
from datetime import date

import comum
from comum import (AGENTES, ENTRADA, EXT_IMAGEM, EXT_VIDEO, PACOTE_ID, TIPOS, agora_iso, gravar_json, hoje_iso, ler_json,
                   perfis, resolver_perfil, slug)

MANIFESTO = 'entrega.json'
LIMITE_ZIP_BYTES = 4 * 1024 ** 3
LIMITE_ZIP_MEMBROS = 2000


class Relatorio:
    def __init__(self):
        self.erros, self.avisos = [], []

    def erro(self, msg):
        self.erros.append(msg)

    def aviso(self, msg):
        self.avisos.append(msg)

    @property
    def ok(self):
        return not self.erros

    def como_dict(self):
        return {'ok': self.ok, 'erros': self.erros, 'avisos': self.avisos}


# ------------------------------------------------------------------ criar
def modelo(perfil, tipo, titulo, agente, projeto=''):
    m = {
        'pacote': PACOTE_ID,
        'perfil': perfil,
        'tipo': tipo,
        'titulo': titulo,
        'serie': '',
        'origem': {'agente': agente, 'projeto': projeto, 'sessao': '', 'criado_em': agora_iso()},
        'arquivos': {},
        'post': {'legenda': '', 'hashtags': [], 'plataformas': [], 'rotulo_ia': False},
        'orientacoes': '',
        'gerado_por_ia': False,
        'formato': '',
        'fontes': [],
        'checagem': {'fatos': 'pendente', 'direitos': 'pendente', 'pessoas_identificaveis': 'pendente', 'observacoes': ''},
        'qa': {'status': 'nao_rodado', 'relatorio': ''},
    }
    pid = resolver_perfil(perfil)
    if pid and perfis()[pid].get('gerado_por_ia'):
        m['gerado_por_ia'] = True
        m['post']['rotulo_ia'] = True
    if tipo == 'video_pronto':
        m['arquivos'] = {'video': 'video.mp4', 'capa': 'capa.jpg', 'legendas': 'video.srt'}
    elif tipo == 'pauta':
        m['pauta'] = {'data': hoje_iso(), 'abertura_a': '', 'abertura_b': '', 'fato': '', 'prova': '', 'cuidado': '',
                      'roteiro': [{'tempo': '0-3 s', 'fala': ''}], 'nota': 3}
    elif tipo == 'material_bruto':
        m['arquivos'] = {'extras': []}
    return m


def novo(perfil, tipo, titulo, agente, projeto=''):
    pid = resolver_perfil(perfil)
    if not pid:
        raise SystemExit(f'Perfil desconhecido: {perfil}. Use: {", ".join(perfis())}')
    if tipo not in TIPOS:
        raise SystemExit(f'Tipo desconhecido: {tipo}. Use: {", ".join(TIPOS)}')
    if agente not in AGENTES:
        raise SystemExit(f'Agente desconhecido: {agente}. Use: {", ".join(AGENTES)}')
    eid = gerar_id(pid, titulo)
    pasta = os.path.join(ENTRADA, eid)
    if os.path.exists(pasta):
        raise SystemExit(f'Já existe: {pasta}')
    os.makedirs(pasta)
    m = modelo(pid, tipo, titulo, agente, projeto)
    m['id'] = eid
    gravar_json(os.path.join(pasta, MANIFESTO), m)
    return pasta


def gerar_id(pid, titulo, quando=None):
    base = f"{(quando or hoje_iso()).replace('-', '')}-{pid}-{slug(titulo, 40)}"
    usados = set(comum.estado_atual()) | (set(os.listdir(ENTRADA)) if os.path.isdir(ENTRADA) else set())
    eid, n = base, 2
    while eid in usados:
        eid, n = f'{base}-{n}', n + 1
    return eid


# ------------------------------------------------------------------ abrir o que chega
def _seguro(nome):
    n = nome.replace('\\', '/')
    return not (n.startswith('/') or re.match(r'^[A-Za-z]:', n) or any(p == '..' for p in n.split('/')))


def abrir_zip(caminho_zip):
    """Extrai um .zip da entrada numa pasta própria, com checagem de caminho, tamanho e número de membros."""
    destino = os.path.splitext(caminho_zip)[0]
    if os.path.exists(destino):
        destino = f'{destino}-{slug(agora_iso())}'
    with zipfile.ZipFile(caminho_zip) as z:
        membros = [i for i in z.infolist() if not i.is_dir()]
        if len(membros) > LIMITE_ZIP_MEMBROS:
            raise ValueError(f'zip com {len(membros)} arquivos (máximo {LIMITE_ZIP_MEMBROS})')
        if sum(i.file_size for i in membros) > LIMITE_ZIP_BYTES:
            raise ValueError('zip descompactado passa de 4 GB')
        ruins = [i.filename for i in membros if not _seguro(i.filename)]
        if ruins:
            raise ValueError(f'caminhos inseguros no zip: {ruins[:3]}')
        os.makedirs(destino)
        for i in membros:
            alvo = os.path.join(destino, *i.filename.replace('\\', '/').split('/'))
            os.makedirs(os.path.dirname(alvo), exist_ok=True)
            with z.open(i) as src, open(alvo, 'wb') as dst:
                shutil.copyfileobj(src, dst)
    # zip com uma pasta única dentro: sobe o conteúdo um nível
    itens = os.listdir(destino)
    if len(itens) == 1 and os.path.isdir(os.path.join(destino, itens[0])) and not os.path.exists(os.path.join(destino, MANIFESTO)):
        interna = os.path.join(destino, itens[0])
        for nome in os.listdir(interna):
            shutil.move(os.path.join(interna, nome), os.path.join(destino, nome))
        os.rmdir(interna)
    os.makedirs(os.path.join(ENTRADA, '_zips_abertos'), exist_ok=True)
    shutil.move(caminho_zip, os.path.join(ENTRADA, '_zips_abertos', os.path.basename(caminho_zip)))
    return destino


def agrupar_soltos():
    """Arquivos soltos na raiz da entrada viram um rascunho de pacote que pede perfil, tipo e título."""
    soltos = [n for n in os.listdir(ENTRADA) if os.path.isfile(os.path.join(ENTRADA, n))
              and not n.startswith(('.', '_')) and n.upper() not in ('LEIA-ME.MD',) and not n.lower().endswith('.zip')]
    if not soltos:
        return None
    pasta = os.path.join(ENTRADA, f'_rascunho-{slug(agora_iso())}')
    os.makedirs(pasta)
    for n in soltos:
        shutil.move(os.path.join(ENTRADA, n), os.path.join(pasta, n))
    videos = [n for n in soltos if n.lower().endswith(EXT_VIDEO)]
    imagens = [n for n in soltos if n.lower().endswith(EXT_IMAGEM)]
    textos = [n for n in soltos if n.lower().endswith(('.txt', '.md'))]
    m = modelo('', 'video_pronto' if videos else 'orientacao', '', 'geovani')
    m['arquivos'] = {}
    if videos:
        m['arquivos']['video'] = videos[0]
    if len(videos) > 1:
        m['arquivos']['extras'] = videos[1:]
    if imagens:
        m['arquivos']['capa'] = imagens[0]
    if textos:
        partes = []
        for t in textos:
            with open(os.path.join(pasta, t), encoding='utf-8', errors='replace') as f:
                partes.append(f.read())
        m['orientacoes'] = '\n\n'.join(partes)[:8000]
    m['_rascunho'] = 'Criado pela recepção a partir de arquivos soltos. Preencha perfil, titulo e checagem, e apague esta linha.'
    gravar_json(os.path.join(pasta, MANIFESTO), m)
    return pasta


def pacotes_na_entrada():
    if not os.path.isdir(ENTRADA):
        return []
    return sorted(os.path.join(ENTRADA, n) for n in os.listdir(ENTRADA)
                  if os.path.isdir(os.path.join(ENTRADA, n)) and not n.startswith(('_modelo', '_zips', '.')))


# ------------------------------------------------------------------ validar
def _arquivo(pasta, relpath, rel, rotulo, obrigatorio=False):
    if not relpath:
        if obrigatorio:
            rel.erro(f'falta arquivos.{rotulo}')
        return None
    if not _seguro(relpath):
        rel.erro(f'arquivos.{rotulo}: caminho inseguro ({relpath})')
        return None
    p = os.path.join(pasta, *relpath.replace('\\', '/').split('/'))
    if not os.path.isfile(p):
        rel.erro(f'arquivos.{rotulo}: não encontrado ({relpath})')
        return None
    return p


def validar(pasta, sondar_midia=True):
    """Valida manifesto e arquivos. Devolve (manifesto normalizado ou None, Relatorio, midia{rotulo: info})."""
    rel, midia = Relatorio(), {}
    mp = os.path.join(pasta, MANIFESTO)
    if not os.path.isfile(mp):
        rel.erro('falta entrega.json na raiz do pacote')
        return None, rel, midia
    try:
        m = ler_json(mp)
    except ValueError as e:
        rel.erro(f'entrega.json não é JSON válido: {e}')
        return None, rel, midia
    if m.get('_rascunho'):
        rel.erro('rascunho criado pela recepção: complete perfil, titulo e checagem e apague o campo _rascunho')
    if m.get('pacote') != PACOTE_ID:
        rel.erro(f'campo pacote deve ser "{PACOTE_ID}"')
    pid = resolver_perfil(m.get('perfil'))
    if not pid:
        rel.erro(f'perfil desconhecido: {m.get("perfil")!r} (use {", ".join(perfis())})')
    perfil = perfis().get(pid, {})
    m['perfil'] = pid or m.get('perfil')
    tipo = m.get('tipo')
    if tipo not in TIPOS:
        rel.erro(f'tipo desconhecido: {tipo!r} (use {", ".join(TIPOS)})')
    titulo = (m.get('titulo') or '').strip()
    if len(titulo) < 3:
        rel.erro('titulo vazio ou curto demais')
    origem = m.get('origem') or {}
    if origem.get('agente') not in AGENTES:
        rel.erro(f'origem.agente desconhecido: {origem.get("agente")!r} (use {", ".join(AGENTES)})')
    if m.get('id') and not re.match(r'^[a-z0-9][a-z0-9-]{2,79}$', m['id']):
        rel.erro('id fora do padrão (minúsculas, números e hífen; 3 a 80 caracteres)')

    arq = m.get('arquivos') or {}
    chec = m.get('checagem') or {}
    post = m.get('post') or {}
    fontes = m.get('fontes') or []

    # checagem editorial
    if chec.get('fatos') == 'conferidos' and not fontes:
        rel.erro('checagem.fatos = conferidos, mas não há fontes: fato só com fonte aberta')
    for f in fontes:
        if not (f.get('nome') or '').strip():
            rel.erro('fonte sem nome')
    if m.get('gerado_por_ia') and post.get('rotulo_ia') is not True and tipo == 'video_pronto':
        rel.erro('vídeo gerado por IA precisa de post.rotulo_ia = true')
    if perfil.get('gerado_por_ia') and tipo == 'video_pronto' and not m.get('gerado_por_ia'):
        rel.aviso(f'o perfil {pid} é 100% IA: marque gerado_por_ia = true')
    if pid in ('drgeovani', 'melinda') and chec.get('pessoas_identificaveis') not in ('nenhuma', 'autorizadas'):
        if tipo in ('video_pronto', 'material_bruto'):
            rel.erro('checagem.pessoas_identificaveis precisa ser "nenhuma" ou "autorizadas" neste perfil (paciente/criança)')
    if pid == 'melinda' and tipo == 'video_pronto':
        rel.aviso('perfil Princesa Melinda ainda não existe no app: a entrega fica na Central até o perfil ser ativado')
    if (m.get('qa') or {}).get('status') == 'fail':
        rel.erro('o próprio produtor marcou QA = fail')

    if tipo == 'video_pronto':
        if chec.get('fatos') == 'pendente':
            rel.erro('checagem.fatos = pendente: vídeo pronto não entra com fato sem conferir (use sem_fatos se não houver)')
        if chec.get('direitos') in ('pendente', 'so_privado'):
            rel.aviso('direitos pendentes: o vídeo vai ao app rotulado "Prévia privada — não publicar"')
        if not (post.get('legenda') or '').strip():
            rel.aviso('sem post.legenda: o Geovani vai ter que escrever a legenda')
        fa = m.get('formato_app')
        if fa and fa not in comum.config_app()['formatos_app']:
            rel.erro(f'formato_app inválido: {fa}')
        for rot, obrig in (('video', True), ('video_b', False)):
            p = _arquivo(pasta, arq.get(rot), rel, rot, obrig)
            if p:
                if not p.lower().endswith(EXT_VIDEO):
                    rel.erro(f'arquivos.{rot} não parece vídeo ({os.path.basename(p)})')
                elif sondar_midia:
                    import midia as _midia
                    try:
                        midia[rot] = midia_info = _midia.sondar(p)
                        if not midia_info['video']:
                            rel.erro(f'arquivos.{rot} não tem faixa de vídeo')
                        elif midia_info['duracao_s'] < 1:
                            rel.erro(f'arquivos.{rot} tem menos de 1 s')
                    except (ValueError, OSError) as e:
                        rel.erro(str(e))
        if arq.get('video_b') and not arq.get('rotulo_b'):
            rel.aviso('há video_b sem rotulo_b: o app vai mostrar "Versão B"')
        _arquivo(pasta, arq.get('capa'), rel, 'capa')
        _arquivo(pasta, arq.get('legendas'), rel, 'legendas')
    elif tipo == 'pauta':
        pa = m.get('pauta') or {}
        if not pa:
            rel.erro('tipo pauta precisa do bloco pauta')
        d = pa.get('data') or hoje_iso()
        try:
            date.fromisoformat(d)
        except ValueError:
            rel.erro(f'pauta.data inválida: {d} (use AAAA-MM-DD)')
        rot = pa.get('roteiro') or []
        if not isinstance(rot, list) or any(not isinstance(r, dict) or not (r.get('fala') or '').strip() for r in rot):
            rel.erro('pauta.roteiro deve ser lista de {tempo, fala} com fala preenchida')
        nota = pa.get('nota', 0)
        if not isinstance(nota, (int, float)) or not 0 <= nota <= 5:
            rel.erro('pauta.nota deve ir de 0 a 5')
        if not (pa.get('abertura_a') or '').strip():
            rel.aviso('pauta sem abertura_a (o gancho que aparece no cartão)')
        if pid == 'arquivo' and not pa.get('cenas'):
            rel.aviso('pauta do Arquivo Oculto sem cenas: fica na Central e não vai ao app (a rotina precisa de cenas)')
        if chec.get('fatos') == 'pendente':
            rel.aviso('pauta com fatos pendentes: a checagem precisa acontecer antes de gravar')
    elif tipo == 'material_bruto':
        itens = [arq.get('video')] + list(arq.get('extras') or [])
        if not any(itens):
            rel.erro('material_bruto sem arquivos (arquivos.video ou arquivos.extras)')
        for i, item in enumerate(x for x in itens if x):
            _arquivo(pasta, item, rel, f'extras[{i}]')
    elif tipo == 'orientacao':
        if not (m.get('orientacoes') or '').strip():
            rel.erro('tipo orientacao precisa do texto em orientacoes')
    for i, extra in enumerate(arq.get('extras') or []):
        if tipo != 'material_bruto':
            _arquivo(pasta, extra, rel, f'extras[{i}]')
    _arquivo(pasta, arq.get('roteiro'), rel, 'roteiro')
    return m, rel, midia


# ------------------------------------------------------------------ receber
def mover_para_entregas(pasta, m):
    eid = m.get('id') or gerar_id(m['perfil'], m['titulo'])
    m['id'] = eid
    destino = comum.caminho_entrega(m['perfil'], eid)
    if os.path.exists(destino):
        raise SystemExit(f'Destino já existe: {destino}. Troque o id do pacote.')
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.move(pasta, destino)
    gravar_json(os.path.join(destino, MANIFESTO), m)
    return destino


def registrar_orientacao(m, destino):
    """Orientação vira registro datado em orientacoes/<perfil>.md (o histórico de instruções do perfil)."""
    os.makedirs(comum.ORIENTACOES, exist_ok=True)
    arq = os.path.join(comum.ORIENTACOES, f"{m['perfil']}.md")
    novo_arq = not os.path.exists(arq)
    with open(arq, 'a', encoding='utf-8', newline='\n') as f:
        if novo_arq:
            f.write(f"# Orientações recebidas — {perfis()[m['perfil']]['nome']}\n\n"
                    'Registro em ordem de chegada. A orientação mais recente vale quando houver conflito, '
                    'exceto regra do perfil em config/perfis/ (essa só muda com decisão do Geovani).\n')
        f.write(f"\n## {m['titulo']}\n\n*{agora_iso()} · de {m['origem']['agente']} · pacote `{comum.rel(destino)}`*\n\n"
                f"{m['orientacoes'].strip()}\n")
        # documentos anexados (roteiro e extras de texto): o resumo acima não substitui a leitura deles
        arqs = m.get('arquivos') or {}
        docs = [d for d in [arqs.get('roteiro')] + list(arqs.get('extras') or []) if d and d.lower().endswith(('.md', '.txt'))]
        for d in docs:
            alvo = os.path.relpath(os.path.join(destino, d), comum.ORIENTACOES).replace('\\', '/')
            f.write(f"\n**Documento completo:** [{d}]({alvo})\n")
    return arq
