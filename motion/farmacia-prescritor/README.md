# Motion: Farmácia de manipulação, "prescritor 24/7"

Código-fonte do motion v2 (estilo Apple, identidade Inpullse).

- `apple.html`: cenas e animações (canvas 1080x1920), com `renderAt(t)` determinístico
- `timeline.json`: tempos de cada cena e palavra, gerados pela narração
- `narr_piper.py`: narração com voz feminina pt-BR (modelo aberto `vits-piper-pt_BR-dii-high`, via sherpa-onnx)
- `narr_eleven.py`: alternativa via ElevenLabs (requer `ELEVEN_KEY` no ambiente e o domínio liberado)
- `audio.py`: efeitos sonoros e trilha sintetizados, mais a mixagem com a voz
- `render.mjs`: renderiza os quadros via Playwright e gera o MP4 com ffmpeg

Ordem: narração → `render.mjs video` (com PAGE=apple.html) → `audio.py` → mux com ffmpeg.
