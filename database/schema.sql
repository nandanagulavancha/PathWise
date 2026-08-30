-- Pathwise AI Database Schema
-- Run this in Supabase SQL Editor

-- Enable pgvector extension
create extension if not exists vector;

-- Profiles
create table if not exists profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade unique not null,
  name text not null,
  experience_level text check (experience_level in ('beginner', 'intermediate', 'advanced')) default 'beginner',
  occupation text,
  preferred_language text default 'English',
  weekly_hours integer default 10,
  preferred_learning_style text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Interests
create table if not exists interests (
  id uuid primary key default gen_random_uuid(),
  name text unique not null
);

-- User Interests
create table if not exists user_interests (
  user_id uuid references auth.users(id) on delete cascade,
  interest_id uuid references interests(id) on delete cascade,
  primary key (user_id, interest_id)
);

-- Skills
create table if not exists skills (
  id uuid primary key default gen_random_uuid(),
  name text unique not null,
  category text,
  description text
);

-- Skill Prerequisites
create table if not exists skill_prerequisites (
  skill_id uuid references skills(id) on delete cascade,
  prerequisite_skill_id uuid references skills(id) on delete cascade,
  primary key (skill_id, prerequisite_skill_id)
);

-- User Skills
create table if not exists user_skills (
  user_id uuid references auth.users(id) on delete cascade,
  skill_id uuid references skills(id) on delete cascade,
  current_level text check (current_level in ('beginner', 'intermediate', 'advanced')) default 'beginner',
  confidence integer check (confidence between 1 and 5) default 3,
  evidence text,
  updated_at timestamptz default now(),
  primary key (user_id, skill_id)
);

-- Goals
create table if not exists goals (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  raw_goal text not null,
  target_role text,
  target_domain text,
  target_level text,
  status text default 'active',
  created_at timestamptz default now()
);

-- Goal Skills
create table if not exists goal_skills (
  goal_id uuid references goals(id) on delete cascade,
  skill_id uuid references skills(id) on delete cascade,
  required_level text default 'intermediate',
  importance float default 0.5,
  primary key (goal_id, skill_id)
);

-- Resources
create table if not exists resources (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  external_id text not null,
  title text not null,
  description text,
  url text not null,
  thumbnail text,
  resource_type text default 'video',
  difficulty text,
  duration text,
  metadata jsonb default '{}',
  embedding vector(768),
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique(provider, external_id)
);

-- Learning Paths
create table if not exists learning_paths (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  goal_id uuid references goals(id),
  title text not null,
  description text,
  estimated_duration text,
  status text default 'active',
  version integer default 1,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Learning Segments
create table if not exists learning_segments (
  id uuid primary key default gen_random_uuid(),
  learning_path_id uuid references learning_paths(id) on delete cascade not null,
  title text not null,
  overview text,
  sequence integer not null,
  estimated_duration text,
  status text default 'locked' check (status in ('locked', 'upcoming', 'in_progress', 'completed', 'needs_review'))
);

-- Segment Skills
create table if not exists segment_skills (
  segment_id uuid references learning_segments(id) on delete cascade,
  skill_id uuid references skills(id) on delete cascade,
  primary key (segment_id, skill_id)
);

-- Segment Resources
create table if not exists segment_resources (
  segment_id uuid references learning_segments(id) on delete cascade,
  resource_id uuid references resources(id) on delete cascade,
  sequence integer default 0,
  recommendation_score float,
  recommendation_reason text,
  primary key (segment_id, resource_id)
);

-- Projects
create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text,
  difficulty text,
  skills jsonb default '[]'
);

-- Segment Projects
create table if not exists segment_projects (
  segment_id uuid references learning_segments(id) on delete cascade,
  project_id uuid references projects(id) on delete cascade,
  primary key (segment_id, project_id)
);

-- Quizzes
create table if not exists quizzes (
  id uuid primary key default gen_random_uuid(),
  segment_id uuid references learning_segments(id) on delete cascade,
  title text,
  generated_at timestamptz default now()
);

