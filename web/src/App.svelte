<script lang="ts">
  // Phase 1 Wave 0 placeholder. Real WebSocket UI lands in Plan 06.
  let status = $state<"idle" | "connecting" | "ready">("idle");
</script>

<main>
  <h1>Hermes Speech Tutor</h1>
  <p>Wave 0 scaffold - UI lands in Plan 06.</p>
  <p>Status: {status}</p>
</main>

<style>
  main {
    font-family: system-ui, sans-serif;
    max-width: 640px;
    margin: 2rem auto;
    padding: 1rem;
  }
</style>
