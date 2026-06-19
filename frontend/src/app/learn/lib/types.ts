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

export interface SkillProfile {
  track_id: number;
  skill_score: number;
  user_id: number;
  attempts: number;
  id: number;
  confidence_score: number;
}