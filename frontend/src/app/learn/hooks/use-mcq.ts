import { useEffect, useState, useContext, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import AuthContext from "@/app/context/AuthContext";
import { Question, GradeEntry, SessionResponse } from "../lib/types";

export function useMCQ(trackId: number) {
  const { isLoggedIn, authLoading, user } = useContext(AuthContext);
  const router = useRouter();
  const [data, setData] = useState<Question[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionType, setSessionType] = useState<"onboarding" | "ai" | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState(-1);
  const [completed, setCompleted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [grade, setGrade] = useState<GradeEntry[]>([]);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const dataRef = useRef<Question[]>(data);
  const currentIndexRef = useRef(currentIndex);
  const marks = grade.filter((entry) => entry.is_correct).length;

  useEffect(() => { dataRef.current = data; }, [data]);
  useEffect(() => { currentIndexRef.current = currentIndex; }, [currentIndex]);

  useEffect(() => {
    if (!authLoading && !isLoggedIn) {
      const name = trackId === 1 ? "python" : trackId === 2 ? "cpp" : "javascript";
      router.push(`/learn/${name}`);
    }
  }, [authLoading, isLoggedIn, router, trackId]);

  const loadServerSession = useCallback(async (key: string) => {
    const response = await axios.post<SessionResponse>(
      `${process.env.NEXT_PUBLIC_API_URL}/sessions/${trackId}`,
      {}, { headers: { "Idempotency-Key": key } },
    );
    return response.data;
  }, [trackId]);

  const applySession = useCallback((session: SessionResponse) => {
    const cursorKey = `learning-session-index:${session.session_id}`;
    const savedIndex = Number(sessionStorage.getItem(cursorKey) || 0);
    const index = Number.isInteger(savedIndex)
      ? Math.max(0, Math.min(savedIndex, session.questions.length))
      : 0;
    setData(session.questions);
    setSessionId(session.session_id);
    setSessionType(session.session_type);
    setCurrentIndex(index);
    setCompleted(session.questions.length > 0 && index >= session.questions.length);
    setProgress(session.questions.length ? (index / session.questions.length) * 100 : 0);
    setQuestionNumber(index + 1);
    setAnswer(-1);
    setGrade([]);
    dataRef.current = session.questions;
    currentIndexRef.current = index;
    if (session.questions.length > 0 && index >= session.questions.length && user?.user_id) {
      sessionStorage.removeItem(`learning-session-key:v2:${user.user_id}:${trackId}`);
    }
  }, [trackId, user?.user_id]);

  useEffect(() => {
    if (authLoading) return;
    if (!isLoggedIn) {
      import("./sample.json").then((module) => {
        const trackName = trackId === 1 ? "Python" : trackId === 2 ? "C++" : "JavaScript";
        const preview = module.default.filter((q) => q.topic === trackName) as Question[];
        setData(preview);
        setLoading(false);
      }).catch(() => {
        setError("Could not load the question preview.");
        setLoading(false);
      });
      return;
    }
    if (!user?.user_id) return;
    let active = true;
    setLoading(true);
    setError(null);
    const scope = `${user.user_id}:${trackId}`;
    const storageKey = `learning-session-key:v2:${scope}`;
    let key = sessionStorage.getItem(storageKey);
    if (!key) {
      key = crypto.randomUUID();
      sessionStorage.setItem(storageKey, key);
    }
    loadServerSession(key).then((session) => {
      if (!active) return;
      applySession(session);
      setLoading(false);
      if (!session.questions.length) setError("There are no questions available for this session.");
    }).catch(async (err) => {
      if (!active) return;
      console.error("Error loading session:", err);
      const detail = err?.response?.data?.detail;
      const staleKey = err?.response?.status === 409 &&
        (String(detail).includes("Idempotency key was already used") || String(detail).includes("Session changed concurrently"));
      if (staleKey) {
        const replacementKey = crypto.randomUUID();
        sessionStorage.setItem(storageKey, replacementKey);
        try {
          const session = await loadServerSession(replacementKey);
          if (!active) return;
          applySession(session);
          setLoading(false);
          return;
        } catch (retryError) {
          console.error("Retrying with a fresh session key failed:", retryError);
        }
      }
      setError(detail || "Could not load a session. Please try again.");
      setLoading(false);
    });
    return () => { active = false; };
  }, [authLoading, isLoggedIn, trackId, user?.user_id, loadServerSession, applySession]);

  const startNewSession = useCallback(async () => {
    if (!user?.user_id) return;
    setLoading(true);
    setError(null);
    const scope = `${user.user_id}:${trackId}`;
    const storageKey = `learning-session-key:v2:${scope}`;
    const key = crypto.randomUUID();
    sessionStorage.setItem(storageKey, key);
    try {
      const session = await loadServerSession(key);
      applySession(session);
      setError(null);
    } catch (err: any) {
      console.error("Failed to load new session:", err);
      setError(err?.response?.data?.detail || "Could not start a new session. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [applySession, loadServerSession, trackId, user?.user_id]);

  const submitAnswer = async () => {
    const currentData = dataRef.current;
    const idx = currentIndexRef.current;
    const question = currentData[idx];
    if (!question) return;
    if (isLoggedIn) {
      if (!sessionId) return;
      try {
        const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/submissions`, {
          question_id: question.id, answer, track_id: trackId, session_id: sessionId,
        });
        const isCorrect = response.data.submission.is_correct;
        setGrade((prev) => [...prev, { question_id: question.id, is_correct: isCorrect }]);
      } catch (err: any) {
        console.error("Error submitting answer:", err);
        setError(err?.response?.data?.detail || "Could not submit your answer. Please try again.");
        return;
      }
    } else {
      setGrade((prev) => [...prev, { question_id: question.id, is_correct: false }]);
    }
    const nextIndex = idx + 1;
    setCurrentIndex(nextIndex);
    currentIndexRef.current = nextIndex;
    setProgress((nextIndex / currentData.length) * 100);
    setQuestionNumber((n) => n + 1);
    setAnswer(-1);
    if (sessionId) {
      sessionStorage.setItem(`learning-session-index:${sessionId}`, String(nextIndex));
    }
    if (nextIndex >= currentData.length) {
      setCompleted(true);
      if (isLoggedIn && user?.user_id) {
        sessionStorage.removeItem(`learning-session-key:v2:${user.user_id}:${trackId}`);
      }
    }
  };

  return { authLoading, isLoggedIn, questionNumber, answer, setAnswer, completed,
    progress, marks, submitAnswer, startNewSession, data, currentIndex, loading,
    error, sessionType };
}
