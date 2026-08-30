from app.services.supabase_service import SupabaseService
from app.services.ai_service import AIService
from app.services.skill_graph import SkillGraph
from app.services.embedding_service import EmbeddingService
from app.providers.youtube import YouTubeProvider
from app.providers.github import GitHubProvider

LEVEL_MAP = {"beginner": 1, "intermediate": 2, "advanced": 3}


class RoadmapGenerator:
    def __init__(self):
        self.db = SupabaseService()
        self.ai = AIService()
        self.youtube = YouTubeProvider()
        self.github = GitHubProvider()
        self.embedding = EmbeddingService()

    def generate(self, goal_id: str) -> dict:
        goal = self.db.get_goal(goal_id)
        if not goal:
            return {"error": "Goal not found"}

        user_id = goal["user_id"]
        profile = self.db.get_profile(user_id)
        if not profile:
            return {"error": "Profile not found"}

        user_skills = self.db.get_user_skills(user_id)

        # ── Stage 1: Goal Analysis via AI ──
        goal_analysis = self.ai.analyze_goal(goal["raw_goal"])
        target_skill_names = goal_analysis.get("target_skills", [])
        prerequisite_names = goal_analysis.get("likely_prerequisites", [])
        all_needed = target_skill_names + prerequisite_names

        # ── Stage 2: Build Skill Graph ──
        graph = SkillGraph.from_db(self.db)

        # Resolve skill names to IDs
        name_to_id = {}
        for sid, info in graph.skill_info.items():
            name_to_id[info["name"].lower()] = sid

        target_ids = []
        for name in all_needed:
            sid = name_to_id.get(name.lower())
            if sid:
                target_ids.append(sid)
            else:
                # Skill not in DB — create it and add to graph
                result = self.db.client.table("skills").upsert(
                    {"name": name, "category": "goal-derived"},
                    on_conflict="name"
                ).execute()
                if result.data:
                    new_id = result.data[0]["id"]
                    graph.add_skill(new_id, name, "goal-derived")
                    name_to_id[name.lower()] = new_id
                    target_ids.append(new_id)

        # ── Stage 3: Topological Sort with Gap Weights ──
        mastered = set()
        gap_weights = {}
        for us in user_skills:
            sid = us.get("skill_id", "")
            level = us.get("current_level", "beginner")
            confidence = us.get("confidence", 1)
            # Consider mastered if advanced with high confidence
            if level == "advanced" and confidence >= 4:
                mastered.add(sid)
            # Compute gap weight (higher = more critical to learn)
            level_num = LEVEL_MAP.get(level, 1)
            gap_weights[sid] = max(0, 3 - level_num) / 3  # 0=advanced, 1=no knowledge

        # Build phases using topological sort
        phases = graph.build_phases(
            target_skill_ids=target_ids,
            mastered_skill_ids=mastered,
            gap_weights=gap_weights,
        )

        if not phases:
            # Fallback to AI-generated structure if graph produces nothing
            phases_raw = self.ai.generate_roadmap_structure(goal_analysis, [], profile)
            phases = [[{"name": p.get("title", "Phase"), "skill_id": None, "category": "", "depth": i}] for i, p in enumerate(phases_raw)]

        # ── Stage 4 & 5: Resource Retrieval + Ranking + Dedup ──
        path_data = {
            "user_id": user_id,
            "goal_id": goal_id,
            "title": goal_analysis.get("target_role", goal["raw_goal"][:100]),
            "description": goal_analysis.get("goal", ""),
            "estimated_duration": f"{len(phases) * 2} weeks",
            "status": "active",
            "version": 1,
        }
        path = self.db.save_learning_path(path_data)
        path_id = path.get("id", "temp")

        used_resource_ids = set()  # Global dedup across segments
        segments = []
        learner_level = profile.get("experience_level", "beginner")

        # Generate a goal embedding for semantic ranking
        goal_text = f"{goal['raw_goal']} {' '.join(target_skill_names)}"
        try:
            goal_embedding = self.embedding.generate_query_embedding(goal_text)
        except Exception:
            goal_embedding = []

        for idx, phase_skills in enumerate(phases):
            phase_name = ", ".join(s["name"] for s in phase_skills)
            main_skill = phase_skills[0]["name"]

            # ── Resource Retrieval ──
            resources = self._fetch_resources(main_skill, learner_level, used_resource_ids)

            # ── Semantic Ranking ──
            if goal_embedding:
                resources = self._rank_resources(resources, goal_embedding, main_skill, learner_level)

            # ── Quality Filtering ──
            resources = self._filter_quality(resources)

            # ── Dedup ──
            unique_resources = []
            for r in resources:
                eid = r.get("external_id")
                if eid not in used_resource_ids:
                    used_resource_ids.add(eid)
                    unique_resources.append(r)
            resources = unique_resources[:5]

            # Save resources
            saved_resources = []
            for r in resources:
                saved = self.db.save_resource(r)
                saved_resources.append(saved)

            # Generate personalized overview
            try:
                overview = self.ai.generate_overview(phase_name, [s["name"] for s in phase_skills], goal["raw_goal"], profile)
            except Exception:
                overview = f"Learn {phase_name} — building toward your goal of {goal_analysis.get('target_role', 'your target')}."

            # Determine difficulty label
            depth = phase_skills[0].get("depth", idx)
            total_phases = len(phases)
            if depth < total_phases * 0.33:
                difficulty = "beginner"
            elif depth < total_phases * 0.66:
                difficulty = "intermediate"
            else:
                difficulty = "advanced"

            status = "in_progress" if idx == 0 else ("upcoming" if idx == 1 else "locked")
            segment_data = {
                "learning_path_id": path_id,
                "title": phase_name,
                "overview": overview,
                "sequence": idx + 1,
                "estimated_duration": "1-2 weeks",
                "status": status,
            }
            segment = self.db.save_learning_segment(segment_data)
            segment["resources"] = saved_resources
            segments.append(segment)

            # Link resources to segment
            for i, r in enumerate(saved_resources):
                if r.get("id") and segment.get("id"):
                    self.db.client.table("segment_resources").insert({
                        "segment_id": segment["id"],
                        "resource_id": r["id"],
                        "sequence": i + 1,
                        "recommendation_score": r.get("_score", 0.8),
                        "recommendation_reason": r.get("_reason", f"Relevant to {main_skill}"),
                    }).execute()

        path["segments"] = segments
        return path

    def _fetch_resources(self, skill: str, level: str, exclude_ids: set) -> list[dict]:
        """Fetch resources with progressive difficulty queries."""
        resources = []
        queries = [
            (f"{skill} beginner tutorial explained", "beginner"),
            (f"{skill} complete guide step by step", "intermediate"),
            (f"{skill} advanced project tutorial", "advanced"),
        ]

        for query, difficulty in queries:
            try:
                results = self.youtube.search_resources(query, difficulty=difficulty, limit=3)
                for r in results:
                    if r.get("external_id") not in exclude_ids:
                        r["difficulty"] = difficulty
                        resources.append(r)
            except Exception as e:
                print(f"YouTube search failed for '{query}': {e}")
            if len(resources) >= 8:
                break

        return resources

    def _rank_resources(self, resources: list[dict], goal_embedding: list[float], skill: str, level: str) -> list[dict]:
        """Rank resources using semantic similarity + quality signals."""
        scored = []
        for r in resources:
            # Compute embedding for resource title
            try:
                text = f"{r.get('title', '')} {r.get('description', '')[:200]}"
                res_embedding = self.embedding.generate_embedding(text)
                semantic = self.embedding.compute_similarity(res_embedding, goal_embedding)
            except Exception:
                semantic = 0.5

            # Quality score from view count
            views = int(r.get("metadata", {}).get("view_count", "0") or "0")
            quality = min(1.0, views / 100000)

            # Difficulty fit
            r_diff = r.get("difficulty", "intermediate")
            diff_fit = 1.0 if r_diff == level else (0.7 if abs(LEVEL_MAP.get(r_diff, 2) - LEVEL_MAP.get(level, 1)) == 1 else 0.4)

            # Combined score
            score = semantic * 0.35 + quality * 0.25 + diff_fit * 0.25 + 0.15
            r["_score"] = round(score, 3)
            r["_reason"] = f"Semantic: {semantic:.0%}, Quality: {quality:.0%}, Difficulty fit: {diff_fit:.0%}"
            scored.append(r)

        scored.sort(key=lambda x: -x.get("_score", 0))
        return scored

    def _filter_quality(self, resources: list[dict]) -> list[dict]:
        """Remove low-quality resources."""
        filtered = []
        seen_titles = set()
        for r in resources:
            title = r.get("title", "").lower().strip()
            # Skip very short titles (likely not educational)
            if len(title) < 10:
                continue
            # Skip near-duplicate titles
            if any(self._title_similarity(title, t) > 0.8 for t in seen_titles):
                continue
            seen_titles.add(title)
            filtered.append(r)
        return filtered

    def _title_similarity(self, a: str, b: str) -> float:
        """Simple word-overlap Jaccard similarity."""
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        return len(words_a & words_b) / len(words_a | words_b)
