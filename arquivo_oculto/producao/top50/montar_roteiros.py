"""Monta os roteiros do reel_leve para as versões Top 25 a partir de especificações compactas.

Cada especificação (producao/top50/specs/Txx.json) usa imagens por índice: "img": "03" pega
acervo_privado/top25/Txx/03_*.jpg, e o crédito da tela vem do fontes.json (autor, licença, Wikimedia Commons),
a menos que o bloco traga "credito" próprio. Gera producao/top50/roteiros/Txx.roteiro.json.

Uso (em arquivo_oculto/): python producao/top50/montar_roteiros.py T01 T02 ...
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
ACERVO = AQUI.parents[1] / "acervo_privado" / "top25"
SAIDA = AQUI / "roteiros"


def credito(f):
    autor = re.sub(r"\s+", " ", f.get("autor") or "").strip()
    autor = re.sub(r"(?i)^(unknown|desconhecido)( author)?$", "autor desconhecido", autor) or "autor desconhecido"
    if re.search(r"[^\x00-ɏ]", autor):  # alfabeto que a fonte da tela não desenha (cirílico etc.)
        autor = "autor indicado na página do arquivo"
    lic = (f.get("licenca") or "").replace("Public domain", "domínio público")
    return f"Imagem: {autor[:48]} · {lic} · Wikimedia Commons"


def montar(tid):
    spec = json.loads((AQUI / "specs" / f"{tid}.json").read_text(encoding="utf-8"))
    # ajustes por bloco escolhidos depois de ver a folha de contato: {"Txx": {"3": {"img": "07", "visual": {...}}}}
    mapas = AQUI / "specs" / "mapas.json"
    ajustes = json.loads(mapas.read_text(encoding="utf-8")).get(tid, {}) if mapas.exists() else {}
    for i, aj in ajustes.items():
        b = spec["blocos"][int(i)]
        for k, val in aj.items():
            if k == "visual":
                b["visual"] = val if val.get("tipo") in ("cartao", "placar", "preto", "retrato") else {**b.get("visual", {}), **val}
            elif k == "remover":
                for r in val:
                    b.pop(r, None)
            else:
                b[k] = val
    pasta = ACERVO / tid
    fontes = {f["arquivo"][:2]: f for f in json.loads((pasta / "fontes.json").read_text(encoding="utf-8"))}
    blocos = []
    for b in spec["blocos"]:
        b = dict(b)
        v = dict(b.get("visual", {}))
        for chave in ("img", "a", "b"):
            if chave in b or chave in v:
                idx = b.pop(chave, None) or v.pop(chave)
                f = fontes[idx]
                destino = "arquivo" if chave == "img" else chave
                v[destino] = str(pasta / f["arquivo"])
                if chave == "img" and v.get("tipo") is None:
                    v["tipo"] = "imagem"
                if "credito" not in b:
                    b["credito"] = credito(f)
        b["visual"] = v
        blocos.append(b)
    # direção de 12/11/2026 (Geovani, via Central): o vídeo termina em aberto, com a pulga atrás da orelha.
    # O placar não "julga" mais no fim, e nenhuma tela fica preta só com legenda: entra a última imagem ao fundo.
    ultima = None
    for b in blocos:
        v = b["visual"]
        if v.get("tipo") == "placar":
            v["titulo"] = "O ARQUIVO CONTINUA ABERTO"
        elif v.get("tipo") == "imagem":
            ultima = (v, b.get("credito"))
        elif v.get("tipo") == "preto" and b.get("voz") and ultima:
            b["visual"] = {"tipo": "imagem", "arquivo": ultima[0]["arquivo"], "modo": "cover", "mov": "out"}
            if ultima[1] and "credito" not in b:
                b["credito"] = ultima[1]
    rot = {"id": f"TOP-{tid}", "num": int(tid[1:]), "serie": spec.get("serie", "ARQUIVO OCULTO · TOP"),
           "selo_fixo": spec.get("selo_fixo"), "blocos": blocos,
           "meta": {k: spec[k] for k in ("titulo", "gancho", "fontes_texto", "legenda_tiktok") if k in spec}}
    SAIDA.mkdir(exist_ok=True)
    (SAIDA / f"{tid}.roteiro.json").write_text(json.dumps(rot, ensure_ascii=False, indent=1), encoding="utf-8")
    abertura = next(b["fala"] for b in blocos if b.get("voz") == "arquivista")
    assert abertura.startswith("Olá, criancinhas") and "Hoje" in abertura, f"{tid}: abertura fora da regra"
    print(tid, len(blocos), "blocos ->", SAIDA / f"{tid}.roteiro.json")


if __name__ == "__main__":
    for t in sys.argv[1:]:
        montar(t)
