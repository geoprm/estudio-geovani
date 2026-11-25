"""Busca imagens livres no Wikimedia Commons por tema e salva com crédito/licença.

Uso: python commons.py <lote.json> <pasta_destino>
lote.json: {"T01": ["consulta 1", "File:Nome exato.jpg", ...], ...}
Saída: <pasta>/<Tid>/NN_<slug>.jpg + <pasta>/<Tid>/fontes.json + contato.jpg (folha de contato)
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "ArquivoResearchBot/1.0 (educational video research)"}
LIVRE = re.compile(r"public domain|^pd|cc0|cc by|cc-by|attribution|no restrictions|gfdl", re.I)


def get(params, tent=5):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json", "formatversion": 2})
    for i in range(tent):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return json.load(r)
        except Exception as e:  # 429/timeout: espera e tenta de novo
            time.sleep(4 * (i + 1))
            err = e
    raise err


def baixar(url, destino, tent=5):
    for i in range(tent):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                destino.write_bytes(r.read())
            return True
        except Exception:
            time.sleep(5 * (i + 1))
    return False


def info(titulos):
    j = get({"action": "query", "titles": "|".join(titulos), "prop": "imageinfo",
             "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1280})
    out = []
    for p in j["query"]["pages"]:
        ii = (p.get("imageinfo") or [None])[0]
        if not ii:
            continue
        md = ii.get("extmetadata", {})
        lic = re.sub("<[^>]+>", "", md.get("LicenseShortName", {}).get("value", ""))
        art = re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip()[:80]
        data = re.sub("<[^>]+>", "", md.get("DateTimeOriginal", {}).get("value", "")).strip()[:40]
        desc = re.sub("<[^>]+>", "", md.get("ImageDescription", {}).get("value", "")).strip()[:160]
        out.append({"titulo": p["title"], "mime": ii["mime"], "w": ii.get("width"), "h": ii.get("height"),
                    "thumb": ii.get("thumburl") or ii["url"], "pagina": ii.get("descriptionurl"),
                    "licenca": lic, "autor": art, "data": data, "descricao": desc})
    return out


def buscar(q, n=6):
    j = get({"action": "query", "list": "search", "srsearch": q, "srnamespace": 6, "srlimit": n})
    return [s["title"] for s in j["query"]["search"]]


def main():
    lote = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    raiz = Path(sys.argv[2])
    for tid, consultas in lote.items():
        pasta = raiz / tid
        pasta.mkdir(parents=True, exist_ok=True)
        titulos = []
        for q in consultas:
            novos = [q] if q.startswith("File:") else buscar(q)
            titulos += [t for t in novos if t not in titulos]
            time.sleep(1)
        cands = []
        for i in range(0, len(titulos), 20):
            cands += info(titulos[i:i + 20])
            time.sleep(1)
        ok = [c for c in cands if c["mime"] in ("image/jpeg", "image/png", "image/svg+xml", "image/tiff")
              and LIVRE.search(c["licenca"] or "") and (c["w"] or 0) >= 500]
        fontes = []
        for k, c in enumerate(ok[:10], 1):
            slug = re.sub(r"[^a-z0-9]+", "_", c["titulo"][5:].lower())[:40].strip("_")
            dest = pasta / f"{k:02d}_{slug}.jpg"
            if not dest.exists():
                if not baixar(c["thumb"], dest):
                    continue
                try:
                    im = Image.open(dest).convert("RGB")
                    im.save(dest, quality=92)
                except Exception:
                    dest.unlink(missing_ok=True)
                    continue
            fontes.append({**c, "arquivo": dest.name})
            time.sleep(1)
        (pasta / "fontes.json").write_text(json.dumps(fontes, ensure_ascii=False, indent=1), encoding="utf-8")
        # folha de contato
        tw, th = 300, 300
        cols = 5
        rows = max(1, (len(fontes) + cols - 1) // cols)
        folha = Image.new("RGB", (cols * tw, rows * (th + 24)), (20, 20, 20))
        d = ImageDraw.Draw(folha)
        for k, f in enumerate(fontes):
            im = Image.open(pasta / f["arquivo"]).convert("RGB")
            im.thumbnail((tw - 8, th - 8))
            x, y = (k % cols) * tw, (k // cols) * (th + 24)
            folha.paste(im, (x + 4, y + 4))
            d.text((x + 6, y + th + 4), f["arquivo"][:44], fill=(230, 200, 120))
        folha.save(pasta / "contato.jpg", quality=80)
        print(tid, len(cands), "candidatos,", len(fontes), "baixadas")


if __name__ == "__main__":
    main()
