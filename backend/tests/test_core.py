import pytest
from app.services.skill_gap_engine import SkillGapEngine, LEVEL_MAP, GAP_LABELS
from app.services.skill_graph import SkillGraph


# ── Skill Graph Tests ──

class TestSkillGraph:
    def _make_graph(self):
        g = SkillGraph()
        g.add_skill("html", "HTML", "Web")
        g.add_skill("css", "CSS", "Web")
        g.add_skill("js", "JavaScript", "Web")
        g.add_skill("react", "React", "Web")
        g.add_skill("next", "Next.js", "Web")
        g.add_skill("node", "Node.js", "Web")
        g.add_skill("ts", "TypeScript", "Web")
        # Prerequisites: HTML -> CSS -> JS -> React -> Next.js
        g.add_prerequisite("css", "html")
        g.add_prerequisite("js", "html")
        g.add_prerequisite("js", "css")
        g.add_prerequisite("react", "js")
        g.add_prerequisite("next", "react")
        g.add_prerequisite("next", "js")
        g.add_prerequisite("node", "js")
        g.add_prerequisite("ts", "js")
        return g

    def test_basic_topological_order(self):
        g = self._make_graph()
        sorted_skills = g.topological_sort_with_depths({"html", "css", "js", "react"})
        names = [g.skill_info[sid]["name"] for _, sid in sorted_skills]
        assert names.index("HTML") < names.index("CSS")
        assert names.index("CSS") < names.index("JavaScript")
        assert names.index("JavaScript") < names.index("React")

    def test_html_before_everything(self):
        g = self._make_graph()
        sorted_skills = g.topological_sort_with_depths({"html", "css", "js", "react", "next"})
        ids = [sid for _, sid in sorted_skills]
        assert ids[0] == "html"

    def test_prerequisite_collection(self):
        g = self._make_graph()
        prereqs = g.get_all_prerequisites("react")
        assert "js" in prereqs
        assert "html" in prereqs
        assert "css" in prereqs
        assert "react" in prereqs  # includes self

    def test_required_subgraph(self):
        g = self._make_graph()
        required = g.get_required_subgraph(["react"])
        assert "html" in required
        assert "css" in required
        assert "js" in required
        assert "react" in required
        assert "next" not in required  # not a prereq of react
        assert "node" not in required

    def test_mastered_skills_excluded(self):
        g = self._make_graph()
        phases = g.build_phases(
            target_skill_ids=["react"],
            mastered_skill_ids={"html", "css"},
        )
        all_skill_ids = [s["skill_id"] for phase in phases for s in phase]
        assert "html" not in all_skill_ids
        assert "css" not in all_skill_ids
        assert "js" in all_skill_ids
        assert "react" in all_skill_ids

    def test_phases_ordered_by_depth(self):
        g = self._make_graph()
        phases = g.build_phases(target_skill_ids=["next"])
        # First phase should contain foundational skills
        first_phase_names = [s["name"] for s in phases[0]]
        assert "HTML" in first_phase_names
        # Last phase should contain the target
        last_phase_names = [s["name"] for s in phases[-1]]
        assert "Next.js" in last_phase_names

    def test_empty_targets(self):
        g = self._make_graph()
        phases = g.build_phases(target_skill_ids=[])
        assert phases == []

    def test_branching_graph(self):
        g = SkillGraph()
        g.add_skill("python", "Python", "Programming")
        g.add_skill("numpy", "NumPy", "Data")
        g.add_skill("pandas", "Pandas", "Data")
        g.add_skill("ml", "Machine Learning", "AI")
        g.add_prerequisite("numpy", "python")
        g.add_prerequisite("pandas", "python")
        g.add_prerequisite("ml", "numpy")
        g.add_prerequisite("ml", "pandas")
        sorted_skills = g.topological_sort_with_depths({"python", "numpy", "pandas", "ml"})
        ids = [sid for _, sid in sorted_skills]
        assert ids.index("python") < ids.index("numpy")
        assert ids.index("python") < ids.index("pandas")
        assert ids.index("numpy") < ids.index("ml")
        assert ids.index("pandas") < ids.index("ml")

    def test_diamond_dependency(self):
        g = SkillGraph()
        g.add_skill("a", "A", "")
        g.add_skill("b", "B", "")
        g.add_skill("c", "C", "")
        g.add_skill("d", "D", "")
        g.add_prerequisite("b", "a")
        g.add_prerequisite("c", "a")
        g.add_prerequisite("d", "b")
        g.add_prerequisite("d", "c")
        sorted_skills = g.topological_sort_with_depths({"a", "b", "c", "d"})
        ids = [sid for _, sid in sorted_skills]
        assert ids[0] == "a"
        assert ids[-1] == "d"

    def test_gap_weight_ordering(self):
        g = SkillGraph()
        g.add_skill("a", "A", "")
        g.add_skill("b", "B", "")
        # Both at same depth (no prerequisites)
        phases = g.build_phases(
            target_skill_ids=["a", "b"],
            gap_weights={"a": 0.3, "b": 0.9},  # B is more critical
        )
        # B should come before A in the first phase
        first_skills = [s["skill_id"] for s in phases[0]]
        assert first_skills[0] == "b"


# ── Resource Dedup and Quality Tests ──

