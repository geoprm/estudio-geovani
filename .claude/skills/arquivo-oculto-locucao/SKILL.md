---
name: arquivo-oculto-locucao
description: Cria e sincroniza locução sintética pt-BR sombria, trilha e efeitos com mixagem clara e consistente.
---

# Skill — Voz sintética, trilha e sound design

## Voz principal
Usar `arquivista-v2-c` em pt-BR, conforme o lock aprovado. Dirigir o grave íntimo pela escrita e pela pausa. Deixar o ambiente recuar quando a evidência aparece e voltar depois que o espectador teve tempo de ler. Medir a fala com a configuração fixa antes de ajustar os cortes. Não clonar vozes sem consentimento nem imitar figura pública.

## Workflow
1. Normalizar nomes, pronúncia e siglas; pontuação deve controlar pausas.
2. Gerar WAV/MP3 de locução e armazenar o arquivo original por episódio, com `provider`, `voice`, `model`, `language`, `output_path`, `duration_ms`.
3. Medir duração REAL via `ffprobe` e realinhar cenas à fala; não cortar frase para bater em 30s.
4. Produzir captions via alinhamento de fala ou ASR revisado, exportar `.srt`/tokens. Evitar quebrar palavra e frases ilegíveis.
5. Criar trilha com licença ou geração autorizada; clima dark ambient, tonalidade menor, pulsos lentos e subida sutil; sem música famosa não licenciada.
6. Efeitos de papel, passos, click de máquina, ruído de fita e clock pontualmente; nunca encobrir a locução.

## Mixagem
Alvo sugerido para mix final -16 LUFS integrado com true peak <= -1 dBTP, ajustar à plataforma e testes. Ducking automático da música ao entrar voz (~12–18 dB de redução conforme audição). Mono-compatibilidade; teste com smartphone e sem fones. Nenhum áudio clipando ou surgindo abrupto.

## QA
Escutar começo, 2 trechos intermediários e final. Verificar voz pt-BR real, sem pronúncias falsas; conferir se cada subtitle corresponde ao áudio, se música licencia e se fecho mantém a assinatura sonora da série.

## V2 — 04/11/2026
- Adapter: `arquivo_oculto/v2/voz.py` (Kokoro ONNX local, Apache-2.0, custo zero). Presets versionados: `arquivista-voz-01` (legado V1), `arquivista-v2-a`, `arquivista-v2-b`, `arquivista-v2-c`.
- **Voz aprovada:** `arquivista-v2-c` (60% pm_alex + 40% pm_santa, velocidade 0,81, tom 0,85, filtro de pente curto, leve saturação, sala curta). F0 ~115 Hz. A aprovação de 04/11/2026 e os parâmetros estão no lock.
- Amostras de 10 s e métricas: `python -m arquivo_oculto.v2.voz amostras <pasta>` gera `comparativo_vozes.mp3` + `amostras_voz.json`.
- A referência sonora do vídeo antigo está AUSENTE: não afirmar semelhança. Não clonar voz sem mecanismo e autorização.
- Cada fala é sintetizada isolada: a duração real vira o `voice_span` da timeline; pausas de 250–650 ms (até 900 ms no fecho) pelo `pausa_ms` da linha.
- Mix V2: voz + trilha sintetizada + efeitos sintetizados; ducking por sidechain (ratio 9); loudnorm -15 LUFS, pico -1,5 dBTP.
