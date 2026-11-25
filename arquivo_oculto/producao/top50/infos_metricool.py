"""Gera o `info` do Metricool (TikTok) para os Dossiês, a partir das specs e das mídias hospedadas.

Uso: python infos_metricool.py midias.json   (midias.json = {"T13": "<url cloudfront>", ...})
Imprime uma linha por vídeo: Txx | data ISO | info JSON compacto. Grade: T13 20/11 10:30, depois 18:30 e 10:30 alternados.
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent


def grade(tid):
    n = int(tid[1:]) - 13  # T13 = 20/11 10:30
    dia = datetime(2026, 11, 20) + timedelta(days=n // 2)
    return dia.replace(hour=10 if n % 2 == 0 else 18, minute=30)


def info(tid, url):
    spec = json.loads((AQUI / "specs" / f"{tid}.json").read_text(encoding="utf-8"))
    quando = grade(tid)
    titulo = (spec.get("gancho") or spec["titulo"])[:90]
    return quando, {
        "autoPublish": True, "descendants": [], "draft": False, "firstCommentText": "", "hasNotReadNotes": False,
        "media": [url], "mediaAltText": [], "videoCoverMilliseconds": 1200, "providers": [{"network": "tiktok"}],
        "publicationDate": {"dateTime": quando.strftime("%Y-%m-%dT%H:%M:%S"), "timezone": "America/Bahia"},
        "shortener": False, "smartLinkData": {"ids": []}, "text": spec["legenda_tiktok"],
        "tiktokData": {"disableComment": False, "disableDuet": False, "disableStitch": False,
                       "privacyOption": "PUBLIC_TO_EVERYONE", "commercialContentThirdParty": False,
                       "commercialContentOwnBrand": False, "title": titulo, "autoAddMusic": False,
                       "photoCoverIndex": 0, "isAigc": True}}


if __name__ == "__main__":
    midias = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for tid, url in midias.items():
        quando, inf = info(tid, url)
        print(tid, "|", quando.strftime("%Y-%m-%dT%H:%M:%S-03:00"), "|", json.dumps(inf, ensure_ascii=False))
