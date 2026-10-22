"""MODELO DE VÍDEO — copie este arquivo para videos/<nome>.py e preencha.
Referência de qualidade: exemplos/tela_dividida_educacao.py (prova no topo mudando a cada 3 a 5 s).

Fluxo completo de um vídeo novo (comandos a partir da pasta estudio/):
  1. python3 preparar.py gravacao.mp4 trabalho/<nome>         # transcreve, rastreia o rosto
  2. python3 ritmo.py trabalho/<nome> [frases.json]           # tira pausas, 1,06x, jump cuts
  3. preencha este arquivo (gancho, selos, prova no topo...)
  4. python3 videos/<nome>.py preview 3,60,120                # confere quadros soltos
  5. python3 videos/<nome>.py audio                           # voz tratada em -14 LUFS + efeitos
  6. python3 videos/<nome>.py render saida_A.mp4              # versão A (rosto + gancho)
     python3 videos/<nome>.py render saida_B.mp4 --B          # versão B (prova em tela cheia na abertura)
  7. python3 videos/<nome>.py capa 2.0 "PALAVRA|PALAVRA|PALAVRA" PALAVRA capa.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import motor as M
import kit
import beleza

NOME = 'meu_video'
PASTA = os.path.join(M.TRABALHO, NOME)
PERFIL = 'direitaxx'          # 'direitaxx' ou 'drgeovani'
LAYOUT = 'dividida'           # 'dividida' (prova em cima) ou 'depoimento' (tela cheia + carimbo)
FRASES = None                 # mesmos trechos passados ao ritmo.py, se houver

SEGS, T, TRACK = kit.carregar_mix(PASTA)
R = M.Reel(os.path.join(PASTA, 'mix.mov'), SEGS, face_src=(540, 900),
           zbase=1.16 if LAYOUT == 'dividida' else 1.0, perfil=PERFIL, layout=LAYOUT)
R.track = TRACK
R.T = T

# Legenda automática. Revise a transcrição (nomes, siglas, números, acentos) e corrija o que o Whisper errou.
R.set_groups(kit.corrigir(kit.grupos_auto(PASTA, destaque=['PALAVRA', 'CHAVE'], frases=FRASES),
                          {'ERRADA': 'CERTA'}))

# Gancho: até 6 palavras, sozinho na tela até 'ate' segundos (a legenda entra depois)
R.gancho = {'linhas': ['QUEM DISSE ISSO', 'FOI O LULA'], 'destaque': ['LULA'], 'ate': 2.4}

# Selo de fonte (tempos do vídeo final; use T(tempo_da_gravação) para converter)
R.selos = [(T(3.0), T(8.0), 'FONTE: PODER360 • 20/10/2026')]

# Prova em tela cheia quando você olha para o papel ou para o lado: [(ini, fim)] em tempo da gravação
R.cutaways = [(T(a), T(b)) for a, b in []]

# Palavra-carimbo atrás da cabeça (melhor no layout 'depoimento'): [(ini, fim, 'PALAVRA')]
# A palavra fica INTEIRA acima da cabeça, só a base passa por trás; se faltar espaço, o motor abre o
# enquadramento durante o carimbo. Use no máximo 3 por vídeo, de 1 a 2 palavras curtas cada.
R.carimbos = [(T(a), T(b), txt) for a, b, txt in []]

# Retoque leve do rosto (padrão do perfil: pele 0.40, dentes/aparelho 0.85). Para desligar: R.retoque = None
# Para ajustar: R.retoque = beleza.Retoque(pele=0.3, dentes=0.9)

# Efeitos sonoros extras: R.add_sfx('whoosh' | 'hit' | 'pop' | 'tick', T(tempo), db=None)


def draw_top(f, t):
    """Desenhe a prova (área de 1080 x 900 px). Na tela dividida ela fica no topo o tempo todo;
    no depoimento ela só aparece em tela cheia: na abertura da versão B e nos cutaways.
    Por isso, no depoimento, desenhe aqui a prova da abertura (manchete, número) também.
    Ferramentas prontas em motor.py:
    Card (manchete com marca-texto), counter (número animado), pop_in, slide_in, check_row,
    hbar (barra), chip, pin_row, ClipReader (vídeo de terceiros no topo, com crédito)."""
    pass


if __name__ == '__main__':
    M.main(R, draw_top, NOME)
