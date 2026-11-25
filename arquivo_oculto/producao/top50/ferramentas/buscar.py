"""Levanta vídeos de maior alcance do nicho (conspiração/mistério/terror real em PT-BR) via yt-dlp.

Só metadados (título, canal, views, duração, url). Sem download de mídia.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

YTDLP = r"C:\Projetos\ARQUIVO OCULTO\estudio-gm\.venv\Scripts\yt-dlp.exe"
OUT = Path(__file__).with_name("brutos.jsonl")

CONSULTAS = [
    "teoria da conspiração documentário",
    "mistérios não resolvidos",
    "documentos secretos desclassificados",
    "illuminati verdade",
    "casos sinistros reais",
    "projeto secreto CIA",
    "o que esconderam de você",
    "história real assustadora",
    "maior mistério do brasil",
    "ninguém sabe explicar",
    "arquivos secretos governo",
    "teoria da conspiração shorts",
    "mistério shorts",
    "curiosidades sombrias",
    "casos paranormais reais brasil",
    "sociedades secretas",
    "maçonaria segredos",
    "profecias que se cumpriram",
    "experimentos secretos",
    "desaparecimentos misteriosos",
]


def buscar(q: str, n: int = 40) -> list[dict]:
    cmd = [YTDLP, f"ytsearch{n}:{q}", "--flat-playlist", "--dump-json",
           "--extractor-args", "youtube:lang=pt", "--no-warnings", "--quiet"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=180)
    itens = []
    for linha in r.stdout.splitlines():
        try:
            j = json.loads(linha)
        except json.JSONDecodeError:
            continue
        itens.append({
            "consulta": q,
            "id": j.get("id"),
            "titulo": j.get("title"),
            "canal": j.get("channel") or j.get("uploader"),
            "views": j.get("view_count"),
            "duracao": j.get("duration"),
            "url": j.get("url") or f"https://www.youtube.com/watch?v={j.get('id')}",
        })
    return itens


def main() -> None:
    feitas = set()
    if OUT.exists():
        for l in OUT.read_text(encoding="utf-8").splitlines():
            feitas.add(json.loads(l)["consulta"])
    with OUT.open("a", encoding="utf-8") as f:
        for q in CONSULTAS:
            if q in feitas:
                continue
            try:
                itens = buscar(q)
            except subprocess.TimeoutExpired:
                print("timeout", q, file=sys.stderr)
                continue
            for it in itens:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
            f.flush()
            print(q, len(itens))
            time.sleep(2)


if __name__ == "__main__":
    main()
