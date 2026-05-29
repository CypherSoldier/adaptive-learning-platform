export interface Question {
  id: number;
  question: string;
  options: string[];
  correct_answer: number;
  difficulty: number;
  topic: string;
}

export interface GradeEntry {
  question_id: number;
  is_correct: boolean;
}