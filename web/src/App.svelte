<script lang="ts">
  import { onMount } from "svelte";
  import AudioPlayer from "./AudioPlayer.svelte";
  import MicButton from "./MicButton.svelte";
  import TextInput from "./TextInput.svelte";
  import TranscriptChip from "./TranscriptChip.svelte";
  import { createWS, type WSClient } from "./lib/ws";

  let wsStatus = $state<"connecting" | "ready" | "closed" | "error">("connecting");
  let turnId = $state<number | null>(null);
  let sttText = $state("");
  let transcriptText = $state("");
  let isTtsPlaying = $state(false);
  let lastError = $state<string | null>(null);
  let streamingReply = $state("");
  let ws = $state<WSClient | null>(null);

  onMount(() => {
    ws = createWS(`ws://${location.host}/ws`);
    wsStatus = "ready";

    ws.on("turn.started", (event) => {
      turnId = event.turn_id;
      lastError = null;
      streamingReply = "";
    });
    ws.on("transcript.ready", (event) => {
      sttText = event.stt_text;
      transcriptText = event.stt_text;
    });
    ws.on("llm.delta", (event) => {
      streamingReply += event.text;
    });
    ws.on("tts.chunk", () => {
      isTtsPlaying = true;
    });
    ws.on("error", (event) => {
      lastError = `${event.stage}: ${event.message}`;
      wsStatus = "error";
    });
    ws.on("turn.failed", (event) => {
      lastError = `Turn ${event.turn_id} failed at ${event.stage}`;
      wsStatus = "error";
    });
    ws.on("turn.canceled", () => {
      isTtsPlaying = false;
    });

    return () => {
      wsStatus = "closed";
      ws?.close();
    };
  });

  async function sendTyped(text: string) {
    if (!ws) return;
    ws.send({ type: "turn.start" });
    const started = await ws.once("turn.started");
    ws.send({ type: "turn.send", turn_id: started.turn_id, text });
  }

  function sendEdited() {
    if (!ws || turnId == null) return;
    ws.send({
      type: "turn.send",
      turn_id: turnId,
      stt_text: sttText,
      text: transcriptText,
    });
  }

  function cancelTurn() {
    if (!ws || turnId == null) return;
    ws.send({ type: "turn.cancel", turn_id: turnId });
  }
</script>

<main>
  <h1>Hermes Speech Tutor</h1>
  <p class="status">WS: {wsStatus} | turn: {turnId ?? "none"}</p>

  {#if lastError}
    <div class="error">{lastError}</div>
  {/if}

  <section>
    <MicButton {ws} {turnId} disabled={isTtsPlaying} onTurnStart={(id: number) => (turnId = id)} />
    <TranscriptChip
      bind:text={transcriptText}
      {sttText}
      onSend={sendEdited}
      onCancel={cancelTurn}
    />
  </section>

  <section>
    <TextInput disabled={isTtsPlaying} onSend={sendTyped} />
  </section>

  {#if streamingReply}
    <section class="reply">
      <strong>Tutor</strong>
      <div>{streamingReply}</div>
    </section>
  {/if}

  <AudioPlayer
    {ws}
    onPlayStart={() => (isTtsPlaying = true)}
    onPlayEnd={() => (isTtsPlaying = false)}
  />
</main>

<style>
  main {
    font-family: system-ui, sans-serif;
    max-width: 720px;
    margin: 2rem auto;
    padding: 1rem;
  }

  .status {
    color: #606b7b;
    font-size: 0.875rem;
  }

  .error {
    background: #fff1f0;
    color: #9f1c14;
    padding: 0.625rem 0.75rem;
    border-radius: 6px;
  }

  section {
    margin: 1rem 0;
  }

  .reply {
    background: #f5f7fa;
    padding: 0.75rem;
    border-radius: 6px;
  }
</style>
