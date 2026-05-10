<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import type { WSClient } from "./lib/ws";

  let {
    ws,
    turnId,
    disabled = false,
    onTurnStart,
  }: {
    ws: WSClient | null;
    turnId: number | null;
    disabled: boolean;
    onTurnStart: (id: number) => void;
  } = $props();

  let recording = $state(false);
  let recorder: MediaRecorder | null = null;
  let stream: MediaStream | null = null;
  let activeTurnId: number | null = null;
  let frameSeq = 0;

  async function startRecording() {
    if (!ws || recording || disabled) return;
    try {
      ws.send({ type: "turn.start" });
      const started = await ws.once("turn.started");
      activeTurnId = started.turn_id;
      onTurnStart(started.turn_id);

      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recorder = new MediaRecorder(stream, { mimeType: "audio/webm;codecs=opus" });
      frameSeq = 0;
      recording = true;

      recorder.ondataavailable = (event) => {
        const id = activeTurnId ?? turnId;
        if (!ws || id == null || event.data.size === 0) return;
        ws.send({ type: "audio.frame", turn_id: id, seq: frameSeq++ });
        event.data.arrayBuffer().then((buffer) => ws?.sendBytes(buffer));
      };
      recorder.onstop = () => {
        ws?.send({ type: "turn.stop" });
        stream?.getTracks().forEach((track) => track.stop());
        stream = null;
        recording = false;
      };
      recorder.start(250);
    } catch (error) {
      console.error("getUserMedia failed", error);
      stream?.getTracks().forEach((track) => track.stop());
      stream = null;
      recording = false;
    }
  }

  function stopRecording() {
    if (!recording || !recorder) return;
    recorder.stop();
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (
      event.code === "Space" &&
      event.target === document.body &&
      !disabled &&
      !recording
    ) {
      event.preventDefault();
      startRecording();
    }
  }

  function handleKeyUp(event: KeyboardEvent) {
    if (event.code === "Space" && recording) {
      event.preventDefault();
      stopRecording();
    }
  }

  onMount(() => {
    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);
  });

  onDestroy(() => {
    window.removeEventListener("keydown", handleKeyDown);
    window.removeEventListener("keyup", handleKeyUp);
    if (recorder && recording) recorder.stop();
    stream?.getTracks().forEach((track) => track.stop());
  });
</script>

<button
  class:recording
  type="button"
  {disabled}
  onpointerdown={startRecording}
  onpointerup={stopRecording}
  onpointercancel={stopRecording}
  onpointerleave={() => recording && stopRecording()}
  title={disabled ? "Tutor is speaking" : "Hold Space or press and hold to talk"}
>
  {#if disabled}
    Tutor is speaking
  {:else if recording}
    Listening
  {:else}
    Hold to talk
  {/if}
</button>

<style>
  button {
    min-width: 9rem;
    min-height: 2.75rem;
    padding: 0.75rem 1.25rem;
    font: inherit;
    color: #fff;
    background: #2f7d57;
    border: 0;
    border-radius: 6px;
    cursor: pointer;
    user-select: none;
  }

  button.recording {
    background: #b42318;
  }

  button:disabled {
    background: #7c8796;
    cursor: not-allowed;
  }
</style>
