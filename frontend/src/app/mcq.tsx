"use client"

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import { mock } from "node:test";

interface Question {
  id: number;
  question: string;
  options: string[];
  correct_answer: string;
  difficulty: number;
  topic: string;
}

export default function MCQ() {
  const [data, setData] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [nextDifficulty, setNextDifficulty] = useState(false);

  useEffect(()=> {
    import('./sample.json')
    .then(module => {
      const data = module.default;
      setData(data); // FROM json to a list of objects
    })
    .catch(error => console.error('Error loading sample JSON', error));
  }, [])

  const handleNextQuestion = (question: Question) => {
    const isCorrect = answer === question.correct_answer;
    
    if (isCorrect) {
      setNextDifficulty(true);
    } else {
      setNextDifficulty(false);
    }

    // fetches the index of higher difficulty questions
    let highDiff = [];
    for (let i = 0; i < data.length; i++) {
      if (data[i].difficulty > question.difficulty) {
        highDiff.push(i);
      }
    }
    console.log(highDiff);

    // TESTING -> only move forward if correct
    if (isCorrect && highDiff.length > 0) {
        setCurrentIndex(highDiff[0]);
    } else {
        setCurrentIndex(currentIndex + 1);
    }

  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-background p-4">
      {data.length > 0 && (
        <Card className="w-full max-w-lg">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Question {data[currentIndex].id}</CardTitle>
            <Badge variant="outline">{data[currentIndex].difficulty}</Badge>
          </div>
          <CardDescription>Answer to proceed to the next (harder) question</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-lg font-medium mb-6">{data[currentIndex].question}</p>

          <RadioGroup defaultValue="">
            {data[currentIndex].options.map((opt, idx) => (
              <div key={idx} className="flex items-center space-x-2 mb-3">
                <RadioGroupItem value={opt} id={`opt-${idx}`} onClick={(e) => setAnswer(opt)}/>
                <Label htmlFor={`opt-${idx}`}>{opt}</Label>
              </div>
            ))}
          </RadioGroup>

          <div className="mt-8">
            <Progress value={20} className="mb-2" /> {/* Later: real progress */}
            <p className="text-sm text-muted-foreground text-center">20% complete</p>
          </div>
        </CardContent>
        <CardFooter className="flex justify-end">
          <Button onClick={() => handleNextQuestion(data[currentIndex])}>Submit & Next Question</Button>
        </CardFooter>
      </Card>
      )}
    </main>
  );
}
