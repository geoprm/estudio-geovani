"""Autoria dos manifestos V2 da temporada 1 (EP03–EP06) — 05/11/2026.

Gera os JSON em arquivo_oculto/producao/v2/. Todos os fatos foram lidos nas fontes listadas em cada episódio nesta sessão
(snapshots com hash em acervo_privado/ e acervo_dominio_publico/). Uso: python arquivo_oculto/producao/v2/_autoria_temporada.py
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PD = 'arquivo_oculto/acervo_dominio_publico/'
PRIV = 'arquivo_oculto/acervo_privado/'

ATUACAO = {
    'aparicao': ('surge da sombra à contraluz e encara a lente', 'cabeça sobe até a câmera', 'dolly-in discreto', 'aparição'),
    'corredor': ('caminha entre fichários e para', 'passos com balanço; vira para a lente', 'travelling lateral', 'apresentação'),
    'virar_cabeca': ('reage ao documento girando a cabeça', 'giro de cabeça e olhar baixo', 'órbita lenta', 'suspeita'),
    'olhar_camera': ('volta o olhar do documento para a lente', 'giro até a câmera', 'micro push-in', 'pergunta'),
    'debrucar': ('inclina-se sobre a mesa; a luz revela a prova', 'tronco avança, cabeça baixa', 'tilt para a mesa', 'nova pista'),
    'silencio': ('rosto imóvel numa batida dramática', 'nenhum, só respiração', 'push-in micro', 'suspense'),
    'encerramento': ('recua e some na sombra', 'tronco recua', 'pull-back', 'assinatura'),
    'ombro': ('examina a prova por cima do ombro', 'cabeça inclinada sobre o papel', 'over-the-shoulder com foco seletivo', 'investigação'),
}


def pers(sid, tipo, peso=1.0, tela='', params=None, prova=None, asset='A-ARQUIVISTA', selo=None, vst='personagem'):
    a = ATUACAO[tipo]
    s = {'id': sid, 'tipo': tipo, 'peso': peso, 'tela': tela, 'asset': asset, 'personagem': True,
         'action': a[0], 'gesture': a[1], 'camera_motion': a[2], 'emotional_beat': a[3],
         'shot_type': 'atuação do Arquivista' if tipo != 'ombro' else 'over-the-shoulder', 'visual_source_type': vst,
         'movement': a[2], 'sound_design': 'ambiente do arquivo, tecido, respiração',
         'prompt': f'Arquivista canônico: {a[0]}', 'negative_prompt': 'boca mexendo, rosto humano, máscara diferente, mãos deformadas'}
    if params: s['params'] = params
    if prova: s['prova'] = prova; s['parcial'] = True; s['credito'] = True
    if selo: s['selo'] = selo
    return s


def ev(sid, tipo, peso, asset, vst, selo=None, params=None, tela='', credito=True, mov='câmera lenta com luz', som='papel',
       prompt='', neg='documento falsificado, logotipos, rostos inventados'):
    s = {'id': sid, 'tipo': tipo, 'peso': peso, 'tela': tela, 'asset': asset, 'shot_type': tipo, 'visual_source_type': vst,
         'movement': mov, 'sound_design': som, 'prompt': prompt or tipo, 'negative_prompt': neg, 'params': params or {}}
    if selo: s['selo'] = selo
    if credito: s['credito'] = True
    return s


def linha(lid, beat, fala, shots, pausa=340, claims=(), tts=None):
    d = {'id': lid, 'beat': beat, 'fala': fala, 'pausa_ms': pausa, 'claims': list(claims), 'shots': shots}
    if tts: d['tts'] = tts
    return d


BASE_ASSETS = [
    {'id': 'A-ARQUIVISTA', 'tipo': 'personagem', 'arquivo': 'arquivo_oculto/assets/arquivista.png', 'rights_status': 'owner_provided', 'credito': 'O Arquivista · Arquivo Oculto'},
    {'id': 'A-PRODUCAO-ORIGINAL', 'tipo': 'ilustracao', 'rights_status': 'original_production', 'credito': 'Ilustração original · Arquivo Oculto'},
]


def outro(num, prox):
    return {'duracao_s': 2.6, 'visual_source_type': 'tipografia', 'rights_status': 'original_production',
            'linhas': [f'ARQUIVO OCULTO · Nº {num:02d}', 'PRÓXIMO ARQUIVO:', prox],
            'aviso': 'Personagem fictício · voz sintética (IA) · ilustrações originais'}


ESTRUTURA = ['cold_open', 'inciting_question', 'dated_evidence', 'competing_interpretations', 'reversal_or_surprise', 'open_loop_or_next_dossier']


# =================================================================================================== EP06 — Northwoods
def ep06():
    NW = PD + 'northwoods_1962-03-13.pdf'
    fontes = [
        {'id': 'S-NW-MEMO', 'titulo': 'Joint Chiefs of Staff — Justification for US Military Intervention in Cuba (13/03/1962), 15 pp.',
         'editor': 'Estado-Maior Conjunto dos EUA (cópia publicada pelo National Security Archive)', 'url': 'https://nsarchive2.gwu.edu/news/20010430/northwoods.pdf',
         'snapshot': NW, 'acessado_em': '2026-11-05', 'data_documento': '1962-03-13',
         'verificacao': 'lido nesta sessão (scan): capa p.0 (13 March 1962; Memorandum for the Secretary of Defense; assinatura L. L. Lemnitzer, Chairman, Joint Chiefs of Staff; carimbo "Systematically reviewed by JCS on 21 May 84 — classification continued"); p.9 anexo "Pretexts to justify US military intervention in Cuba" com nota "preliminary submission suitable only for planning purposes"; p.10 item 3a "We could blow up a US ship in Guantanamo Bay and blame Cuba."',
         'direitos': 'documento do governo federal dos EUA: domínio público'},
        {'id': 'S-NSA-2001', 'titulo': 'Pentagon Proposed Pretexts for Cuba Invasion in 1962 (30/04/2001)', 'editor': 'National Security Archive (George Washington University)',
         'url': 'https://nsarchive2.gwu.edu/news/20010430/', 'snapshot': PD + 'nsarchive_northwoods_2001-04-30.html', 'acessado_em': '2026-11-05',
         'verificacao': 'lido: entregue a McNamara em 13/03/1962; codinome Operation Northwoods; pedido do chefe do Cuba Project (Lansdale); inclui falsa campanha de terror na região de Miami e simular ataque da força aérea cubana a avião civil'},
        {'id': 'S-NEWSREEL-1962', 'titulo': 'Universal Newsreel — The Red Threat. President Orders Cuban Blockade (22/10/1962)', 'editor': 'Universal-International News (NARA / Internet Archive)',
         'url': 'https://archive.org/details/1962-10-22_The_Red_Threat', 'snapshot': PD + 'newsreel_1962-10-22_The_Red_Threat.mp4', 'acessado_em': '2026-11-05',
         'verificacao': 'cartela e discurso de Kennedy sobre a "quarantine" de equipamento militar ofensivo para Cuba', 'direitos': 'marcado como domínio público no Internet Archive'},
    ]
    claims = [
        {'id': 'C1', 'texto': 'Em 13/03/1962 o Estado-Maior Conjunto enviou ao secretário de Defesa o memorando "Justification for US Military Intervention in Cuba"', 'status': 'documented', 'fontes': ['S-NW-MEMO', 'S-NSA-2001']},
        {'id': 'C2', 'texto': 'O memorando é assinado por L. L. Lemnitzer, presidente do Estado-Maior Conjunto', 'status': 'documented', 'fontes': ['S-NW-MEMO']},
        {'id': 'C3', 'texto': 'O conjunto de propostas ficou conhecido como Operation Northwoods', 'status': 'documented', 'fontes': ['S-NSA-2001']},
        {'id': 'C4', 'texto': 'O anexo se apresenta como submissão preliminar, só para planejamento', 'status': 'documented', 'fontes': ['S-NW-MEMO']},
        {'id': 'C5', 'texto': 'Um item propõe explodir um navio americano na baía de Guantánamo e culpar Cuba', 'status': 'documented', 'fontes': ['S-NW-MEMO', 'S-NSA-2001']},
        {'id': 'C6', 'texto': 'Outras propostas: falsa campanha de terror na região de Miami e simular ataque cubano a avião civil', 'status': 'documented', 'fontes': ['S-NSA-2001']},
        {'id': 'C7', 'texto': 'Em 22/10/1962 Kennedy anunciou a quarentena/bloqueio a Cuba', 'status': 'documented', 'fontes': ['S-NEWSREEL-1962']},
        {'id': 'C8', 'texto': 'O memorando prova a proposta por escrito; não prova a execução', 'status': 'interpretation', 'fontes': []},
        {'id': 'C9', 'texto': 'Em 21/05/1984 o Estado-Maior revisou o documento e manteve a classificação', 'status': 'documented', 'fontes': ['S-NW-MEMO']},
        {'id': 'C10', 'texto': 'Em 30/04/2001 o National Security Archive publicou o memorando completo', 'status': 'documented', 'fontes': ['S-NSA-2001']},
    ]
    assets = BASE_ASSETS + [
        {'id': 'A-NW-MEMO', 'tipo': 'documento_autentico', 'arquivo': NW, 'fonte': 'S-NW-MEMO', 'rights_status': 'public_domain',
         'autenticidade': 'scan do documento original (domínio público)', 'credito': 'Memorando do Estado-Maior Conjunto, 13/03/1962 · cópia do National Security Archive · domínio público'},
        {'id': 'A-NEWSREEL-1962', 'tipo': 'video_arquivo', 'arquivo': PD + 'newsreel_1962-10-22_The_Red_Threat.mp4', 'fonte': 'S-NEWSREEL-1962', 'rights_status': 'public_domain',
         'autenticidade': 'cinejornal original de 22/10/1962', 'credito': 'Universal Newsreel, 22/10/1962 · Internet Archive · domínio público'},
        {'id': 'A-DATAS', 'tipo': 'dado_documental', 'fonte': 'S-NSA-2001', 'rights_status': 'fact_citation', 'credito': 'Fontes: memorando JCS (1962) · National Security Archive (2001)'},
    ]
    pg = lambda sid, peso, pagina, foco, circ=True, inv=False, selo='DOCUMENTO ORIGINAL', mov='da página ao trecho; lápis marca': ev(
        sid, 'pagina_documento', peso, 'A-NW-MEMO', 'documento_autentico', selo, {'pagina': pagina, 'foco': foco, 'circular': circ, 'inverter': inv},
        mov=mov, som='papel, lápis', prompt=f'página {pagina} do memorando original', neg='documento recriado, texto inventado')
    L = [
        linha('L01', 'cold_open', 'Março de 1962. Um memorando ultrassecreto chega ao secretário de Defesa americano.',
              [pg('S01', 1.0, 0, [0.08, 0.0, 0.52, 0.06], circ=False, inv=True, mov='do carimbo TOP SECRET à página inteira'),
               ev('S02', 'escritorio_epoca', 1.0, 'A-PRODUCAO-ORIGINAL', 'reconstituicao_ilustrada', 'RECONSTITUIÇÃO ILUSTRADA', {'acao': 'luminaria', 'semente': 9},
                  tela='MARÇO DE 1962', credito=False, mov='a luminária acende; câmera se aproxima das pastas', som='clique do interruptor, papel',
                  prompt='gabinete de repartição de 1962: mesa, máquina de escrever, pastas', neg='documento falsificado, logotipos, rostos inventados, monitor, computador')], 340, ['C1'],
              tts='Março de mil novecentos e sessenta e dois. Um memorando ultrassecreto chega ao secretário de Defesa americano.'),
        linha('L02', 'cold_open', 'O assunto: justificar uma intervenção militar em Cuba.', [pg('S03', 1.0, 0, [0.14, 0.195, 0.90, 0.28])], 420, ['C1']),
        linha('L03', 'inciting_question', 'Eu sou o Arquivista. E isto não é boato: é papel com assinatura.',
              [pers('S04', 'aparicao', 1.0, 'PAPEL COM ASSINATURA'), pers('S05', 'corredor', 1.0, params={'direcao': 1})], 360),
        linha('L04', 'dated_evidence', 'Quem assina é o general L. L. Lemnitzer, presidente do Estado-Maior Conjunto.',
              [pg('S06', 1.1, 0, [0.42, 0.655, 0.90, 0.77]), pers('S06b', 'virar_cabeca', 0.9, params={'lado': -1})], 300, ['C2'],
              tts='Quem assina é o general Lemnítzer, presidente do Estado-Maior Conjunto.'),
        linha('L05', 'dated_evidence', 'Os planos ficaram conhecidos como Operação Northwoods.',
              [ev('S07', 'titulo_obra', 1.0, 'A-DATAS', 'dado_documental', 'DOCUMENTADO', {'linhas': ['OPERAÇÃO', 'NORTHWOODS'], 'sub': 'ESTADO-MAIOR CONJUNTO · EUA · 1962'},
                  mov='luz revela o nome', som='varredura metálica', prompt='nome da operação em tipografia própria')], 300, ['C3'],
              tts='Os planos ficaram conhecidos como Operação Nórthuuds.'),
        linha('L06', 'dated_evidence', 'No anexo: pretextos para justificar a intervenção. Uma proposta preliminar, só para planejamento, avisa o texto.',
              [pers('S08', 'ombro', 1.0, prova={'tipo': 'pagina_documento', 'params': {'pagina': 9, 'foco': [0.14, 0.035, 0.86, 0.10], 'circular': False}},
                    params={'lado': 1}, asset='A-NW-MEMO', selo='DOCUMENTO ORIGINAL', vst='documento_autentico'),
               pg('S08b', 1.0, 9, [0.12, 0.105, 0.86, 0.165])], 340, ['C4']),
        linha('L07', 'dated_evidence', 'E um dos itens diz, com todas as letras: poderíamos explodir um navio americano na baía de Guantánamo e culpar Cuba.',
              [pg('S09', 1.4, 10, [0.04, 0.41, 0.82, 0.50]), pers('S10', 'silencio', 0.6)], 650, ['C5'],
              tts='E um dos itens diz, com todas as letras: poderíamos explodir um navio americano na baía de Guantânamo... e culpar Cuba.'),
        linha('L08', 'dated_evidence', 'Outros falam em falso terror na região de Miami e em simular um ataque cubano a um avião civil.',
              [pg('S11', 1.0, 11, [0.05, 0.30, 0.95, 0.62], circ=False, mov='página do anexo; câmera desce'),
               ev('S12', 'dossies', 0.9, 'A-PRODUCAO-ORIGINAL', 'ilustracao', 'ILUSTRAÇÃO', {'rotulos': ['PRETEXTO', 'PRETEXTO', 'PRETEXTO'], 'dur': 2.6},
                  credito=False, som='pastas caindo', prompt='pastas genéricas carimbadas PRETEXTO')], 400, ['C6'],
              tts='Outros falam em falso terror na região de Maiâmi e em simular um ataque cubano a um avião civil.'),
        linha('L09', 'competing_interpretations', 'Sete meses depois, Kennedy anunciava o bloqueio a Cuba. Era a crise dos mísseis.',
              [ev('S13', 'video_arquivo', 0.8, 'A-NEWSREEL-1962', 'video_arquivo', 'CINEJORNAL DE 1962', {'inicio': 0.4}, mov='cartela do cinejornal', som='chiado de película'),
               ev('S14', 'video_arquivo', 1.2, 'A-NEWSREEL-1962', 'video_arquivo', 'CINEJORNAL DE 1962', {'inicio': 55.0}, mov='discurso de Kennedy', som='chiado de película')],
              420, ['C7'], tts='Sete meses depois, Quénedi anunciava o bloqueio a Cuba. Era a crise dos mísseis.'),
        linha('L10', 'reversal_or_surprise', 'Mas aqui está a linha que separa arquivo de teoria.', [pers('S15', 'debrucar', 1.0)], 600),
        linha('L11', 'reversal_or_surprise', 'O papel prova que os pretextos foram propostos. Não prova que foram executados.',
              [ev('S16', 'leituras', 1.0, 'A-PRODUCAO-ORIGINAL', 'tipografia', 'ANÁLISE', {'a': ['PROPOSTO', 'prova: o memorando'], 'b': ['EXECUTADO?', 'sem prova neste arquivo'], 'sync_b': 0.48, 'brilho_fundo': 0.5},
                  credito=False, mov='cada lado acende', som='dois pulsos graves', prompt='proposto x executado')], 520, ['C8']),
        linha('L12', 'reversal_or_surprise', 'E um carimbo conta mais: em 1984, o Estado-Maior revisou o papel e manteve o sigilo.',
              [pg('S17', 1.1, 0, [0.07, 0.635, 0.48, 0.725]), pg('S17b', 0.9, 0, [0.06, 0.93, 0.94, 0.995], circ=False, mov='a faixa TOP SECRET riscada')], 400, ['C9'],
              tts='E um carimbo conta mais: em mil novecentos e oitenta e quatro, o Estado-Maior revisou o papel e manteve o sigilo.'),
        linha('L13', 'open_loop_or_next_dossier', 'Em 2001, o Arquivo de Segurança Nacional, em Washington, publicou o memorando inteiro.',
              [ev('S18', 'salto_datas', 1.0, 'A-DATAS', 'dado_documental', 'DOCUMENTADO', {'de': '13·03·1962', 'ate': '30·04·2001', 'rot_de': 'MEMORANDO', 'rot_ate': 'PUBLICADO NA ÍNTEGRA', 'gap': '39 ANOS'},
                  mov='linha do tempo corre', som='relógio')], 400, ['C10'],
              tts='Em dois mil e um, o Arquivo de Segurança Nacional, em Uóchinton, publicou o memorando inteiro.'),
        linha('L14', 'open_loop_or_next_dossier', 'Conspiração real deixa papel. E papel pode ser conferido.',
              [pg('S19a', 1.0, 10, [0.04, 0.41, 0.82, 0.50], circ=False, mov='volta ao item do navio, sem lápis'),
               pers('S19', 'olhar_camera', 1.0, 'PAPEL PODE SER CONFERIDO', params={'de_yaw': 12})], 500, ['C8']),
        linha('L15', 'open_loop_or_next_dossier', 'No próximo arquivo: capas de revista que muita gente jura serem profecias.',
              [ev('S20', 'telas', 0.9, 'A-PRODUCAO-ORIGINAL', 'ilustracao', 'ILUSTRAÇÃO', {'anos': [1988, 2026]}, credito=False, som='chiado', prompt='monitores abstratos'),
               pers('S21', 'encerramento', 1.1)], 900),
    ]
    return {'schema': 'arquivo-oculto/episodio-v2', 'episode_id': 'AO-S01-E06', 'versao': 'v2.0', 'num': 6, 'formato': 'investigacao_90',
            'titulo': 'Operação Northwoods: o plano que ficou no papel', 'serie': 'Conspirações Documentadas', 'hook': 'UM PLANO PARA CULPAR CUBA',
            'status_editorial': 'pronto_para_render', 'estrutura': ESTRUTURA,
            'nota_editorial': 'Fatos lidos no próprio memorando (scan) e na página do National Security Archive. Não se afirma rejeição nem data de liberação oficial (sem fonte nesta sessão). Virada: o papel prova a proposta, não a execução.',
            'fontes': fontes, 'claims': claims, 'assets': assets, 'linhas': L, 'outro': outro(6, 'CAPAS QUE PARECEM PROFECIAS'), 'listas': {},
            'legenda_post': 'Em 13/03/1962, o Estado-Maior Conjunto dos EUA mandou ao secretário de Defesa uma lista de pretextos para justificar uma invasão de Cuba — entre eles, explodir um navio americano em Guantánamo e culpar Cuba. O documento prova a proposta. Não prova a execução.\n\nFontes: memorando JCS de 13/03/1962 (cópia do National Security Archive) · Universal Newsreel, 22/10/1962 (domínio público).\nPersonagem fictício, voz sintética.\n\n#ArquivoOculto #Northwoods #GuerraFria #historia #documentos'}


# =================================================================================================== EP04 — COINTELPRO
def ep04():
    CH = PD + 'church_committee_book_III_1976.pdf'
    CARTA = PD + 'nara_cointelpro_1967-08-25_p2.jpg'
    fontes = [
        {'id': 'S-FBI-HIST', 'titulo': 'FBI — And Justice for All, 1954–1971', 'editor': 'FBI (fbi.gov)', 'url': 'https://www.fbi.gov/history/history-of-the-fbi/and-justice-for-all',
         'snapshot': PD + 'fbi_history_and_justice_for_all.html', 'acessado_em': '2026-11-05',
         'verificacao': 'lido: Cointelpro aprovado pelo National Security Council em 1956; o público soube após o arrombamento de um escritório do FBI em Media, Pensilvânia, em 1971, com vazamento à imprensa e ao Congresso; infiltração, discórdia e descrédito mesmo com pouca ou nenhuma evidência de atividade ilegal; Hoover encerrou formalmente em abril de 1971',
         'direitos': 'texto do governo federal dos EUA: domínio público'},
        {'id': 'S-CHURCH-1976', 'titulo': 'Senate Select Committee (Church Committee) — Final Report, Book III (1976), "COINTELPRO: The FBI\'s Covert Action Programs Against American Citizens"',
         'editor': 'Senado dos EUA (cópia do Internet Archive: finalreportofsel03unit)', 'url': 'https://archive.org/details/finalreportofsel03unit', 'snapshot': CH, 'acessado_em': '2026-11-05',
         'verificacao': 'lido p.12 do PDF: COINTELPRO = programas de ação encoberta contra grupos domésticos; ação secreta para "disrupt" e "neutralize"; técnicas do trivial ao degradante (cartas anônimas para destruir casamentos) e ao perigoso; base de mais de 20.000 páginas de documentos do FBI',
         'direitos': 'documento do Congresso dos EUA: domínio público'},
        {'id': 'S-NARA-2020', 'titulo': 'National Archives — When the FBI Used a Stamp Collecting Club as a Counterintelligence Tool (26/03/2020)', 'editor': 'National Archives (The Text Message)',
         'url': 'https://text-message.blogs.archives.gov/2020/03/26/when-the-fbi-used-a-stamp-collecting-club-as-a-counterintelligence-tool/', 'snapshot': PD + 'nara_stamp_club_cointelpro.html', 'acessado_em': '2026-11-05',
         'verificacao': 'lido: memorando de Hoover de 28/08/1956 inicia o COINTELPRO; em 1970 o FBI usou/planejou um clube de colecionadores de selos como fachada; reproduz a carta de 25/08/1967 (ARC ID 5060504) e o retrato de Hoover (NAID 518187)'},
        {'id': 'S-NEWSREEL-1957', 'titulo': 'Universal Newsreel — Red Colonel. Top-Ranking Russian Spy Chief Captured (12/08/1957)', 'editor': 'Universal-International News (Internet Archive)',
         'url': 'https://archive.org/details/1957-08-12_Red_Colonel', 'snapshot': PD + 'newsreel_1957-08-12_Red_Colonel.mp4', 'acessado_em': '2026-11-05', 'direitos': 'marcado como domínio público no Internet Archive'},
    ]
    claims = [
        {'id': 'C1', 'texto': 'Em 1971 um escritório do FBI em Media, Pensilvânia, foi arrombado e informações vazaram para a imprensa e o Congresso', 'status': 'documented', 'fontes': ['S-FBI-HIST']},
        {'id': 'C2', 'texto': 'O FBI reconhece que táticas do Cointelpro foram longe demais', 'status': 'documented', 'fontes': ['S-FBI-HIST']},
        {'id': 'C3', 'texto': 'Cointelpro foi aprovado em 1956', 'status': 'documented', 'fontes': ['S-FBI-HIST', 'S-NARA-2020']},
        {'id': 'C4', 'texto': 'Em 1957 cinejornais mostraram a prisão de um espião soviético nos EUA', 'status': 'documented', 'fontes': ['S-NEWSREEL-1957']},
        {'id': 'C5', 'texto': 'COINTELPRO foram programas de ação encoberta contra grupos domésticos', 'status': 'documented', 'fontes': ['S-CHURCH-1976']},
        {'id': 'C6', 'texto': 'Carta do Diretor do FBI de 25/08/1967 abre o programa contra grupos nacionalistas negros com o objetivo de "expose, disrupt, misdirect, discredit, or otherwise neutralize"', 'status': 'documented', 'fontes': ['S-NARA-2020']},
        {'id': 'C7', 'texto': 'O relatório de 1976 se baseou em mais de 20 mil páginas do FBI e descreve técnicas do trivial ao degradante e ao perigoso', 'status': 'documented', 'fontes': ['S-CHURCH-1976']},
        {'id': 'C8', 'texto': 'Em 1970 o FBI usou um clube de colecionadores de selos como fachada de contrainteligência', 'status': 'documented', 'fontes': ['S-NARA-2020']},
        {'id': 'C9', 'texto': 'Hoover encerrou formalmente o Cointelpro em abril de 1971', 'status': 'documented', 'fontes': ['S-FBI-HIST']},
        {'id': 'C10', 'texto': 'Uma conspiração comprovada não prova outras; o fim formal não prova ausência de abusos posteriores', 'status': 'interpretation', 'fontes': []},
    ]
    assets = BASE_ASSETS + [
        {'id': 'A-FBI-HIST', 'tipo': 'documento_autentico', 'fonte': 'S-FBI-HIST', 'rights_status': 'public_domain', 'credito': 'FBI · And Justice for All, 1954–1971 (fbi.gov) · domínio público'},
        {'id': 'A-CHURCH', 'tipo': 'documento_autentico', 'arquivo': CH, 'fonte': 'S-CHURCH-1976', 'rights_status': 'public_domain', 'credito': 'Senado dos EUA · Church Committee, Livro III, 1976 · domínio público'},
        {'id': 'A-CARTA-1967', 'tipo': 'documento_autentico', 'arquivo': CARTA, 'fonte': 'S-NARA-2020', 'rights_status': 'public_domain', 'credito': 'Carta do Diretor do FBI, 25/08/1967 · Arquivo Nacional dos EUA · domínio público'},
        {'id': 'A-HOOVER', 'tipo': 'foto_arquivo', 'arquivo': PD + 'nara_stamp_club_doc.gif', 'fonte': 'S-NARA-2020', 'rights_status': 'public_domain', 'credito': 'Retrato de J. Edgar Hoover · Arquivo Nacional dos EUA (NAID 518187) · domínio público'},
        {'id': 'A-NEWSREEL-1957', 'tipo': 'video_arquivo', 'arquivo': PD + 'newsreel_1957-08-12_Red_Colonel.mp4', 'fonte': 'S-NEWSREEL-1957', 'rights_status': 'public_domain', 'credito': 'Universal Newsreel, 12/08/1957 · Internet Archive · domínio público'},
        {'id': 'A-NARA-FATO', 'tipo': 'dado_documental', 'fonte': 'S-NARA-2020', 'rights_status': 'fact_citation', 'credito': 'Fonte: Arquivo Nacional dos EUA (The Text Message, 26/03/2020)'},
        {'id': 'A-DATAS', 'tipo': 'dado_documental', 'fonte': 'S-FBI-HIST', 'rights_status': 'fact_citation', 'credito': 'Fonte: FBI · And Justice for All, 1954–1971'},
    ]
    church = lambda sid, peso, foco: ev(sid, 'pagina_documento', peso, 'A-CHURCH', 'documento_autentico', 'DOCUMENTO ORIGINAL', {'pagina': 12, 'foco': foco},
                                       mov='da página ao trecho; lápis marca', som='papel, lápis', prompt='página do relatório do Senado de 1976')
    carta = lambda sid, peso, foco, inv=False: ev(sid, 'imagem_arquivo', peso, 'A-CARTA-1967', 'documento_autentico', 'DOCUMENTO ORIGINAL',
                                                 {'moldura': 'foto', 'foco': foco, 'largura': 900, 'inclinacao': -1.2}, mov='câmera vai ao trecho', som='papel',
                                                 prompt='carta original do FBI de 1967')
    FBITXT = {'publico': {'cabecalho': 'FBI · HISTÓRIA OFICIAL', 'texto': '...began to learn about the classified program after an FBI office in Media, Pennsylvania, was burglarized in 1971 by radicals and information was leaked to the press and Congress.',
                          'destaque': 'Media, Pennsylvania', 'rodape': 'TRANSCRIÇÃO · fbi.gov · domínio público'}}
    L = [
        linha('L01', 'cold_open', 'Em 1971, um escritório do FBI na Pensilvânia é arrombado.',
              [ev('S01', 'escritorio_epoca', 1.1, 'A-PRODUCAO-ORIGINAL', 'reconstituicao_ilustrada', 'RECONSTITUIÇÃO ILUSTRADA', {'acao': 'lanterna', 'semente': 5},
                  tela='PENSILVÂNIA · 1971', credito=False, mov='lanterna varre os arquivos de aço; uma gaveta se abre', som='vidro, passos, gaveta',
                  prompt='escritório de repartição de 1971 à noite: arquivos de aço, máquina de escrever', neg='documento falsificado, logotipos, rostos inventados, monitor, computador'),
               ev('S02', 'dossies', 0.9, 'A-PRODUCAO-ORIGINAL', 'ilustracao', 'ILUSTRAÇÃO', {'rotulos': ['ARQUIVO', 'ARQUIVO', 'ARQUIVO'], 'dur': 2.4}, credito=False,
                  som='pastas', prompt='pastas genéricas')], 340, ['C1'],
              tts='Em mil novecentos e setenta e um, um escritório do efe-bê-i na Pensilvânia é arrombado.'),
        linha('L02', 'cold_open', 'Os papéis levados dali vão parar na imprensa e no Congresso.',
              [ev('S03', 'trecho_documento', 1.0, 'A-FBI-HIST', 'documento_autentico', 'DOCUMENTADO', FBITXT, mov='lápis circula o lugar', som='lápis')], 400, ['C1', 'C2']),
        linha('L03', 'inciting_question', 'Eu sou o Arquivista. Aqui não há teoria: o FBI reconhece.',
              [pers('S04', 'aparicao', 1.0, 'O FBI RECONHECE'), pers('S05', 'corredor', 1.0, params={'direcao': -1})], 360, ['C2']),
        linha('L04', 'dated_evidence', 'O nome era Cointelpro. Aprovado em 1956, segundo o FBI.',
              [ev('S06', 'titulo_obra', 1.0, 'A-DATAS', 'dado_documental', 'DOCUMENTADO', {'linhas': ['COINTELPRO'], 'sub': 'FBI · 1956–1971'}, som='varredura', prompt='nome do programa'),
               ev('S07', 'imagem_arquivo', 1.0, 'A-HOOVER', 'foto_arquivo', 'FOTO DE ARQUIVO', {'moldura': 'foto', 'legenda': 'J. Edgar Hoover, diretor do FBI', 'largura': 760},
                  mov='push-in lento no retrato', som='obturador', prompt='retrato oficial de Hoover (NARA)', neg='retrato alterado')], 340, ['C3'],
              tts='O nome era Cointélpro. Aprovado em mil novecentos e cinquenta e seis, segundo o efe-bê-i.'),
        linha('L05', 'dated_evidence', 'Era a Guerra Fria. Em 1957, os cinejornais mostravam a prisão de um espião soviético.',
              [ev('S08', 'video_arquivo', 0.8, 'A-NEWSREEL-1957', 'video_arquivo', 'CINEJORNAL DE 1957', {'inicio': 0.5}, mov='cartela', som='chiado de película'),
               ev('S09', 'video_arquivo', 1.2, 'A-NEWSREEL-1957', 'video_arquivo', 'CINEJORNAL DE 1957', {'inicio': 33.5}, mov='tribunal', som='chiado de película')],
              360, ['C4'], tts='Era a Guerra Fria. Em mil novecentos e cinquenta e sete, os cinejornais mostravam a prisão de um espião soviético.'),
        linha('L06', 'dated_evidence', 'Mas o alvo não eram só espiões estrangeiros. Eram grupos do próprio país.',
              [church('S10', 1.1, [0.03, 0.10, 0.97, 0.15]), pers('S11', 'virar_cabeca', 0.9, params={'lado': 1})], 360, ['C5']),
        linha('L07', 'dated_evidence', 'Em 1967, uma carta do diretor do FBI abre uma nova frente, contra grupos nacionalistas negros.',
              [carta('S12', 1.0, [0.10, 0.20, 0.55, 0.28]), carta('S12b', 1.0, [0.62, 0.10, 0.97, 0.16])], 340, ['C6'],
              tts='Em mil novecentos e sessenta e sete, uma carta do diretor do efe-bê-i abre uma nova frente, contra grupos nacionalistas negros.'),
        linha('L08', 'dated_evidence', 'O objetivo, nas palavras do documento: expor, perturbar, desviar, desacreditar ou neutralizar.',
              [carta('S13', 1.3, [0.10, 0.435, 0.96, 0.49]), pers('S14', 'silencio', 0.7)], 620, ['C6']),
        linha('L09', 'dated_evidence', 'Em 1976, o Senado expôs o programa, com base em mais de vinte mil páginas do FBI.',
              [pers('S15', 'ombro', 1.0, prova={'tipo': 'pagina_documento', 'params': {'pagina': 12, 'foco': [0.03, 0.185, 0.97, 0.245], 'circular': False}},
                    params={'lado': -1}, asset='A-CHURCH', selo='DOCUMENTO ORIGINAL', vst='documento_autentico'),
               church('S16', 1.0, [0.03, 0.352, 0.97, 0.395])], 300, ['C7'],
              tts='Em mil novecentos e setenta e seis, o Senado expôs o programa, com base em mais de vinte mil páginas do efe-bê-i.'),
        linha('L09b', 'dated_evidence', 'As técnicas iam do trivial ao degradante: cartas anônimas para destruir casamentos.',
              [church('S16b', 1.0, [0.03, 0.245, 0.97, 0.355])], 400, ['C7']),
        linha('L10', 'reversal_or_surprise', 'E o detalhe mais estranho: em 1970, o FBI usou até um clube de selos como fachada.',
              [ev('S17', 'titulo_obra', 1.0, 'A-NARA-FATO', 'dado_documental', 'DOCUMENTADO', {'linhas': ['UM CLUBE', 'DE SELOS'], 'sub': 'FACHADA DE CONTRAINTELIGÊNCIA · 1970'},
                  som='carimbo', prompt='frase factual em tipografia própria'), pers('S17b', 'virar_cabeca', 0.8, params={'lado': -1})], 500, ['C8'],
              tts='E o detalhe mais estranho: em mil novecentos e setenta, o efe-bê-i usou até um clube de selos como fachada.'),
        linha('L11', 'reversal_or_surprise', 'Segundo o FBI, Hoover encerrou o programa em abril de 1971.',
              [ev('S18', 'salto_datas', 1.0, 'A-DATAS', 'dado_documental', 'DOCUMENTADO', {'de': '1956', 'ate': 'ABRIL · 1971', 'rot_de': 'COINTELPRO APROVADO', 'rot_ate': 'ENCERRAMENTO FORMAL', 'gap': '15 ANOS'},
                  mov='linha do tempo', som='relógio'), pers('S18b', 'debrucar', 0.8)], 400, ['C9'],
              tts='Segundo o efe-bê-i, Húver encerrou o programa em abril de mil novecentos e setenta e um.'),
        linha('L12', 'competing_interpretations', 'Conspiração comprovada não prova todas as outras. E o fim oficial não prova que nada parecido voltou a acontecer.',
              [ev('S19', 'leituras', 0.9, 'A-PRODUCAO-ORIGINAL', 'tipografia', 'ANÁLISE', {'a': ['COMPROVADA', '1956–1971'], 'b': ['E AS OUTRAS?', 'cada uma exige prova'], 'sync_b': 2.0, 'brilho_fundo': 0.5},
                  credito=False, som='pulso grave', prompt='comprovada'),
               ev('S19b', 'leituras', 1.1, 'A-PRODUCAO-ORIGINAL', 'tipografia', 'ANÁLISE', {'a': ['COMPROVADA', '1956–1971'], 'b': ['E AS OUTRAS?', 'cada uma exige prova'], 'sync_b': 0.0, 'brilho_fundo': 0.5},
                  credito=False, som='pulso grave', prompt='e as outras')], 500, ['C10']),
        linha('L13', 'open_loop_or_next_dossier', 'No próximo arquivo: outra agência e uma ordem para destruir papéis.',
              [pers('S20', 'olhar_camera', 0.9, 'PRÓXIMO ARQUIVO', params={'de_yaw': -12}), pers('S21', 'encerramento', 1.1)], 900),
    ]
    return {'schema': 'arquivo-oculto/episodio-v2', 'episode_id': 'AO-S01-E04', 'versao': 'v2.0', 'num': 4, 'formato': 'investigacao_90',
            'titulo': 'COINTELPRO: uma conspiração comprovada', 'serie': 'Conspirações Documentadas', 'hook': 'O FBI RECONHECE',
            'status_editorial': 'pronto_para_render', 'estrutura': ESTRUTURA,
            'nota_editorial': 'Documentos de domínio público lidos nesta sessão (FBI, Senado, Arquivo Nacional, cinejornal). Pessoas reais só como agentes públicos documentados; alvos citados pelo rótulo do próprio documento, sem nomes privados.',
            'fontes': fontes, 'claims': claims, 'assets': assets, 'linhas': L, 'outro': outro(4, 'A ORDEM PARA DESTRUIR PAPÉIS'), 'listas': {},
            'legenda_post': 'COINTELPRO não é teoria: o próprio FBI reconhece. Aprovado em 1956, exposto depois do arrombamento de um escritório em Media (Pensilvânia) em 1971, investigado pelo Senado em 1976 com base em mais de 20 mil páginas do FBI.\n\nFontes: FBI (And Justice for All) · Church Committee, Livro III (1976) · Arquivo Nacional dos EUA · Universal Newsreel 1957 (domínio público).\nPersonagem fictício, voz sintética.\n\n#ArquivoOculto #COINTELPRO #FBI #historia #documentos'}


# =================================================================================================== EP05 — MKULTRA
def ep05():
    C77 = PD + 'cia_1977-08-02_release_mkultra_documents.pdf'
    S119 = PD + 'cia_mkultra_subproject_119.pdf'
    fontes = [
        {'id': 'S-SENATE-1977', 'titulo': 'Senado dos EUA — Project MKULTRA, audiência conjunta de 03/08/1977 (transcrição e anexos)', 'editor': 'Senate Select Committee on Intelligence',
         'url': 'https://www.intelligence.senate.gov/wp-content/uploads/2024/08/sites-default-files-hearings-95mkultra.pdf', 'data_documento': '1977-08-03',
         'verificacao': 'conferido pelo site Arquivo Oculto v0.8 (docs/FONTES_MKULTRA_V08.md, 03/11/2026): aprovação em 13/04/1953 (Anexo A); Turner identifica testes sem conhecimento documentados em 6 dos 149 subprojetos então discutidos; registros recuperados principalmente financeiros. O servidor do Senado respondeu 403 a downloads automáticos nesta sessão; não relido.',
         'direitos': 'documento do Congresso dos EUA: domínio público'},
        {'id': 'S-CIA-1975', 'titulo': 'CIA Office of Inspector General — Destruction of Records on Drugs and Toxins (20/10/1975)', 'editor': 'CIA Reading Room',
         'url': 'https://www.cia.gov/readingroom/docs/DESTRUCTION%20OF%20RECORDS%20ON%20DRUGS%20AND%20TOXINS%5B12886309%5D.pdf',
         'verificacao': 'conferido pelo site v0.8: destruição de registros em janeiro de 1973; materiais remanescentes e não localizados. Não relido nesta sessão (o link redireciona).'},
        {'id': 'S-CIA-1977', 'titulo': 'CIA — Release of MKULTRA Documents on 2 August 1977 (memorando, 2 pp.)', 'editor': 'CIA Reading Room (cópia do Internet Archive, CIA-RDP81-00261R000300050017-0)',
         'url': 'https://archive.org/details/cia-readingroom-document-cia-rdp81-00261r000300050017-0', 'snapshot': C77, 'acessado_em': '2026-11-05', 'data_documento': '1977-08-02',
         'verificacao': 'lido nesta sessão: primeira liberação dos registros financeiros dos subprojetos 1–11; 415 documentos revisados; lista de áreas que a imprensa poderia "elaborar ou distorcer": estudo de plantas, manual de um mágico para uso de truques na administração de drogas a participantes que não sabiam (b), testes de LSD (f), ansiedade induzida por hipnose em 18 pessoas (d)',
         'direitos': 'documento do governo federal dos EUA: domínio público'},
        {'id': 'S-CIA-SP119', 'titulo': 'CIA — MKULTRA Subproject 119 (documentos a partir de 1959)', 'editor': 'CIA Reading Room (cópia do Internet Archive, 00017376)',
         'url': 'https://archive.org/details/cia-readingroom-document-00017376', 'snapshot': S119, 'acessado_em': '2026-11-05',
         'verificacao': 'lido nesta sessão (p.1 do PDF): "Purpose of Project: To make a critical review of the literature and scientific development related to the interpretation of bioelectric signals from the human organism, and activation of human behavior by remote means."',
         'direitos': 'documento do governo federal dos EUA: domínio público'},
    ]
    claims = [
        {'id': 'C1', 'texto': 'Parte dos registros do MKULTRA foi destruída em janeiro de 1973', 'status': 'documented', 'fontes': ['S-CIA-1975']},
        {'id': 'C2', 'texto': 'O registro do Senado situa a aprovação do MKULTRA em 13/04/1953', 'status': 'documented', 'fontes': ['S-SENATE-1977']},
        {'id': 'C3', 'texto': 'Em 02/08/1977 a CIA fez a primeira liberação dos registros financeiros dos subprojetos 1–11', 'status': 'documented', 'fontes': ['S-CIA-1977']},
        {'id': 'C4', 'texto': 'O memorando lista áreas que a imprensa poderia "elaborar ou distorcer", incluindo um manual de um mágico para administrar drogas a participantes que não sabiam e testes de LSD', 'status': 'documented', 'fontes': ['S-CIA-1977']},
        {'id': 'C5', 'texto': 'Em 03/08/1977 o Senado fez audiência sobre o MKULTRA', 'status': 'documented', 'fontes': ['S-SENATE-1977']},
        {'id': 'C6', 'texto': 'Turner afirmou haver documentação de testes sem conhecimento dos participantes em 6 dos 149 subprojetos então discutidos', 'status': 'documented', 'fontes': ['S-SENATE-1977'], 'nota': 'não é total definitivo de vítimas'},
        {'id': 'C7', 'texto': 'O subprojeto 119 propôs revisar a literatura sobre sinais bioelétricos e ativação do comportamento humano à distância', 'status': 'documented', 'fontes': ['S-CIA-SP119']},
        {'id': 'C8', 'texto': 'As fontes não demonstram uma técnica de controle total da mente', 'status': 'interpretation', 'fontes': [], 'nota': 'classificação do site: indeterminado'},
    ]
    assets = BASE_ASSETS + [
        {'id': 'A-CIA-1977', 'tipo': 'documento_autentico', 'arquivo': C77, 'fonte': 'S-CIA-1977', 'rights_status': 'public_domain', 'credito': 'CIA, memorando de 02/08/1977 · CIA Reading Room · domínio público'},
        {'id': 'A-CIA-SP119', 'tipo': 'documento_autentico', 'arquivo': S119, 'fonte': 'S-CIA-SP119', 'rights_status': 'public_domain', 'credito': 'CIA, MKULTRA Subprojeto 119 · CIA Reading Room · domínio público'},
        {'id': 'A-SENADO', 'tipo': 'dado_documental', 'fonte': 'S-SENATE-1977', 'rights_status': 'fact_citation', 'credito': 'Fonte: Senado dos EUA, audiência de 03/08/1977'},
        {'id': 'A-CIA-1975', 'tipo': 'dado_documental', 'fonte': 'S-CIA-1975', 'rights_status': 'fact_citation', 'credito': 'Fonte: CIA, Inspetor-Geral, memorando de 20/10/1975'},
    ]
    m77 = lambda sid, peso, pagina, foco, circ=True: ev(sid, 'pagina_documento', peso, 'A-CIA-1977', 'documento_autentico', 'DOCUMENTO ORIGINAL',
                                                        {'pagina': pagina, 'foco': foco, 'circular': circ}, mov='da página ao trecho; lápis marca', som='papel, lápis',
                                                        prompt='memorando original da CIA de 1977')
    L = [
        linha('L01', 'cold_open', 'Janeiro de 1973. Na CIA, papéis de um programa secreto são destruídos.',
              [ev('S01', 'escritorio_epoca', 1.0, 'A-PRODUCAO-ORIGINAL', 'reconstituicao_ilustrada', 'RECONSTITUIÇÃO ILUSTRADA', {'acao': 'gaveta', 'semente': 13},
                  tela='JANEIRO DE 1973', credito=False, mov='uma gaveta de aço se abre sob a luz', som='gaveta de aço, fragmentadora distante',
                  prompt='escritório de repartição de 1973: arquivos de aço, máquina de escrever', neg='documento falsificado, logotipos, rostos inventados, monitor, computador'),
               ev('S02', 'dossies', 1.0, 'A-CIA-1975', 'ilustracao', 'ILUSTRAÇÃO', {'rotulos': ['DESTRUÍDO', 'DESTRUÍDO', 'DESTRUÍDO'], 'dur': 2.6},
                  som='pastas', prompt='pastas genéricas carimbadas')], 360, ['C1'],
              tts='Janeiro de mil novecentos e setenta e três. Na CIA, papéis de um programa secreto são destruídos.'),
        linha('L02', 'cold_open', 'Mas nem tudo desapareceu.', [pers('S03', 'silencio', 1.0)], 600, ['C1']),
        linha('L03', 'inciting_question', 'Eu sou o Arquivista. O nome do programa era MKUltra.',
              [pers('S04', 'aparicao', 1.0, 'O NOME ERA MKULTRA'), pers('S05', 'corredor', 1.0, params={'direcao': 1})], 360,
              tts='Eu sou o Arquivista. O nome do programa era Êmi-Quêi-Últra.'),
        linha('L04', 'dated_evidence', 'Segundo o Senado americano, ele foi aprovado em abril de 1953.',
              [ev('S06', 'titulo_obra', 1.0, 'A-SENADO', 'dado_documental', 'DOCUMENTADO', {'linhas': ['MKULTRA'], 'sub': 'CIA · APROVADO EM 13/04/1953'}, som='varredura', prompt='nome do programa e data')],
              340, ['C2'], tts='Segundo o Senado americano, ele foi aprovado em abril de mil novecentos e cinquenta e três.'),
        linha('L05', 'dated_evidence', 'Em 2 de agosto de 1977, a CIA liberou os primeiros papéis: registros financeiros.',
              [m77('S07', 1.0, 0, [0.15, 0.38, 0.93, 0.415], circ=False), m77('S08', 1.0, 0, [0.15, 0.44, 0.93, 0.50])], 340, ['C3'],
              tts='Em dois de agosto de mil novecentos e setenta e sete, a CIA liberou os primeiros papéis: registros financeiros.'),
        linha('L06', 'dated_evidence', 'E um memorando lista o que a imprensa poderia, nas palavras da CIA, elaborar ou distorcer.',
              [pers('S09', 'ombro', 1.0, prova={'tipo': 'pagina_documento', 'params': {'pagina': 0, 'foco': [0.15, 0.69, 0.93, 0.77], 'circular': False}},
                    params={'lado': 1}, asset='A-CIA-1977', selo='DOCUMENTO ORIGINAL', vst='documento_autentico'),
               m77('S10', 1.0, 0, [0.15, 0.69, 0.93, 0.77])], 340, ['C4']),
        linha('L07', 'dated_evidence', 'Um item: um manual, escrito por um mágico, para usar truques ao dar drogas a pessoas que não sabiam.',
              [m77('S11', 1.4, 0, [0.18, 0.83, 0.90, 0.885]), pers('S12', 'virar_cabeca', 0.8, params={'lado': -1})], 600, ['C4']),
        linha('L08', 'dated_evidence', 'Outro item fala em testes com LSD.', [m77('S13', 1.0, 1, [0.22, 0.44, 0.93, 0.51])], 400, ['C4'],
              tts='Outro item fala em testes com éli-ésse-dê.'),
        linha('L09', 'dated_evidence', 'No dia seguinte, o diretor da CIA depôs no Senado.',
              [ev('S14a', 'salto_datas', 1.0, 'A-SENADO', 'dado_documental', 'DOCUMENTADO', {'de': '13·04·1953', 'ate': '03·08·1977', 'rot_de': 'MKULTRA APROVADO', 'rot_ate': 'AUDIÊNCIA NO SENADO', 'gap': '24 ANOS'},
                  mov='linha do tempo', som='relógio', prompt='datas com fonte'), pers('S15', 'debrucar', 0.9)], 300, ['C5', 'C2']),
        linha('L09b', 'dated_evidence', 'Disse haver documentação de testes sem conhecimento dos participantes em seis dos 149 subprojetos discutidos.',
              [ev('S14', 'titulo_obra', 1.0, 'A-SENADO', 'dado_documental', 'DOCUMENTADO', {'linhas': ['6 DE 149'], 'sub': 'SUBPROJETOS COM TESTES SEM CONHECIMENTO DOCUMENTADOS · 1977'},
                  som='grave', prompt='número da audiência'),
               m77('S14b', 1.0, 0, [0.15, 0.44, 0.93, 0.50], circ=False)], 460, ['C6'],
              tts='Disse haver documentação de testes sem conhecimento dos participantes em seis dos cento e quarenta e nove subprojetos discutidos.'),
        linha('L10', 'reversal_or_surprise', 'Seis não é o total de vítimas. É o que sobrou de papel para documentar.',
              [ev('S16', 'leituras', 1.0, 'A-PRODUCAO-ORIGINAL', 'tipografia', 'ANÁLISE', {'a': ['6', 'documentados'], 'b': ['O RESTO?', 'papéis destruídos em 1973'], 'sync_b': 0.45, 'brilho_fundo': 0.5},
                  credito=False, som='dois pulsos', prompt='documentado x destruído')], 600, ['C6', 'C1']),
        linha('L11', 'reversal_or_surprise', 'E há um subprojeto que parece ficção científica: o 119.',
              [ev('S17', 'pagina_documento', 1.0, 'A-CIA-SP119', 'documento_autentico', 'DOCUMENTO ORIGINAL', {'pagina': 1, 'foco': [0.30, 0.10, 0.95, 0.16], 'circular': False},
                  mov='página do subprojeto', som='papel', prompt='documento original do subprojeto 119')], 400, ['C7'],
              tts='E há um subprojeto que parece ficção científica: o cento e dezenove.'),
        linha('L12', 'reversal_or_surprise', 'O objetivo: revisar a ciência dos sinais bioelétricos do corpo e da ativação do comportamento à distância.',
              [pers('S18a', 'ombro', 1.0, prova={'tipo': 'pagina_documento', 'params': {'pagina': 1, 'foco': [0.46, 0.16, 0.93, 0.32], 'circular': False}},
                    params={'lado': -1}, asset='A-CIA-SP119', selo='DOCUMENTO ORIGINAL', vst='documento_autentico'),
               ev('S18', 'pagina_documento', 1.0, 'A-CIA-SP119', 'documento_autentico', 'DOCUMENTO ORIGINAL', {'pagina': 1, 'foco': [0.46, 0.16, 0.93, 0.32]},
                  mov='lápis circula o objetivo', som='lápis', prompt='objetivo do subprojeto 119')], 500, ['C7']),
        linha('L13', 'competing_interpretations', 'Prova controle da mente? Não. Prova que a ideia foi estudada em segredo.',
              [ev('S19', 'leituras', 1.0, 'A-PRODUCAO-ORIGINAL', 'tipografia', 'ANÁLISE', {'a': ['ESTUDADO', 'documentos da CIA'], 'b': ['CONTROLE TOTAL?', 'sem prova'], 'sync_b': 2.0, 'brilho_fundo': 0.5},
                  credito=False, som='pulso', prompt='estudado'),
               ev('S19b', 'leituras', 1.0, 'A-PRODUCAO-ORIGINAL', 'tipografia', 'ANÁLISE', {'a': ['ESTUDADO', 'documentos da CIA'], 'b': ['CONTROLE TOTAL?', 'sem prova'], 'sync_b': 0.0, 'brilho_fundo': 0.5},
                  credito=False, som='pulso', prompt='controle total')], 500, ['C8']),
        linha('L14', 'open_loop_or_next_dossier', 'No próximo arquivo: um plano militar que propunha culpar outro país. Por escrito.',
              [pers('S20', 'olhar_camera', 0.9, 'POR ESCRITO', params={'de_yaw': 12}), pers('S21', 'encerramento', 1.1)], 900),
    ]
    return {'schema': 'arquivo-oculto/episodio-v2', 'episode_id': 'AO-S01-E05', 'versao': 'v2.0', 'num': 5, 'formato': 'investigacao_90',
            'titulo': 'MKULTRA: quando o segredo foi confirmado', 'serie': 'Conspirações Documentadas', 'hook': 'PAPÉIS DESTRUÍDOS EM 1973',
            'status_editorial': 'pronto_para_render', 'estrutura': ESTRUTURA,
            'nota_editorial': 'Documentos da CIA de 1977 e do subprojeto 119 lidos nesta sessão; dados do Senado e da destruição de 1973 conferidos pelo site v0.8 (fontes registradas). Sem procedimentos, doses, nomes privados ou imagens de vítimas. "Seis" não é apresentado como total de vítimas.',
            'fontes': fontes, 'claims': claims, 'assets': assets, 'linhas': L, 'outro': outro(5, 'UM PLANO PARA CULPAR CUBA'), 'listas': {},
            'legenda_post': 'MKULTRA não é lenda: a própria CIA liberou registros em 02/08/1977 e um memorando interno listou o que a imprensa poderia "elaborar ou distorcer" — incluindo um manual de um mágico para administrar drogas a pessoas que não sabiam. Mas papéis foram destruídos em 1973, e o que sobrou não prova controle total da mente.\n\nFontes: CIA (memorando de 02/08/1977; subprojeto 119) · Senado dos EUA, audiência de 03/08/1977.\nPersonagem fictício, voz sintética.\n\n#ArquivoOculto #MKULTRA #CIA #historia #documentos'}


# =================================================================================================== EP03 — Enough is Enough
def ep03():
    ENOUGH = PRIV + 'cartas/enough_is_enough.png'
    SNIPER = PRIV + 'cartas/sniper.jpg'
    fontes = [
        {'id': 'S-FBI-BUTLER', 'titulo': 'FBI — Butler Investigation Updates (comunicados de 13 e 14/07/2024)', 'editor': 'FBI (fbi.gov)', 'url': 'https://www.fbi.gov/news/press-releases/butler-investigation-updates',
         'snapshot': PD + 'fbi_butler_investigation_updates.html', 'acessado_em': '2026-11-05',
         'verificacao': 'lido: o FBI investiga o tiroteio no comício de 13 de julho em Butler, Pensilvânia, como tentativa de assassinato do ex-presidente Donald Trump', 'direitos': 'texto do governo federal dos EUA: domínio público'},
        {'id': 'S-ASSASSINS-1996', 'titulo': 'Steve Jackson — lista oficial de Assassins (Usenet, jan/1996)', 'editor': 'Steve Jackson Games (rec.games.trading-cards.announce)',
         'url': 'https://groups.google.com/g/rec.games.trading-cards.announce/c/aRuYIKEv8Zc',
         'verificacao': 'conferido pelo site v0.6/v0.8 (dossiê enough): Enough is Enough consta como Plot / Paralysis, Common; não relido nesta sessão'},
        {'id': 'S-LIST-1995', 'titulo': 'The Official INWO Card List - April 18, 1995', 'editor': 'Steve Jackson Games', 'url': 'https://www.sjgames.com/inwo/lists/ill.html',
         'snapshot': PRIV + 'sjgames_inwo_lists_ill_1995-04-18.html', 'acessado_em': '2026-11-04',
         'verificacao': 'lido: 5 cartas do tipo Ass.: Car Bomb (C, Dan/Derek), Hit and Run (C, Gary/Derek), Poison (C, Shea/Derek), Sniper (U, Dan/Rick), Withering Curse (R, Shea/Jeff)'},
        {'id': 'S-CGG-ENOUGH', 'titulo': 'CardGameGeek — reprodução de Enough is Enough', 'editor': 'CardGameGeek (vendedor)', 'url': 'https://shop.cardgamegeek.com/shop/product/enough-is-enough',
         'snapshot': ENOUGH, 'acessado_em': '2026-11-05',
         'verificacao': 'frente lida nesta sessão: título, arte com rosto em tons escuros e roxos, texto de ambientação "At any time, at any place, our snipers can drop you. Have a nice day." e regra sobre remover Zap, Paralysis ou Attribute Freeze da própria Power Structure ("house-cleaning")',
         'direitos': 'reprodução de vendedor; titularidade Steve Jackson Games; só pesquisa privada'},
        {'id': 'S-CGG-BRIEF', 'titulo': 'CardGameGeek — reprodução de A Brief Attack of Conscience', 'editor': 'CardGameGeek (vendedor)', 'url': 'https://shop.cardgamegeek.com/',
         'snapshot': PRIV + 'cartas/a_brief_attack_of_conscience.png', 'acessado_em': '2026-11-05',
         'verificacao': 'frente lida: carta Zap; "The target Illuminati cannot use Assassinations or Discounts"', 'direitos': 'reprodução de vendedor; só pesquisa privada'},
        {'id': 'S-CGG-SNIPER', 'titulo': 'CardGameGeek — reprodução de Sniper', 'editor': 'CardGameGeek (vendedor)', 'url': 'https://shop.cardgamegeek.com/',
         'snapshot': SNIPER, 'acessado_em': '2026-11-05', 'direitos': 'reprodução de vendedor; só pesquisa privada'},
    ]
    claims = [
        {'id': 'C1', 'texto': 'Em 13/07/2024 houve uma tentativa de assassinato de Donald Trump num comício em Butler, Pensilvânia', 'status': 'documented', 'fontes': ['S-FBI-BUTLER']},
        {'id': 'C2', 'texto': 'Depois do atentado, a carta Enough is Enough circulou como "prova" de conhecimento prévio', 'status': 'allegation', 'fontes': [], 'nota': 'primeira circulação não rastreada'},
        {'id': 'C3', 'texto': 'Enough is Enough consta da lista oficial de Assassins (jan/1996)', 'status': 'documented', 'fontes': ['S-ASSASSINS-1996']},
        {'id': 'C4', 'texto': 'A arte mostra um rosto em tons escuros e roxos; a identificação com uma pessoa real não foi demonstrada', 'status': 'interpretation', 'fontes': [], 'nota': 'site: hipótese em investigação'},
        {'id': 'C5', 'texto': 'O texto de ambientação fala em atiradores; a regra trata de remover efeitos da própria estrutura de poder', 'status': 'documented', 'fontes': ['S-CGG-ENOUGH']},
        {'id': 'C6', 'texto': 'A lista de 1995 tem 5 cartas do tipo Assassination, entre elas Sniper', 'status': 'documented', 'fontes': ['S-LIST-1995']},
        {'id': 'C7', 'texto': 'Previsão exigiria data anterior e alvo identificável; há data, não há alvo identificado', 'status': 'interpretation', 'fontes': []},
    ]
    assets = BASE_ASSETS + [
        {'id': 'A-FBI-BUTLER', 'tipo': 'documento_autentico', 'fonte': 'S-FBI-BUTLER', 'rights_status': 'public_domain', 'credito': 'FBI · Butler Investigation Updates (fbi.gov) · domínio público'},
        {'id': 'A-CARTA-ENOUGH', 'tipo': 'arte_autentica', 'arquivo': ENOUGH, 'fonte': 'S-CGG-ENOUGH', 'rights_status': 'private_research', 'fallback': 'placeholder',
         'credito': 'Carta Enough is Enough · © Steve Jackson Games · reprodução CardGameGeek'},
        {'id': 'A-CARTA-BRIEF', 'tipo': 'arte_autentica', 'arquivo': PRIV + 'cartas/a_brief_attack_of_conscience.png', 'fonte': 'S-CGG-BRIEF', 'rights_status': 'private_research', 'fallback': 'placeholder',
         'credito': 'Carta A Brief Attack of Conscience · © Steve Jackson Games · reprodução CardGameGeek'},
        {'id': 'A-CARTA-SNIPER', 'tipo': 'arte_autentica', 'arquivo': SNIPER, 'fonte': 'S-CGG-SNIPER', 'rights_status': 'private_research', 'fallback': 'placeholder',
         'credito': 'Carta Sniper · © Steve Jackson Games · reprodução CardGameGeek'},
        {'id': 'A-ASSASSINS', 'tipo': 'dado_documental', 'fonte': 'S-ASSASSINS-1996', 'rights_status': 'fact_citation', 'credito': 'Fonte: lista oficial de Assassins, Steve Jackson Games, jan/1996'},
        {'id': 'A-LISTA-DADOS', 'tipo': 'dado_documental', 'fonte': 'S-LIST-1995', 'rights_status': 'fact_citation', 'credito': 'Fonte: lista oficial INWO, Steve Jackson Games, 18/04/1995'},
    ]
    carta = lambda sid, peso, foco, circ=False, asset='A-CARTA-ENOUGH': ev(sid, 'imagem_arquivo', peso, asset, 'arte_autentica', 'CARTA ORIGINAL',
                                                                          {'moldura': 'carta', 'foco': foco, 'largura': 600, 'inclinacao': -2.0},
                                                                          mov='câmera vai ao detalhe da carta', som='carta na mesa', prompt='reprodução da carta original', neg='carta redesenhada')
    FBITXT = {'publico': {'cabecalho': 'FBI · 14/07/2024', 'texto': 'The FBI continues to investigate the shooting incident at the July 13 rally in Butler, Pennsylvania, as an assassination attempt on former President Donald Trump.',
                          'destaque': 'July 13 rally in Butler', 'rodape': 'TRANSCRIÇÃO · fbi.gov · domínio público'}}
    L = [
        linha('L01', 'cold_open', '13 de julho de 2024. Um atentado contra Donald Trump, num comício em Butler, na Pensilvânia.',
              [ev('S01', 'trecho_documento', 1.1, 'A-FBI-BUTLER', 'documento_autentico', 'DOCUMENTADO', FBITXT, mov='lápis marca data e lugar', som='papel'),
               ev('S02', 'telas', 0.9, 'A-PRODUCAO-ORIGINAL', 'ilustracao', 'ILUSTRAÇÃO', {'anos': [1996, 2024]}, credito=False, som='chiado', prompt='monitores abstratos')],
              360, ['C1'], tts='Treze de julho de dois mil e vinte e quatro. Um atentado contra Donald Trâmp, num comício em Bâtler, na Pensilvânia.'),
        linha('L02', 'cold_open', 'Depois disso, uma carta de baralho passou a circular como prova de que alguém sabia.',
              [ev('S03', 'cartas_caem', 1.0, 'A-PRODUCAO-ORIGINAL', 'ilustracao', 'ILUSTRAÇÃO', {'n': 8, 'semente': 21}, credito=False, som='cartas', prompt='versos genéricos AO', neg='arte de INWO')],
              400, ['C2']),
        linha('L03', 'inciting_question', 'Eu sou o Arquivista. Vamos ler a carta, não o boato.',
              [pers('S04', 'aparicao', 1.0, 'LER A CARTA, NÃO O BOATO'), pers('S05', 'corredor', 0.9, params={'direcao': 1})], 360),
        linha('L04', 'dated_evidence', 'O nome dela é Enough is Enough. Em português: basta.',
              [carta('S06', 1.0, [0.06, 0.0, 0.94, 0.10])], 360, ['C3'], tts='O nome dela é Inâf is Inâf. Em português: basta.'),
        linha('L05', 'dated_evidence', 'Ela consta da lista oficial da expansão Assassins, divulgada em janeiro de 1996.',
              [ev('S07', 'titulo_obra', 1.0, 'A-ASSASSINS', 'dado_documental', 'DOCUMENTADO', {'linhas': ['ENOUGH', 'IS ENOUGH'], 'sub': 'ASSASSINS · LISTA OFICIAL · JAN/1996'}, som='varredura', prompt='nome e data'),
               pers('S08', 'virar_cabeca', 0.9, params={'lado': -1})], 360, ['C3'],
              tts='Ela consta da lista oficial da expansão Assassins, divulgada em janeiro de mil novecentos e noventa e seis.'),
        linha('L06', 'competing_interpretations', 'Na arte, um rosto em tons escuros e roxos. De quem? A carta não diz.',
              [carta('S09', 1.2, [0.05, 0.10, 0.95, 0.56]), pers('S10', 'silencio', 0.7)], 500, ['C4']),
        linha('L07', 'dated_evidence', 'Em itálico, uma frase de ambientação: nossos atiradores podem te derrubar a qualquer hora, em qualquer lugar.',
              [carta('S11', 1.3, [0.06, 0.69, 0.94, 0.75], circ=True), pers('S11b', 'silencio', 0.7)], 400, ['C5']),
        linha('L08', 'reversal_or_surprise', 'Mas a regra da carta não fala em atentado. Fala em faxina: remover efeitos de paralisia da sua própria estrutura de poder.',
              [pers('S12', 'ombro', 1.0, prova={'tipo': 'imagem_arquivo', 'params': {'moldura': 'carta', 'foco': [0.06, 0.76, 0.94, 0.90], 'largura': 600}},
                    params={'lado': 1}, asset='A-CARTA-ENOUGH', selo='CARTA ORIGINAL', vst='arte_autentica'),
               carta('S13', 1.0, [0.06, 0.76, 0.94, 0.90])], 600, ['C5']),
        linha('L09', 'dated_evidence', 'E a lista do jogo de 1995 já tinha cinco cartas do tipo assassinato. Uma delas: Sniper.',
              [ev('S14', 'lista_oficial', 1.0, 'A-LISTA-DADOS', 'dado_documental', 'DOCUMENTADO', {'lista': 'ep03', 'sync': [0.62], 'camera': 'geral'}, mov='lápis circula Sniper', som='lápis'),
               ev('S15', 'imagem_arquivo', 1.0, 'A-CARTA-SNIPER', 'arte_autentica', 'CARTA ORIGINAL', {'moldura': 'carta', 'largura': 640, 'inclinacao': 2.5},
                  mov='push-in na carta', som='carta na mesa', prompt='reprodução da carta Sniper', neg='carta redesenhada')], 400, ['C6'],
              tts='E a lista do jogo de mil novecentos e noventa e cinco já tinha cinco cartas do tipo assassinato. Uma delas: Snáiper.'),
        linha('L10', 'reversal_or_surprise', 'E uma expansão inteira se chama Assassins. Quando o tema é atentado, alguma carta vai parecer familiar.',
              [ev('S16', 'dossies', 1.0, 'A-PRODUCAO-ORIGINAL', 'ilustracao', 'ANÁLISE', {'rotulos': ['ASSASSINS', 'ASSASSINS', 'ASSASSINS'], 'dur': 2.6}, credito=False, som='pastas', prompt='pastas genéricas'),
               ev('S16b', 'imagem_arquivo', 1.0, 'A-CARTA-BRIEF', 'arte_autentica', 'CARTA ORIGINAL', {'moldura': 'carta', 'largura': 600, 'inclinacao': -2.5},
                  mov='push-in na carta', som='carta na mesa', prompt='reprodução da carta A Brief Attack of Conscience', neg='carta redesenhada')],
              460, ['C6', 'C7']),
        linha('L11', 'competing_interpretations', 'Previsão exige data antes do fato e um alvo identificável. Aqui existe a data. O alvo, não.',
              [ev('S17', 'leituras', 1.1, 'A-PRODUCAO-ORIGINAL', 'tipografia', 'ANÁLISE', {'a': ['DATA', 'jan/1996: documentada'], 'b': ['ALVO?', 'não identificado'], 'sync_b': 2.0, 'brilho_fundo': 0.5},
                  credito=False, som='pulso', prompt='data'),
               ev('S17b', 'leituras', 0.9, 'A-PRODUCAO-ORIGINAL', 'tipografia', 'ANÁLISE', {'a': ['DATA', 'jan/1996: documentada'], 'b': ['ALVO?', 'não identificado'], 'sync_b': 0.0, 'brilho_fundo': 0.5},
                  credito=False, som='pulso', prompt='alvo')], 500, ['C7']),
        linha('L12', 'open_loop_or_next_dossier', 'E quem ligou esta carta a Trump pela primeira vez? Este arquivo ainda não encontrou a origem.',
              [carta('S18a', 1.0, [0.05, 0.10, 0.95, 0.56]), pers('S18', 'debrucar', 1.0)], 500, ['C2'],
              tts='E quem ligou esta carta a Trâmp pela primeira vez? Este arquivo ainda não encontrou a origem.'),
        linha('L13', 'open_loop_or_next_dossier', 'No próximo arquivo: uma conspiração que o próprio FBI reconhece.',
              [pers('S19', 'olhar_camera', 0.9, 'O FBI RECONHECE', params={'de_yaw': -12}), pers('S20', 'encerramento', 1.1)], 900,
              tts='No próximo arquivo: uma conspiração que o próprio efe-bê-i reconhece.'),
    ]
    return {'schema': 'arquivo-oculto/episodio-v2', 'episode_id': 'AO-S01-E03', 'versao': 'v2.0', 'num': 3, 'formato': 'investigacao_90',
            'titulo': 'A carta associada a Trump', 'serie': 'Cartas do Futuro', 'hook': 'UMA CARTA DE 1996 PREVIU?',
            'status_editorial': 'pronto_para_render', 'estrutura': ESTRUTURA,
            'nota_editorial': 'Sem imagens do atentado e sem simulação de pessoa real. A carta é mostrada só na prévia privada (reprodução de vendedor); no modo público vira IMAGEM RETIDA. A identificação do rosto não é afirmada. A primeira circulação da associação não foi rastreada e isso é dito.',
            'fontes': fontes, 'claims': claims, 'assets': assets, 'linhas': L, 'outro': outro(3, 'UMA CONSPIRAÇÃO QUE O FBI RECONHECE'),
            'listas': {'ep03': [['Car Bomb', 'C', 'Ass.', 'Dan / Derek'], ['Hit and Run', 'C', 'Ass.', 'Gary / Derek'], ['Poison', 'C', 'Ass.', 'Shea / Derek'],
                                ['Sniper', 'U', 'Ass.', 'Dan / Rick', 1], ['Withering Curse', 'R', 'Ass.', 'Shea / Jeff']]},
            'legenda_post': 'Depois do atentado de 13/07/2024 em Butler, a carta "Enough is Enough" (Assassins, 1996) virou "prova" de que alguém sabia. O Arquivista leu a carta: a regra fala em "faxina" na própria estrutura de poder, e o rosto não é identificado. O jogo de 1995 já tinha 5 cartas de assassinato.\n\nFontes: FBI (Butler Investigation Updates) · lista oficial INWO (1995) · lista oficial de Assassins (1996).\nPersonagem fictício, voz sintética.\n\n#ArquivoOculto #INWO #Illuminati #misterio #checagem'}


EPISODIOS = {'AO-S01-E06': ep06, 'AO-S01-E04': ep04, 'AO-S01-E05': ep05, 'AO-S01-E03': ep03}

if __name__ == '__main__':
    import sys
    for eid, fn in EPISODIOS.items():
        if len(sys.argv) > 1 and eid not in sys.argv[1:]:
            continue
        m = fn()
        p = os.path.join(AQUI, f'{eid}.v2.json')
        json.dump(m, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(eid, sum(len(l['shots']) for l in m['linhas']) + 1, 'planos ->', p)
