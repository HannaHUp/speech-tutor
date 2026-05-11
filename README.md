# Hermes Speech Tutor - Project Overview

## What This Is

Hermes Speech Tutor is an intentionally scoped **Phase 1 prototype** for a browser-based English speaking tutor.

It proves a local voice loop:

`browser mic -> speech-to-text -> LLM response -> text-to-speech -> playback`

This is not a production-ready tutor. It is a vertical slice built to show how I would validate the hardest core workflow first, then evolve it toward a production foundation.
![alt text](image.png)
## What The Prototype Proves

- A learner can speak in the browser and hear a spoken tutor response.
- The learner can edit the transcript before the LLM sees it.
- STT, LLM, TTS, and pronunciation analysis are separated behind provider interfaces.
- The backend has an explicit WebSocket turn flow instead of a black-box request/response.
- Prompt construction has a stable session boundary and typed user-turn context.
- The app has early latency/debug hooks for inspecting what happened during a turn.
- The code is structured so later persistence, learner profiles, correction policy, and evals have clear attachment points.

## What This Is Not

- Not production-ready.
- No durable learner/session database yet.
- No full Iris tutor persona yet.
- No CEFR-aware correction policy yet.
- No session modes such as role-play or topic talk yet.
- No real-user validation yet.
- No claim of pedagogical effectiveness yet.

Those are intentional deferrals. Phase 1 is about proving the speech loop and architecture before layering on tutoring behavior.

## Production Thinking Demonstrated

The repo is meant to show engineering judgment more than feature breadth.

- **Provider abstraction:** STT, TTS, LLM, and pronunciation are not hard-coded into one vendor path.
- **Explicit turn model:** the app tracks turn start, audio capture, transcript readiness, edited submission, LLM streaming, TTS chunks, and completion.
- **Prompt/context seam:** `UserTurnContext` keeps edited text, raw STT, input source, and prosody together before rendering the LLM message.
- **Frozen session prompt:** the system prompt is captured per session, which supports later prompt versioning, caching, and debugging.
- **Observability hooks:** latency logs and optional turn-debug JSONL logs make speech-loop behavior inspectable.
- **Honest roadmap:** production gaps are documented instead of hidden behind prototype success.

## If I Continued This Toward Production

1. Add SQLite-backed learner, session, utterance, correction, and summary persistence.
2. Version prompt components and add a real tutor policy for correction behavior.
3. Build evals for false-positive corrections, STT normalization, latency, role-play adherence, and tutor tone.
4. Add privacy, retention, and consent rules before storing learner data.
5. Dogfood with real L2 learners before claiming tutor quality.

## Suggested Review Path

For a quick review, this file is the intended starting point.

If you want more detail:

- `ARCHITECTURE.md` explains the current system structure.
- `PRODUCTION_GAP_ANALYSIS.md` lists the biggest gaps between this prototype and a production foundation.
- `PROMPT_ARCHITECTURE.md` explains the prompt/context strategy.
- `MEMORY_AND_STATE_STRATEGY.md` outlines how learner/session state should evolve.
- `EVAL_STRATEGY.md` describes what should be measured before calling this a real tutor.

## Summary

This repo should be read as an MVP-to-production thinking exercise:

- the speech loop is real
- the architecture has useful seams
- the production gaps are explicit
- the next steps are concrete

It is not a finished tutoring product. It is a Phase 1 foundation designed to make the next production decisions easier and more honest.
