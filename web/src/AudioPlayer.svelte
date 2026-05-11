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
  let unsubscribeDone: (() => void) | null = null;
  let unsubscribeTurnStart: (() => void) | null = null;
  let started = false;
  let streamDone = false;
  const pendingChunks: ArrayBuffer[] = [];

  function handlePlaybackEnded() {
    onPlayEnd();
    started = false;
    streamDone = false;
    setupMediaSource();
  }

  function maybeFinishStream() {
    if (
      !streamDone ||
      !mediaSource ||
      mediaSource.readyState !== "open" ||
      !sourceBuffer ||
      sourceBuffer.updating ||
      pendingChunks.length > 0
    ) {
      return;
    }
    mediaSource.endOfStream();
  }

  function handleSourceBufferUpdateEnd() {
    drain();
    maybeFinishStream();
  }

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

  function handleSourceOpen() {
    if (!mediaSource) return;
    sourceBuffer = mediaSource.addSourceBuffer("audio/mpeg");
    sourceBuffer.addEventListener("updateend", handleSourceBufferUpdateEnd);
    drain();
  }

  function teardownMediaSource() {
    if (sourceBuffer) {
      sourceBuffer.removeEventListener("updateend", handleSourceBufferUpdateEnd);
    }
    sourceBuffer = null;
    if (mediaSource) {
      mediaSource.removeEventListener("sourceopen", handleSourceOpen);
    }
    mediaSource = null;
    if (objectUrl) {
      URL.revokeObjectURL(objectUrl);
    }
    objectUrl = null;
  }

  function setupMediaSource() {
    if (!audioEl || !codecOk) return;
    teardownMediaSource();
    mediaSource = new MediaSource();
    objectUrl = URL.createObjectURL(mediaSource);
    audioEl.src = objectUrl;
    mediaSource.addEventListener("sourceopen", handleSourceOpen);
  }

  onMount(() => {
    if (!("MediaSource" in window) || !MediaSource.isTypeSupported("audio/mpeg")) {
      codecOk = false;
      return;
    }
    if (!audioEl) return;
    audioEl.addEventListener("ended", handlePlaybackEnded);
    setupMediaSource();
  });

  $effect(() => {
    unsubscribeBinary?.();
    unsubscribeDone?.();
    unsubscribeTurnStart?.();
    unsubscribeBinary = null;
    unsubscribeDone = null;
    unsubscribeTurnStart = null;
    if (ws) {
      unsubscribeBinary = ws.onBinary((bytes) => {
        if (!mediaSource || mediaSource.readyState === "ended") {
          setupMediaSource();
        }
        pendingChunks.push(bytes);
        drain();
      });
      unsubscribeDone = ws.on("tts.done", () => {
        streamDone = true;
        maybeFinishStream();
      });
      unsubscribeTurnStart = ws.on("turn.started", () => {
        streamDone = false;
      });
    }
  });

  onDestroy(() => {
    unsubscribeBinary?.();
    unsubscribeDone?.();
    unsubscribeTurnStart?.();
    audioEl?.removeEventListener("ended", handlePlaybackEnded);
    teardownMediaSource();
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
