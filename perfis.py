"""Perfis de marca do Estúdio de Reels. Mesmo motor, duas identidades.

Cada perfil define cores, fontes, fundo, assinatura e o estilo das legendas e dos carimbos.
Para criar um terceiro perfil, copie um dicionário e troque os valores.
"""
import os

RAIZ = os.environ.get('ESTUDIO_ROOT', os.path.dirname(os.path.abspath(__file__)))
FONTES = os.path.join(RAIZ, 'fontes')


def fonte(nome):
    return os.path.join(FONTES, nome)


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


PERFIS = {
    # ---------------------------------------------------------------- liderança política e social
    'direitaxx': {
        'nome': '@direitaxx',
        'destaque': hexrgb('#FFD400'),       # palavra-chave na legenda e no gancho
        'moldura': (236, 190, 90),           # dourado: divisão da tela, selos
        'alerta': (227, 38, 43),             # vermelho dos carimbos
        'texto': (255, 255, 255),
        'fonte_legenda': fonte('Montserrat_800ExtraBold.ttf'),
        'fonte_gancho': fonte('Montserrat_900Black.ttf'),
        'fonte_carimbo': fonte('Anton_400Regular.ttf'),
        'fonte_lower': fonte('Montserrat_900Black.ttf'),
        'fonte_lower2': fonte('Montserrat_600SemiBold.ttf'),
        'fonte_selo': fonte('Montserrat_800ExtraBold.ttf'),
        'legenda': {'n': 72, 'e': 86, 'contorno': 0.11},
        'legenda_cheia': {'n': 60, 'e': 70, 'contorno': 0.10},   # layout depoimento (sem divisão)
        'fundo': 'bandeira',                 # bandeira LED; 'real' mantém o cenário gravado
        'rim': (1.0, 0.80, 0.45),
        'lower': ('GEOVANI MIRANDA', 'Xique-Xique • Sertão da Bahia'),
        'assinatura': 'Aqui é o sertão falando.',
        'carimbo_cor': 'alerta',             # carimbos vermelhos, como na referência
        'carimbo_sob': 0.18,                 # só a base da palavra (18%) passa atrás da cabeça: lê inteira
        'retoque': {'pele': 0.40, 'dentes': 0.85},   # pele lisa de leve; aparelho e dentes mais claros
    },
    # ---------------------------------------------------------------- autoridade profissional que acolhe
    'drgeovani': {
        'nome': 'Dr. Geovani Miranda',
        'destaque': hexrgb('#E5A93C'),
        'moldura': hexrgb('#E5A93C'),
        'alerta': hexrgb('#E5A93C'),
        'texto': (255, 255, 255),
        'marinho': hexrgb('#030B1E'),
        'fonte_legenda': fonte('Montserrat_700Bold.ttf'),
        'fonte_gancho': fonte('PlayfairDisplay_900Black.ttf'),
        'fonte_carimbo': fonte('PlayfairDisplay_700Bold_Italic.ttf'),
        'fonte_lower': fonte('PlayfairDisplay_700Bold.ttf'),
        'fonte_lower2': fonte('Montserrat_500Medium.ttf'),
        'fonte_selo': fonte('Montserrat_700Bold.ttf'),
        'legenda': {'n': 62, 'e': 72, 'contorno': 0.0},
        'legenda_cheia': {'n': 54, 'e': 62, 'contorno': 0.0},
        'fundo': 'marinho',                  # azul-marinho com brilho dourado suave
        'rim': (1.0, 0.82, 0.55),
        'lower': ('Dr. Geovani Miranda', 'Fonoaudiólogo • CRFa 4-12208'),
        'assinatura': '',                    # a definir pelo Geovani
        'carimbo_cor': 'destaque',
        'carimbo_sob': 0.06,                 # frase elegante acima da cabeça, só encostando
        'retoque': {'pele': 0.40, 'dentes': 0.85},
    },
    # ---------------------------------------------------------------- Arquivo Oculto (vídeos gerados por IA)
    # Este perfil NÃO passa pelo fluxo de gravação/edição acima: os vídeos são gerados por arquivo_oculto/fabrica.py
    # (formato "ia") ou por arquivo_oculto/filtro.py (formato "filtro", o Arquivista no rosto de quem gravou).
    'arquivo-oculto': {
        'nome': 'Arquivo Oculto',
        # Perfil V2 (04/11/2026): contrato em config/profiles/arquivo_oculto_v2.json (cópia fiel do pacote) e decisões da
        # instância em arquivo_oculto_v2.lock.json. Fábrica V2: python -m arquivo_oculto.v2.fabrica_v2 <manifesto>.
        'profile_version': '2.0.0',
        'perfil_v2': 'config/profiles/arquivo_oculto_v2.json',
        'perfil_v2_lock': 'config/profiles/arquivo_oculto_v2.lock.json',
        'pipeline_v2': 'arquivo_oculto/v2/fabrica_v2.py',
        'editorial_version': '3.0.0',
        'perfil_editorial': 'config/profiles/arquivo_oculto_editorial_v3.json',
        'formatos': ('reel_30', 'investigacao_90', 'reel_profundo', 'youtube_5min', 'youtube_10min', 'microdrama'),
        'formato_padrao': 'investigacao_90',
        'character_id': 'arquivista-v2',     # aparência premium (assets/arquivista.png) + máscara rígida marfim/ouro
        'character_id_legado': 'arquivista-classico-v1',
        'voz_v2': 'arquivista-v2-c',         # aprovada para a temporada (ver lock)
        'voz': 'arquivista-voz-01',          # legado V1: kokoro-onnx pm_alex, velocidade 1.0, pitch 0.9 + eco de sala
        'destaque': hexrgb('#D6A854'),
        'moldura': hexrgb('#D6A854'),
        'alerta': hexrgb('#B22A26'),
        'texto': (241, 233, 214),
        'fonte_legenda': fonte('Montserrat_800ExtraBold.ttf'),
        'fonte_gancho': fonte('Anton_400Regular.ttf'),
        'fonte_carimbo': fonte('Anton_400Regular.ttf'),
        'fonte_lower': fonte('Montserrat_900Black.ttf'),
        'fonte_lower2': fonte('Montserrat_600SemiBold.ttf'),
        'fonte_selo': fonte('Montserrat_800ExtraBold.ttf'),
        'legenda': {'n': 62, 'e': 72, 'contorno': 0.10},
        'legenda_cheia': {'n': 62, 'e': 72, 'contorno': 0.10},
        'fundo': 'real',
        'rim': (1.0, 0.78, 0.45),
        'lower': ('O ARQUIVISTA', 'Arquivo Oculto'),
        'assinatura': '',
        'carimbo_cor': 'alerta',
        'carimbo_sob': 0.10,
        'retoque': None,
        'pipeline': 'arquivo_oculto',
    },
}
