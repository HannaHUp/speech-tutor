# Hermes Speech Tutor

Hermes Speech Tutor is an intentionally scoped **Phase 1 prototype** for a browser-based English speaking tutor.

It proves a local voice loop:

`browser mic -> speech-to-text -> LLM response -> text-to-speech -> playback`

This is not a production-ready tutor. It is a vertical slice built to show how I would validate the hardest core workflow first, then evolve it toward a production foundation.




## Requirements

- Python 3.11
- Node.js 18+ with `npm`
- `uv`
- `ffmpeg` on `PATH`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` only if `LLM_IMPL=anthropic`

## Provider Modes

This app is a pipelined voice loop, not a single realtime multimodal session:

- browser records audio
- STT transcribes the audio
- LLM generates the tutor reply text
- TTS synthesizes reply audio

By default, the backend uses the paid OpenAI-backed stack:

- `STT_IMPL=openai`
- `TTS_IMPL=openai`
- `LLM_IMPL=openai`

That means one spoken turn can incur three separate OpenAI-backed operations:

- speech-to-text
- text generation
- text-to-speech

## Paid Stack vs Free Dev Stack

The default `openai` providers are the paid stack in this repo:

- STT uses OpenAI transcription
- TTS uses OpenAI speech synthesis
- LLM uses OpenAI chat generation

For lower-cost local development, you can switch only STT and TTS in `.env`:

```text
STT_IMPL=faster_whisper
TTS_IMPL=edge
```

What that changes:

- `faster_whisper` runs speech-to-text locally on your machine
- `edge-tts` uses Microsoft Edge TTS voices instead of OpenAI TTS
- `LLM_IMPL` remains `openai` unless you explicitly change it

So with the free dev stack:

- STT: no OpenAI billing
- TTS: no OpenAI billing
- LLM: still billed if `LLM_IMPL=openai`

"Free" here means not billed by OpenAI. It does not mean zero cost in every sense:

- `faster-whisper` uses your local CPU/RAM and may download model weights on first run
- `edge-tts` avoids OpenAI billing, but it is still a separate service path with its own behavior and availability

## Provider Details

OpenAI STT:

- The browser sends one recorded `audio/webm` blob to the backend.
- The OpenAI STT provider wraps those bytes in an in-memory file and calls `client.audio.transcriptions.create(...)`.
- The current model is `gpt-4o-mini-transcribe`.

OpenAI TTS:

- The assistant reply text is split into sentence-sized chunks.
- Each chunk is sent to `client.audio.speech.create(...)`.
- The current TTS model is `tts-1`.

Local/dev alternatives:

- `faster-whisper` loads a local Whisper model and transcribes audio on CPU; audio stays on your machine for STT
- `edge-tts` synthesizes speech with the Phase 1 voice `en-US-JennyNeural`; text is handed to the `edge-tts` client, which then streams synthesized audio back. In practice, that is a Microsoft/Edge service path, not local CPU-only TTS like `faster-whisper` is for STT.

Prosody extraction:

- prosody is the "how it was said" layer, such as pace, pitch, hesitations, and stress
- prosody extraction itself runs locally in this repo and is not a separate paid API call
- it uses the recorded audio plus STT word timestamps
- if `STT_IMPL=openai`, those timestamps come from a paid OpenAI transcription call
- if `STT_IMPL=faster_whisper`, both STT and prosody stay local

## Why Edge TTS Can Seem "Free"

This part is easy to misunderstand.

Microsoft's official developer speech product is Azure AI Speech, which is a paid service with limited free-tier allowances. That is the supported API product with pricing, quotas, and service terms.

`edge-tts` is different. It is commonly used as a wrapper around Microsoft Edge's online read-aloud / text-to-speech path and does not require you to provision an Azure Speech resource or API key.

That is why people often describe it as "free":

- you are not billed through OpenAI
- you are not directly provisioning Azure Speech for this repo's TTS path
- the library can often be used without a separate paid API setup

But the tradeoff is important:

- it is not the same as the official Azure AI Speech API
- it likely does not provide the same product guarantees, SLAs, or stability expectations
- behavior, availability, quotas, or blocking can change over time
- your text still leaves your machine and is sent to a Microsoft/Edge service path

So for this project, the safest framing is:

- `edge-tts` is useful as a low-cost dev/test TTS option
- it should not be assumed to be a formally supported, permanently free production TTS API

## Start from scratch

1. Clone the repo and open the project folder.
2. Create your local environment file:

```powershell
Copy-Item .env.example .env
```

3. Edit `.env` and set your real keys:

```text
OPENAI_API_KEY=...
```

Optional Anthropic backend:

```text
LLM_IMPL=anthropic
ANTHROPIC_API_KEY=...
```

Optional free/dev STT + TTS swap:

```text
STT_IMPL=faster_whisper
TTS_IMPL=edge
```

Optional structured turn debug log:

```text
DEBUG_TURN_LOG=true
DEBUG_TURN_LOG_PATH=debug/turns.jsonl
DEBUG_TURN_LOG_INCLUDE_SYSTEM_PROMPT=false
```

After changing provider settings in `.env`, restart the Python backend.

4. Install Python dependencies:

```powershell
uv sync
```

5. Install frontend dependencies:

```powershell
cd web
npm ci
```

6. Build the frontend:

```powershell
npm run build
```

7. Start the backend:

```powershell
cd ..
uv run uvicorn server.main:app --host 127.0.0.1 --port 8000
```

8. Open the app in your browser:

```text
http://localhost:8000
```

## Daily dev loop

Use the backend for the actual app:

```powershell
uv run uvicorn server.main:app --host 127.0.0.1 --port 8000
```

Rebuild the frontend after UI changes:

```powershell
cd web
npm run build
```

## Frontend-only dev server

Vite is available for editing the Svelte UI:

```powershell
cd web
npm run dev
```

That server is frontend-only. The app WebSocket connects to `ws://localhost:8000/ws`, so the full voice loop still needs the FastAPI backend running on port 8000.

