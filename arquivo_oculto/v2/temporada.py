"""Converte pautas do app (formato V1: cenas {fala, tts, tela, selo, v}) em RASCUNHOS de manifesto V2.

Uso: python -m arquivo_oculto.v2.temporada <pasta_das_pautas> <pasta_saida> [ao-ep03 ao-ep04 ...]

O rascunho sai com status_editorial = "rascunho_pendente_checagem": a fábrica V2 recusa renderizar até que as fontes sejam
lidas, os claims classificados e o status trocado para "pronto_para_render". Nada aqui verifica fatos: só prepara o fluxo.
Mapeamento V1 -> V2: o Arquivista vira planos de atuação variados (aparição, corredor, giro de cabeça, olhar, debruçar, saída);
documentos desenhados viram dossiês ILUSTRAÇÃO; datas e linhas do tempo viram linha do tempo; nenhum asset autêntico é inventado.
"""
import json
import os
import sys

ATUACAO = ['aparicao', 'corredor', 'virar_cabeca', 'olhar_camera', 'debrucar', 'silencio']
BEATS = ['cold_open', 'inciting_question', 'dated_evidence', 'dated_evidence', 'competing_interpretations',
         'reversal_or_surprise', 'open_loop_or_next_dossier']


def _campos_personagem(tipo):
    d = {
        'aparicao': ('surge da sombra à contraluz e encara a lente', 'cabeça sobe', 'dolly-in', 'aparição'),
        'corredor': ('caminha entre fichários', 'passos com balanço', 'travelling lateral', 'apresentação'),
        'virar_cabeca': ('reage à prova girando a cabeça', 'giro de cabeça', 'órbita lenta', 'suspeita'),
        'olhar_camera': ('volta o olhar para a lente', 'giro até a câmera', 'micro push-in', 'pergunta'),
        'debrucar': ('inclina-se sobre a mesa', 'tronco avança', 'tilt para a mesa', 'nova pista'),
        'silencio': ('rosto imóvel numa batida', 'nenhum', 'push-in micro', 'suspense'),
        'encerramento': ('recua e some na sombra', 'tronco recua', 'pull-back', 'assinatura'),
    }[tipo]
    return {'action': d[0], 'gesture': d[1], 'camera_motion': d[2], 'emotional_beat': d[3], 'shot_type': 'atuação do Arquivista',
            'visual_source_type': 'personagem', 'movement': d[2], 'sound_design': 'ambiente do arquivo',
            'prompt': f'Arquivista canônico: {d[0]}', 'negative_prompt': 'boca mexendo, rosto humano, máscara diferente',
            'asset': 'A-ARQUIVISTA', 'personagem': True}


def _ilustracao(tipo, params, selo='ILUSTRAÇÃO', vst='ilustracao'):
    return {'tipo': tipo, 'params': params, 'selo': selo, 'asset': 'A-PRODUCAO-ORIGINAL', 'shot_type': tipo,
            'visual_source_type': vst, 'movement': 'câmera lenta com luz', 'sound_design': 'papel / pulso grave',
            'prompt': f'{tipo} original do Arquivo Oculto', 'negative_prompt': 'documento real falsificado, logotipos, rostos reais'}


def _ano(texto):
    """Primeiro ano de quatro dígitos (1900–2099) citado no texto; 9999 quando não há."""
    import re
    anos = [int(x) for x in re.findall(r'\b(19\d\d|20\d\d)\b', texto)]
    return min(anos) if anos else 9999


