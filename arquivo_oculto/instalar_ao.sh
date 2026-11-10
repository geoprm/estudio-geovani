#!/usr/bin/env bash
# Prepara o Arquivo Oculto (uma vez por máquina). Tudo gratuito e de fontes oficiais (PyPI + releases do GitHub).
set -euo pipefail
cd "$(dirname "$0")"
pip install --break-system-packages -q kokoro-onnx soundfile opencv-python-headless onnxruntime numpy pillow pymupdf 2>/dev/null \
  || pip install -q kokoro-onnx soundfile opencv-python-headless onnxruntime numpy pillow pymupdf
mkdir -p tts modelos
[ -f tts/kokoro-v1.0.int8.onnx ] || curl -sSfL -o tts/kokoro-v1.0.int8.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
[ -f tts/voices-v1.0.bin ] || curl -sSfL -o tts/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
if [ "${1:-}" = "--filtro" ]; then   # só para o Arquivista no rosto
  pip install --break-system-packages -q insightface 2>/dev/null || pip install -q insightface
  [ -f modelos/u2net_human_seg.onnx ] || curl -sSfL -o modelos/u2net_human_seg.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx
  mkdir -p ~/.insightface/models
  [ -d ~/.insightface/models/buffalo_s ] || { curl -sSfL -o /tmp/buffalo_s.zip https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_s.zip && unzip -o -q /tmp/buffalo_s.zip -d ~/.insightface/models/buffalo_s; }
fi
echo "Arquivo Oculto pronto."
