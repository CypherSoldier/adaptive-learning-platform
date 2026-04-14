"use client";

import { Button } from "@/components/ui/mcq_ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/mcq_ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/mcq_ui/radio-group";
import { Label } from "@/components/ui/mcq_ui/label";
import { Progress } from "@/components/ui/mcq_ui/progress";
import { Badge } from "@/components/ui/mcq_ui/badge";
import { useEffect, useState } from "react";
import { mock } from "node:test";
import { redirect } from 'next/navigation';

interface Question {
  id: number;
  question: string;
  options: string[];
  correct_answer: string;
  difficulty: number;
  topic: string;
}

interface GradeEntry {
  question_id: number;
  is_correct: boolean;
}


export default function MCQ() {
  const [data, setData] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [completed, setCompleted] = useState(false);
  const [progress, setProgress] = useState(0.00);
  const [grade, setGrade] = useState<GradeEntry[]>([]);
  const [marks, setMarks] = useState(0);

  const user =  false; //await getCurrentUser();

  if (!user) {
    redirect('/login?redirect=/learn/python');
  }

  useEffect(() => {
    import("../sample.json")
      .then((module) => {
        const data = module.default;
        const js_data = data.filter((q) => q.topic === "JavaScript");
        setData(js_data); // FROM json to a list of objects
      })
      .catch((error) => console.error("Error loading sample JSON", error));
  }, []);

  useEffect(() => {
    completed && setMarks(
      // or grade.filter(g => g.is_correct).length
      grade.filter(g => g.is_correct === true).length
    )
  }, [completed, grade])

  const handleNextQuestion = (question: Question) => {
    const isCorrect = answer === question.correct_answer;

    const inputAnswer = {
      question_id: question.id,
      is_correct: isCorrect,
    };
    setGrade(prevGrade => [...prevGrade, inputAnswer]);

    // fetches the index of higher difficulty questions
    let highDiff = [];
    for (let i = 0; i < data.length; i++) {
      if (data[i].difficulty > question.difficulty) {
        highDiff.push(i);
      }
    }

    // TESTING -> only move forward if correct
    if (isCorrect && highDiff.length > 0) {
      setCurrentIndex(highDiff[0]);
    } else {
      highDiff.length > 0
        ? setCurrentIndex(currentIndex + 1)
        : setCompleted(true);
    }

    let percentage = ((currentIndex + 1) / data.length) * 100
    setProgress(percentage);
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-background p-4">
      {data.length > 0 && !completed ? (
        <Card className="w-full max-w-lg">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Question {data[currentIndex].id}</CardTitle>
              <Badge variant="outline">{data[currentIndex].difficulty}</Badge>
            </div>
            <CardDescription>
              Answer to proceed to the next (harder) question
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-lg font-medium mb-6">
              {data[currentIndex].question}
            </p>

            <RadioGroup defaultValue="">
              {data[currentIndex].options.map((opt, idx) => (
                <div key={idx} className="flex items-center space-x-2 mb-3">
                  <RadioGroupItem
                    value={opt}
                    id={`opt-${idx}`}
                    onClick={(e) => setAnswer(opt)}
                  />
                  <Label htmlFor={`opt-${idx}`}>{opt}</Label>
                </div>
              ))}
            </RadioGroup>

            <div className="mt-8">
              <Progress value={progress} className="mb-2" />{" "}
              {/* Later: real progress */}
              <p className="text-sm text-muted-foreground text-center">
                {progress}
              </p>
            </div>
          </CardContent>
          <CardFooter className="flex justify-end">
            <Button onClick={() => handleNextQuestion(data[currentIndex])}>
              Submit & Next Question
            </Button>
          </CardFooter>
        </Card>
      ) : (
        <div className="min-h-screen flex items-center justify-center bg-background p-6">
          <Card className="w-full max-w-md text-center border-2 border-primary/30 shadow-lg">
            <CardHeader className="pb-2">
              <div className="mx-auto bg-primary/10 text-primary rounded-full w-20 h-20 flex items-center justify-center mb-4 text-4xl">
                🎉
              </div>
              <CardTitle className="text-3xl">Session Complete!</CardTitle>
              <CardDescription className="text-lg mt-2">
                You've conquered the adaptive challenge. You got {marks} correct answers! 
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-4 pb-8">
              <p className="text-muted-foreground">
                Great job pushing through progressively harder questions. Your
                brain just leveled up.
              </p>
            </CardContent>
            <CardFooter className="flex flex-col sm:flex-row justify-center gap-4">
              <Button variant="default" size="lg">
                <a href="/">Start New Session</a>
              </Button>
              <Button variant="outline" size="lg">
                <a href="/dashboard">View Progress</a>{" "}
                {/* or wherever your summary lives later */}
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}
    </main>
  );
}
