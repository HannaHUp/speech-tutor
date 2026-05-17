# Personalized Practice Starters

## Table Of Contents

- [Short Version](#short-version)
- [Research Inspiration](#research-inspiration)
- [Why This Matters For Hermes](#why-this-matters-for-hermes)
- [What Makes This Different From Generic Prompt Suggestions](#what-makes-this-different-from-generic-prompt-suggestions)
- [Product Principle](#product-principle)
- [Relationship To Curriculum](#relationship-to-curriculum)
- [Architecture Fit](#architecture-fit)
- [Future Production Plan](#future-production-plan)
  - [Phase 1: Lightweight Prototype](#phase-1-lightweight-prototype)
  - [Phase 2: Session Summary Integration](#phase-2-session-summary-integration)
  - [Phase 3: Starter Feedback Loop](#phase-3-starter-feedback-loop)
  - [Phase 4: Evaluation Layer](#phase-4-evaluation-layer)
- [Possible Scoring Model](#possible-scoring-model)
- [Example User Experience](#example-user-experience)
  - [Why Allow Transcript Correction?](#why-allow-transcript-correction)

## Short Version

Personalized Practice Starters are a future production feature for Hermes Speech Tutor.

The idea is simple: before the learner starts speaking, Hermes can offer a small set of speaking prompts that are tailored to the learner's level, interests, recent mistakes, and practice goals.

Instead of asking every learner a generic question like:

```text
Tell me about your day.
```

Hermes could offer prompts like:

```text
1. Tell me about a recent work meeting. Try using past tense clearly.
2. Role-play: you are checking into a hotel and there is a problem with your room.
3. Describe your favorite cafe in 60 seconds. Focus on word stress and natural pacing.
```

This turns Hermes from a purely reactive tutor into a more proactive practice partner.

## Research Inspiration

This idea is inspired by the paper "IceBreaker for Conversational Agents: Breaking the First-Message Barrier with Personalized Starters" from ByteDance.(https://arxiv.org/html/2604.18375v1)

The paper studies a common problem in conversational AI: many users open an agent but do not know what to ask first. The authors call this the "first-message barrier."

Their solution is to generate personalized conversation starters from a user's past session summaries. The system works in two broad steps:

1. Find interests from past sessions that are likely to resonate with the user.
2. Generate a small, diverse list of conversation starters based on those interests.

The important lesson for Hermes is not to copy the paper exactly. The useful idea is this:

```text
Past user behavior can help the agent suggest better first turns.
```

For a general assistant, the goal may be engagement. For Hermes, the goal should be learning-quality engagement.

## Why This Matters For Hermes

The hardest moment in a speaking tutor is often getting the learner to speak at all.

A learner may open the tutor with a vague goal:

```text
I want to practice English.
```

But that is not enough to start a useful conversation. The learner still has to decide what topic to discuss, what difficulty level is right, and what kind of practice they want.

Personalized Practice Starters reduce that friction. They give the learner a few useful paths into speaking practice.

They can help Hermes with:

- Conversation initiation: the learner can start faster.
- Personalization: prompts can reflect topics the learner actually cares about.
- Pedagogy: prompts can target grammar, pronunciation, fluency, vocabulary, or role-play skills.
- Continuity: future sessions can build on previous sessions.
- Measurement: Hermes can track which prompts lead to useful speaking practice.

## What Makes This Different From Generic Prompt Suggestions

Generic prompt suggestions are static. They might look like this:

```text
Talk about travel.
Practice ordering food.
Describe your weekend.
```

Personalized Practice Starters are adaptive. They should be generated from learner context:

```text
Learner level: B1
Recent topics: work presentations, travel, coffee shops
Recent mistakes: past tense, word stress, follow-up questions
Preferred mode: role-play
Session goal: fluency
```

From that context, Hermes might generate:

```text
1. Role-play a project update. Explain one project you worked on last year.
2. Tell me about a trip you took recently. Use at least five past-tense verbs.
3. Order coffee and ask two follow-up questions about the menu.
```

The point is not just to make the learner click. The point is to elicit speech that gives the tutor something useful to coach.

## Product Principle

Hermes should optimize for learning-quality engagement, not raw engagement.

A prompt is not good just because the learner selects it. A prompt is good if it:

- Gets the learner speaking.
- Matches the learner's level.
- Targets a useful skill.
- Feels personally relevant.
- Produces enough language for the tutor to evaluate.
- Avoids sensitive or uncomfortable topics.
- Does not overload the learner.

This is an important distinction for an education product.

The feature should not become clickbait for conversation. It should become a structured way to create better speaking opportunities.

## Relationship To Curriculum

Personalized Practice Starters should not replace curriculum.

They should become the entry point into curriculum practice.

The clean framing is:

```text
Curriculum decides what the learner should practice next.
Personalized Practice Starters decide how to invite the learner into that practice.
```

For example:

```text
Curriculum objective:
Practice past-tense storytelling at B1 level.

Personalized starter:
Tell me about a trip you took last year. Use at least five past-tense verbs.
```

The starter is not random personalization. It is a personalized wrapper around a curriculum goal.

A future production architecture could look like this:

```text
CurriculumEngine
  -> selects next learning objective

LearnerProfile
  -> provides level, interests, history, weak areas

StarterService
  -> turns objective + learner context into 3-5 speaking starters

TutorTurnFlow
  -> runs the selected starter through voice practice and feedback
```

This gives Hermes both structure and relevance.

Curriculum provides:

- Progression.
- Skill coverage.
- Level-appropriate sequencing.
- Pedagogical intent.

Personalization provides:

- Relevant topics.
- Familiar scenarios.
- Motivation to speak.
- Lower first-turn friction.

The same curriculum objective can be practiced through different learner interests.

Example:

```text
Shared curriculum goal:
Practice giving opinions with reasons.

Target language:
"I think..."
"because..."
"for example..."
```

Different learners could receive different starters:

```text
Learner A likes work topics:
Do you think remote work is better than office work? Give two reasons.

Learner B likes travel:
Do you think traveling alone is better than traveling with friends? Give two reasons.

Learner C likes food:
Do you think eating out is better than cooking at home? Give two reasons.
```

The important design rule is that curriculum should remain the controlling layer.

If starters are optimized only around learner interests, the tutor may overfit to fun topics and under-cover important skills. Hermes should personalize the path into the objective, not ignore the objective.

In one sentence:

```text
Personalized Practice Starters are curriculum-aware prompts.
```

## Architecture Fit

This feature fits the current Hermes architecture because the prototype already separates important pieces:

- Voice turn flow.
- Raw transcript plus optional recognition-error correction.
- LLM prompt construction.
- Typed user-turn context.
- STT, TTS, LLM, and pronunciation provider interfaces.
- Debug and latency hooks.
- Future attachment points for persistence, learner profiles, correction policy, and evals.

Personalized Practice Starters would not require replacing the speech pipeline. It would sit above the existing turn loop.

A future service boundary could look like this:

```text
StarterService
  -> reads LearnerProfile
  -> reads SessionSummaries
  -> reads CorrectionHistory
  -> generates StarterList
  -> logs StarterInteraction
```

The starter becomes the first input into the existing tutor flow.

## Future Production Plan

### Phase 1: Lightweight Prototype

Build a simple starter generator that uses current session context or manually supplied learner notes.

Possible inputs:

```text
CEFR level
recent topic
target skill
recent correction focus
preferred practice mode
```

Possible output:

```text
3-5 diverse speaking starters
```

The goal is to validate the user experience: does the tutor feel easier to start when it offers relevant practice options?

### Phase 2: Session Summary Integration

After Hermes has persistence, summarize each session into structured learner memory.

Example:

```json
{
  "topics": ["work presentations", "travel", "coffee shops"],
  "skill_focus": ["past tense", "word stress", "follow-up questions"],
  "learner_level": "B1",
  "successful_starter_types": ["role-play", "personal experience"],
  "avoid_topics": ["medical topics"]
}
```

The starter generator can then use these summaries to create more relevant prompts.

### Phase 3: Starter Feedback Loop

Track how each starter performs.

Signals could include:

```text
shown
selected
skipped
completed
speech duration
number of learner turns
correction density
learner confidence signal
follow-up depth
```

This creates a feedback loop. Hermes can learn which starter types actually produce useful practice for each learner.

### Phase 4: Evaluation Layer

Create evals for starter quality.

Useful evaluation dimensions:

- CEFR appropriateness.
- Topic relevance.
- Skill targeting.
- Diversity across the starter list.
- Privacy and sensitivity safety.
- Likelihood of eliciting speech.
- Whether the prompt is too easy or too hard.
- Whether the prompt supports useful tutor feedback.

The goal is to prove that starters improve learning behavior, not just engagement metrics.

## Possible Scoring Model

A future version could score candidate starters with a formula like:

```text
starter_score =
  personalization
  + expected_speech_volume
  + target_skill_relevance
  + CEFR_fit
  + topic_diversity
  - redundancy
  - privacy_or_sensitivity_risk
  - overcorrection_risk
```

This does not need to be implemented immediately. It is a useful way to explain the product direction.

## Example User Experience

A learner opens Hermes.

Hermes shows:

```text
Choose a practice starter

1. Tell me about a recent work meeting. Try using past tense clearly.
2. Role-play: you are calling a hotel to change your reservation.
3. Describe your favorite cafe. Focus on clear word stress.
```

The learner chooses one and starts speaking.

Hermes listens, transcribes the learner's speech, lets the learner correct speech-recognition errors when needed, then sends both the raw transcript and corrected meaning to the tutor model before speaking back a response.

Behind the scenes, Hermes records whether the starter led to useful practice. Over time, the tutor gets better at suggesting practice that fits this learner.

### Why Allow Transcript Correction?

Transcript correction is not meant to let the learner polish their English before being evaluated.

It is meant to protect the tutor from speech-recognition errors.

For example, the learner may say:

```text
I went to the beach last weekend.
```

But speech recognition might hear:

```text
I want to the pitch last weekend.
```

If Hermes sends only the bad transcript to the LLM, the tutor may correct the wrong thing. The learner would be evaluated on STT noise instead of their actual speech.

The safer design is to keep both versions:

```text
Raw transcript:
what the STT system heard

Corrected meaning:
what the learner says they meant
```

Then Hermes can use them differently:

```text
Use corrected meaning for conversation understanding.
Use raw transcript, audio, and prosody for speaking feedback.
```

This matters because a learner might also rewrite a sentence to make it more grammatically correct.

Example:

```text
Raw transcript:
I go to beach yesterday.

Corrected meaning:
I went to the beach yesterday.
```

In that case, the edit may hide the original speaking mistake. Hermes should not treat the corrected version as the only source of truth.

The product rule should be:

```text
The learner can fix recognition errors, but Hermes preserves the original spoken evidence for feedback.
```

The UI should also make this clear. It should ask whether Hermes heard the learner correctly, not invite the learner to rewrite the answer as a writing exercise.

Possible UI framing:

```text
Did Hermes hear you correctly?

[Yes, continue]
[Fix recognition error]
```

Hermes can also track how much the learner changed:

```text
Small edit:
likely speech-recognition correction

Large grammar rewrite:
possible self-correction or switch from speaking practice to writing practice
```

If the learner changes a lot, Hermes can still use the corrected meaning for the conversation, but should base speaking feedback on the original spoken version.
