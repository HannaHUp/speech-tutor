# Production Gap Analysis

## Positioning

This repository is a Phase 1 proof of concept, not a production speech tutor. It validates the hard early voice-interaction path:

`browser mic -> STT (OpenAI STT or faster-whisper) -> editable transcript -> LLM -> TTS (OpenAI TTS or edge-tts) -> playback`

The current value is architectural evidence: provider seams, turn orchestration, editable transcripts, latency/debug hooks, and a session prompt boundary. The production work is still ahead.

## What Exists Today

- A localhost FastAPI + Svelte speech loop over WebSocket.
- A traditional STT -> LLM -> TTS voice pipeline.
- Provider protocols for STT, LLM, TTS, and pronunciation analysis.
- Two STT paths planned/implemented behind configuration, depending on local setup.
- Two TTS paths planned/implemented behind configuration, depending on local setup.
- OpenAI LLM default with Anthropic alternate path.
- In-memory session history with a frozen system-prompt snapshot.
- Editable transcript flow before the LLM sees the learner text.
- Prosody metadata attached to voice turns when extraction succeeds.
- Stage latency logging and optional per-turn JSONL debug logging.
- Startup validation for required API keys and ffmpeg availability.

## Highest-Risk Gaps

### 1. No Durable Learner Or Session Model

Current state is per-WebSocket and in memory. A production tutor needs learner identity, session lifecycle, persisted utterances, corrections, summaries, and recoverability after browser/server restarts.

Production direction:

- Add SQLite first, not Postgres, because the roadmap targets 1-3 local learners.
- Store learners, sessions, utterances, corrections, summaries, and provider metadata.
- Write turn rows with explicit statuses such as `ok`, `stt_failed`, `llm_failed`, and `tts_failed`.
- Keep LLM streaming hot path in memory and persist at turn boundaries.

### 2. Tutor Behavior Is Not Yet A Product Policy

The current prompt is intentionally placeholder-level. It does not yet encode correction policy, CEFR adaptation, role-play behavior, praise limits, or "do not invent corrections" constraints.

Production direction:

- Version prompt components as product artifacts.
- Separate stable persona, mode policy, learner state, recent conversation, and turn context.
- Add regression probes for false-positive corrections, tone, refusal behavior, and mode adherence.
- Treat prompt changes like code changes: reviewed, tested, and tied to observed failures.

### 3. Evaluation Is Manual And Incomplete

There are useful engineering tests, but no tutor-quality eval suite yet. A speech tutor can fail while all unit tests pass: wrong correction, patronizing tone, STT silently normalizing learner errors, or latency making conversation unusable.

Production direction:

- Add deterministic prompt/provider unit tests where possible.
- Add scripted L2 utterance probes with expected correction behavior.
- Maintain a small gold set for grammar, vocabulary, clean utterances, and role-play turns.
- Track correction false positives and STT normalization rate manually before automating more.

### 4. Privacy And Data Handling Are Prototype-Grade

Debug logs can contain transcripts, prosody, LLM inputs, and assistant outputs. System prompt logging is disabled by default in code but configurable. There is no retention policy, consent flow, redaction layer, or secure deployment boundary.

Production direction:

- Keep debug logging opt-in and off by default.
- Add explicit learner consent before recording or storing sessions.
- Redact or avoid storing raw audio unless needed for evaluation.
- Define retention windows and delete-my-data behavior before multi-learner use.
- Never expose the localhost server beyond the local machine without HTTPS and auth.

### 5. Operational Resilience Is Early

The loop has error messages and startup checks, but production operation would need cancellation guarantees, provider timeouts, rate-limit handling, retries where safe, queue backpressure, health checks that verify dependencies, and deploy-time configuration validation.

Production direction:

- Add per-provider timeout budgets.
- Emit structured events for STT/LLM/TTS failure classes.
- Avoid silent retries for pedagogy-affecting operations; surface failures clearly.
- Add cancellation and cleanup tests for disconnects and mid-turn cancel.
- Track provider cost and usage per session.

### 6. Frontend Is A Functional Control Surface, Not Learner UX

The UI proves push-to-talk, transcript editing, and playback. It does not yet optimize onboarding, error recovery, accessibility, session history, or learner trust.

Production direction:

- Add learner mode selection and clear session lifecycle states.
- Make transcript editing and "what the tutor heard" obvious.
- Add visible failure states for STT, LLM, and TTS.
- Keep push-to-talk until echo-loop risk is better characterized.

### 7. Future Direct-Voice Product Choice Is Not Settled

The prototype validates the traditional pipeline today, but production still needs a decision about whether a future direct multimodal voice route should coexist with it. The traditional pipeline gives an explicit transcript surface for learner review and correction. A direct multimodal route may feel smoother, but it needs separate validation for transcript visibility, correction accuracy, cost, latency, and debuggability.

Production direction:

- Prototype a direct multimodal route and compare it with the explicit pipeline using the same scripted learner turns.
- Decide which path owns correction-heavy tutoring flows.
- Keep explicit transcript visibility wherever correction pedagogy depends on what the learner actually said.
- Track latency, cost, and failure modes separately for each path.

## Production Foundation Already Present

- Provider interfaces reduce vendor lock-in and make cost/performance comparisons testable.
- The turn protocol is explicit enough to persist later.
- The frozen session prompt avoids accidental prompt drift mid-session.
- The typed `UserTurnContext` keeps raw STT, edited text, source, and prosody together before rendering to the LLM.
- Future direct multimodal voice work has clear comparison criteria against the explicit pipeline.
- Debug and latency hooks make the system observable enough for Phase 2/3 iteration.
- The roadmap has concrete deferral triggers instead of vague "later" work.

## Recommended Next Production Steps

1. Phase 2 should add SQLite persistence and tutor policy together, because corrections without durable audit trails are hard to evaluate.
2. Add prompt regression probes before expanding persona complexity.
3. Add a small evaluation corpus before dogfooding with real learners.
4. Add privacy/retention documentation before storing learner data.
5. Keep deployment local-only until authentication, HTTPS, and consent are real.

## Honest Summary

This repo is not production-ready. It is a credible production-minded prototype because it validates a traditional speech pipeline, isolates provider dependencies, records useful turn diagnostics, and defines the next hardening steps without pretending they are already complete.
