import json
from app.services.supabase_service import SupabaseService
from app.services.ai_service import AIService


# Hardcoded prerequisite relationships for common tech skills.
# These are deterministic and don't require an AI call.
CORE_PREREQUISITES = {
    # Web Dev chain
    "CSS": ["HTML"],
    "JavaScript": ["HTML", "CSS"],
    "TypeScript": ["JavaScript"],
    "React": ["JavaScript", "HTML", "CSS"],
    "Vue.js": ["JavaScript", "HTML", "CSS"],
    "Angular": ["TypeScript", "HTML", "CSS"],
    "Svelte": ["JavaScript", "HTML", "CSS"],
    "Next.js": ["React", "JavaScript"],
    "Tailwind CSS": ["CSS", "HTML"],
    "Node.js": ["JavaScript"],
    "Express.js": ["Node.js", "JavaScript"],
    "Django": ["Python"],
    "Flask": ["Python"],
    "FastAPI": ["Python"],
    "REST APIs": ["JavaScript"],
    "GraphQL": ["REST APIs", "JavaScript"],
    "WebSockets": ["JavaScript", "Node.js"],
    "OAuth/Auth": ["REST APIs"],

    # Programming fundamentals
    "OOP": ["Python"],
    "Functional Programming": ["Python"],
    "Design Patterns": ["OOP"],
    "Data Structures": ["Python"],
    "Algorithms": ["Data Structures"],
    "System Design": ["Data Structures", "Algorithms", "Databases"],
    "Testing": ["Python"],
    "Debugging": ["Python"],
    "Version Control": [],
    "Git": ["Version Control"],

    # AI/ML chain
    "NumPy": ["Python"],
    "Pandas": ["Python", "NumPy"],
    "Matplotlib": ["Python", "NumPy"],
    "Data Visualization": ["Matplotlib", "Pandas"],
    "Statistics": ["Python"],
    "Probability": ["Statistics"],
    "Data Cleaning": ["Pandas"],
    "Feature Engineering": ["Pandas", "Statistics"],
    "Scikit-learn": ["Python", "NumPy", "Pandas", "Statistics"],
    "Machine Learning": ["Statistics", "Python", "NumPy"],
    "Deep Learning": ["Machine Learning", "NumPy"],
    "Neural Networks": ["Deep Learning"],
    "PyTorch": ["Python", "Deep Learning", "NumPy"],
    "TensorFlow": ["Python", "Deep Learning", "NumPy"],
    "Keras": ["TensorFlow"],
    "NLP": ["Deep Learning", "Python"],
    "Computer Vision": ["Deep Learning", "Python"],
    "Reinforcement Learning": ["Machine Learning", "Python"],
    "Hugging Face": ["PyTorch", "NLP"],
    "LLMs/Generative AI": ["Deep Learning", "NLP", "PyTorch"],
    "Prompt Engineering": ["LLMs/Generative AI"],
    "MLOps": ["Machine Learning", "Docker", "CI/CD"],
    "Model Deployment": ["Machine Learning", "Docker"],

    # Data Science
    "A/B Testing": ["Statistics", "Probability"],
    "Jupyter Notebooks": ["Python"],
    "Power BI": ["SQL"],
    "Tableau": ["SQL"],

    # Databases
    "SQL": ["Python"],
    "PostgreSQL": ["SQL"],
    "MySQL": ["SQL"],
    "SQLite": ["SQL"],
    "MongoDB": ["JavaScript"],
    "Redis": ["SQL"],
    "Elasticsearch": ["SQL"],
    "Firebase": ["JavaScript"],
    "Supabase": ["PostgreSQL", "JavaScript"],
    "Database Design": ["SQL"],
    "ORMs": ["SQL", "Python"],

    # Cloud / DevOps
    "Docker": ["Linux"],
    "Kubernetes": ["Docker"],
    "CI/CD": ["Git", "Docker"],
    "Linux": [],
    "Terraform": ["Cloud"],
    "Nginx": ["Linux"],
    "Monitoring/Observability": ["Docker", "Linux"],
    "AWS": ["Linux"],
    "Azure": ["Linux"],
    "GCP": ["Linux"],

    # Mobile
    "React Native": ["React", "JavaScript"],
    "Flutter": [],
    "iOS Development": ["Swift"],
    "Android Development": ["Kotlin"],

    # Security
    "Network Security": ["Linux"],
    "Penetration Testing": ["Network Security", "Linux"],
    "Cryptography": ["Python", "Statistics"],
    "OWASP": ["REST APIs", "JavaScript"],
    "Security Auditing": ["Network Security", "OWASP"],
}


