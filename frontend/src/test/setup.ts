import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Node 25 exposes an experimental global `localStorage` that can shadow jsdom's
// and lacks methods like `clear()`. Install a small, spec-shaped in-memory
// Storage on both globalThis and window so app code and tests share one store.
class MemoryStorage implements Storage {
  private store = new Map<string, string>();
  get length(): number {
    return this.store.size;
  }
  clear(): void {
    this.store.clear();
  }
  getItem(key: string): string | null {
    return this.store.has(key) ? this.store.get(key)! : null;
  }
  key(index: number): string | null {
    return Array.from(this.store.keys())[index] ?? null;
  }
  removeItem(key: string): void {
    this.store.delete(key);
  }
  setItem(key: string, value: string): void {
    this.store.set(key, String(value));
  }
}

const memoryStorage = new MemoryStorage();
Object.defineProperty(globalThis, "localStorage", {
  value: memoryStorage,
  configurable: true,
  writable: true,
});
if (typeof window !== "undefined") {
  Object.defineProperty(window, "localStorage", {
    value: memoryStorage,
    configurable: true,
    writable: true,
  });
}

// React Testing Library doesn't auto-clean between tests under Vitest globals
// in every config; do it explicitly so each test starts with a fresh DOM. Also
// reset the shared in-memory localStorage so writes (theme, auth, quiz
// persistence, device id) don't leak across tests and cause order-dependent
// failures as the suite grows.
afterEach(() => {
  cleanup();
  memoryStorage.clear();
});
