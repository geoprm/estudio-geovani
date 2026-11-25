#!/usr/bin/env bash
# Renderiza versões Top 25 em sequência (uma por vez, por causa da memória). Uso: bash fila_render.sh T02 T03 ...
cd "/c/Projetos/ARQUIVO OCULTO/estudio-gm"
PY=.venv/Scripts/python.exe
for t in "$@"; do
  if [ -f "arquivo_oculto/saida_v2/top25/$t/registro.json" ]; then echo "$t JA_EXISTE"; continue; fi
  (cd arquivo_oculto && ../$PY producao/top50/montar_roteiros.py "$t") || { echo "$t ERRO_MONTAGEM"; continue; }
  if $PY -m arquivo_oculto.v2.reel_leve "arquivo_oculto/producao/top50/roteiros/$t.roteiro.json" "arquivo_oculto/saida_v2/top25/$t" > "arquivo_oculto/saida_v2/top25/$t.log" 2>&1; then
    echo "$t PRONTO $(ffprobe -v error -show_entries format=duration -of csv=p=0 arquivo_oculto/saida_v2/top25/$t/video_app.mp4)"
  else
    echo "$t ERRO_RENDER $(tail -2 arquivo_oculto/saida_v2/top25/$t.log | tr '\n' ' ')"
  fi
done
