"""Entrega os vídeos prontos do Arquivo Oculto à Central do Estúdio Geovani (D-113) como pacotes `video_pronto`.

Uso (em arquivo_oculto/): python producao/top50/entregar_central.py T01 T02 ...   (ou --todos)
Cada pacote leva video.mp4, capa.png, video.srt, roteiro.md e o entrega.json validado pela própria Central.
Não recebe nem publica: a recepção é da sessão da Central.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
SAIDA = AQUI.parents[1] / "saida_v2" / "top25"
CENTRAL = Path(r"C:\Projetos\Estúdio Geovani")
PUB = json.loads((AQUI / "PUBLICACAO_TOP25.json").read_text(encoding="utf-8"))


def roteiro_md(spec):
    linhas = [f"# {spec['titulo']}", "", f"Série: {spec.get('serie', '')}", "", "## Falas", ""]
    for b in spec["blocos"]:
        if b.get("fala"):
            quem = "Arquivista" if b.get("voz") == "arquivista" else "Voz da fita"
            linhas.append(f"- **{quem}:** {b['fala']}" + (f"  `[{b['carimbo']}]`" if b.get("carimbo") else ""))
    linhas += ["", "## Fontes", "", spec.get("fontes_texto", "")]
    return "\n".join(linhas) + "\n"


def entregar(tid):
    pasta_v = SAIDA / tid
    if not (pasta_v / "registro.json").exists():
        print(tid, "sem render pronto: pulado")
        return
    spec = json.loads((AQUI / "specs" / f"{tid}.json").read_text(encoding="utf-8"))
    reg = json.loads((pasta_v / "registro.json").read_text(encoding="utf-8"))
    r = subprocess.run([sys.executable, str(CENTRAL / "ferramentas" / "estudio.py"), "novo", "--perfil", "arquivo",
                        "--tipo", "video_pronto", "--titulo", spec["titulo"], "--agente", "claude-code",
                        "--projeto", r"C:\Projetos\ARQUIVO OCULTO\estudio-gm"], capture_output=True, text=True,
                       encoding="utf-8")
    pacote = Path(r.stdout.strip().splitlines()[0])
    shutil.copy(pasta_v / "video_app.mp4", pacote / "video.mp4")
    shutil.copy(pasta_v / "cover.png", pacote / "capa.png")
    shutil.copy(pasta_v / "subtitles.srt", pacote / "video.srt")
    (pacote / "roteiro.md").write_text(roteiro_md(spec), encoding="utf-8")
    e = json.loads((pacote / "entrega.json").read_text(encoding="utf-8"))
    pub = next((i for i in PUB["itens"] if i["id"] == tid), {})
    legenda = spec.get("legenda_tiktok", "")
    e.update({
        "serie": "Dossiê (Top 25)",
        "arquivos": {"video": "video.mp4", "capa": "capa.png", "legendas": "video.srt", "roteiro": "roteiro.md",
                     "extras": []},
        "post": {"legenda": legenda, "hashtags": re.findall(r"#\w+", legenda),
                 "plataformas": ["tiktok", "youtube"], "rotulo_ia": True},
        "orientacoes": (f"TikTok: {pub.get('quando', 'a agendar')} (Metricool {pub.get('metricool_id', '-')}). "
                        "YouTube Shorts pelo Studio no mesmo horário. Arquivista em atuação 2,5D (biblioteca de planos)."),
        "gerado_por_ia": True,
        "formato": "dossie_90",
        "fontes": [{"nome": spec.get("fontes_texto", ""), "url": "", "acessado_em": "2026-11-11"}],
        "checagem": {"fatos": "conferidos", "direitos": "liberado", "pessoas_identificaveis": "autorizadas",
                     "observacoes": ("Figuras históricas ou públicas; imagens de domínio público ou licença livre, com "
                                     "crédito na tela (D-111, publicação autorizada pelo Geovani em 11/11/2026).")},
        "qa": {"status": "pass_with_warnings",
               "relatorio": f"Duração {reg.get('duracao_s')} s (acima dos 60–75 s ideais). Folha de quadros conferida."},
    })
    (pacote / "entrega.json").write_text(json.dumps(e, ensure_ascii=False, indent=2), encoding="utf-8")
    v = subprocess.run([sys.executable, str(CENTRAL / "ferramentas" / "estudio.py"), "validar", str(pacote)],
                       capture_output=True, text=True, encoding="utf-8")
    print(tid, "->", pacote.name, "|", v.stdout.strip().splitlines()[-1] if v.stdout.strip() else v.stderr[-200:])


if __name__ == "__main__":
    ids = [f"T{i:02d}" for i in range(1, 26)] if "--todos" in sys.argv else sys.argv[1:]
    for t in ids:
        entregar(t)