def converter(pauta):
    cenas = pauta.get('cenas', [])
    linhas = []
    n_arq = 0
    for i, c in enumerate(cenas):
        v = c.get('v', {}); t = v.get('tipo')
        ultimo = i == len(cenas) - 1
        if t == 'arq' or (t == 'pergunta' and ultimo):
            tipo = 'encerramento' if ultimo else ATUACAO[n_arq % len(ATUACAO)]
            n_arq += 1
            shot = {**_campos_personagem(tipo), 'tipo': tipo}
        elif t == 'pergunta':
            shot = {**_campos_personagem('olhar_camera'), 'tipo': 'olhar_camera'}
        elif t in ('data', 'tipo'):
            shot = _ilustracao('titulo_obra', {'linhas': [v.get('texto') or c.get('tela', '')], 'sub': v.get('sub', '')}, selo=None, vst='tipografia')
        elif t in ('timeline', 'salto'):
            pts = v.get('pontos') or [[v.get('de', ''), v.get('rot_de', '')], [v.get('ate', ''), v.get('rot_ate', '')]]
            shot = _ilustracao('salto_datas', {'de': str(pts[0][0]), 'ate': str(pts[-1][0]), 'rot_de': pts[0][1], 'rot_ate': pts[-1][1], 'gap': ''},
                               selo='A VERIFICAR', vst='dado_documental')
        elif t == 'split':
            shot = _ilustracao('leituras', {'a': list(v.get('a', ['', ''])), 'b': list(v.get('b', ['', ''])), 'sync_b': 0.45}, selo='INTERPRETAÇÃO', vst='tipografia')
        elif t == 'doc':
            shot = _ilustracao('dossie_abre', {'cabecalho': v.get('cabecalho', 'ARQUIVO'), 'linhas': v.get('linhas', []), 'rotulo': (c.get('tela') or 'DOSSIÊ')[:24], 'data': ''})
        elif t in ('telas', 'escritorio', 'dossies'):
            prm = {k: x for k, x in v.items() if k != 'tipo'}
            if t == 'escritorio' and _ano(c.get('fala', '') + ' ' + c.get('tela', '') + ' ' + str(pauta.get('fato', ''))) < 1980:
                t = 'escritorio_epoca'; prm = {'acao': 'lanterna', **prm}      # a cena V1 tem monitor e disquete: anacronismo antes de 1980
            shot = _ilustracao(t, prm, selo='RECONSTITUIÇÃO ILUSTRADA' if t.startswith('escritorio') else 'ILUSTRAÇÃO',
                               vst='reconstituicao_ilustrada' if t.startswith('escritorio') else 'ilustracao')
        elif t == 'cartas':
            shot = _ilustracao('cartas_caem', {'n': v.get('n', 7)})
        else:   # crop, grade e outros: dossiê ilustrado com o título da tela
            shot = _ilustracao('dossie_abre', {'cabecalho': 'ARQUIVO', 'linhas': [c.get('tela', '')], 'rotulo': (c.get('tela') or 'DOSSIÊ')[:24], 'data': ''})
        shot.update({'id': f'S{i + 1:02d}', 'peso': 1, 'tela': ' '.join((c.get('tela') or '').split()[:8])})
        if shot.get('selo') is None:
            shot.pop('selo', None)
        linhas.append({'id': f'L{i + 1:02d}', 'beat': BEATS[min(i, len(BEATS) - 1)] if not ultimo else 'open_loop_or_next_dossier',
                       'fala': c['fala'], **({'tts': c['tts']} if c.get('tts') else {}), 'pausa_ms': 900 if ultimo else 340,
                       'claims': [], 'shots': [shot]})
    palavras = sum(len(c['fala'].split()) for c in cenas)
    # ritmo medido no EP01 V2 (voz arquivista-v2-c): ~125 palavras/min contando pausas, + 0,4 s de entrada + 2,6 s de cartela
    dur_est = round(palavras / 125 * 60 + 3.0, 1)
    fontes = [{'id': f'S-PAUTA-{j + 1}', 'titulo': f.get('nome', ''), 'url': f.get('url', ''),
               'verificacao': 'NÃO VERIFICADA no fluxo V2: fonte herdada da pauta do app'} for j, f in enumerate(pauta.get('fontes', []))]
    return {
        'schema': 'arquivo-oculto/episodio-v2', 'episode_id': f"AO-S01-E{int(pauta.get('ordem', 0)):02d}", 'versao': 'v2.0-rascunho',
        'num': int(pauta.get('ordem', 0)), 'formato': 'reel_30' if dur_est <= 35 else 'investigacao_90',
        'duracao_estimada_s': dur_est,
        'expandir_para_formato': dur_est > 35 and dur_est < 60,
        'titulo': pauta.get('titulo', ''), 'serie': pauta.get('serie', ''), 'hook': (pauta.get('aberturaA') or pauta.get('titulo', ''))[:60].upper(),
        'status_editorial': 'rascunho_pendente_checagem',
        'pendencias': ['ler cada fonte e salvar snapshot com hash em acervo_privado/',
                       'classificar claims (documented/interpretation/allegation) e ligar às falas',
                       'trocar dossiês ilustrados por evidência autêntica quando houver direitos',
                       'expandir para investigacao_90 (85 s, 25–30 planos) se o tema sustentar',
                       'conferir cuidado editorial: ' + (pauta.get('cuidado') or '')],
        'origem': {'pauta_app': pauta.get('id') or pauta.get('codigo'), 'codigo': pauta.get('codigo'), 'palavras': palavras},
        'fontes': fontes, 'claims': [],
        'assets': [{'id': 'A-ARQUIVISTA', 'tipo': 'personagem', 'arquivo': 'arquivo_oculto/assets/arquivista.png', 'rights_status': 'owner_provided', 'credito': 'O Arquivista · Arquivo Oculto'},
                   {'id': 'A-PRODUCAO-ORIGINAL', 'tipo': 'ilustracao', 'rights_status': 'original_production', 'credito': 'Ilustração original · Arquivo Oculto'}],
        'linhas': linhas,
        'outro': {'duracao_s': 2.6, 'visual_source_type': 'tipografia', 'rights_status': 'original_production',
                  'linhas': [f"ARQUIVO OCULTO · Nº {int(pauta.get('ordem', 0)):02d}", 'ARQUIVO OCULTO', pauta.get('serie', '').upper()],
                  'aviso': 'Personagem fictício · voz sintética (IA) · ilustrações originais'},
        'listas': {}, 'legenda_post': pauta.get('legenda', ''),
    }


if __name__ == '__main__':
    ent, sai = sys.argv[1], sys.argv[2]
    ids = sys.argv[3:] or [f'ao-ep{n:02d}' for n in range(3, 11)]
    os.makedirs(sai, exist_ok=True)
    for pid in ids:
        p = json.load(open(os.path.join(ent, pid + '.json'), encoding='utf-8'))
        p.setdefault('id', pid)
        m = converter(p)
        out = os.path.join(sai, f"{m['episode_id']}.v2.rascunho.json")
        json.dump(m, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f"{m['episode_id']}  {m['formato']:16s} ~{m['duracao_estimada_s']}s expandir={m['expandir_para_formato']} {len(m['linhas'])} falas  {m['origem']['palavras']} palavras  -> {out}")
