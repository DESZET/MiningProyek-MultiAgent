import { useCallback, useState } from "react";
import {
  generateQuiz,
  generateQuizFromPdf,
  generateQuizFromUrl,
  getDailyChallenge,
  regenerateQuiz,
  submitQuiz,
} from "@/services/api";
import type {
  QuizGenerateResponse,
  QuizSettings,
  QuizSubmitRequest,
} from "@/types/quiz";
import type { QuizSubmitResponse } from "@/types/result";
import { ApiException } from "@/types/api";

interface UseQuizState {
  generating: boolean;
  submitting: boolean;
  generateError: ApiException | null;
  submitError: ApiException | null;
}

/**
 * Hook for orchestrating the generate (text/url/pdf) + submit flow.
 * Owns the loading/error states; pages own the navigation between them.
 */
export function useQuiz() {
  const [state, setState] = useState<UseQuizState>({
    generating: false,
    submitting: false,
    generateError: null,
    submitError: null,
  });

  function toApiException(err: unknown): ApiException {
    return err instanceof ApiException
      ? err
      : new ApiException({ detail: "Terjadi kesalahan tak terduga." }, 0);
  }

  const generateFromText = useCallback(
    async (
      materialText: string,
      settings?: Partial<QuizSettings>,
    ): Promise<QuizGenerateResponse | null> => {
      setState((s) => ({ ...s, generating: true, generateError: null }));
      try {
        const res = await generateQuiz({
          material_text: materialText,
          ...settings,
        });
        setState((s) => ({ ...s, generating: false }));
        return res;
      } catch (err) {
        setState((s) => ({
          ...s,
          generating: false,
          generateError: toApiException(err),
        }));
        return null;
      }
    },
    [],
  );

  const generateFromUrl = useCallback(
    async (
      url: string,
      settings?: Partial<QuizSettings>,
    ): Promise<QuizGenerateResponse | null> => {
      setState((s) => ({ ...s, generating: true, generateError: null }));
      try {
        const res = await generateQuizFromUrl({ url, ...settings });
        setState((s) => ({ ...s, generating: false }));
        return res;
      } catch (err) {
        setState((s) => ({
          ...s,
          generating: false,
          generateError: toApiException(err),
        }));
        return null;
      }
    },
    [],
  );

  const generateFromPdf = useCallback(
    async (
      file: File,
      settings?: Partial<QuizSettings>,
    ): Promise<QuizGenerateResponse | null> => {
      setState((s) => ({ ...s, generating: true, generateError: null }));
      try {
        const res = await generateQuizFromPdf(file, settings);
        setState((s) => ({ ...s, generating: false }));
        return res;
      } catch (err) {
        setState((s) => ({
          ...s,
          generating: false,
          generateError: toApiException(err),
        }));
        return null;
      }
    },
    [],
  );

  const regenerate = useCallback(
    async (quizId: string): Promise<QuizGenerateResponse | null> => {
      setState((s) => ({ ...s, generating: true, generateError: null }));
      try {
        const res = await regenerateQuiz(quizId);
        setState((s) => ({ ...s, generating: false }));
        return res;
      } catch (err) {
        setState((s) => ({
          ...s,
          generating: false,
          generateError: toApiException(err),
        }));
        return null;
      }
    },
    [],
  );

  const startDailyChallenge = useCallback(
    async (): Promise<QuizGenerateResponse | null> => {
      setState((s) => ({ ...s, generating: true, generateError: null }));
      try {
        const res = await getDailyChallenge();
        setState((s) => ({ ...s, generating: false }));
        return res;
      } catch (err) {
        setState((s) => ({
          ...s,
          generating: false,
          generateError: toApiException(err),
        }));
        return null;
      }
    },
    [],
  );

  const submit = useCallback(
    async (req: QuizSubmitRequest): Promise<QuizSubmitResponse | null> => {
      setState((s) => ({ ...s, submitting: true, submitError: null }));
      try {
        const res = await submitQuiz(req);
        setState((s) => ({ ...s, submitting: false }));
        return res;
      } catch (err) {
        setState((s) => ({
          ...s,
          submitting: false,
          submitError: toApiException(err),
        }));
        return null;
      }
    },
    [],
  );

  return {
    ...state,
    generateFromText,
    generateFromUrl,
    generateFromPdf,
    regenerate,
    startDailyChallenge,
    submit,
  };
}