def seed_prerequisites():
    """Populate the skill_prerequisites table from the hardcoded map."""
    db = SupabaseService()

    # Load all skills
    skills = db.client.table("skills").select("id, name").execute()
    name_to_id = {s["name"]: s["id"] for s in (skills.data or [])}
    # Also map lowercase for fuzzy matching
    name_lower_to_id = {s["name"].lower(): s["id"] for s in (skills.data or [])}

    inserted = 0
    skipped = 0

    for skill_name, prereq_names in CORE_PREREQUISITES.items():
        skill_id = name_to_id.get(skill_name) or name_lower_to_id.get(skill_name.lower())
        if not skill_id:
            skipped += 1
            continue

        for prereq_name in prereq_names:
            prereq_id = name_to_id.get(prereq_name) or name_lower_to_id.get(prereq_name.lower())
            if not prereq_id:
                skipped += 1
                continue

            try:
                db.client.table("skill_prerequisites").upsert(
                    {"skill_id": skill_id, "prerequisite_skill_id": prereq_id},
                    on_conflict="skill_id,prerequisite_skill_id"
                ).execute()
                inserted += 1
            except Exception as e:
                print(f"Failed to insert {skill_name} -> {prereq_name}: {e}")
                skipped += 1

    print(f"Seeded {inserted} prerequisite relationships ({skipped} skipped)")
    return inserted


def seed_prerequisites_with_ai():
    """Use AI to generate prerequisites for skills not covered by the hardcoded map."""
    db = SupabaseService()
    ai = AIService()

    # First run the hardcoded ones
    seed_prerequisites()

    # Then check which skills have no prerequisites defined
    skills = db.client.table("skills").select("id, name, category").execute()
    existing = db.client.table("skill_prerequisites").select("skill_id").execute()
    has_prereqs = {r["skill_id"] for r in (existing.data or [])}

    orphan_skills = [s for s in (skills.data or []) if s["id"] not in has_prereqs]

    if not orphan_skills:
        print("All skills have prerequisites defined")
        return

    # Ask AI for missing prerequisites
    skill_names = [s["name"] for s in orphan_skills]
    all_skill_names = [s["name"] for s in (skills.data or [])]

    prompt = f"""Given these skills that need prerequisite relationships:
{json.dumps(skill_names)}

And this full list of available skills:
{json.dumps(all_skill_names)}

For each skill, list which other skills from the full list are direct prerequisites.
Return a JSON object where keys are skill names and values are arrays of prerequisite skill names.
Only include skills that genuinely need to be learned before the key skill.
If a skill has no prerequisites, use an empty array.
Return ONLY valid JSON."""

    try:
        response = ai._generate_with_retry(prompt)
        data = json.loads(ai._clean_json(response))
        name_to_id = {s["name"]: s["id"] for s in (skills.data or [])}

        for skill_name, prereqs in data.items():
            skill_id = name_to_id.get(skill_name)
            if not skill_id:
                continue
            for prereq_name in prereqs:
                prereq_id = name_to_id.get(prereq_name)
                if prereq_id:
                    db.client.table("skill_prerequisites").upsert(
                        {"skill_id": skill_id, "prerequisite_skill_id": prereq_id},
                        on_conflict="skill_id,prerequisite_skill_id"
                    ).execute()
    except Exception as e:
        print(f"AI prerequisite seeding failed: {e}")


if __name__ == "__main__":
    seed_prerequisites()
