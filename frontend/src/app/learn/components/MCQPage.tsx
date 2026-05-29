"use client";

import { Button } from "@/components/ui/mcq_ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/mcq_ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/mcq_ui/radio-group";
import { Label } from "@/components/ui/mcq_ui/label";
import { Progress } from "@/components/ui/mcq_ui/progress";
import { Badge } from "@/components/ui/mcq_ui/badge";
import Question from '@/components/markdown_question';
import { useMCQ } from "@/app/learn/hooks/use-mcq";
import { useRouter } from "next/navigation";
import { Spinner } from "@/components/ui/spinner";
import axios from 'axios';

export default function MCQ({ trackId }: { trackId: number }) {
  const router = useRouter();
  const {
    authLoading, isLoggedIn,
    data, currentIndex, questionNumber,
    setAnswer, completed, progress,
    marks, submitAnswer, loading,
    resetSession,
  } = useMCQ(trackId);

  //if (!isLoggedIn) return null;

  if (authLoading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-background">
        <p className="text-muted-foreground">Loading…</p>
      </main>
    );
  }
  if (loading) return <Spinner />;

  const handleNewSession = async () => {
    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/questions/${trackId}`);
      const questions = response.data;

      if (questions.length === 0) {
        alert('No questions available. Please try again later.');
        return;
      }

      const selected = questions
        .sort(() => 0.5 - Math.random())
        .slice(0, 15);

      resetSession(selected); 
    } catch (error: any) {
      if (error.response?.data?.detail === 'complete_seeded_session') {
        alert('Login to complete your first session to unlock AI-generated questions and update your skill profile for AI-curated questions.');
      } else {
        console.error('Failed to load new session:', error);
      }
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-background p-4">
      {data.length > 0 && !completed ? (
        <Card className="w-full max-w-lg">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Question {questionNumber}</CardTitle>
              <Badge variant="outline">{data[currentIndex].difficulty}</Badge>
            </div>
            <CardDescription>
              Answer to proceed to the next (harder) question
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Question question={data[currentIndex].question} />
            <RadioGroup defaultValue="">
              {data[currentIndex].options.map((opt, idx) => (
                <div key={idx} className="flex items-center space-x-2 mb-3">
                  <RadioGroupItem
                    value={opt}
                    id={`opt-${idx}`}
                    onClick={() => setAnswer(idx)}
                  />
                  <Label htmlFor={`opt-${idx}`}>{opt}</Label>
                </div>
              ))}
            </RadioGroup>
            <div className="mt-8">
              <Progress value={progress} className="mb-2" />
              <p className="text-sm text-muted-foreground text-center">{progress.toFixed(0)}%</p>
            </div>
          </CardContent>
          <CardFooter className="flex justify-end">
            <Button onClick={submitAnswer}>Submit & Next Question</Button>
          </CardFooter>
        </Card>
      ) : (
        <div className="min-h-screen flex items-center justify-center bg-background p-6">
          <Card className="w-full max-w-md text-center border-2 border-primary/30 shadow-lg">
            <CardHeader className="pb-2">
              <div className="mx-auto bg-primary/10 text-primary rounded-full w-20 h-20 flex items-center justify-center mb-4 text-4xl">
                🎉
              </div>
              {!isLoggedIn && 
              <CardDescription className="text-lg mt-2">
                Create an account/login to get your correct answers to build your skill profile for the AI to generate questions based on your current skill level.
              </CardDescription>}
              <CardTitle className="text-3xl">Session Complete!</CardTitle>
              <CardDescription className="text-lg mt-2">
                You've conquered the adaptive challenge. You got {marks} correct answers!
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-4 pb-8">
              <p className="text-muted-foreground">
                Great job pushing through progressively harder questions. Your brain just leveled up.
              </p>
            </CardContent>
            <CardFooter className="flex flex-col sm:flex-row justify-center gap-4">
              <Button variant="default" size="lg" onClick={handleNewSession}>
                Start New Session
              </Button>
              <Button variant="outline" size="lg" onClick={() => router.push("/progress")}>
                View Progress
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}
    </main>
  );
}