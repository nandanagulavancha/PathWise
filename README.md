# Pathwise AI

**Learn what matters. In the right order. At your pace.**

Pathwise AI is an AI-powered personalized learning path recommender that understands your goals, identifies skill gaps, discovers real learning resources, generates a prerequisite-aware roadmap, and adapts as you learn.

---

## Features

- **Natural Language Goal Analysis** -- Describe your learning goal in plain English; Gemini AI extracts skills, prerequisites, and milestones
- **Skill Gap Engine** -- Compares your current skills against target requirements with deterministic gap scoring
- **Personalized Roadmap** -- AI-generated phased learning path ordered from fundamentals to advanced topics
- **Real Resources** -- YouTube videos and GitHub repos fetched via live APIs (no fake data)
- **Progressive Difficulty** -- Resources within each phase are ordered beginner to advanced
- **Reflection Quizzes** -- AI-generated quizzes with easy/medium/hard categories after each segment
- **Quick Quizzes** -- Inline quiz question after completing each video
- **Adaptive Learning** -- Path adapts based on quiz performance and feedback
- **AI Mentor** -- Context-aware chat assistant that knows your profile, progress, and roadmap
- **Locked/Unlocked Flow** -- Toggle between sequential progression or free access to all segments
- **Dashboard** -- Progress stats, skill development, roadmap preview, and next actions
- **Sentry-Inspired Dark UI** -- Midnight violet canvas with electric lime accents

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React, TypeScript, Tailwind CSS, shadcn/ui, Lucide Icons |
| Backend | Python, FastAPI, Pydantic |
| Database | Supabase (PostgreSQL + pgvector) |
| Auth | Supabase Auth with Row Level Security |
| AI | Google Gemini API (gemini-3.6-flash) |
| Resources | YouTube Data API v3, GitHub REST API |

---

## Prerequisites

Before you start, make sure you have:

