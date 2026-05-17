<script lang="ts">
  import { onMount } from "svelte";
  import AudioPlayer from "./AudioPlayer.svelte";
  import Dashboard from "./Dashboard.svelte";
  import MicButton from "./MicButton.svelte";
  import TextInput from "./TextInput.svelte";
  import TranscriptChip from "./TranscriptChip.svelte";
  import { createWS, type WSClient } from "./lib/ws";

  let activeView = $state<"practice" | "dashboard">("practice");
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

<main class="app-shell">
  <header class="app-header">
    <div>
      <span class="brand">Hermes</span>
      <p>Speech tutor and spoken-evidence dashboard</p>
    </div>
    <nav aria-label="Primary">
      <button
        type="button"
        class:active={activeView === "practice"}
        onclick={() => (activeView = "practice")}
      >
        Practice
      </button>
      <button
        type="button"
        class:active={activeView === "dashboard"}
        onclick={() => (activeView = "dashboard")}
      >
        Dashboard
      </button>
    </nav>
  </header>

  {#if activeView === "practice"}
    <section class="practice-view" aria-labelledby="practice-title">
      <div class="practice-header">
        <div>
          <h1 id="practice-title">Practice</h1>
          <p class="status">WS: {wsStatus} | turn: {turnId ?? "none"}</p>
        </div>
      </div>

      {#if lastError}
        <div class="error">{lastError}</div>
      {/if}

      <section class="practice-card">
        <MicButton {ws} {turnId} disabled={isTtsPlaying} onTurnStart={(id: number) => (turnId = id)} />
        <TranscriptChip
          bind:text={transcriptText}
          {sttText}
          onSend={sendEdited}
          onCancel={cancelTurn}
        />
      </section>

      <section class="practice-card">
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
    </section>
  {:else}
    <Dashboard />
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    background: #f6f8fb;
  }

  :global(*) {
    box-sizing: border-box;
  }

  .app-shell {
    font-family: system-ui, sans-serif;
    width: min(1320px, calc(100% - 2rem));
    margin: 0 auto;
    padding: 1rem 0 2rem;
    color: #172033;
  }

  .app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.75rem 0 1rem;
  }

  .brand {
    display: block;
    color: #172033;
    font-size: 1.25rem;
    font-weight: 750;
    line-height: 1.2;
  }

  .app-header p {
    margin: 0.2rem 0 0;
    color: #667085;
    font-size: 0.875rem;
  }

  nav {
    display: inline-flex;
    gap: 0.25rem;
    padding: 0.25rem;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
  }

  nav button {
    min-width: 6.5rem;
    padding: 0.55rem 0.8rem;
    color: #475467;
    background: transparent;
    border: 0;
    border-radius: 6px;
    font: inherit;
    font-weight: 700;
    cursor: pointer;
  }

  nav button.active {
    color: #ffffff;
    background: #2563eb;
  }

  .practice-view {
    max-width: 760px;
    margin: 0 auto;
    padding: 1rem;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
  }

  .practice-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  h1 {
    margin: 0;
    font-size: 1.35rem;
    line-height: 1.2;
  }

  .status {
    margin: 0.25rem 0 0;
    color: #606b7b;
    font-size: 0.875rem;
  }

  .error {
    background: #fff1f0;
    color: #9f1c14;
    padding: 0.625rem 0.75rem;
    border-radius: 6px;
  }

  .practice-card {
    margin: 1rem 0;
  }

  .reply {
    background: #f5f7fa;
    padding: 0.75rem;
    border-radius: 6px;
  }

  @media (max-width: 700px) {
    .app-shell {
      width: min(100% - 1rem, 1320px);
      padding-top: 0.5rem;
    }

    .app-header {
      display: grid;
      align-items: start;
    }

    nav {
      width: 100%;
      display: grid;
      grid-template-columns: 1fr 1fr;
    }

    nav button {
      min-width: 0;
    }

    .practice-view {
      padding: 0.875rem;
    }
  }
</style>
