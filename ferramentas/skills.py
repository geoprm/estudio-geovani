"""Skills da Central: uma fonte (.claude/skills), espelho para o Codex (.agents/skills) e .zip para o claude.ai.

- Claude Code lê .claude/skills/<nome>/SKILL.md sozinho.
- Codex lê .agents/skills/<nome>/SKILL.md (cópia gerada aqui; não edite a cópia).
- Claude chat (claude.ai) aceita skill enviada como .zip: dist/skills/<nome>.zip.
- ChatGPT não tem skills de arquivo: use modelos/INSTRUCOES_PARA_CHATS.md.
"""
import filecmp
import os
import re
import shutil
import zipfile

from comum import RAIZ

FONTE = os.path.join(RAIZ, '.claude', 'skills')
ESPELHO = os.path.join(RAIZ, '.agents', 'skills')
DIST = os.path.join(RAIZ, 'dist', 'skills')
NOME_OK = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')


def ler_frontmatter(caminho):
    texto = open(caminho, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---\n', texto, re.S)
    if not m:
        return None, texto
    campos = {}
    for linha in m.group(1).splitlines():
        if ':' in linha and not linha.startswith(' '):
            k, _, v = linha.partition(':')
            campos[k.strip()] = v.strip().strip('"')
    return campos, texto[m.end():]


def listar():
    if not os.path.isdir(FONTE):
        return []
    return sorted(n for n in os.listdir(FONTE) if os.path.isfile(os.path.join(FONTE, n, 'SKILL.md')))


def verificar():
    """Lista de problemas (vazia = tudo certo): frontmatter, nome, descrição, links locais e paridade do espelho."""
    problemas = []
    for nome in listar():
        sk = os.path.join(FONTE, nome, 'SKILL.md')
        fm, corpo = ler_frontmatter(sk)
        if fm is None:
            problemas.append(f'{nome}: SKILL.md sem frontmatter')
            continue
        if fm.get('name') != nome:
            problemas.append(f'{nome}: name "{fm.get("name")}" diferente da pasta')
        if not NOME_OK.match(nome) or len(nome) > 64:
            problemas.append(f'{nome}: nome fora do padrão (minúsculas e hífen, até 64)')
        desc = fm.get('description', '')
        if not 40 <= len(desc) <= 1024:
            problemas.append(f'{nome}: description com {len(desc)} caracteres (40 a 1024)')
        if len(corpo.splitlines()) > 500:
            problemas.append(f'{nome}: SKILL.md passa de 500 linhas (mova detalhe para references/)')
        for alvo in re.findall(r'\]\(((?:references|scripts|assets)/[^)#\s]+)\)', corpo):
            if not os.path.exists(os.path.join(FONTE, nome, alvo)):
                problemas.append(f'{nome}: link quebrado para {alvo}')
    problemas += paridade()
    return problemas


def paridade():
    probs = []
    fonte, espelho = set(listar()), set(os.listdir(ESPELHO)) if os.path.isdir(ESPELHO) else set()
    for n in sorted(fonte - espelho):
        probs.append(f'espelho do Codex sem {n} (rode: python ferramentas/estudio.py skills)')
    for n in sorted(espelho - fonte):
        probs.append(f'espelho do Codex tem {n}, que não existe em .claude/skills')
    for n in sorted(fonte & espelho):
        cmp = filecmp.dircmp(os.path.join(FONTE, n), os.path.join(ESPELHO, n))
        if _difere(cmp):
            probs.append(f'espelho do Codex desatualizado em {n} (rode: python ferramentas/estudio.py skills)')
    return probs


def _difere(cmp):
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return True
    _, ruins, erros = filecmp.cmpfiles(cmp.left, cmp.right, cmp.common_files, shallow=False)
    return bool(ruins or erros) or any(_difere(s) for s in cmp.subdirs.values())


def sincronizar(zips=True):
    os.makedirs(ESPELHO, exist_ok=True)
    nomes = listar()
    for n in os.listdir(ESPELHO):
        if n not in nomes:
            shutil.rmtree(os.path.join(ESPELHO, n))
    for n in nomes:
        alvo = os.path.join(ESPELHO, n)
        if os.path.exists(alvo):
            shutil.rmtree(alvo)
        shutil.copytree(os.path.join(FONTE, n), alvo)
    feitos = []
    if zips:
        os.makedirs(DIST, exist_ok=True)
        for n in nomes:
            z = os.path.join(DIST, f'{n}.zip')
            with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
                base = os.path.join(FONTE, n)
                for raiz, _, arquivos in os.walk(base):
                    for a in sorted(arquivos):
                        p = os.path.join(raiz, a)
                        zf.write(p, os.path.join(n, os.path.relpath(p, base)).replace('\\', '/'))
            feitos.append(z)
    return nomes, feitos
