# Evaluating Direct Multimodal Voice For Speech Tutoring

This document defines how Hermes should evaluate a future direct multimodal voice route before using it for correction-heavy tutoring.

The current implementation uses an explicit pipeline:

```text
browser mic -> STT -> transcript review -> LLM -> TTS -> playback
```

A direct multimodal route would look more like:

```text
browser mic -> multimodal voice model -> playback
```

Direct voice may feel smoother, but correction-heavy tutoring needs evidence. The key question is not whether the model can hold a conversation. The key question is whether the tutor can give accurate, auditable feedback on learner speech.

## Decision Standard

Use direct multimodal voice for correction-heavy tutoring only if it can support:

- transcript or transcript-like evidence of what the system heard
- separation between recognition errors and learner errors
- level-appropriate correction behavior
- debuggable logs for bad feedback
- privacy-safe storage and retention choices
- measurable quality against scripted learner utterances

If it cannot expose enough evidence, use direct multimodal voice only for lower-risk modes such as casual fluency practice, warm-up conversation, or role-play where correction is delayed or summarized.

## Evaluation Dimensions

### 1. Transcript Fidelity

Goal: verify that the system preserves what the learner actually said instead of silently normalizing errors.

Test with deliberate learner errors:

```text
I go to beach yesterday.
She don't like coffee.
I am agree with you.
He have three brother.
Yesterday I meet my friend.
```

Measure:

- Does the system expose what it heard?
- Does it preserve the learner's original error?
- Does it silently rewrite the sentence into correct English?
- Can the raw evidence be inspected after the turn?

Failure mode:

The model responds as if the learner said a corrected version and never surfaces the original error.

### 2. False-Positive Corrections

Goal: verify that the tutor does not invent mistakes in clean speech.

Test with clean utterances:

```text
I went to the beach yesterday.
She doesn't like coffee.
I agree with you.
He has three brothers.
Yesterday I met my friend.
```

Measure:

- Does the tutor avoid unnecessary corrections?
- Does it overcorrect natural spoken language?
- Does it confuse accent, pacing, or disfluency with grammar error?

Failure mode:

The tutor gives correction feedback when the learner's sentence is already acceptable.

### 3. Recognition-Error Handling

Goal: verify that the tutor does not correct the learner for model or transcription mistakes.

Test with:

- quiet speech
- fast speech
- non-native accents
- background noise
- similar-sounding words
- short utterances with limited context

Measure:

- Does the tutor distinguish learner error from recognition error?
- Can the learner repair what the system heard?
- Does the system preserve uncertainty?
- Does the tutor avoid confident correction when the audio evidence is weak?

Failure mode:

The tutor corrects an error introduced by the model rather than an error made by the learner.

### 4. Correction Quality

Goal: verify that feedback is accurate, useful, and appropriate for the learner's level.

Score each correction on:

- accuracy
- clarity
- level fit
- concision
- tone
- whether it targets the most useful issue
- whether it avoids correcting too many issues at once

Example tutoring policy:

```text
Correct at most one grammar issue per turn.
Do not interrupt fluency practice unless the error blocks meaning.
Prefer short recasts for A1-A2 learners.
Give explicit grammar explanations for B2+ learners.
Do not correct pronunciation unless the prompt asks for pronunciation feedback.
```

Failure mode:

The tutor gives technically correct but overwhelming, poorly leveled, or pedagogically unhelpful feedback.

### 5. Policy Adherence

Goal: verify that the direct voice route follows the same tutor policy as the explicit pipeline.

Test scenarios:

- fluency mode where corrections should be minimal
- grammar mode where one correction per turn is expected
- pronunciation mode where speech features matter more
- role-play mode where the tutor should stay in character
- clean utterance probes where no correction should be given

Measure:

- Does the route follow the selected mode?
- Does it respect correction limits?
- Does it avoid invented corrections?
- Can prompt or policy changes be regression-tested?

Failure mode:

The direct voice route feels conversational but cannot be reliably constrained as a tutor.

### 6. Latency Versus Feedback Quality

Goal: compare whether direct voice improves experience without damaging correction quality.

Measure:

- time to first audio
- total turn time
- interruption or overlap issues
- learner-perceived smoothness
- correction accuracy
- correction completeness
- whether the learner can review what happened

Failure mode:

Direct voice is faster, but feedback becomes less inspectable or less accurate.

### 7. Auditability

Goal: ensure bad feedback can be investigated.

For every correction-heavy turn, the system should make it possible to answer:

- What did the learner say?
- What did the system hear?
- What did the system think the learner meant?
- What correction did it choose?
- What evidence supported that correction?
- Which model and prompt version were used?
- What was logged, redacted, retained, or deleted?

Failure mode:

A learner receives bad correction and the team cannot reconstruct why.

## Suggested Test Set

Create a small gold set before broad dogfooding:

- 20 clean utterances that should receive no correction
- 20 grammar-error utterances with expected correction targets
- 10 pronunciation or prosody-sensitive utterances
- 10 noisy or ambiguous audio samples
- 10 role-play turns where correction should be delayed
- 10 level-specific turns across A2, B1, and B2 behavior

Each sample should include:

- audio file or scripted utterance
- expected transcript
- expected correction behavior
- expected no-correction behavior, if applicable
- learner level
- practice mode
- notes about ambiguity

## Pass Criteria

Direct multimodal voice can be considered for correction-heavy tutoring only if:

- clean utterance false-positive correction rate is acceptably low
- deliberate learner errors are preserved or recoverable often enough for feedback
- recognition uncertainty is handled conservatively
- correction policy adherence is comparable to or better than the explicit pipeline
- bad feedback can be audited from logs without storing unnecessary sensitive data
- latency improvement does not come at the cost of feedback quality

If those criteria are not met, direct multimodal voice should stay limited to lower-risk modes.

## Recommended Product Split

Use the explicit pipeline for:

- correction-heavy grammar tutoring
- transcript review
- learner-error analysis
- eval-heavy product development
- privacy-sensitive flows that need clear data boundaries

Evaluate direct multimodal voice for:

- casual fluency practice
- warm-up conversation
- low-friction role-play
- latency-sensitive back-and-forth
- sessions where feedback is delayed until the end

The production decision does not have to be one route forever. Hermes can support both if the product modes have different quality, latency, and auditability requirements.
