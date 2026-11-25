import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).parent
r = [json.loads(l) for l in (BASE / "brutos.jsonl").read_text(encoding="utf-8").splitlines()]

FORA = ["lyric", "official", "clipe", "music", "ft.", "feat", "reformei", "minecraft", "free fire", "roblox",
        "gta", "novela", "trailer", "react", "podcast ao vivo", "live"]
vistos = {}
for x in r:
    if not x.get("views") or not x.get("id"):
        continue
    t = (x.get("titulo") or "").lower()
    if any(k in t for k in FORA):
        continue
    if x["id"] in vistos:
        continue
    vistos[x["id"]] = x

lista = sorted(vistos.values(), key=lambda x: -x["views"])
top = lista[:80]
for i, x in enumerate(top, 1):
    d = x.get("duracao") or 0
    print(f"{i:02d} {x['views']:>11,} {int(d)//60:>3}m {x['canal'][:22]:<22} | {x['titulo'][:95]}")
(BASE / "top80.json").write_text(json.dumps(top, ensure_ascii=False, indent=1), encoding="utf-8")
