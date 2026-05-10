<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import type { WSClient } from "./lib/ws";

  let {
    ws,
    onPlayStart,
    onPlayEnd,
  }: {
    ws: WSClient | null;
    onPlayStart: () => void;
    onPlayEnd: () => void;
  } = $props();

  let audioEl = $state<HTMLAudioElement | null>(null);
  let codecOk = $state(true);
  let mediaSource: MediaSource | null = null;
  let sourceBuffer: SourceBuffer | null = null;
  let objectUrl: string | null = null;
  let unsubscribeBinary: (() => void) | null = null;
  let started = false;
  const pendingChunks: ArrayBuffer[] = [];

  function drain() {
    if (!sourceBuffer || sourceBuffer.updating || pendingChunks.length === 0) return;
    const next = pendingChunks.shift();
    if (!next) return;
    try {
      sourceBuffer.appendBuffer(next);
      if (!started) {
        started = true;
        onPlayStart();
        audioEl?.play().catch(() => {});
      }
    } catch (error) {
      console.error("appendBuffer failed", error);
    }
  }

  onMount(() => {
    if (!("MediaSource" in window) || !MediaSource.isTypeSupported("audio/mpeg")) {
      codecOk = false;
      return;
    }
    if (!audioEl) return;

    mediaSource = new MediaSource();
    objectUrl = URL.createObjectURL(mediaSource);
    audioEl.src = objectUrl;
    audioEl.addEventListener("ended", onPlayEnd);

    mediaSource.addEventListener("sourceopen", () => {
      if (!mediaSource) return;
      sourceBuffer = mediaSource.addSourceBuffer("audio/mpeg");
      sourceBuffer.addEventListener("updateend", drain);
      drain();
    });
  });

  $effect(() => {
    unsubscribeBinary?.();
    unsubscribeBinary = null;
    if (ws) {
      unsubscribeBinary = ws.onBinary((bytes) => {
        pendingChunks.push(bytes);
        drain();
      });
    }
  });

  onDestroy(() => {
    unsubscribeBinary?.();
    sourceBuffer?.removeEventListener("updateend", drain);
    audioEl?.removeEventListener("ended", onPlayEnd);
    if (objectUrl) URL.revokeObjectURL(objectUrl);
  });
</script>

{#if !codecOk}
  <div class="error">Streaming audio playback is not supported in this browser.</div>
{/if}

<audio bind:this={audioEl} controls preload="none"></audio>

<style>
  .error {
    background: #fff1f0;
    color: #9f1c14;
    padding: 0.625rem 0.75rem;
    border-radius: 6px;
  }

  audio {
    width: 100%;
    margin-top: 0.75rem;
  }
</style>
