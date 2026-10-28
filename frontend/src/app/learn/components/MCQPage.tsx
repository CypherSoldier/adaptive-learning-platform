"use client";

import { Button } from "@/components/ui/mcq_ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/mcq_ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/mcq_ui/radio-group";
import { Label } from "@/components/ui/mcq_ui/label";
import { Progress } from "@/components/ui/mcq_ui/progress";
import { Badge } from "@/components/ui/mcq_ui/badge";
import Question from "@/components/markdown_question";
import { useMCQ } from "@/app/learn/hooks/use-mcq";
import { useRouter } from "next/navigation";
import { Spinner } from "@/components/ui/spinner";

export default function MCQ({ trackId }: { trackId: number }) {
  const router = useRouter();
  const { authLoading, isLoggedIn, data, currentIndex, questionNumber, answer, setAnswer,
    completed, progress, marks, submitAnswer, loading, startNewSession, error,
    sessionType } = useMCQ(trackId);

  if (authLoading) return <main className="min-h-screen flex items-center justify-center bg-background"><p>Loading…</p></main>;
  if (loading) return <div className="min-h-screen flex items-center justify-center bg-background p-6"><p>Loading questions…</p><Spinner className="ml-4" /></div>;
  if (error) return (
    <main className="min-h-screen flex items-center justify-center bg-background p-6">
      <Card className="w-full max-w-md"><CardHeader><CardTitle>Session unavailable</CardTitle><CardDescription>{error}</CardDescription></CardHeader>
        <CardFooter className="justify-center"><Button onClick={startNewSession}>Try again</Button></CardFooter>
      </Card>
    </main>
  );

  return (
    <main className="min-h-screen flex items-center justify-center bg-background p-4">
      {data.length > 0 && !completed ? (
        <Card className="w-full max-w-lg">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>{sessionType === "onboarding" ? `Getting started · ${questionNumber}` : `Question ${questionNumber}`}</CardTitle>
              <Badge variant="outline">{data[currentIndex].difficulty}</Badge>
            </div>
            <CardDescription>{sessionType === "onboarding" ? "Answer the seeded questions to set your starting skill level." : "Answer to continue your adaptive session."}</CardDescription>
          </CardHeader>
          <CardContent>
            <Question question={data[currentIndex].question} />
            <RadioGroup key={currentIndex} defaultValue="">
              {data[currentIndex].options.map((opt, idx) => (
                <div key={idx} className="flex items-center space-x-2 mb-3">
                  <RadioGroupItem value={opt} id={`opt-${idx}`} onClick={() => setAnswer(idx)} />
                  <Label htmlFor={`opt-${idx}`}>{opt}</Label>
                </div>
              ))}
            </RadioGroup>
            <div className="mt-8"><Progress value={progress} className="mb-2" /><p className="text-sm text-muted-foreground text-center">{progress.toFixed(0)}%</p></div>
          </CardContent>
          <CardFooter className="flex justify-end"><Button onClick={submitAnswer} disabled={answer < 0}>Submit & Next Question</Button></CardFooter>
        </Card>
      ) : (
        <div className="min-h-screen flex items-center justify-center bg-background p-6">
          <Card className="w-full max-w-md text-center border-2 border-primary/30 shadow-lg">
            <CardHeader className="pb-2">
              <div className="mx-auto bg-primary/10 text-primary rounded-full w-20 h-20 flex items-center justify-center mb-4 text-4xl">🎉</div>
              {!isLoggedIn && <CardDescription className="text-lg mt-2">Create an account or log in to save your progress and build your skill profile.</CardDescription>}
              <CardTitle className="text-3xl">Session Complete!</CardTitle>
              <CardDescription className="text-lg mt-2">You got {marks} correct answers.</CardDescription>
            </CardHeader>
            <CardContent className="pt-4 pb-8"><p className="text-muted-foreground">Your progress has been saved.</p></CardContent>
            <CardFooter className="flex flex-col sm:flex-row justify-center gap-4">
              <Button variant="default" size="lg" onClick={startNewSession}>Start New Session</Button>
              <Button variant="outline" size="lg" onClick={() => router.push("/progress")}>View Progress</Button>
            </CardFooter>
          </Card>
        </div>
      )}
    </main>
  );
}
