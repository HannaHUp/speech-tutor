# Memory And State Strategy

## Current State

Phase 1 has no database and no durable memory. State is intentionally limited to the active WebSocket session.

Current in-memory state includes:

- Frozen system prompt for the session.
- Ordered user and assistant messages.
- Last STT transcript for the active turn.
- Last extracted prosody for the active turn.
- Active turn id and audio buffer inside the WebSocket handler.

When the server restarts or the WebSocket is lost, that state is gone.

## Why This Is Acceptable For Phase 1

The Phase 1 goal is to prove the speech loop, not learner continuity. Avoiding persistence keeps the prototype focused on the real-time path:

- browser audio capture
- STT
- editable transcript
- LLM streaming
- sentence-level TTS
- playback

Adding persistence before the loop worked would create schema work around unproven behavior.

## What Should Become Durable

The first durable model should support auditability and tutor improvement, not generic chat history.

Recommended Phase 2 tables:

- `learners`: display name, CEFR band, optional L1, optional goal.
- `sessions`: learner id, mode, started/ended timestamps, prompt version, status.
- `utterances`: raw STT text, edited text, assistant text, source, provider metadata, latency fields.
- `corrections`: correction text, rule label, confidence/review fields, false-positive review flag.
- `session_summaries`: markdown summary plus structured JSON for error patterns and vocabulary.
- `prompt_versions`: prompt source hash, rendered prefix hash, date, and notes.

SQLite is the right first database for this roadmap because the project targets 1-3 local learners. Postgres should wait for multi-host deployment or real contention.

## Turn State Boundary

The code now has a small boundary object: `UserTurnContext`.

It carries:

- `source`: `voice` or `text`
- `edited_text`: final learner text submitted to the LLM
- `stt_text`: raw transcription when the turn came from speech
- `prosody`: extracted voice metadata when available

This is the right level of state to persist later because it separates learner input facts from the rendered prompt string.

## Session Lifecycle Target

Production session state should move through explicit states:

- `created`
- `active`
- `ending`
- `ended`
- `failed`

Each turn should have an explicit status:

- `ok`
- `stt_failed`
- `llm_failed`
- `tts_failed`
- `canceled`

That makes failure analysis possible without reading ad hoc logs.

## Context Window Strategy

Do not add complex long-term memory yet. The right sequence is:

1. Keep full in-memory turn history for short Phase 1 sessions.
2. Persist turns at turn boundaries in Phase 2.
3. Add session summaries in Phase 3.
4. Add context compression only if sessions routinely exceed practical prompt limits.
5. Add cross-session memory only after real learners show the summaries are useful.

## Privacy And Retention

Learner speech data is sensitive. Before durable storage is enabled:

- Ask for consent before saving transcripts or audio.
- Prefer storing transcripts and metadata over raw audio.
- Make debug logging opt-in and visibly local.
- Define a retention window for transcripts and debug logs.
- Add delete-my-data behavior before multi-learner usage.

## What Not To Build Yet

- Vector memory.
- Passive CEFR estimation.
- Cross-session personalization beyond stored learner profile.
- Cloud database.
- Teacher dashboard.
- Multi-device sync.

Those are plausible later features, but they are not justified before Phase 2/3 prove correction quality and learner value.

## Honest Summary

The app currently has session memory, not product memory. The production path is to persist turn facts and prompt versions first, then add summaries, then add personalization only when real learner data justifies it.
