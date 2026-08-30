from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class SegmentStatus(str, Enum):
    locked = "locked"
    upcoming = "upcoming"
    in_progress = "in_progress"
    completed = "completed"
    needs_review = "needs_review"


class FeedbackType(str, Enum):
    too_easy = "too_easy"
    too_difficult = "too_difficult"
    already_know = "already_know"
    need_more_practice = "need_more_practice"
    not_relevant = "not_relevant"
    helpful = "helpful"
    not_helpful = "not_helpful"
    custom = "custom"


# Profile
class ProfileCreate(BaseModel):
    name: str
    experience_level: ExperienceLevel
    occupation: Optional[str] = None
    preferred_language: str = "English"
    weekly_hours: int = 10
    preferred_learning_style: Optional[str] = None


class ProfileResponse(ProfileCreate):
    id: str
    user_id: str
    created_at: datetime


# Skills
class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None


class UserSkillCreate(BaseModel):
    skill_id: str
    current_level: ExperienceLevel
    confidence: int = Field(ge=1, le=5, default=3)


class SkillGap(BaseModel):
    skill_name: str
    skill_id: str
    current_level: str
    target_level: str
    gap: str  # "none", "low", "medium", "high", "critical"
    importance: float = Field(ge=0, le=1)
    prerequisites: list[str] = []
    recommended_action: str = ""


# Goals
class GoalCreate(BaseModel):
    raw_goal: str
    target_level: Optional[ExperienceLevel] = None


class GoalAnalysis(BaseModel):
    goal: str
    target_role: str = ""
    domain: str = ""
    target_skills: list[str] = []
    optional_skills: list[str] = []
    likely_prerequisites: list[str] = []
    estimated_difficulty: str = "intermediate"
    suggested_milestones: list[str] = []


# Resources
class ResourceBase(BaseModel):
    provider: str
    external_id: str
    title: str
    description: Optional[str] = None
    url: str
    thumbnail: Optional[str] = None
    resource_type: str = "video"
    difficulty: Optional[str] = None
    duration: Optional[str] = None
    metadata: dict = {}


class ResourceResponse(ResourceBase):
    id: str
    recommendation_score: Optional[float] = None
    recommendation_reason: Optional[str] = None


# Learning Path
class LearningPathResponse(BaseModel):
    id: str
    user_id: str
    goal_id: str
    title: str
    description: Optional[str] = None
    estimated_duration: Optional[str] = None
    status: str = "active"
    version: int = 1
    segments: list["LearningSegmentResponse"] = []


class LearningSegmentResponse(BaseModel):
    id: str
    learning_path_id: str
    title: str
    overview: Optional[str] = None
    sequence: int
    estimated_duration: Optional[str] = None
    status: SegmentStatus = SegmentStatus.locked
    skills: list[str] = []
    resources: list[ResourceResponse] = []


# Quiz
class QuizQuestion(BaseModel):
    id: Optional[str] = None
    question: str
    options: list[str]
    correct_answer: int = Field(ge=0, le=3)
    explanation: str = ""
    skill_tested: str = ""
    difficulty: str = "medium"


class QuizGenerateRequest(BaseModel):
    segment_id: str


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: list[int]


class QuizResult(BaseModel):
    quiz_id: str
    score: float
    total_questions: int
    correct_answers: int
    skill_assessment: list[dict] = []
    weak_concepts: list[str] = []
    strong_concepts: list[str] = []
    recommended_action: str = ""


# Feedback
class FeedbackCreate(BaseModel):
    resource_id: Optional[str] = None
    segment_id: Optional[str] = None
    type: FeedbackType
    text: Optional[str] = None


# Mentor
class MentorMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class MentorChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class MentorChatResponse(BaseModel):
    response: str
    conversation_id: str


# Onboarding
class OnboardingData(BaseModel):
    user_id: str = ""
    profile: ProfileCreate
    interests: list[str] = []
    skills: list[UserSkillCreate] = []
    previous_learning: list[str] = []
    goal: str
    preferences: dict = {}


# Roadmap Generation
class RoadmapGenerateRequest(BaseModel):
    goal_id: str


class AdaptationEvent(BaseModel):
    type: str
    reason: str
    changes: list[dict] = []


# Recommendation
class RecommendationScore(BaseModel):
    resource_id: str
    score: float
    semantic_similarity: float = 0
    skill_gap_relevance: float = 0
    prerequisite_fit: float = 0
    learner_level_fit: float = 0
    goal_alignment: float = 0
    learning_preference_fit: float = 0
    resource_quality: float = 0
    difficulty_fit: float = 0
    feedback_adjustment: float = 0
    matched_skills: list[str] = []
    reason: str = ""
