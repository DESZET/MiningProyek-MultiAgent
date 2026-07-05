/**
 * API client — single source of all backend HTTP access.
 * Implements the contract defined in API.md §10.
 *
 * Components MUST NOT call fetch() directly. Always go through this module.
 */

import type {
  QuizGenerateFromUrlRequest,
  QuizGenerateRequest,
  QuizGenerateResponse,
  QuizSettings,
  QuizSubmitRequest,
} from "@/types/quiz";
import type { QuizSubmitResponse } from "@/types/result";
import type {
  ChatHistoryResponse,
  ChatRequest,
  ChatResponse,
  FreeChatRequest,
  FreeChatResponse,
} from "@/types/chat";
import type { ApiError } from "@/types/api";
import { ApiException } from "@/types/api";
import type {
  Badge,
  Bookmark,
  BookmarkList,
  GamificationStats,
  GamificationAnalytics,
  HistoryResponse,
  LeaderboardResponse,
  RecordAttemptResult,
  UserPreferences,
  WeeklyProgress,
} from "@/types/gamification";
import type { AuthUser } from "@/types/auth";
import { getDeviceId, setDeviceId } from "@/lib/deviceId";

const BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000";

// Default timeout for most endpoints
const DEFAULT_TIMEOUT_MS = 10_000;

// Submit goes through multi-agent orchestrator (Evaluator + Insight LLM) — can take 20-40s
const QUIZ_SUBMIT_TIMEOUT_MS = 60_000;

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs: number,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timeoutId);
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errBody: ApiError;
    try {
      errBody = (await res.json()) as ApiError;
    } catch {
      errBody = { detail: "Terjadi kesalahan tak terduga." };
    }
    throw new ApiException(errBody, res.status);
  }
  return (await res.json()) as T;
}

function networkErrorToApiException(err: unknown): ApiException {
  if (err instanceof DOMException && err.name === "AbortError") {
    return new ApiException(
      {
        detail:
          "Permintaan terlalu lama. Coba lagi sebentar, sistem sedang menyiapkan model.",
        code: "TIMEOUT",
      },
      408,
    );
  }
  return new ApiException(
    { detail: "Koneksi terputus. Pastikan kamu terhubung ke internet." },
    0,
  );
}

