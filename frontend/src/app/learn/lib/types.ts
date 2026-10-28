export interface Question {
  id: number;
  question: string;
  options: string[];
  correct_answer: number;
  difficulty: number;
  track_id?: number;
  source?: string;
  explanation?: string;
  topic?: string;
}

export interface SessionResponse {
  session_id: string;
  session_type: "onboarding" | "ai";
  track_id: number;
  questions: Question[];
}

export interface GradeEntry { question_id: number; is_correct: boolean; }
export interface SkillProfile {
  track_id: number; skill_score: number; user_id: number; attempts: number;
  id: number; confidence_score: number;
}
