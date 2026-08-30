import json
import time
import google.generativeai as genai
from app.config import get_settings
from app.models.schemas import GoalAnalysis, QuizQuestion


class AIService:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-3.6-flash")

    def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                    wait = 15 * (attempt + 1)
                    print(f"Rate limited, waiting {wait}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait)
                else:
                    raise
        raise Exception("Max retries exceeded for Gemini API")

    async def analyze_goal(self, raw_goal: str) -> dict:
        prompt = f"""Analyze this learning goal and extract structured information.

Goal: "{raw_goal}"

Return a JSON object with exactly these fields:
{{
  "goal": "cleaned version of the goal",
  "target_role": "the role/position they want to achieve",
  "domain": "primary domain (e.g. web development, data science, AI/ML)",
  "target_skills": ["list of specific skills needed"],
  "optional_skills": ["nice-to-have skills"],
  "likely_prerequisites": ["foundational skills needed first"],
  "estimated_difficulty": "beginner|intermediate|advanced",
  "suggested_milestones": ["ordered list of major milestones"]
}}

Be specific and practical. List 8-15 target skills. Return ONLY valid JSON."""

        response = self._generate_with_retry(prompt)
        return self._parse_json(response, GoalAnalysis)

    async def extract_skills(self, text: str) -> list[str]:
        prompt = f"""Extract technical/professional skills from this text.
Text: "{text}"
Return a JSON array of skill names. Example: ["Python", "Machine Learning", "SQL"]
Return ONLY the JSON array."""

        response = self.model.generate_content(prompt)
        try:
            return json.loads(self._clean_json(response.text))
        except json.JSONDecodeError:
            return []

    async def generate_overview(self, segment_title: str, skills: list[str], goal: str, profile: dict) -> str:
        prompt = f"""Generate a personalized learning overview for a segment.

Segment: {segment_title}
Skills covered: {', '.join(skills)}
Learner's goal: {goal}
Learner's level: {profile.get('experience_level', 'beginner')}

Write a concise overview (150-200 words) that answers:
- What will I learn?
- Why am I learning it?
- How does it connect to my goal?
- What will I need to know?
- What will I be able to do afterward?

Make it personalized and motivating. Do not be generic."""

        response = self.model.generate_content(prompt)
        return response.text

    async def generate_quiz(self, segment_title: str, skills: list[str], resource_titles: list[str]) -> list[dict]:
        prompt = f"""Generate a reflection quiz for this learning segment with questions at 3 difficulty levels.

Segment: {segment_title}
Skills: {', '.join(skills)}
Resources studied: {', '.join(resource_titles[:5])}

Generate exactly 6 multiple-choice questions:
- 2 EASY questions (basic recall, definitions, simple concepts)
- 2 MEDIUM questions (understanding, application, comparing concepts)
- 2 HARD questions (analysis, problem-solving, real-world scenarios)

Return a JSON array where each element has:
{{
  "question": "the question text",
  "options": ["option A", "option B", "option C", "option D"],
  "correct_answer": 0,
  "explanation": "why this is correct and what to learn from it",
  "skill_tested": "which skill this tests",
  "difficulty": "easy|medium|hard"
}}

IMPORTANT:
- Easy questions should be answerable by anyone who watched the videos
- Medium questions require understanding the material
- Hard questions require applying knowledge to new scenarios
- Order: easy first, then medium, then hard
- Questions must be grounded in the segment context
Return ONLY valid JSON array."""

        response = self.model.generate_content(prompt)
        try:
            questions = json.loads(self._clean_json(response.text))
            validated = []
            for q in questions:
                if all(k in q for k in ["question", "options", "correct_answer", "explanation"]):
                    if len(q["options"]) == 4 and 0 <= q["correct_answer"] <= 3:
                        validated.append(q)
            return validated[:5]
        except (json.JSONDecodeError, KeyError):
            return []

    async def analyze_quiz_result(self, score: float, questions: list, answers: list, profile: dict) -> dict:
        weak = []
        strong = []
        for i, (q, a) in enumerate(zip(questions, answers)):
            skill = q.get("skill_tested", "unknown")
            if a == q.get("correct_answer"):
                strong.append(skill)
            else:
                weak.append(skill)

        if score < 0.5:
            action = "Review prerequisite materials and retry. Focus on: " + ", ".join(set(weak))
        elif score < 0.8:
            action = "Good progress! Practice more on: " + ", ".join(set(weak))
        else:
            action = "Excellent! Ready to advance to the next segment."

        return {
            "score": score,
            "weak_concepts": list(set(weak)),
            "strong_concepts": list(set(strong)),
            "recommended_action": action,
        }

    async def explain_recommendation(self, resource_id: str, user_id: str) -> str:
        return "This resource was recommended based on your skill gaps and learning goals."

    async def chat_with_mentor(self, message: str, context: dict, history: list) -> str:
        profile = context.get("profile", {})
        path = context.get("learning_path")
        skills = context.get("skills", [])

        system_prompt = f"""You are Pathwise Mentor, a personalized AI learning assistant.

Learner profile:
- Name: {profile.get('name', 'Learner')}
- Level: {profile.get('experience_level', 'beginner')}
- Goal: {path.get('title', 'Not set') if path else 'Not set'}
- Current skills: {', '.join(s.get('skills', {}).get('name', '') for s in skills[:10]) if skills else 'None recorded'}

You know their roadmap, progress, and quiz performance. Be helpful, encouraging, and specific.
Answer questions about their learning path, explain concepts, suggest what to study next.
Keep responses concise (2-4 paragraphs max)."""

        messages = [{"role": "user", "parts": [system_prompt + "\n\nConversation so far:"]}]
        for msg in history[-10:]:
            role = "user" if msg.get("role") == "user" else "model"
            messages.append({"role": role, "parts": [msg.get("content", "")]})
        messages.append({"role": "user", "parts": [message]})

        chat = self.model.start_chat(history=messages[:-1])
        response = chat.send_message(message)
        return response.text

    async def generate_roadmap_structure(self, goal_analysis: dict, skill_gaps: list, profile: dict) -> list[dict]:
        prompt = f"""Create a structured learning roadmap that progresses from easy to complex.

Goal: {goal_analysis.get('goal', '')}
Target role: {goal_analysis.get('target_role', '')}
Target skills: {', '.join(goal_analysis.get('target_skills', []))}
Prerequisites: {', '.join(goal_analysis.get('likely_prerequisites', []))}
Learner level: {profile.get('experience_level', 'beginner')}
Weekly hours: {profile.get('weekly_hours', 10)}

IMPORTANT RULES:
1. Start with absolute fundamentals — assume the learner needs grounding
2. Each phase MUST build directly on the previous phase — strict prerequisite chain
3. Progress: fundamentals → core theory → hands-on practice → real projects → advanced optimization
4. Each phase has exactly 1 clear topic focus — no cramming multiple unrelated skills
5. Make it feel like a story: each phase ends with a small achievable milestone
6. Early phases = quick wins (watch, understand, try). Later phases = deeper projects
7. Create 8-12 phases, each 1-2 weeks at {profile.get('weekly_hours', 10)} hrs/week
8. Name phases clearly so the learner knows exactly what they will learn
9. Phase titles should be specific (e.g. "Python Basics: Variables & Control Flow" not just "Python")
10. Include a capstone/project phase near the end

Return a JSON array where each phase has:
{{
  "title": "Specific descriptive phase title (e.g. 'Understanding Neural Networks from Scratch')",
  "objective": "By the end of this phase, you will be able to: [specific outcome]",
  "skills": ["one_primary_skill"],
  "estimated_duration": "1-2 weeks",
  "difficulty": "beginner|intermediate|advanced",
  "search_queries": ["specific youtube search query to find good tutorials for this exact topic"]
}}

Ensure proper prerequisite ordering — foundational first, advanced last. Return ONLY valid JSON array."""

        response = self.model.generate_content(prompt)
        try:
            phases = json.loads(self._clean_json(response.text))
            return phases if isinstance(phases, list) else []
        except json.JSONDecodeError:
            return []

    def _parse_json(self, text: str, model_class=None) -> dict:
        cleaned = self._clean_json(text)
        try:
            data = json.loads(cleaned)
            if model_class:
                validated = model_class(**data)
                return validated.model_dump()
            return data
        except (json.JSONDecodeError, Exception):
            if model_class:
                return model_class(goal="Unable to parse goal").model_dump()
            return {}

    def _clean_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