async function postJson<TReq, TRes>(
  path: string,
  body: TReq,
  timeoutMs: number = DEFAULT_TIMEOUT_MS,
  headers?: Record<string, string>,
): Promise<TRes> {
  let res: Response;
  try {
    res = await fetchWithTimeout(
      `${BASE_URL}${path}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json", ...headers },
        body: JSON.stringify(body),
      },
      timeoutMs,
    );
  } catch (err) {
    throw networkErrorToApiException(err);
  }
  return handleResponse<TRes>(res);
}

async function getJson<TRes>(
  path: string,
  timeoutMs: number = DEFAULT_TIMEOUT_MS,
  headers?: Record<string, string>,
): Promise<TRes> {
  let res: Response;
  try {
    res = await fetchWithTimeout(
      `${BASE_URL}${path}`,
      { method: "GET", headers },
      timeoutMs,
    );
  } catch (err) {
    throw networkErrorToApiException(err);
  }
  return handleResponse<TRes>(res);
}

// ============================================================================
// Public API
// ============================================================================

export interface HealthResponse {
  status: "ok";
  version: string;
}

export function checkHealth(): Promise<HealthResponse> {
  return getJson<HealthResponse>("/health");
}

export function generateQuiz(
  req: QuizGenerateRequest,
): Promise<QuizGenerateResponse> {
  return postJson<QuizGenerateRequest, QuizGenerateResponse>(
    "/quiz/generate",
    req,
    QUIZ_GENERATE_TIMEOUT_MS,
  );
}

export function generateQuizFromUrl(
  req: QuizGenerateFromUrlRequest,
): Promise<QuizGenerateResponse> {
  return postJson<QuizGenerateFromUrlRequest, QuizGenerateResponse>(
    "/quiz/generate-from-url",
    req,
    QUIZ_GENERATE_TIMEOUT_MS,
  );
}

export async function generateQuizFromPdf(
  file: File,
  settings?: Partial<QuizSettings>,
): Promise<QuizGenerateResponse> {
  const formData = new FormData();
  formData.append("file", file);

  // §4.3 settings go on the query string — the body is multipart for the file.
  const params = new URLSearchParams();
  if (settings?.num_questions != null)
    params.set("num_questions", String(settings.num_questions));
  if (settings?.difficulty) params.set("difficulty", settings.difficulty);
  if (settings?.shuffle_options != null)
    params.set("shuffle_options", String(settings.shuffle_options));
  const query = params.toString();

  let res: Response;
  try {
    res = await fetchWithTimeout(
      `${BASE_URL}/quiz/generate-from-pdf${query ? `?${query}` : ""}`,
      { method: "POST", body: formData },
      QUIZ_GENERATE_TIMEOUT_MS,
    );
  } catch (err) {
    throw networkErrorToApiException(err);
  }
  return handleResponse<QuizGenerateResponse>(res);
}

export function submitQuiz(
  req: QuizSubmitRequest,
): Promise<QuizSubmitResponse> {
  return postJson<QuizSubmitRequest, QuizSubmitResponse>("/quiz/submit", req, QUIZ_SUBMIT_TIMEOUT_MS);
}

/**
 * Today's Daily Challenge quiz (curated, +50 XP bonus on first completion).
 * Cached server-side per day, so the first request of the day runs DL inference
 * (slow) and the rest are fast — hence the long generate timeout. The device id
 * is sent so the backend can pick an adaptive difficulty.
 */
export async function getDailyChallenge(): Promise<QuizGenerateResponse> {
  let res: Response;
  try {
    res = await fetchWithTimeout(
      `${BASE_URL}/quiz/daily-challenge`,
      { method: "GET", headers: { "X-Device-Id": getDeviceId() } },
      QUIZ_GENERATE_TIMEOUT_MS,
    );
  } catch (err) {
    throw networkErrorToApiException(err);
  }
  return handleResponse<QuizGenerateResponse>(res);
}

// ============================================================================
// Auth — Google login. Throws ApiException on failure (caller handles it).
// ============================================================================

/**
 * Verify a Google ID token (credential) with the backend and link/create the
 * account. The caller's current anonymous device id is sent so guest progress
 * carries over; on success the client adopts the returned canonical device id.
 */
export async function loginWithGoogle(credential: string): Promise<AuthUser> {
  const user = await postJson<
    { credential: string; device_id: string },
    AuthUser
  >("/auth/google", { credential, device_id: getDeviceId() });
  setDeviceId(user.device_id);
  return user;
}

// ============================================================================
// Gamification — non-blocking. All methods return null on any failure
// (including 503 when DATABASE_URL is unset) so quiz UX is never blocked.
// ============================================================================

async function gamificationFetch<T>(
  path: string,
  init: RequestInit,
): Promise<T | null> {
  try {
    const res = await fetchWithTimeout(
      `${BASE_URL}${path}`,
      {
        ...init,
        headers: { ...init.headers, "X-Device-Id": getDeviceId() },
      },
      DEFAULT_TIMEOUT_MS,
    );
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export function getGamificationStats(): Promise<GamificationStats | null> {
  return gamificationFetch<GamificationStats>("/gamification/stats", {
    method: "GET",
  });
}

export function recordQuizAttempt(body: {
  quiz_id: string;
  score: number;
  understanding_level: string;
}): Promise<RecordAttemptResult | null> {
  return gamificationFetch<RecordAttemptResult>("/gamification/record-attempt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

/**
 * Quiz history (summary + items). Returns null when gamification is unavailable
 * (503 / network failure) so the History page can show a graceful "off" state.
 */
export function getGamificationHistory(
  limit = 10,
): Promise<HistoryResponse | null> {
  return gamificationFetch<HistoryResponse>(
    `/gamification/history?limit=${limit}`,
    { method: "GET" },
  );
}

export async function getGamificationAnalytics(): Promise<GamificationAnalytics | null> {
  return gamificationFetch<GamificationAnalytics>("/gamification/analytics", {
    method: "GET",
  });
}

export async function getAchievements(): Promise<Badge[]> {
  const res = await gamificationFetch<Badge[]>("/gamification/achievements", {
    method: "GET",
  });
  return res ?? [];
}

export function getLeaderboard(
  limit = 20,
): Promise<LeaderboardResponse | null> {
  return gamificationFetch<LeaderboardResponse>(
    `/gamification/leaderboard?limit=${limit}`,
    { method: "GET" },
  );
}

export function getWeeklyProgress(): Promise<WeeklyProgress | null> {
  return gamificationFetch<WeeklyProgress>("/gamification/weekly-progress", {
    method: "GET",
  });
}

// §4.8 Batch 2-B — preferences + bookmarks (need migration 0005; return null
// until the tables exist, so the UI degrades gracefully).

export function getPreferences(): Promise<UserPreferences | null> {
  return gamificationFetch<UserPreferences>("/gamification/preferences", {
    method: "GET",
  });
}

export function updatePreferences(
  changes: Partial<UserPreferences>,
): Promise<UserPreferences | null> {
  return gamificationFetch<UserPreferences>("/gamification/preferences", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(changes),
  });
}

export function getBookmarks(): Promise<BookmarkList | null> {
  return gamificationFetch<BookmarkList>("/gamification/bookmarks", {
    method: "GET",
  });
}

export function createBookmark(body: {
  title: string;
  material_text: string;
}): Promise<Bookmark | null> {
  return gamificationFetch<Bookmark>("/gamification/bookmarks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function deleteBookmark(id: string): Promise<boolean> {
  const res = await gamificationFetch<{ deleted: boolean }>(
    `/gamification/bookmarks/${id}`,
    { method: "DELETE" },
  );
  return res != null;
}

export function regenerateQuiz(
  quizId: string,
): Promise<QuizGenerateResponse> {
  return postJson<{ quiz_id: string }, QuizGenerateResponse>(
    "/quiz/regenerate",
    { quiz_id: quizId },
    QUIZ_GENERATE_TIMEOUT_MS,
  );
}

// Asahi chatbot — model call can take a few seconds; give headroom.
const CHAT_TIMEOUT_MS = 35_000;

export function sendChat(req: ChatRequest): Promise<ChatResponse> {
  return postJson<ChatRequest, ChatResponse>("/chat", req, CHAT_TIMEOUT_MS);
}

export function askAsahi(req: FreeChatRequest): Promise<FreeChatResponse> {
  return postJson<FreeChatRequest, FreeChatResponse>("/chat/ask", req, CHAT_TIMEOUT_MS, {
    "X-Device-Id": getDeviceId(),
  });
}

export function getAsahiHistory(): Promise<ChatHistoryResponse> {
  return getJson<ChatHistoryResponse>("/chat/history", DEFAULT_TIMEOUT_MS, {
    "X-Device-Id": getDeviceId(),
  });
}

// Quiz generation goes through multi-agent orchestrator (Extractor + Quiz Maker + LLM polish)
// can take 15-30s. 90s gives headroom for cold HF Space start.
const QUIZ_GENERATE_TIMEOUT_MS = 90_000;
