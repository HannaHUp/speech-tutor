# Evaluation Strategy

## Current Status

The repo currently has engineering tests for provider seams, session prompt behavior, WebSocket flow, TTS chunking, STT utilities, and startup checks. It does not yet have a complete tutor-quality evaluation suite.

That distinction matters. A speech tutor can pass code tests and still fail as a learning product.

## Evaluation Goals

A production-minded evaluation plan should answer four questions:

- Does the speech loop work reliably?
- Does the tutor correct real learner errors without inventing problems?
- Does the tutor sound useful rather than patronizing or fake?
- Is the system affordable and fast enough for the target usage?

## Phase 1 Evals

These are appropriate for the current repo.

### Speech Loop

- Run 10 consecutive voice turns on the paid stack.
- Measure end-of-speech to first audible audio.
- Target p50 under 4.5 seconds for the paid stack.
- Record free-stack latency as a baseline, not a gate.

### STT Normalization

- Prepare 10 utterances with deliberate L2 errors.
- Run each through each STT implementation.
- Count cases where STT silently normalizes the error.
- Target under 30 percent silent normalization, or rely on editable transcript UX as mitigation.

### Echo Loop

- Play tutor TTS through normal laptop speakers.
- Keep push-to-talk behavior active.
- Confirm no runaway self-transcription across 5 turns.

### Prompt Payload Inspection

- Enable turn debug logs locally.
- Confirm the LLM receives edited learner text, not only raw STT.
- Confirm prosody metadata appears for voice turns when extraction succeeds.
- Confirm system prompt logging remains disabled unless explicitly enabled.

## Phase 2 Tutor Evals

These should be added before claiming the app is a tutor.

### Clean Utterance Guardrail

Input 10 grammatically correct simple utterances. Expected result: the tutor continues naturally and does not invent corrections.

### Seeded Error Correction

Input 30 utterances across A/B/C CEFR bands with known grammar or vocabulary issues. Expected result: correction is accurate, concise, and appropriate to the learner level.

### Correction Budget

Force A, B, and C learner bands. Expected result:

- A band: no more than 1 correction per turn.
- B band: no more than 2 corrections per turn.
- C band: no more than 3 corrections per turn.

### Role-Play Mode

Run 3 role-play sessions. Expected result: the tutor stays in character and batches corrections at scene end instead of interrupting the scene.

## Phase 3 Memory Evals

These should be added when persistence lands.

- Two learners can use the app back-to-back without state leakage.
- Every query filters by learner id.
- Session summaries are generated once and are idempotent.
- Reconnect within the allowed window restores the correct session.
- Stale sessions close and summarize without duplicate rows.

## Phase 4 Human Evals

Human testing is required before claiming tutor quality.

- 3-5 real L2 learners complete 15-minute sessions.
- At least two learners should be A2-B1, where correction tone risk is high.
- Review every correction for false positives and wrong explanations.
- Target correction false-positive rate under 10 percent.
- Record qualitative feedback on tone, usefulness, and frustration.
- Project monthly cost from real token and TTS-character logs.

## Suggested Eval Fixtures

Create small fixture files before expanding the model:

- `evals/utterances/clean_a2.jsonl`
- `evals/utterances/seeded_errors_a2_b1.jsonl`
- `evals/utterances/seeded_errors_b2_c1.jsonl`
- `evals/roleplay/scenes.jsonl`
- `evals/rubrics/correction_quality.md`
- `evals/rubrics/persona_tone.md`

Keep the first eval set small and hand-reviewable. Over-automating early tutor evals can hide bad pedagogy behind misleading metrics.

## Metrics To Track

- End-to-end latency by stage.
- STT normalization rate on deliberate errors.
- Transcript edit rate.
- LLM first-token and first-sentence latency.
- TTS first-chunk latency.
- Correction false-positive rate.
- Correction count per turn.
- Role-play mode adherence.
- Token and TTS-character cost per minute.
- User-reported annoyance or confusion.

## What Not To Claim Yet

- No claim of pedagogical effectiveness.
- No claim of CEFR accuracy.
- No claim of production safety.
- No claim of robust personalization.
- No claim that prosody improves outcomes.

## Honest Summary

The repo currently has engineering validation for a Phase 1 speech loop. The next evaluation layer should focus on tutor quality: correction accuracy, no invented errors, tone, latency under real use, and cost. Those evals should be built before the project is presented as a learner-ready tutor.
