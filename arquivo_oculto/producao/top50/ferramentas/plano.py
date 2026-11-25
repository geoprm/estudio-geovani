"""Gera producao/top50/TOP50_NICHO.json e PLANO_TOP25.md a partir do levantamento curado."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).parent
DEST = Path(r"C:\Projetos\ARQUIVO OCULTO\estudio-gm\arquivo_oculto\producao\top50")
top = json.loads((BASE / "top50_curado.json").read_text(encoding="utf-8"))

# nossas 25 versões: (id, título-gancho, tema, trecho do título de referência, ângulo e carimbo final)
VERSOES = [
    ("T01", "Os Illuminati existiram. E acabaram em 1785.", "Illuminati da Baviera", "ILLUMINATI - 15 COISAS",
     "Fundação em 1776 por Adam Weishaupt, proibição por édito de Karl Theodor (1785). O resto é lenda posterior. DOCUMENTADO + SEM PROVA"),
    ("T02", "O olho na nota de 1 dólar não é dos Illuminati", "Grande Selo dos EUA", "ILLUMINATI - SÍMBOLOS",
     "Reverso do Grande Selo desenhado em 1782; o olho entrou na nota em 1935. FALSO para a ligação Illuminati"),
    ("T03", "5 aviões sumiram no Triângulo. O 6º, que foi buscá-los, também.", "Voo 19 (1945)", "Triângulo das Bermudas",
     "Relatório da Marinha dos EUA; o PBM Mariner de resgate explodiu (navio viu chamas). DOCUMENTADO; 'triângulo' = SEM PROVA"),
    ("T04", "Um morto numa praia, um bolso secreto e duas palavras: Tamam Shud", "Homem de Somerton (1948)", "MISTÉRIOS SEM SOLUÇÃO QUE VÃO",
     "Pedaço do Rubaiyat no bolso, código no livro, identificação por DNA em 2022 (Carl Webb). Código segue sem solução"),
    ("T05", "9 mortos na neve, barraca cortada por dentro", "Passo Dyatlov (1959)", "27 MISTÉRIOS INEXPLICÁVEIS",
     "Estudo de 2021 (Gaume e Puzrin, Communications Earth & Environment): avalanche de placa. Míssil/yeti = SEM PROVA"),
    ("T06", "72 segundos que vieram do espaço: o sinal Wow!", "Sinal Wow! (1977)", "35 MISTÉRIOS que a CIÊNCIA",
     "Big Ear, Ohio, 15/08/1977, Jerry Ehman anota 'Wow!'. Nunca se repetiu. Hipótese do hidrogênio (2024) = INTERPRETAÇÃO"),
    ("T07", "Quem construiu as pirâmides deixou um diário", "Diário de Merer", "Quem construiu as pirâmides",
     "Papiros de Wadi al-Jarf (2013): equipe que levava calcário de Tura a Gizé. Tumbas dos trabalhadores. Alienígenas = SEM PROVA"),
    ("T08", "O Pentágono publicou os vídeos. E não explicou.", "UAP / vídeos da Marinha", "Tudo o que sabemos sobre OVNIs",
     "FLIR, Gimbal e GoFast liberados oficialmente em 27/04/2020; relatório de 2021 com 144 casos. 'Alienígena' = SEM PROVA"),
    ("T09", "Ele ia revelar os segredos da Maçonaria. Sumiu.", "Caso William Morgan (1826)", "6 SEGREDOS revelados da Maçonaria",
     "Batávia, NY: Morgan anuncia livro, é sequestrado e nunca mais visto; nasce o Partido Antimaçônico. Destino = SEM PROVA"),
    ("T10", "A maior farsa contra a Maçonaria foi confessada em 1897", "Farsa de Léo Taxil", "A Iniciação Maçônica",
     "Taxil inventou o culto satânico maçônico e confessou em Paris, 19/04/1897. FALSO"),
    ("T11", "Deram aos ratos o paraíso. Eles se destruíram.", "Universo 25 (Calhoun)", "10 EXPERIMENTOS CIENTÍFICOS",
     "John B. Calhoun, NIMH, 1968–1973. Extrapolação para humanos = INTERPRETAÇÃO"),
    ("T12", "Em 2000, um homem disse que veio de 2036", "John Titor", "Os viajantes do tempo",
     "Posts em fóruns (2000–2001), previsões que falharam (guerra civil nos EUA em 2004). FALSO para as previsões"),
    ("T13", "Os tijolos com suástica do interior de São Paulo", "Fazenda Cruzeiro do Sul", "relação do BRASIL com o NAZISMO",
     "Campina do Monte Alegre (SP): tijolos marcados e os 50 meninos levados do Rio nos anos 1930. DOCUMENTADO"),
    ("T14", "A noite em que um mascarado invadiu a TV de Chicago", "Invasão Max Headroom (1987)", "50 Vídeos Que Ninguém Consegue Explicar",
     "22/11/1987, WGN e WTTW. Autores nunca identificados. Reconstituição (sem imagem da transmissão)"),
    ("T15", "A CIA pagou videntes por 20 anos", "Projeto Stargate", "Projeto Stargate",
     "Documentos liberados (CIA Reading Room, 1995/2017); avaliação AIR de 1995 encerrou o programa. DOCUMENTADO; poderes = SEM PROVA"),
    ("T16", "O enigma da internet que recrutava gênios", "Cicada 3301", "Cicada 3301",
     "Quebra-cabeças de 2012, 2013 e 2014; autoria desconhecida. Recrutamento de agência = SEM PROVA"),
    ("T17", "Luzes que queimavam pessoas no Pará", "Operação Prato (1977)", "O ASSUSTADOR CASO BRASILEIRO",
     "FAB investigou em Colares; documentos liberados pelo Arquivo Nacional. Relatos = DOCUMENTADO como relato; origem = SEM PROVA"),
    ("T18", "O governo deixou 399 homens doentes por 40 anos", "Estudo de Tuskegee", "7 Experimentos Más Aterradores",
     "Serviço de Saúde Pública dos EUA, 1932–1972; denúncia de 1972; pedido de desculpas de Clinton, 1997. DOCUMENTADO"),
    ("T19", "O livro que ninguém consegue ler há 600 anos", "Manuscrito Voynich", "50 Mistérios Inexplicáveis",
     "Pergaminho datado por carbono de 1404–1438 (Universidade do Arizona, 2009); Biblioteca Beinecke. Tradução = SEM PROVA"),
    ("T20", "O exorcismo que terminou num tribunal", "Anneliese Michel (1976)", "Emily Rose",
     "Klingenberg, Alemanha; pais e dois padres condenados por homicídio culposo em 1978. DOCUMENTADO; possessão = SEM PROVA"),
    ("T21", "12.618 relatos de OVNI e uma pasta fechada", "Projeto Livro Azul", "A MAIOR INVESTIGAÇÃO OVNI",
     "Força Aérea dos EUA, 1952–1969; 701 casos sem explicação no relatório final. DOCUMENTADO"),
    ("T22", "A cifra do Zodíaco levou 51 anos para cair", "Z340 decifrado (2020)", "O MASCARADO MAIS ASSUSTADOR",
     "Oranchak, Blake e Van Eycke, dezembro de 2020, confirmado pelo FBI. Identidade do assassino = SEM PROVA"),
    ("T23", "O 'Anjo da Morte' de Auschwitz morreu numa praia de SP", "Mengele em Bertioga (1979)", "OS EXPERIMENTOS DE MENGELE",
     "Afogado em Bertioga em 07/02/1979, enterrado em Embu como Wolfgang Gerhard; exumação de 1985, DNA em 1992. DOCUMENTADO"),
    ("T24", "O pó azul que brilhava no escuro em Goiânia", "Césio-137 (1987)", "ACIDENTE EM GOIÂNIA",
     "Cápsula de radioterapia aberta num ferro-velho; 4 mortes diretas segundo a AIEA. DOCUMENTADO"),
    ("T25", "O memorando da CIA que a ditadura não queria", "Memorando Colby–Kissinger (1974)", "documentos secretos' da ditadura",
     "Memorando de 11/04/1974, liberado em 2018 (FRUS): relato de autorização de execuções. DOCUMENTADO como relato da CIA"),
]

PLANEJADAS = [
    ("P01", "A criança que lembrava de ter morrido num avião", "James Leininger", "COISAS ESTRANHAS que as CRIANÇAS"),
    ("P02", "As fadas fotografadas que enganaram Conan Doyle", "Fadas de Cottingley", "10 FOTOS NORMAIS"),
    ("P03", "A casa de Enfield e a voz do velho", "Poltergeist de Enfield", "VERDADEIRAS HISTÓRIAS SOBRENATURAIS"),
    ("P04", "O coronel que entrou no Mato Grosso atrás de uma cidade e não voltou", "Percy Fawcett / Serra do Roncador", "OS LUGARES MAIS  MISTERIOSOS DO BRASIL"),
    ("P05", "Uma carta psicografada absolveu um réu", "Chico Xavier no tribunal (Goiânia, 1979)", "Histórias ASSUSTADORAS de espíritos"),
    ("P06", "A Ilha da Queimada Grande", "Ilha das cobras (SP)", "Mistérios brasileiros obscuros"),
    ("P07", "Os caixões da FEMA", "Revestimentos de jazigo", "CAIXÕES DA FEMA"),
    ("P08", "Skull and Bones: a tumba de Yale", "Skull and Bones", "As sociedades secretas mais misteriosas"),
    ("P09", "A casa dos Perron", "Família Perron / Warren", "Família Perron"),
    ("P10", "Geoglifos: as cidades que a floresta escondia", "Geoglifos do Acre", "2.124.000 milhas"),
    ("P11", "A teoria da internet morta", "Internet morta", "Teoria da Internet Morta"),
    ("P12", "Amelia Earhart: o último rádio", "Amelia Earhart (1937)", "AMELIA EARHART"),
    ("P13", "Slender Man nasceu num fórum em 2009", "Slender Man", "SLENDER MAN"),
    ("P14", "A Área 51 existe: a CIA admitiu em 2013", "Área 51", "Tudo o que sabemos sobre OVNIs"),
    ("P15", "Roswell: o balão que virou disco", "Roswell / Projeto Mogul", "A MAIOR INVESTIGAÇÃO OVNI"),
    ("P16", "Operação Paperclip: os nazistas que foram para a NASA", "Operação Paperclip", "OS EXPERIMENTOS DE MENGELE"),
    ("P17", "Golfo de Tonkin: o ataque que não aconteceu", "Incidente do Golfo de Tonkin", "30 Maiores TEORIAS"),
    ("P18", "Mary Celeste: o navio sem ninguém", "Mary Celeste (1872)", "Triângulo das Bermudas"),
    ("P19", "Roanoke: uma palavra numa árvore", "Colônia perdida de Roanoke", "MISTÉRIOS SEM SOLUÇÃO QUE VÃO"),
    ("P20", "O Experimento Filadélfia", "USS Eldridge", "Os viajantes do tempo"),
    ("P21", "Unidade 731", "Unidade 731", "Os Piores Experimentos Científicos"),
    ("P22", "O homem-mariposa de Point Pleasant", "Mothman (1966–67)", "As lendas brasileiras mais assustadoras"),
    ("P23", "Arquivo Morto: o corpo-seco", "Folclore: corpo-seco (FICÇÃO)", "Iceberg do Folclore"),
    ("P24", "Arquivo Morto: a Comadre Fulozinha", "Folclore nordestino (FICÇÃO)", "As lendas brasileiras mais assustadoras"),
    ("P25", "O caso dos homens das máscaras de chumbo (Niterói, 1966)", "Máscaras de chumbo", "O ASSUSTADOR CASO BRASILEIRO"),
]


def ref(trecho):
    m = [x for x in top if trecho.lower() in x["titulo"].lower()]
    return max(m, key=lambda x: x["views"]) if m else None


def grade():
    """2 por dia, 10:30 e 18:30, a partir de 14/11/2026."""
    from datetime import date, timedelta
    d0 = date(2026, 11, 14)
    for i in range(25):
        d = d0 + timedelta(days=i // 2)
        yield f"{d.isoformat()} {'10:30' if i % 2 == 0 else '18:30'}"


dados = {"schema": "arquivo-oculto/top50-v1", "levantado_em": "2026-11-11",
         "metodo": "yt-dlp ytsearch40 em 20 consultas do nicho (800 resultados, só metadados); filtro de ruído (música, "
                   "infantil, games, canais de entretenimento sem relação); curadoria manual de 50 vídeos por views. "
                   "Excluídos: acusações a pessoas vivas sem fonte e crimes com vítimas privadas.",
         "top50": [{"pos": i + 1, **{k: x[k] for k in ("titulo", "canal", "views", "duracao", "id")},
                    "url": f"https://www.youtube.com/watch?v={x['id']}"} for i, x in enumerate(top)],
         "versoes": [], "planejadas": []}
for (vid, gancho, tema, trecho, angulo), quando in zip(VERSOES, grade()):
    r = ref(trecho)
    dados["versoes"].append({"id": vid, "gancho": gancho, "tema": tema, "angulo": angulo, "tiktok": quando,
                             "referencia": {"titulo": r["titulo"], "canal": r["canal"], "views": r["views"]} if r else None,
                             "estado": "planejado"})
for vid, gancho, tema, trecho in PLANEJADAS:
    r = ref(trecho)
    dados["planejadas"].append({"id": vid, "gancho": gancho, "tema": tema,
                                "referencia": {"titulo": r["titulo"], "views": r["views"]} if r else None})
DEST.mkdir(parents=True, exist_ok=True)
(DEST / "TOP50_NICHO.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")

md = ["# Top 50 do nicho e as 25 versões do Arquivista", "",
      "Levantamento de 11/11/2026 (YouTube, PT-BR). Fonte completa: [TOP50_NICHO.json](TOP50_NICHO.json).",
      "", "## Método", "", dados["metodo"], "",
      "**Regra das versões:** o tema é o mesmo que deu audiência, mas roteiro, voz e imagens são nossos. Cada versão "
      "abre com \"Olá, criancinhas... Hoje...\" e põe carimbo em cada alegação (DOCUMENTADO, SEM PROVA, INTERPRETAÇÃO, "
      "FALSO). As imagens são reais e de domínio público ou licença livre, com crédito na tela.", "",
      "## Os 50 vídeos de referência", "", "| # | Views | Min | Canal | Título |", "|---|---|---|---|---|"]
for t in dados["top50"]:
    md.append(f"| {t['pos']} | {t['views']:,} | {int(t['duracao'] or 0)//60} | {t['canal']} | [{t['titulo'][:70]}]({t['url']}) |".replace(",", "."))
md += ["", "## As 25 versões (produção, 2 por dia no TikTok)", "",
       "| Id | Quando | Gancho | Tema | Ângulo e carimbo |", "|---|---|---|---|---|"]
for v in dados["versoes"]:
    md.append(f"| {v['id']} | {v['tiktok'][8:10]}/{v['tiktok'][5:7]} {v['tiktok'][11:]} | {v['gancho']} | {v['tema']} | {v['angulo']} |")
md += ["", "## As outras 25 (planejadas)", "", "| Id | Gancho | Tema |", "|---|---|---|"]
for p in dados["planejadas"]:
    md.append(f"| {p['id']} | {p['gancho']} | {p['tema']} |")
md += ["", "Daniel Mastral fica fora desta lista: é a próxima série própria (coordenar com `pesquisa/mastral` do Codex)."]
(DEST / "PLANO_TOP25.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(len(dados["top50"]), len(dados["versoes"]), len(dados["planejadas"]),
      sum(1 for v in dados["versoes"] if v["referencia"] is None), "sem ref")