## Smoke check

After startup, these should work:

- `http://localhost:8000/healthz` returns `{"status":"ok"}`
- The main page loads at `http://localhost:8000`
- The mic button and transcript UI appear
- Use Chrome or Edge and allow microphone access when prompted

## Runtime Logs

The backend prints newline-delimited JSON logs to stdout during each turn. These are mainly for timing and basic verification.

Example:

```json
{"event":"stage_latency","turn_id":3,"stage":"stt","ms":4452,"ts":1778463119.0330718}
{"event":"stage_latency","turn_id":3,"stage":"prosody","ms":0,"ts":1778463119.0344238}
{"event":"stt_divergence","turn_id":3,"edited":false,"stt_len":42,"text_len":42,"ts":1778463120.6095521}
{"event":"stage_latency","turn_id":3,"stage":"llm_ttft","ms":422,"ts":1778463121.0433233}
{"event":"stage_latency","turn_id":3,"stage":"llm_first_sentence","ms":16155,"ts":1778463136.777486}
```

What the fields mean:

- `event`: the kind of log line, such as `stage_latency` or `stt_divergence`
- `turn_id`: the voice-turn number within the current WebSocket session
- `stage`: which pipeline step the timing refers to
- `ms`: elapsed milliseconds for that stage
- `ts`: Unix timestamp when the line was emitted

Current `stage_latency` stages you may see:

- `stt`: speech-to-text transcription finished
- `prosody`: prosody extraction finished
- `llm_ttft`: LLM time-to-first-token
- `llm_first_sentence`: time until the first sentence was ready for TTS
- `tts_first_chunk`: first TTS audio chunk became available

`stt_divergence` explains whether the sent text matched the raw transcript:

- `edited: false` means the user sent the transcript as-is
- `edited: true` means the user changed the text before sending
- `stt_len` and `text_len` are the raw and final character lengths

Important limitation:

- a `stage: "prosody"` log line only proves that prosody extraction ran
- it does not show the actual prosody values such as `pace`, `pitch`, `hesitations`, or `stress`
- those values are currently attached to the LLM input message, but not printed directly in runtime logs

So if you see:

```json
{"event":"stage_latency","turn_id":3,"stage":"prosody","ms":0,"ts":1778463119.0344238}
```

that means the prosody step executed for turn 3, but it does not by itself prove what metadata was extracted.

## Structured Debug Turn Log

For turn-by-turn backend inspection, you can enable an opt-in JSON Lines debug log written by the Python server:

```text
DEBUG_TURN_LOG=true
DEBUG_TURN_LOG_PATH=debug/turns.jsonl
```

Optional:

```text
DEBUG_TURN_LOG_INCLUDE_SYSTEM_PROMPT=true
```

Behavior:

- the file defaults to `debug/turns.jsonl` relative to the repo root
- parent directories are created automatically
- the backend appends one JSON object per line
- existing stdout latency logs stay unchanged

Typical events include:

- `turn_started`
- `transcript_ready`
- `prosody_extracted`
- `llm_input`
- `llm_delta`
- `llm_complete`
- `tts_chunk_meta`
- `turn_done`
- `turn_failed`

Typical fields include:

- `event`, `turn_id`, `ts`
- `stt_text`
- `edited_text`
- `prosody`
- `llm_user_message`
- `llm_messages`
- `delta`
- `assistant_text`
- `tts_chunk_count`
- `error`

If `DEBUG_TURN_LOG_INCLUDE_SYSTEM_PROMPT=true`, `llm_input` records also include `llm_system_prompt`.

Sensitive content warning:

- this log may contain raw transcripts, edited user text, prosody metadata, full LLM user-message content, message history, and final assistant output
- do not enable it in environments where logging that content would be inappropriate

## Troubleshooting

- If startup fails with an ffmpeg error, install it and reopen the shell:

```powershell
winget install Gyan.FFmpeg
```

- Use `http://localhost:8000`, not `http://127.0.0.1:8000` or a LAN IP, for the browser mic flow.
- If the page loads but the voice loop does not connect, make sure the backend is running and `web/dist` exists because FastAPI serves the built frontend.

