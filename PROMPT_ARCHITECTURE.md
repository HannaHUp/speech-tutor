# Prompt Architecture

## Current Status

Prompting is intentionally minimal in Phase 1. The app uses a stable session-level system prompt and appends learner turns to an in-memory message list. The current prompt does not yet implement the full Iris persona, correction policy, CEFR adaptation, or mode-specific behavior planned for Phase 2.

## Current Code Path

- `server/prompt_builder.py` builds the session prompt from `SOUL.md` when available.
- `server/session.py` freezes that system prompt when a `Session` is created.
- `server/ws_handler.py` converts each submitted learner turn into a `UserTurnContext`.
- `UserTurnContext` preserves source, edited learner text, raw STT text when available, and prosody metadata.
- The LLM receives the edited learner text plus a fenced `prosody` block for voice turns.
- `server/providers/llm_openai.py` sends the system prompt as an OpenAI chat system message.
- `server/providers/llm_anthropic.py` sends the system prompt with Anthropic ephemeral cache control.

## Why The Prompt Snapshot Matters

The system prompt is frozen per session. That is deliberate:

- It prevents mid-session prompt drift if `SOUL.md` changes while a learner is talking.
- It creates a stable prefix suitable for provider-side prompt caching.
- It makes later debugging cleaner because each session can be tied to one prompt version.

In production, the frozen prompt should be persisted with a prompt version, not just held in memory.

## Current Prompt Layers

Today, the practical layers are:

- Stable persona prefix from `SOUL.md`.
- Conversation history in `Session.messages`.
- Current learner turn rendered from `UserTurnContext`.
- Optional prosody block attached to voice turns.

This is enough for Phase 1. It is not enough for a production tutor.

## Target Prompt Layers

Phase 2 and beyond should split prompt construction into explicit components:

- Persona: stable Iris behavior, tone, response length, praise limits, and boundaries.
- Pedagogy policy: when to correct, how many corrections to give, and how to explain them.
- Learner state: CEFR band, L1 if known, goals, prior error patterns, and correction budget.
- Mode policy: free conversation, topic talk, or role-play rules.
- Recent conversation: bounded turn history.
- Current turn context: edited text, raw STT text, source, prosody, and pronunciation metadata.
- Output contract: response shape, correction format, and "no invented corrections" rule.

## Prompt Risks

### False-Positive Corrections

A tutor that invents errors is worse than a generic chatbot. Clean utterances need explicit no-correction probes.

### Sycophantic Or Patronizing Tone

Language learners need encouragement without fake praise. Persona work must be validated with real learners, not only with the operator.

### STT Normalization

STT can silently fix learner errors before the LLM sees them. The app already keeps raw STT versus edited text visible in logs; evaluation should measure how often intended learner mistakes are normalized.

### Context Bloat

Phase 1 keeps all session messages in memory. Production should introduce context windows, summaries, and prompt compaction only after sessions exceed practical limits.

## Versioning Strategy

Prompt changes should be treated as product changes:

- Assign a prompt version to each session.
- Store the rendered system prompt or a hash plus source version.
- Run prompt regression probes before accepting changes.
- Track real-user feedback against prompt versions.
- Keep prompt changes reviewable in git.

## What Not To Claim Yet

- Do not claim there is a robust correction engine.
- Do not claim CEFR-aware adaptation exists.
- Do not claim prompt behavior has been validated with learners.
- Do not claim prosody currently improves tutor decisions; Phase 1 only passes prosody into the prompt path.

## Current Production-Minded Seam

`UserTurnContext` is the main prompt-side seam added for future production work. It keeps learner-turn facts together before rendering them into LLM text. That makes future persistence, eval, prompt inspection, and context compression easier without changing the WebSocket contract again.
