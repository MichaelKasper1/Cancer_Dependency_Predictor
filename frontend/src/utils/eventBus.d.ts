// src/utils/eventBus.d.ts
import mitt from 'mitt';

declare module '../utils/eventBus' {
  const eventBus: mitt.Emitter;
  export default eventBus;
}