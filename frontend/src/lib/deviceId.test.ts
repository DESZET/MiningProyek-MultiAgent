import { describe, it, expect, beforeEach } from "vitest";
import { getDeviceId, resetDeviceId, setDeviceId } from "@/lib/deviceId";

const KEY = "asahlagi-device-id";

describe("deviceId", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("generates and persists an id, returning the same one on re-read", () => {
    const first = getDeviceId();
    expect(first).toBeTruthy();
    expect(localStorage.getItem(KEY)).toBe(first);
    expect(getDeviceId()).toBe(first);
  });

  it("adopts a canonical id via setDeviceId", () => {
    setDeviceId("canonical-123");
    expect(getDeviceId()).toBe("canonical-123");
  });

  it("mints a fresh id on reset", () => {
    const before = getDeviceId();
    const after = resetDeviceId();
    expect(after).not.toBe(before);
    expect(getDeviceId()).toBe(after);
  });
});
