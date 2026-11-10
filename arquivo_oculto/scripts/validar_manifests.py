#!/usr/bin/env python3
"""Valida os manifestos de produção do Arquivo Oculto; não gera mídia."""
import json
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parents[1]
SKILLS = BASE / '.claude' / 'skills'
EXAMPLES = BASE / 'examples'
REQUIRED = ('episode_id', 'title', 'brand_id', 'character_id', 'target_duration_sec',
            'voiceover_script', 'scenes', 'claims', 'voice', 'source_urls', 'delivery')

def validate(path):
    data = json.loads(path.read_text(encoding='utf-8'))
    errors = []
    for k in REQUIRED:
        if k not in data:
            errors.append(f'Campo obrigatorio ausente: {k}')
    if errors:
        return errors
    if data['brand_id'] != 'arquivo-oculto':
        errors.append('Marca incorreta')
    if data['character_id'] != 'arquivista-classico-v1':
        errors.append('Referencia do personagem incorreta')
    if data['delivery'].get('width') != 1080 or data['delivery'].get('height') != 1920:
        errors.append('Entrega precisa ser 1080x1920')
    if data['voice'].get('language') != 'pt-BR':
        errors.append('Voz precisa ser pt-BR')
    if data['rights'].get('publication_approved') is not False:
        errors.append('Aprovacao publica nao pode ser presumida')
    scenes = data['scenes']
    if not 6 <= len(scenes) <= 14:
        errors.append('Numero de cenas fora do intervalo de teste')
    cursor = 0
    for idx, s in enumerate(scenes, 1):
        for f in ['start_sec', 'end_sec', 'visual_prompt', 'asset_class']:
            if f not in s:
                errors.append(f'Cena {idx}: sem {f}')
        if s.get('start_sec') != cursor:
            errors.append(f'Cena {idx}: inicio {s.get("start_sec")} != {cursor}')
        if s.get('end_sec', 0) <= s.get('start_sec', 0):
            errors.append(f'Cena {idx}: intervalo invalido')
        cursor = s.get('end_sec', cursor)
    if cursor != data['target_duration_sec']:
        errors.append(f'Tempo final {cursor} difere de meta {data["target_duration_sec"]}')
    for c in data['claims']:
        if c.get('status') == 'documented' and not c.get('sources'):
            errors.append(f'Claim {c.get("id")} documentado sem fonte')
    return errors


def main():
    total_errors = 0
    all_skills = list(SKILLS.glob('*/SKILL.md'))
    for p in all_skills:
        content = p.read_text(encoding='utf-8')
        if not (content.startswith('---\n') and '\nname: ' in content and '\ndescription: ' in content):
            print('FAIL skill:', p)
            total_errors += 1
    if len(all_skills) < 7:
        print('FAIL: esperado >= 7 Skills')
        total_errors += 1
    for path in EXAMPLES.glob('*.json'):
        errs = validate(path)
        print(('OK' if not errs else 'FAIL') + ': ' + path.name)
        for e in errs:
            print('  -', e)
        total_errors += len(errs)
    print(f'Skills: {len(all_skills)} | Erros: {total_errors}')
    return 0 if total_errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
