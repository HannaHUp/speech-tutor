# Hermes Speech Tutor - Architecture

## Goal

Phase 1 exists to prove a practical speech-tutor pipeline on localhost:

`browser mic -> STT -> LLM -> TTS -> playback`

The architecture is organized so that the core loop works today while leaving clear extension points for later tutoring features such as learner profiles, correction policies, and persistence.

## System Flow

1. The browser captures microphone audio and sends it to the backend over a WebSocket connection.
2. The backend buffers audio for the active turn.
3. When the user stops speaking, the backend runs speech-to-text.
4. The transcript is returned to the UI and can be edited before submission.
5. The backend appends the final user text to the session state.
6. The LLM streams a tutor response.
7. The response is chunked into sentence-level TTS units.
8. The synthesized audio is streamed back to the browser for playback.

This gives the learner a controllable turn flow instead of a black-box "send audio, get magic" interaction.

## Main Components

### Frontend

The frontend is a Svelte app responsible for:

- microphone capture
- push-to-talk interaction
- transcript display and editing
- audio playback
- turn-level WebSocket messaging

The UI is intentionally minimal in Phase 1. Its job is to expose the conversation loop clearly and reliably.

### Backend

The backend is a FastAPI application that owns:

- application startup and config validation
- provider initialization
- WebSocket turn orchestration
- session state
- observability hooks
- error handling

The key orchestration logic lives in the WebSocket handler and session pipeline rather than being scattered across the UI.

## Provider Abstractions

One of the main design choices in this repo is explicit provider interfaces for STT, TTS, and LLM behavior.

Why that matters:

- it separates product flow from vendor-specific SDK code
- it makes cost/performance tradeoffs easier to test
- it reduces coupling when changing providers later
- it creates cleaner seams for testing

Current provider strategy:

- STT: OpenAI and faster-whisper
- TTS: OpenAI and edge-tts
- LLM: OpenAI by default, Anthropic as an alternate path

This is useful for a product team because it keeps "which vendor do we use?" from being baked into the entire application structure.

## Turn Model

The turn model is intentionally explicit:

- `turn.start`
- audio frames
- `turn.stop`
- transcript ready
- `turn.send`
- streamed LLM deltas
- streamed TTS chunks
- `turn.done`

That structure helps with:

- debugging
- latency instrumentation
- cancellation behavior
- later persistence of session events

It is more operationally useful than a single opaque request/response cycle.

## Observability And Debugging

Phase 1 includes early observability because speech systems are difficult to reason about without instrumentation.

Current hooks include:

- stage latency logging
- divergence logging between raw STT text and edited user text
- optional turn-level JSONL debug logs

This supports questions such as:

- where time is being spent
- whether STT output is being edited frequently
- what the LLM actually received
- what assistant output was produced on a given turn

Those capabilities are especially important when moving from prototype behavior to production reliability.

## Prosody And Tutor-Specific Scaffolding

The repo also includes early tutor-oriented scaffolding rather than postponing it entirely:

- prosody extraction
- pronunciation provider protocol
- tutor/session prompt construction

Even though Phase 1 does not yet implement the richer pedagogy planned for later phases, these seams make it easier to add:

- level-aware feedback
- pronunciation analysis
- mode-specific prompts
- learner personalization

## Production-Minded Decisions Already Present

Even as a prototype, the repo already reflects several production-oriented choices:

- config validation at startup
- explicit ffmpeg dependency checks
- backend/provider separation
- structured protocols instead of ad hoc vendor calls everywhere
- tests around critical behavior
- ignored local secret and debug paths

These choices matter because many AI demos work only as long as the original builder is nearby. This project is structured to reduce that fragility.

## What Is Not Built Yet

Phase 1 intentionally stops before adding:

- persistent learner/session storage
- CEFR onboarding
- tutor correction policy
- persona-rich conversation modes
- multi-learner isolation
- summaries and progress tracking

Those are roadmap items, not architectural omissions. The current codebase is the substrate those features would attach to.

## Phase 2 Direction

The next major step is to turn the pipeline into a more opinionated tutor:

- add a stable tutor persona
- enforce correction behavior
- support session modes
- persist learner and session data

That transition is meaningful because the repo would move from "working speech agent" to "working speech tutor."

## Summary

The architecture is intentionally layered around one principle: prove the speech loop first, then add tutoring intelligence and persistence on top of a working system.

That is why the current prototype is useful. It is not just a UI mock or prompt experiment. It is an engineering slice designed to support later product growth.
