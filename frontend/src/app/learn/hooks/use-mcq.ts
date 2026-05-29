import { useEffect, useState, useContext, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import AuthContext from "@/app/context/AuthContext";
import { Question, GradeEntry } from "../lib/types";

function grabHighDiff(question: Question, data: Question[]) {
    let highDiff = [];
    for (let i = 0; i < data.length; i++) {
        if (data[i].difficulty > question.difficulty) {
            highDiff.push(i);
        }
    }
    return highDiff;
}

export function useMCQ(trackId: number) {
  const { isLoggedIn, authLoading } = useContext(AuthContext);
  const router = useRouter();

  const [data, setData] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [grade, setGrade] = useState<GradeEntry[]>([]);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [loading, setLoading] = useState(true);

  // Ref mirrors data so submitAnswer always sees the latest array
  const dataRef = useRef<Question[]>(data);
  const currentIndexRef = useRef<number>(currentIndex);

  useEffect(() => { dataRef.current = data; }, [data]);
  useEffect(() => { currentIndexRef.current = currentIndex; }, [currentIndex]);

  const marks = grade.filter((g) => g.is_correct).length;

  useEffect(() => {
    if (!authLoading && !isLoggedIn) {
      //router.push(`/login?redirect=/learn/${trackId}`)
      let name;
      if (trackId === 1) {
        name = "py";
      } else if (trackId === 2) {
        name = "cpp";
      } else {
        name = "js";
      }
      router.push(`/learn/${name}`);
    }
  }, [authLoading, isLoggedIn, router, trackId]);

  // load sample question for a user not logged in
  useEffect(() => {
    if (!isLoggedIn) {
      import("./sample.json")
        .then((module) => {
          const data = module.default;
          let filtered_data;
          if (trackId === 1) {
            filtered_data = data.filter((q) => q.topic === "Python");
          } else if (trackId === 2) {
            filtered_data = data.filter((q) => q.topic === "C++");
          } else {
            filtered_data = data.filter((q) => q.topic === "JavaScript");
          }

          setData(filtered_data);
          setLoading(false);
        })
        .catch((error) => console.error("Error loading sample JSON", error));
    }
  }, [isLoggedIn, trackId]);

  useEffect(() => {
    if (!isLoggedIn) return;
    axios
      .get(`${process.env.NEXT_PUBLIC_API_URL}/questions/${trackId}`)
      .then((res) => {
        setData(res.data);
        setLoading(false);
      })
      .catch((err) => console.error("Error fetching questions:", err));
  }, [isLoggedIn, trackId]);

  const resetSession = useCallback((newQuestions: Question[]) => {
    setData(newQuestions);
    setCurrentIndex(0);
    setCompleted(false);
    setProgress(0);
    setGrade([]);
    setAnswer(0);
    setQuestionNumber(1);
    // Keep the refs in sync immediately so the very first submitAnswer
    // after a reset reads the new data, not the old
    dataRef.current = newQuestions;
    currentIndexRef.current = 0;
  }, []);

  const submitAnswer = async () => {
    // Read from refs — always current, never stale
    const currentData = dataRef.current;
    const idx = currentIndexRef.current;
    const question = currentData[idx];

    if (!question) return;

    if (isLoggedIn) {
    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/submissions`, {
        question_id: question.id,
        answer,
        track_id: trackId,
      });
      const { submission } = response.data;
      const isCorrect = submission.is_correct;

      setGrade((prev) => [...prev, { question_id: question.id, is_correct: isCorrect }]);

      const highDiff = grabHighDiff(question, currentData);

      if (isCorrect && highDiff.length > 0) {
        setCurrentIndex(highDiff[0]);
      } else if (highDiff.length > 0) {
        setCurrentIndex((i) => i + 1);
      } else {
        setCompleted(true);
      }

      setProgress(((idx + 1) / currentData.length) * 100);
      setQuestionNumber((n) => n + 1);
    } catch (err) {
      console.error("Error submitting answer:", err);
    }
  } else {
      const highDiff = grabHighDiff(question, currentData);

      if ( highDiff.length > 0) {
        setCurrentIndex(highDiff[0]);
      } else if (highDiff.length > 0) {
        setCurrentIndex((i) => i + 1);
      } else {
        setCompleted(true);
      }

      setProgress(((idx + 1) / currentData.length) * 100);
      setQuestionNumber((n) => n + 1);
  }
  };

  return {
    authLoading,
    isLoggedIn,
    questionNumber,
    answer,
    setAnswer,
    completed,
    progress,
    marks,
    submitAnswer,
    resetSession, 
    data,
    currentIndex,
    loading,
  };
}