class TestResourceDedup:
    def test_title_similarity(self):
        from app.services.roadmap_generator import RoadmapGenerator
        gen = RoadmapGenerator.__new__(RoadmapGenerator)
        sim = gen._title_similarity("python tutorial for beginners", "python tutorial for beginners 2024")
        assert sim > 0.6

    def test_different_titles(self):
        from app.services.roadmap_generator import RoadmapGenerator
        gen = RoadmapGenerator.__new__(RoadmapGenerator)
        sim = gen._title_similarity("react hooks explained", "machine learning introduction")
        assert sim < 0.2

    def test_quality_filter_removes_short_titles(self):
        from app.services.roadmap_generator import RoadmapGenerator
        gen = RoadmapGenerator.__new__(RoadmapGenerator)
        resources = [
            {"title": "ab", "external_id": "1"},
            {"title": "Complete Python Tutorial for Beginners", "external_id": "2"},
        ]
        filtered = gen._filter_quality(resources)
        assert len(filtered) == 1
        assert filtered[0]["external_id"] == "2"

    def test_quality_filter_removes_duplicates(self):
        from app.services.roadmap_generator import RoadmapGenerator
        gen = RoadmapGenerator.__new__(RoadmapGenerator)
        resources = [
            {"title": "Python Tutorial for Beginners Full Course", "external_id": "1"},
            {"title": "Python Tutorial for Beginners Full Course 2024", "external_id": "2"},
            {"title": "React Hooks Complete Guide", "external_id": "3"},
        ]
        filtered = gen._filter_quality(resources)
        assert len(filtered) == 2  # Second python tutorial filtered as near-dupe


# ── Skill Gap Engine Tests ──

class TestSkillGapCalculation:
    def test_level_map(self):
        assert LEVEL_MAP["beginner"] == 1
        assert LEVEL_MAP["intermediate"] == 2
        assert LEVEL_MAP["advanced"] == 3

    def test_gap_labels(self):
        assert GAP_LABELS[0] == "none"
        assert GAP_LABELS[1] == "low"
        assert GAP_LABELS[2] == "medium"
        assert GAP_LABELS[3] == "high"

    def test_get_action_no_gap(self):
        engine = SkillGapEngine.__new__(SkillGapEngine)
        action = engine._get_action(0, "Python", "advanced")
        assert "proficient" in action.lower()

    def test_get_action_critical(self):
        engine = SkillGapEngine.__new__(SkillGapEngine)
        action = engine._get_action(3, "Node.js", "none")
        assert "begin" in action.lower() or "start" in action.lower()


# ── Recommendation Scoring Tests ──

class TestRecommendationScoring:
    def test_level_fit_same(self):
        from app.services.recommendation_engine import RecommendationEngine
        engine = RecommendationEngine.__new__(RecommendationEngine)
        score = engine._level_fit({"difficulty": "beginner"}, {"experience_level": "beginner"})
        assert score == 1.0

    def test_level_fit_different(self):
        from app.services.recommendation_engine import RecommendationEngine
        engine = RecommendationEngine.__new__(RecommendationEngine)
        score = engine._level_fit({"difficulty": "advanced"}, {"experience_level": "beginner"})
        assert score == 0.6

    def test_preference_fit_match(self):
        from app.services.recommendation_engine import RecommendationEngine
        engine = RecommendationEngine.__new__(RecommendationEngine)
        score = engine._preference_fit({"resource_type": "video"}, {"preferred_learning_style": "video"})
        assert score == 1.0


# ── Other Tests ──

class TestQuizScoring:
    def test_score_calculation(self):
        questions = [
            {"correct_answer": 0, "skill_tested": "Python"},
            {"correct_answer": 1, "skill_tested": "JavaScript"},
            {"correct_answer": 2, "skill_tested": "React"},
        ]
        answers = [0, 1, 0]
        correct = sum(1 for q, a in zip(questions, answers) if q["correct_answer"] == a)
        score = correct / len(questions)
        assert abs(score - 0.667) < 0.01


class TestProgressCalculation:
    def test_overall_progress(self):
        items = [
            {"status": "completed", "segment_id": "s1", "time_spent": 30},
            {"status": "completed", "segment_id": "s1", "time_spent": 45},
            {"status": "in_progress", "segment_id": "s2", "time_spent": 10},
        ]
        completed = [i for i in items if i["status"] == "completed"]
        percentage = int((len(completed) / max(len(items), 1)) * 100)
        assert percentage == 66

    def test_empty_progress(self):
        items = []
        completed = [i for i in items if i.get("status") == "completed"]
        percentage = int((len(completed) / max(len(items), 1)) * 100)
        assert percentage == 0


class TestAIServiceParsing:
    def test_clean_json_markdown(self):
        from app.services.ai_service import AIService
        ai = AIService.__new__(AIService)
        text = '```json\n{"key": "value"}\n```'
        result = ai._clean_json(text)
        assert result == '{"key": "value"}'


class TestYouTubeDuration:
    def test_hours_minutes(self):
        from app.providers.youtube import YouTubeProvider
        yt = YouTubeProvider.__new__(YouTubeProvider)
        assert yt._parse_duration("PT1H30M") == "1h 30m"

    def test_minutes_only(self):
        from app.providers.youtube import YouTubeProvider
        yt = YouTubeProvider.__new__(YouTubeProvider)
        assert yt._parse_duration("PT45M") == "45m"
