import { describe, it, expect, beforeEach, vi } from "vitest";
import * as api from "@/services/api";
import { ApiException } from "@/types/api";
import { getDeviceId } from "@/lib/deviceId";

function jsonResponse(data: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: async () => data,
  } as unknown as Response;
}

const fetchMock = vi.fn();

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
  localStorage.clear();
});

describe("api — happy paths", () => {
  it("checkHealth GETs /health and returns the body", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ status: "ok", version: "1" }));
    const res = await api.checkHealth();
    expect(res).toEqual({ status: "ok", version: "1" });
    const [url, init] = fetchMock.mock.calls[0]!;
    expect(url).toContain("/health");
    expect(init.method).toBe("GET");
  });

  it("generateQuiz POSTs material to /quiz/generate", async () => {
    const quiz = { quiz_id: "q1", questions: [], total_questions: 0, generated_at: "x" };
    fetchMock.mockResolvedValue(jsonResponse(quiz));
    const res = await api.generateQuiz({ material_text: "halo dunia" });
    expect(res).toEqual(quiz);
    const [url, init] = fetchMock.mock.calls[0]!;
    expect(url).toContain("/quiz/generate");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ material_text: "halo dunia" });
  });

  it("generateQuiz forwards §4.3 settings in the body", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ quiz_id: "q1" }));
    await api.generateQuiz({
      material_text: "halo dunia",
      num_questions: 7,
      difficulty: "hard",
      shuffle_options: false,
    });
    const [, init] = fetchMock.mock.calls[0]!;
    expect(JSON.parse(init.body)).toEqual({
      material_text: "halo dunia",
      num_questions: 7,
      difficulty: "hard",
      shuffle_options: false,
    });
  });

  it("generateQuizFromPdf puts §4.3 settings on the query string", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ quiz_id: "pdf1" }));
    const file = new File(["%PDF-1.4"], "m.pdf", { type: "application/pdf" });
    await api.generateQuizFromPdf(file, {
      num_questions: 10,
      difficulty: "easy",
      shuffle_options: false,
    });
    const [url, init] = fetchMock.mock.calls[0]!;
    expect(url).toContain("/quiz/generate-from-pdf?");
    expect(url).toContain("num_questions=10");
    expect(url).toContain("difficulty=easy");
    expect(url).toContain("shuffle_options=false");
    expect(init.method).toBe("POST");
  });

  it("submitQuiz POSTs to /quiz/submit", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ quiz_id: "q1" }));
    await api.submitQuiz({ quiz_id: "q1", answers: [], time_taken_seconds: 5 });
    expect(fetchMock.mock.calls[0]![0]).toContain("/quiz/submit");
  });

  it("regenerateQuiz and generateQuizFromUrl hit their endpoints", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ quiz_id: "q2" }));
    await api.regenerateQuiz("q1");
    expect(fetchMock.mock.calls[0]![0]).toContain("/quiz/regenerate");

    fetchMock.mockResolvedValue(jsonResponse({ quiz_id: "q3" }));
    await api.generateQuizFromUrl({ url: "https://x.test" });
    expect(fetchMock.mock.calls[1]![0]).toContain("/quiz/generate-from-url");
  });

  it("getDailyChallenge GETs with a device id header", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ quiz_id: "daily-x" }));
    await api.getDailyChallenge();
    const [url, init] = fetchMock.mock.calls[0]!;
    expect(url).toContain("/quiz/daily-challenge");
    expect(init.headers["X-Device-Id"]).toBeTruthy();
  });
});

describe("api — error handling", () => {
  it("throws ApiException with code/status on a non-ok response", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse({ detail: "kosong", code: "MATERIAL_EMPTY" }, false, 422),
    );
    await expect(api.generateQuiz({ material_text: "" })).rejects.toMatchObject({
      status: 422,
    });
    await expect(
      api.generateQuiz({ material_text: "" }),
    ).rejects.toBeInstanceOf(ApiException);
  });

  it("maps a dropped connection to a status-0 ApiException", async () => {
    fetchMock.mockRejectedValue(new TypeError("network down"));
    await expect(api.submitQuiz({ quiz_id: "q", answers: [], time_taken_seconds: 1 }))
      .rejects.toMatchObject({ status: 0 });
  });

  it("maps an aborted (timeout) request to a 408 TIMEOUT ApiException", async () => {
    fetchMock.mockRejectedValue(
      new DOMException("The operation was aborted.", "AbortError"),
    );
    await expect(
      api.generateQuiz({ material_text: "x" }),
    ).rejects.toMatchObject({ status: 408, code: "TIMEOUT" });
  });
});

describe("api — auth + gamification", () => {
  it("loginWithGoogle posts the credential and adopts the returned device id", async () => {
    const user = {
      id: "u1",
      email: "a@b.c",
      name: "A",
      avatar_url: null,
      device_id: "canonical-xyz",
    };
    fetchMock.mockResolvedValue(jsonResponse(user));
    const res = await api.loginWithGoogle("google-cred");
    expect(res).toEqual(user);
    const [url, init] = fetchMock.mock.calls[0]!;
    expect(url).toContain("/auth/google");
    expect(JSON.parse(init.body).credential).toBe("google-cred");
    // Adopts the canonical device id for subsequent gamification calls.
    expect(getDeviceId()).toBe("canonical-xyz");
  });

  it("getGamificationStats returns data and sends the device header", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ total_xp: 10, level: 1 }));
    const stats = await api.getGamificationStats();
    expect(stats).toMatchObject({ total_xp: 10 });
    expect(fetchMock.mock.calls[0]![1].headers["X-Device-Id"]).toBeTruthy();
  });

  it("gamification calls return null on a non-ok response (graceful 503)", async () => {
    fetchMock.mockResolvedValue(jsonResponse({}, false, 503));
    expect(await api.getGamificationStats()).toBeNull();
    expect(await api.getGamificationAnalytics()).toBeNull();
    expect(await api.getGamificationHistory()).toBeNull();
    expect(await api.getAchievements()).toEqual([]);
  });

  it("gamification calls return null when fetch throws", async () => {
    fetchMock.mockRejectedValue(new Error("boom"));
    expect(await api.getGamificationStats()).toBeNull();
    expect(await api.getAchievements()).toEqual([]);
  });

  it("getGamificationHistory returns the full summary + items response", async () => {
    const payload = {
      summary: { total_quizzes: 2, average_score: 80, total_xp: 100, best_score: 90, worst_score: 70 },
      items: [{ quiz_id: "q1" }],
    };
    fetchMock.mockResolvedValue(jsonResponse(payload));
    expect(await api.getGamificationHistory(5)).toEqual(payload);
  });

  it("recordQuizAttempt POSTs the attempt", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ xp_earned: 10 }));
    await api.recordQuizAttempt({ quiz_id: "q1", score: 80, understanding_level: "high" });
    const [url, init] = fetchMock.mock.calls[0]!;
    expect(url).toContain("/gamification/record-attempt");
    expect(init.method).toBe("POST");
  });
});
