export type ExperienceLevel = "beginner" | "intermediate" | "advanced";

export type SegmentStatus = "locked" | "upcoming" | "in_progress" | "completed" | "needs_review";

export type FeedbackType = "too_easy" | "too_difficult" | "already_know" | "need_more_practice" | "not_relevant" | "helpful" | "not_helpful" | "custom";

export interface Profile {
  id: string;
  user_id: string;
  name: string;
  experience_level: ExperienceLevel;
  occupation?: string;
  preferred_language: string;
  weekly_hours: number;
  preferred_learning_style?: string;
  created_at: string;
}

export interface Skill {
  id: string;
  name: string;
  category?: string;
  description?: string;
}

export interface UserSkill {
  skill_id: string;
  skill_name?: string;
  current_level: ExperienceLevel;
  confidence: number;
}

export interface SkillGap {
  skill_name: string;
  skill_id: string;
  current_level: string;
  target_level: string;
  gap: "none" | "low" | "medium" | "high" | "critical";
  importance: number;
  prerequisites: string[];
  recommended_action: string;
}

export interface Goal {
  id: string;
  user_id: string;
  raw_goal: string;
  target_role?: string;
  target_domain?: string;
  target_level?: string;
  status: string;
}

export interface GoalAnalysis {
  goal: string;
  target_role: string;
  domain: string;
  target_skills: string[];
  optional_skills: string[];
  likely_prerequisites: string[];
  estimated_difficulty: string;
  suggested_milestones: string[];
}

export interface Resource {
  id: string;
  provider: string;
  external_id: string;
  title: string;
  description?: string;
  url: string;
  thumbnail?: string;
  resource_type: string;
  difficulty?: string;
  duration?: string;
  metadata: Record<string, unknown>;
  recommendation_score?: number;
  recommendation_reason?: string;
}

export interface LearningPath {
  id: string;
  user_id: string;
  goal_id: string;
  title: string;
  description?: string;
  estimated_duration?: string;
  status: string;
  version: number;
  segments: LearningSegment[];
}

export interface LearningSegment {
  id: string;
  learning_path_id: string;
  title: string;
  overview?: string;
  sequence: number;
  estimated_duration?: string;
  status: SegmentStatus;
  skills: string[];
  resources: Resource[];
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  skill_tested: string;
  difficulty: string;
}

export interface QuizResult {
  quiz_id: string;
  score: number;
  total_questions: number;
  correct_answers: number;
  skill_assessment: Record<string, unknown>[];
  weak_concepts: string[];
  strong_concepts: string[];
  recommended_action: string;
}

export interface MentorMessage {
  role: "user" | "assistant";
  content: string;
}

export interface DashboardData {
  progress: {
    overall_percentage: number;
    segments_completed: number;
    total_segments: number;
    resources_completed: number;
    hours_learned: number;
    current_streak: number;
  };
  skills: UserSkill[];
  learning_path: LearningPath | null;
}

export interface OnboardingData {
  profile: {
    name: string;
    experience_level: ExperienceLevel;
    occupation?: string;
    preferred_language: string;
    weekly_hours: number;
    preferred_learning_style?: string;
  };
  interests: string[];
  skills: { skill_id: string; current_level: ExperienceLevel; confidence: number }[];
  previous_learning: string[];
  goal: string;
  preferences: Record<string, unknown>;
}
