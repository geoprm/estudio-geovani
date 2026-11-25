"""Ponte para reaproveitar o motor V1 do Arquivo Oculto (fontes, texto, trilha, cenário) sem modificá-lo.

O estúdio tem dois motor.py (o dos perfis @direitaxx/Dr. Geovani na raiz e o do Arquivo Oculto em arquivo_oculto/):
este módulo garante que o importado é o do Arquivo Oculto.
"""
import os
import sys

AO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys.path[0] != AO:
    sys.path.insert(0, AO)

import motor as _m  # noqa: E402

assert os.path.dirname(os.path.abspath(_m.__file__)) == AO, 'motor errado importado'

fonte = _m.fonte
quebrar = _m.quebrar
texto_centro = _m.texto_centro
trilha = _m.trilha
srt = _m.srt
blocos_legenda = _m.blocos_legenda
vinheta = _m.vinheta
graos = _m.graos
poeira = _m.poeira
Base = _m.Base
REGIOES = _m.REGIOES
OURO, OURO_CLARO, CREME, VERMELHO = _m.OURO, _m.OURO_CLARO, _m.CREME, _m.VERMELHO
SR = _m.SR
