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
}
