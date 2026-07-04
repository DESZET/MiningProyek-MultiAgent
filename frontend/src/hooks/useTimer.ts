import { useEffect, useRef, useState } from "react";

interface UseTimerOptions {
  autoStart?: boolean;
  initialSeconds?: number;
}

/**
 * Counts elapsed seconds since start. Used by QuizPage to track time_taken_seconds.
 *
 * Usage:
 *   const { seconds, start, stop, reset } = useTimer({ autoStart: true });
 */
export function useTimer({
  autoStart = false,
  initialSeconds = 0,
}: UseTimerOptions = {}) {
  const [seconds, setSeconds] = useState(initialSeconds);
  const [running, setRunning] = useState(autoStart);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!running) return;
    intervalRef.current = setInterval(() => {
      setSeconds((s) => s + 1);
    }, 1000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [running]);

  return {
    seconds,
    running,
    start: () => setRunning(true),
    stop: () => setRunning(false),
    reset: () => {
      setSeconds(0);
      setRunning(false);
    },
  };
}
