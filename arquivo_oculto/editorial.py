"""Consulta e valida a direção editorial do Arquivo Oculto, antes da produção."""

import argparse
import json
import re
from pathlib import Path

from perfis import PERFIS
from .v2 import perfil as tecnico


ESTUDIO = Path(__file__).resolve().parent.parent
PERFIL = PERFIS['arquivo-oculto']
SCHEMA_ROTEIRO = 'arquivo-oculto/roteiro-v3'
STATUS_ROTEIRO = 'revisado_narrativamente_pendente_preproducao'
FUNCOES = {'abertura', 'pista', 'virada', 'hipotese', 'desfecho'}
CLASSES_VISUAIS = {'documental', 'ilustracao', 'reconstituicao', 'personagem', 'tipografia'}


def ler_json(caminho):
    return json.loads(caminho.read_text(encoding='utf-8'))


def carregar_perfil():
    perfil = ler_json(ESTUDIO / PERFIL['perfil_editorial'])
    if perfil['profile_id'] != 'arquivo-oculto' or perfil['editorial_version'] != PERFIL['editorial_version']:
        raise ValueError('O perfil editorial não corresponde ao registro do estúdio.')
    if (perfil['perfil_tecnico'] != PERFIL['perfil_v2'] or perfil['lock_identidade'] != PERFIL['perfil_v2_lock']
            or perfil['formato_padrao'] != PERFIL['formato_padrao']):
        raise ValueError('O perfil editorial deve herdar o contrato técnico e o lock registrados.')
    base = tecnico.carregar(ESTUDIO / perfil['perfil_tecnico'])
    lock = tecnico.carregar_lock(ESTUDIO / perfil['lock_identidade'])
    if not lock['character']['approved_look'] or not lock['voice']['approved']:
        raise ValueError('A direção pressupõe a identidade do Arquivista aprovada no lock.')
    if lock['character']['id'] != PERFIL['character_id'] or lock['voice']['voice_id'] != PERFIL['voz_v2']:
        raise ValueError('A identidade do perfil não corresponde ao lock aprovado.')
    templates = perfil['templates']
    if set(templates) != set(base['formats']):
        raise ValueError('Os templates editoriais devem cobrir todos os formatos técnicos registrados.')
    for nome, template in templates.items():
        if not template['montagem'].startswith(base['formats'][nome]['aspect_ratio']) or not template['estrutura']:
            raise ValueError(f'Template incompleto ou incompatível com o formato técnico: {nome}.')
    return perfil, base


def carregar_roteiro(pasta, episodio, base):
    caminho = pasta / f'{episodio}.v3.json'
    roteiro = ler_json(caminho)
    if roteiro['episode_id'] != episodio or roteiro['schema'] != SCHEMA_ROTEIRO:
        raise ValueError(f'{episodio}: identificação de roteiro inválida.')
    if roteiro['status_editorial'] != STATUS_ROTEIRO or not roteiro['preproducao']:
        raise ValueError(f'{episodio}: registrar pendências e manter o estado de pré-produção.')
    if roteiro['formato'] not in base['formats']:
        raise ValueError(f'{episodio}: formato desconhecido.')
    manifesto = ler_json(caminho.parent / roteiro['manifesto_base'])
    if manifesto['episode_id'] != episodio or manifesto['titulo'] != roteiro['titulo']:
        raise ValueError(f'{episodio}: título e ID precisam corresponder à base histórica.')
    fontes = {fonte['id']: fonte for fonte in manifesto['fontes']}
    for fonte in roteiro['fontes_adicionais']:
        if fonte['id'] in fontes or not fonte['url'].startswith('https://') or not fonte['localizador']:
            raise ValueError(f'{episodio}: fonte adicional inválida ou duplicada ({fonte["id"]}).')
        fontes[fonte['id']] = fonte
    claims = {claim['id']: claim for claim in manifesto['claims']}
    fim = 0
    beats = roteiro['beats']
    if not 6 <= len(beats) <= 9 or beats[0]['funcao'] != 'abertura' or beats[-1]['funcao'] != 'desfecho':
        raise ValueError(f'{episodio}: abertura, desenvolvimento e desfecho são obrigatórios.')
    if not any(beat['funcao'] == 'virada' for beat in beats):
        raise ValueError(f'{episodio}: a leitura precisa mudar durante a investigação.')
    for ordem, beat in enumerate(beats, start=1):
        rotulo = f'{episodio}/{beat["id"]}'
        if (beat['id'] != f'B{ordem:02d}' or beat['inicio_s'] != fim or beat['fim_s'] <= fim
                or beat['funcao'] not in FUNCOES or beat['classe_visual'] not in CLASSES_VISUAIS):
            raise ValueError(f'{rotulo}: beat ou intervalo inválido.')
        fim = beat['fim_s']
        if not all(beat[chave].strip() for chave in ('fala', 'visual', 'som')):
            raise ValueError(f'{rotulo}: falta locução, direção de imagem ou de som.')
        classe, selo = beat['classe_visual'], beat['selo'].upper()
        if classe == 'documental' and not beat['referencias']:
            raise ValueError(f'{rotulo}: plano documental sem referência.')
        if classe == 'ilustracao' and 'ILUSTRA' not in selo:
            raise ValueError(f'{rotulo}: ilustração sem selo.')
        if classe == 'reconstituicao' and not any(label in selo for label in ('RECONSTITUI', 'FICÇÃO')):
            raise ValueError(f'{rotulo}: dramatização sem identificação.')
        if not set(beat['claims_base']) <= claims.keys() or not set(beat['referencias']) <= fontes.keys():
            raise ValueError(f'{rotulo}: claim ou referência inexistente.')
    duracao = base['formats'][roteiro['formato']]['default_seconds']
    if fim != duracao:
        raise ValueError(f'{episodio}: a soma dos beats precisa cobrir {duracao} s planejados.')
    return roteiro, fontes


