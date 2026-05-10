<script lang="ts">
  let {
    text = $bindable(""),
    sttText = "",
    onSend,
    onCancel,
  }: {
    text: string;
    sttText: string;
    onSend: () => void;
    onCancel: () => void;
  } = $props();

  let editor = $state<HTMLDivElement | null>(null);

  function handleKey(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSend();
    } else if (event.key === "Escape") {
      text = sttText;
      if (editor) editor.textContent = sttText;
      onCancel();
    }
  }

  function handleInput(event: Event) {
    if (event.target instanceof HTMLElement) {
      text = event.target.textContent ?? "";
    }
  }

  $effect(() => {
    if (editor && editor.textContent !== text) {
      editor.textContent = text;
    }
  });
</script>

<div class="chip">
  <span>You said</span>
  <div
    bind:this={editor}
    class="editor"
    contenteditable="true"
    spellcheck="false"
    role="textbox"
    tabindex="0"
    onkeydown={handleKey}
    oninput={handleInput}
  ></div>
  <button type="button" onclick={onSend} disabled={!text.trim()}>Send</button>
</div>

<style>
  .chip {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.75rem;
  }

  span {
    color: #606b7b;
    white-space: nowrap;
  }

  .editor {
    flex: 1;
    min-height: 1.5rem;
    padding: 0.375rem 0.5rem;
    background: #fff;
    border: 1px dashed #aab4c2;
    border-radius: 6px;
  }

  .editor:focus {
    outline: 2px solid #2f7d57;
    outline-offset: 1px;
  }

  button {
    padding: 0.375rem 0.75rem;
    font: inherit;
  }
</style>
