"""EXEMPLO COMPLETO de tela dividida (@direitaxx, vídeo de Educação de 20/10/2026).
Mostra o padrão de qualidade: legenda corrigida (kit.corrigir), gancho fiel ao dado, selo de fonte e prova
no topo que muda a cada 3 a 5 s acompanhando a fala (manchete, número, contador, lista, chamada final).
Para um vídeo novo, copie o modelo_video.py; use este arquivo como referência."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import motor as M
import kit

NOME = 'teste_preparo'
PASTA = os.path.join(M.TRABALHO, NOME)
SEGS, T, TRACK = kit.carregar_mix(PASTA)
R = M.Reel(os.path.join(PASTA, 'mix.mov'), SEGS, face_src=(540, 900), zbase=1.16, perfil='direitaxx', layout='dividida')
R.track = TRACK
R.T = T
R.set_groups(kit.corrigir(kit.grupos_auto(PASTA, destaque=['METADE', 'BÁSICO', '46,8%', 'FUTURO.', '22', 'TODOS']),
                          {'TODO': 'TODOS', 'DEIS': 'DEIXE', 'MED': 'MEC'}))
R.gancho = {'linhas': ['QUASE METADE NÃO', 'APRENDEU O BÁSICO'], 'destaque': ['METADE', 'BÁSICO'], 'ate': 2.4}
R.selos = [(T(8.0), T(13.0), 'FONTE: TODOS PELA EDUCAÇÃO • MEC/SAEB')]
CARD = M.Card('Bahia Notícias', '21/08/2026',
              'Bahia tem 46,8% dos alunos do ensino médio no nível abaixo do básico em aprendizagem, indica '
              'levantamento', '46,8% dos alunos do ensino médio no nível abaixo do básico', fsize=46)
NUM = M.text_layer([('46,8%', M.F_BL, 190, M.RED2)])
ABX = M.text_layer([('ABAIXO DO BÁSICO', M.F_BL, 62, M.WHITE)])
ADQ = M.text_layer([('APRENDERAM O ADEQUADO', M.F_BL, 58, M.WHITE)])
PRAT = M.text_layer([('NA PRÁTICA, O JOVEM SAI', M.F_BL, 64, M.WHITE), ('DA ESCOLA SEM CONSEGUIR:', M.F_BL, 64, M.WHITE)])
SEM = [M.text_layer([(txt, M.F_BL, 104, cor)]) for txt, cor in
       (('SEM EDUCAÇÃO', M.WHITE), ('SEM EMPREGO', M.WHITE), ('SEM FUTURO', M.RED2))]
CTA1 = M.text_layer([('E AÍ NA SUA CIDADE?', M.F_BL, 84, M.GOLD)])
CTA2 = M.text_layer([('Comente como está a escola', M.F_BL, 60, M.WHITE), ('do seu filho ou a sua.', M.F_BL, 60, M.WHITE)])


def draw_top(f, t):
    """A prova muda a cada 3 a 5 s, sempre acompanhando o que ele fala."""
    if t < T(12.3):
        M.draw_card(f, CARD, t, 0.2, 470)
    elif t < T(17.4):
        M.pop_in(f, NUM, t, T(12.44), M.W / 2, 330)
        M.pop_in(f, ABX, t, T(15.6), M.W / 2, 560)
    elif t < T(21.0):
        M.counter(f, t, T(17.48), 0.6, 0, 22, M.W / 2, 330, 190, M.GOLD, suffix=' EM 100')
        M.pop_in(f, ADQ, t, T(19.04), M.W / 2, 560)
    elif t < T(32.3):
        M.pop_in(f, PRAT, t, T(21.06), M.W / 2, 250)
        for i, (lab, t0) in enumerate((('Interpretar um texto', 25.42), ('Fazer contas básicas', 29.06))):
            if t >= T(t0):
                im = M.check_row(lab, M.clamp01((t - T(t0)) / 0.3), 66, mark='x')
                M.blend(f, im, 120 + im.width / 2, 490 + i * 150, 1.0, 0, M.SEAM)
    elif t < T(35.7):
        for i, t0 in enumerate((32.36, 33.42, 34.5)):
            M.pop_in(f, SEM[i], t, T(t0), M.W / 2, 230 + i * 200)
    else:
        M.pop_in(f, CTA1, t, T(35.76), M.W / 2, 330)
        M.pop_in(f, CTA2, t, T(36.62), M.W / 2, 540)


if __name__ == '__main__':
    M.main(R, draw_top, NOME)
