"""Perfil Arquivo Oculto V2: carrega, valida e expõe o contrato de config/profiles/arquivo_oculto_v2.json.

O JSON do pacote é guardado sem alteração (cópia byte a byte em docs/v2/originals/). O que é decisão desta
instância (voz escolhida, referência de aparência, modo visual) fica em arquivo_oculto_v2.lock.json, para que
o formato do pacote nunca seja trocado sem migração.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERFIL_JSON = os.path.join(RAIZ, 'config', 'profiles', 'arquivo_oculto_v2.json')
LOCK_JSON = os.path.join(RAIZ, 'config', 'profiles', 'arquivo_oculto_v2.lock.json')

FORMATOS_OBRIGATORIOS = ('reel_30', 'investigacao_90', 'reel_profundo', 'youtube_5min', 'youtube_10min', 'microdrama')
ETAPAS = ('planned', 'sources_verified', 'generating_visuals', 'generating_voice', 'assembling', 'qa', 'completed', 'blocked')
CAMPOS_CENA = ('shot_type', 'visual_source_type', 'duration', 'asset_path', 'prompt', 'negative_prompt', 'movement',
               'sound_design', 'voice_span', 'source_id', 'rights_status')
CAMPOS_ATUACAO = ('action', 'gesture', 'camera_motion', 'emotional_beat', 'reference_image', 'duration', 'sync_to_voice')
RIGHTS = ('verified_license', 'public_domain', 'owner_provided', 'original_production', 'fact_citation',
          'quotation_excerpt', 'private_research', 'unknown', 'restricted')
# Mesma regra do gate do site (docs/ACERVO_E_DIREITOS.md), com dois estados próprios do vídeo:
#  original_production: imagem/som criados por esta fábrica (código, personagem do proprietário, trilha sintetizada);
#  fact_citation: dado factual (nome de carta, data, número) recomposto em tipografia própria, com fonte.
#  quotation_excerpt: citação curta de obra protegida (LDA art. 46, III) — só pública após revisão humana.
PUBLICO_OK = {'verified_license', 'public_domain', 'owner_provided', 'original_production', 'fact_citation'}
PRIVADO_OK = PUBLICO_OK | {'quotation_excerpt', 'private_research'}


def carregar(caminho=PERFIL_JSON):
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def carregar_lock(caminho=LOCK_JSON):
    if not os.path.exists(caminho):
        return {}
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def validar(p):
    """Validação de esquema sem dependências. Devolve lista de erros (vazia = válido)."""
    e = []

    def req(obj, chave, tipo, onde):
        if chave not in obj:
            e.append(f'{onde}.{chave} ausente'); return None
        if tipo and not isinstance(obj[chave], tipo):
            e.append(f'{onde}.{chave} deveria ser {tipo.__name__ if isinstance(tipo, type) else tipo}'); return None
        return obj[chave]

    if req(p, 'profile_id', str, 'perfil') != 'arquivo-oculto':
        e.append('perfil.profile_id deve ser "arquivo-oculto"')
    v = req(p, 'profile_version', str, 'perfil')
    if v and not v.startswith('2.'):
        e.append('perfil.profile_version deve ser 2.x')
    iso = req(p, 'isolation', dict, 'perfil') or {}
    outros = iso.get('do_not_modify_other_brands', [])
    for marca in ('direitaxx', 'dr-geovanimiranda'):
        if marca not in outros:
            e.append(f'isolation.do_not_modify_other_brands deve conter {marca}')
    ch = req(p, 'character', dict, 'perfil') or {}
    for k, t in (('id', str), ('identity_lock', bool), ('mask_flexible_or_lipsync', bool), ('performance_shots', list),
                 ('character_screen_time_range_pct', list), ('minimum_distinct_character_shots_per_60s', int),
                 ('static_character_shot_max_sec', (int, float))):
        req(ch, k, t, 'character')
    if ch.get('mask_flexible_or_lipsync') is not False:
        e.append('character.mask_flexible_or_lipsync deve ser false (máscara rígida, sem boca falando)')
    vo = req(p, 'voice', dict, 'perfil') or {}
    for k in ('profile_id', 'language', 'rate_wpm', 'pause_after_reveal_ms', 'voice_ducking_db'):
        req(vo, k, None, 'voice')
    if vo.get('language') != 'pt-BR':
        e.append('voice.language deve ser pt-BR')
    fm = req(p, 'formats', dict, 'perfil') or {}
    for k in FORMATOS_OBRIGATORIOS:
        f = fm.get(k)
        if not isinstance(f, dict):
            e.append(f'formats.{k} ausente'); continue
        d = f.get('duration_seconds')
        if not (isinstance(d, list) and len(d) == 2 and d[0] < d[1]):
            e.append(f'formats.{k}.duration_seconds inválido')
        elif not d[0] <= f.get('default_seconds', -1) <= d[1]:
            e.append(f'formats.{k}.default_seconds fora da faixa')
        if f.get('aspect_ratio') not in ('9:16', '16:9'):
            e.append(f'formats.{k}.aspect_ratio inválido')
        res = f.get('resolution', '')
        if f.get('aspect_ratio') == '9:16' and res != '1080x1920' or f.get('aspect_ratio') == '16:9' and res != '1920x1080':
            e.append(f'formats.{k}.resolution não bate com o aspecto')
    pl = req(p, 'pipeline', dict, 'perfil') or {}
    for k in ('publication_requires_approval', 'paid_services_require_approval', 'no_payment_or_autopost'):
        if pl.get(k) is not True:
            e.append(f'pipeline.{k} deve ser true')
    co = req(p, 'compliance', dict, 'perfil') or {}
    lab = co.get('depiction_labels', {})
    if lab.get('reenactment') != 'RECONSTITUIÇÃO COM IA':
        e.append('compliance.depiction_labels.reenactment deve ser "RECONSTITUIÇÃO COM IA"')
    return e


def formato(p, chave):
    if chave not in p['formats']:
        raise KeyError(f'formato desconhecido: {chave}. Use um de {sorted(p["formats"])}')
    f = dict(p['formats'][chave])
    f['chave'] = chave
    f['largura'], f['altura'] = (int(x) for x in f['resolution'].split('x'))
    return f


def metas_personagem(p, duracao_s):
    """Metas de atuação derivadas do perfil para uma duração real."""
    ch = p['character']
    lo, hi = ch['character_screen_time_range_pct']
    return {
        'min_planos_distintos': max(3, int(-(-ch['minimum_distinct_character_shots_per_60s'] * duracao_s // 60))),
        'max_plano_estatico_s': float(ch['static_character_shot_max_sec']),
        'tempo_tela_pct': (lo, hi),
        'boca_da_mascara_anima': bool(ch['mask_flexible_or_lipsync']),
    }


def gate_direitos(rights_status, modo):
    """True se o asset pode entrar no render deste modo ('private_preview' ou 'public_release')."""
    if rights_status not in RIGHTS:
        return False
    return rights_status in (PUBLICO_OK if modo == 'public_release' else PRIVADO_OK)


if __name__ == '__main__':
    perfil = carregar()
    erros = validar(perfil)
    print('perfil', perfil['profile_id'], perfil['profile_version'], '| erros:', len(erros))
    for x in erros:
        print(' -', x)
    raise SystemExit(1 if erros else 0)