-- Quiz Questions
create table if not exists quiz_questions (
  id uuid primary key default gen_random_uuid(),
  quiz_id uuid references quizzes(id) on delete cascade not null,
  question text not null,
  options jsonb not null,
  correct_answer integer not null,
  explanation text,
  skill_id uuid references skills(id),
  difficulty text default 'medium'
);

-- Quiz Attempts
create table if not exists quiz_attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  quiz_id uuid references quizzes(id) on delete cascade not null,
  score float not null,
  answers jsonb,
  completed_at timestamptz default now()
);

-- Feedback
create table if not exists feedback (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  resource_id uuid references resources(id),
  segment_id uuid references learning_segments(id),
  type text not null,
  text text,
  created_at timestamptz default now()
);

-- Progress
create table if not exists progress (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  segment_id uuid references learning_segments(id),
  resource_id uuid references resources(id),
  status text default 'in_progress',
  progress_percentage integer default 0,
  time_spent integer default 0,
  completed_at timestamptz
);

-- AI Conversations
create table if not exists ai_conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  title text,
  created_at timestamptz default now()
);

-- AI Messages
create table if not exists ai_messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid references ai_conversations(id) on delete cascade not null,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  created_at timestamptz default now()
);

-- Recommendation Events
create table if not exists recommendation_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  resource_id uuid references resources(id),
  score float,
  reason text,
  action text,
  created_at timestamptz default now()
);

-- Skill Assessments
create table if not exists skill_assessments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  skill_id uuid references skills(id),
  estimated_level text,
  evidence text,
  source text,
  created_at timestamptz default now()
);

-- Indexes
create index if not exists idx_profiles_user_id on profiles(user_id);
create index if not exists idx_goals_user_id on goals(user_id);
create index if not exists idx_user_skills_user_id on user_skills(user_id);
create index if not exists idx_learning_paths_user_id on learning_paths(user_id);
create index if not exists idx_learning_segments_path_id on learning_segments(learning_path_id);
create index if not exists idx_segment_resources_segment on segment_resources(segment_id);
create index if not exists idx_resources_provider on resources(provider, external_id);
create index if not exists idx_quiz_attempts_user on quiz_attempts(user_id);
create index if not exists idx_feedback_user on feedback(user_id);
create index if not exists idx_progress_user on progress(user_id);
create index if not exists idx_ai_messages_conversation on ai_messages(conversation_id);

-- Vector similarity index
create index if not exists idx_resources_embedding on resources using hnsw (embedding vector_cosine_ops);

-- Row Level Security
alter table profiles enable row level security;
alter table user_interests enable row level security;
alter table user_skills enable row level security;
alter table goals enable row level security;
alter table learning_paths enable row level security;
alter table quiz_attempts enable row level security;
alter table feedback enable row level security;
alter table progress enable row level security;
alter table ai_conversations enable row level security;
alter table ai_messages enable row level security;

-- RLS Policies
create policy "Users can view own profile" on profiles for select using (auth.uid() = user_id);
create policy "Users can update own profile" on profiles for update using (auth.uid() = user_id);
create policy "Users can insert own profile" on profiles for insert with check (auth.uid() = user_id);

create policy "Users can manage own interests" on user_interests for all using (auth.uid() = user_id);
create policy "Users can manage own skills" on user_skills for all using (auth.uid() = user_id);
create policy "Users can manage own goals" on goals for all using (auth.uid() = user_id);
create policy "Users can view own paths" on learning_paths for select using (auth.uid() = user_id);
create policy "Users can manage own quiz attempts" on quiz_attempts for all using (auth.uid() = user_id);
create policy "Users can manage own feedback" on feedback for all using (auth.uid() = user_id);
create policy "Users can manage own progress" on progress for all using (auth.uid() = user_id);
create policy "Users can manage own conversations" on ai_conversations for all using (auth.uid() = user_id);
create policy "Users can view own messages" on ai_messages for select using (
  conversation_id in (select id from ai_conversations where user_id = auth.uid())
);

-- Public read for reference tables
alter table skills enable row level security;
create policy "Anyone can read skills" on skills for select using (true);
alter table interests enable row level security;
create policy "Anyone can read interests" on interests for select using (true);
