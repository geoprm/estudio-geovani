// Transcrição palavra a palavra com Whisper small (roda local, sem internet depois de instalado).
// Uso: node transcribe.mjs audio16k.f32 saida.json word
import { pipeline, env } from '@huggingface/transformers';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const aqui = path.dirname(fileURLToPath(import.meta.url));
env.allowRemoteModels = false;
env.localModelPath = process.env.WHISPER_DIR || path.join(aqui, '..', 'modelos', 'whisper', 'models') + '/';

const [, , rawPath, outPath, mode] = process.argv;
const buf = fs.readFileSync(rawPath);
const audio = new Float32Array(buf.buffer, buf.byteOffset, buf.byteLength / 4);
const asr = await pipeline('automatic-speech-recognition', 'Xenova/whisper-small', { dtype: 'q8' });
const t0 = Date.now();
const out = await asr(audio, {
  language: 'portuguese', task: 'transcribe', chunk_length_s: 30, stride_length_s: 5,
  return_timestamps: mode === 'word' ? 'word' : true,
});
fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
console.log(`ok em ${((Date.now() - t0) / 1000).toFixed(1)}s`);