- **Node.js** >= 18 ([download](https://nodejs.org))
- **Python** >= 3.11 ([download](https://python.org))
- **npm** (comes with Node.js)
- **Git** ([download](https://git-scm.com))

You will also need accounts and API keys for:

1. **Supabase** (free tier) -- [supabase.com](https://supabase.com)
2. **Google AI Studio** (Gemini API key) -- [aistudio.google.com](https://aistudio.google.com/apikey)
3. **YouTube Data API** -- [Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com)
4. **GitHub Personal Access Token** (optional) -- [github.com/settings/tokens](https://github.com/settings/tokens)

---

## Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/pathwise-ai.git
cd pathwise-ai
```

### 2. Set Up Supabase

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the project to finish provisioning
3. Go to **SQL Editor** in the Supabase dashboard
4. Open the file `database/schema.sql` from this repo, copy its contents, and paste into the SQL Editor
5. Click **Run** -- this creates all tables, indexes, RLS policies, and enables pgvector
6. Go to **Authentication** > **Providers** > **Email** and turn OFF **"Confirm email"** (for development)
7. Collect your keys from **Settings** > **API**:
   - **Project URL** (e.g. `https://abcdef.supabase.co`)
   - **anon public** key
   - **service_role** key (click to reveal)

### 3. Get API Keys

#### Gemini API Key
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy the key

#### YouTube Data API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Go to **APIs & Services** > **Library**
4. Search for "YouTube Data API v3" and enable it
5. Go to **APIs & Services** > **Credentials**
6. Click **Create Credentials** > **API Key**
7. Copy the key

#### GitHub Token (Optional)
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Select scope: `public_repo`
4. Copy the token

### 4. Configure Environment Variables

#### Frontend (.env.local)

Create a file called `.env.local` in the project root:

```bash
cp .env.example .env.local
```

Edit `.env.local` with your values:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
GEMINI_API_KEY=your_gemini_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
GITHUB_TOKEN=your_github_token_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Backend (backend/.env)

Create a file called `.env` inside the `backend/` folder:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with the same values:

```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SUPABASE_ANON_KEY=your_anon_key_here
GEMINI_API_KEY=your_gemini_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
GITHUB_TOKEN=your_github_token_here
FRONTEND_URL=http://localhost:3000
```

### 5. Install Dependencies

#### Frontend

```bash
npm install
```

#### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 6. Seed the Skills Database

This populates the skills table with ~100 tech skills across programming, web dev, AI/ML, data science, cloud, and more:

```bash
cd backend
source venv/bin/activate
python -c "
from app.services.supabase_service import SupabaseService
db = SupabaseService()

skills = [
    ('Python', 'Programming'), ('JavaScript', 'Programming'), ('TypeScript', 'Programming'),
    ('Java', 'Programming'), ('C++', 'Programming'), ('Go', 'Programming'),
    ('Rust', 'Programming'), ('SQL', 'Programming'),
    ('HTML', 'Web Development'), ('CSS', 'Web Development'), ('React', 'Web Development'),
    ('Next.js', 'Web Development'), ('Node.js', 'Web Development'), ('Django', 'Web Development'),
    ('FastAPI', 'Web Development'), ('REST APIs', 'Web Development'),
    ('Machine Learning', 'AI/ML'), ('Deep Learning', 'AI/ML'), ('NLP', 'AI/ML'),
    ('PyTorch', 'AI/ML'), ('TensorFlow', 'AI/ML'), ('LLMs/Generative AI', 'AI/ML'),
    ('Pandas', 'Data Science'), ('NumPy', 'Data Science'), ('Statistics', 'Data Science'),
    ('PostgreSQL', 'Databases'), ('MongoDB', 'Databases'), ('Redis', 'Databases'),
    ('AWS', 'Cloud'), ('Docker', 'DevOps'), ('Kubernetes', 'DevOps'),
    ('Git', 'DevOps'), ('Linux', 'DevOps'), ('CI/CD', 'DevOps'),
    ('Data Structures', 'Fundamentals'), ('Algorithms', 'Fundamentals'),
    ('System Design', 'Fundamentals'), ('OOP', 'Fundamentals'),
]
for name, cat in skills:
    db.client.table('skills').upsert({'name': name, 'category': cat}, on_conflict='name').execute()
print(f'Seeded {len(skills)} skills')
"
cd ..
```

---

## Running the Application

You need two terminals -- one for the backend and one for the frontend.

### Terminal 1: Start the Backend

```bash
cd backend
source venv/bin/activate    # On Windows: venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Terminal 2: Start the Frontend

```bash
npm run dev
```

You should see:
```
▲ Next.js 16.x
- Local: http://localhost:3000
✓ Ready
```

### Open the App

Go to **http://localhost:3000** in your browser.

---

## User Journey

1. **Sign Up** at `/signup` with email and password
2. **Onboarding** -- 7-step wizard: profile, interests, skills, previous learning, goal, preferences, confirmation
3. **Roadmap Generated** -- AI analyzes your goal, finds skill gaps, fetches YouTube resources, builds a phased plan
4. **Dashboard** -- See your progress, skill development, and next actions
5. **Learn** -- Open each phase, watch videos, take quick quizzes after each resource
6. **Full Quiz** -- Take a segment reflection quiz with easy/medium/hard questions
7. **AI Mentor** -- Chat with your personalized learning assistant
8. **Adapt** -- Roadmap changes based on quiz performance and feedback

---

## Project Structure

```
pathwise-ai/
├── src/                          # Next.js frontend
│   ├── app/
│   │   ├── (auth)/               # Login, signup pages
│   │   ├── (app)/                # Authenticated pages (dashboard, roadmap, etc.)
│   │   ├── onboarding/           # Multi-step onboarding wizard
│   │   └── page.tsx              # Landing page
│   ├── components/               # React components
│   └── lib/
│       ├── api.ts                # FastAPI client
│       ├── auth-context.tsx      # Supabase auth provider
│       ├── supabase/             # Supabase client setup
│       └── types.ts              # TypeScript types
├── backend/                      # Python FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI app entry point
│   │   ├── config.py             # Environment settings
│   │   ├── routers/              # API endpoints
│   │   ├── services/
│   │   │   ├── ai_service.py     # Gemini AI integration
│   │   │   ├── skill_gap_engine.py
│   │   │   ├── recommendation_engine.py
│   │   │   ├── roadmap_generator.py
│   │   │   ├── quiz_engine.py
│   │   │   ├── adaptive_engine.py
│   │   │   └── supabase_service.py
│   │   ├── providers/
│   │   │   ├── youtube.py        # YouTube Data API
│   │   │   └── github.py         # GitHub API
│   │   └── models/
│   │       └── schemas.py        # Pydantic models
│   └── tests/                    # pytest tests
├── database/
│   └── schema.sql                # Supabase database schema
├── .env.example                  # Frontend env template
├── backend/.env.example          # Backend env template
└── FRONTEND_DESIGN.md            # Sentry-inspired design system
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/goals/onboarding` | Complete onboarding and generate roadmap |
| POST | `/api/goals/analyze` | Analyze a learning goal with AI |
| GET | `/api/roadmap/{user_id}` | Get user's learning roadmap |
| GET | `/api/skills/` | List all available skills |
| GET | `/api/skills/gap/{user_id}` | Get skill gaps for user |
| GET | `/api/resources/search` | Search YouTube/GitHub for resources |
| POST | `/api/quiz/generate` | Generate a reflection quiz for a segment |
| POST | `/api/quiz/quick` | Generate a single quick quiz question |
| POST | `/api/quiz/submit` | Submit quiz answers and get results |
| GET | `/api/progress/dashboard/{user_id}` | Get dashboard data |
| POST | `/api/feedback/` | Submit feedback on a resource/segment |
| POST | `/api/mentor/chat` | Chat with AI mentor |
| GET | `/api/health` | Health check |

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

---

## Troubleshooting

### "Failed to fetch" in the browser
The backend server at `localhost:8000` is not running. Start it with `uvicorn app.main:app --port 8000`.

### "Email not confirmed"
Go to Supabase dashboard > **Authentication** > **Providers** > **Email** and disable "Confirm email".

### "RESOURCE_EXHAUSTED" / Rate limited
You've hit the Gemini free-tier limit (20 requests/day). Wait 15 seconds between requests, or upgrade your Google AI plan.

### "invalid input syntax for type uuid"
The user_id is not being passed correctly. Make sure you're logged in before completing onboarding.

### YouTube returns no results
Check that your YouTube Data API key is valid and the API is enabled in Google Cloud Console.

---

## Rate Limits (Free Tier)

| Service | Free Limit |
|---------|-----------|
| Gemini API | 20 requests/day (gemini-3.6-flash) |
| YouTube Data API | 10,000 units/day |
| Supabase | 500MB database, 50,000 auth users |
| GitHub API | 60 requests/hour (unauthenticated), 5,000/hour (with token) |

---

## License

MIT
