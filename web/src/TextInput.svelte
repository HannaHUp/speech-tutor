<script lang="ts">
  let {
    disabled = false,
    onSend,
  }: {
    disabled?: boolean;
    onSend: (text: string) => void;
  } = $props();

  let value = $state("");

  function handleKey(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey && value.trim()) {
      event.preventDefault();
      onSend(value.trim());
      value = "";
    }
  }
</script>

<input
  type="text"
  bind:value
  onkeydown={handleKey}
  {disabled}
  placeholder="Type a message"
/>

<style>
  input {
    width: 100%;
    box-sizing: border-box;
    padding: 0.625rem 0.75rem;
    font: inherit;
    border: 1px solid #c7ced8;
    border-radius: 6px;
  }

  input:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }
</style>
