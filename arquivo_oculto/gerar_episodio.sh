#!/usr/bin/env bash
# Um comando para gerar um episódio: ./gerar_episodio.sh AO-S01-E01
set -euo pipefail
cd "$(dirname "$0")"
ID="$1"
PROD="producao/$ID.prod.json"
MAN=$(python3 -c "import json;print('examples/'+json.load(open('$PROD'))['manifesto_origem'].split('/')[-1])")
python3 fabrica.py "$MAN" "$PROD" "saida/$ID"
echo "Arquivos em saida/$ID/"