def carregar_temporada(perfil, base):
    pasta = ESTUDIO / perfil['temporada']
    esperados = [f'AO-S01-E{n:02d}' for n in range(1, 11)]
    temporada = [carregar_roteiro(pasta, episodio, base) for episodio in esperados]
    for (roteiro, _), proximo in zip(temporada, esperados[1:] + [None]):
        if roteiro['proximo_episode_id'] != proximo:
            raise ValueError(f'{roteiro["episode_id"]}: ponte de continuidade fora da sequência.')
    return temporada


def apresentar(temporada):
    linhas = ['# Arquivo Oculto · Temporada 1 · Roteiros V3', '',
              'Revisão narrativa para pré-produção. Os tempos são estimados. A minutagem dos planos parte da locução medida.',
              'Cada roteiro aguarda o fechamento dos materiais, dos direitos e do manifesto de produção.', '']
    for roteiro, fontes in temporada:
        linhas += [f'## {roteiro["episode_id"]} · {roteiro["titulo"]}', '']
        for beat in roteiro['beats']:
            linhas += [f'### {beat["inicio_s"]}–{beat["fim_s"]} s · {beat["funcao"]}', '',
                       f'> {beat["fala"]}', '', f'**Imagem** · {beat["visual"]}',
                       '', f'**Som** · {beat["som"]}']
            if beat['selo']:
                linhas += ['', f'**Selo** · {beat["selo"]}']
            referencias = [fontes[id_] for id_ in beat['referencias']]
            if referencias:
                links = ', '.join(f'[{fonte["titulo"]}]({fonte["url"]})' for fonte in referencias)
                linhas += ['', f'**Fontes da cena** · {links}']
            linhas.append('')
        linhas += ['**Pré-produção**', ''] + [f'- {item}' for item in roteiro['preproducao']] + ['']
    return '\n'.join(linhas)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    saida = parser.add_mutually_exclusive_group()
    saida.add_argument('--template', choices=PERFIL['formatos'])
    saida.add_argument('--episodio', metavar='AO-S01-E01')
    saida.add_argument('--temporada', action='store_true')
    args = parser.parse_args()
    try:
        perfil, base = carregar_perfil()
        if args.template:
            template = perfil['templates'][args.template]
            print('\n'.join([perfil['direcao']['assinatura_abertura'], '',
                             *template['estrutura'], '', template['montagem']]))
            return
        if args.episodio:
            if not re.fullmatch(r'AO-S01-E(?:0[1-9]|10)', args.episodio):
                raise ValueError('Informe um episódio entre AO-S01-E01 e AO-S01-E10.')
            print(apresentar([carregar_roteiro(ESTUDIO / perfil['temporada'], args.episodio, base)]))
            return
        temporada = carregar_temporada(perfil, base)
        if args.temporada:
            print(apresentar(temporada))
        else:
            print(f'Direção {perfil["editorial_version"]}: {len(perfil["templates"])} templates, {len(temporada)} roteiros em pré-produção.')
    except (OSError, ValueError, KeyError, TypeError) as erro:
        parser.exit(1, f'{erro}\n')


if __name__ == '__main__':
    main()
