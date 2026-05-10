export type ServerEvent =
  | { type: "turn.started"; turn_id: number }
  | { type: "stt.running"; turn_id: number }
  | { type: "transcript.ready"; turn_id: number; stt_text: string }
  | { type: "llm.delta"; turn_id: number; text: string }
  | {
      type: "tts.chunk";
      turn_id: number;
      seq: number;
      sentence_idx: number;
      mime: string;
      bytes: number;
    }
  | { type: "tts.done"; turn_id: number; total_chunks: number }
  | { type: "turn.done"; turn_id: number }
  | {
      type: "error";
      turn_id: number;
      stage: string;
      code: string;
      message: string;
      retriable: boolean;
    }
  | { type: "turn.failed"; turn_id: number; stage: string }
  | { type: "turn.canceled"; turn_id: number; at_stage: string };

export type ClientEvent =
  | { type: "turn.start" }
  | { type: "turn.stop" }
  | { type: "audio.frame"; turn_id: number; seq: number }
  | { type: "turn.send"; turn_id: number; stt_text?: string; text: string }
  | { type: "turn.cancel"; turn_id: number };

export interface WSClient {
  send(evt: ClientEvent): void;
  sendBytes(bytes: ArrayBuffer | Blob): void;
  on<T extends ServerEvent["type"]>(
    type: T,
    handler: (evt: Extract<ServerEvent, { type: T }>) => void,
  ): () => void;
  once<T extends ServerEvent["type"]>(
    type: T,
  ): Promise<Extract<ServerEvent, { type: T }>>;
  onBinary(handler: (bytes: ArrayBuffer) => void): () => void;
  close(): void;
  readonly readyState: number;
}

export function createWS(url: string): WSClient {
  const ws = new WebSocket(url);
  ws.binaryType = "arraybuffer";
  const handlers = new Map<string, Set<(evt: ServerEvent) => void>>();
  const binaryHandlers = new Set<(bytes: ArrayBuffer) => void>();

  ws.addEventListener("message", (ev) => {
    if (typeof ev.data === "string") {
      const evt = JSON.parse(ev.data) as ServerEvent;
      handlers.get(evt.type)?.forEach((handler) => handler(evt));
      return;
    }
    binaryHandlers.forEach((handler) => handler(ev.data as ArrayBuffer));
  });

  const client: WSClient = {
    send(evt) {
      ws.send(JSON.stringify(evt));
    },
    sendBytes(bytes) {
      ws.send(bytes);
    },
    on(type, handler) {
      if (!handlers.has(type)) {
        handlers.set(type, new Set());
      }
      const wrapped = handler as (evt: ServerEvent) => void;
      handlers.get(type)!.add(wrapped);
      return () => handlers.get(type)?.delete(wrapped);
    },
    once(type) {
      return new Promise((resolve) => {
        const off = client.on(type, (evt) => {
          off();
          resolve(evt as Extract<ServerEvent, { type: typeof type }>);
        });
      });
    },
    onBinary(handler) {
      binaryHandlers.add(handler);
      return () => binaryHandlers.delete(handler);
    },
    close() {
      ws.close();
    },
    get readyState() {
      return ws.readyState;
    },
  };
  return client;
}
