import pytest
from app.services.skill_gap_engine import SkillGapEngine, LEVEL_MAP, GAP_LABELS


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
        action = engine._get_action(0, "Python")
        assert "Maintain" in action

    def test_get_action_low_gap(self):
        engine = SkillGapEngine.__new__(SkillGapEngine)
        action = engine._get_action(1, "JavaScript")
        assert "advanced" in action.lower()

    def test_get_action_medium_gap(self):
        engine = SkillGapEngine.__new__(SkillGapEngine)
        action = engine._get_action(2, "React")
        assert "fundamentals" in action.lower()

    def test_get_action_high_gap(self):
        engine = SkillGapEngine.__new__(SkillGapEngine)
        action = engine._get_action(3, "Node.js")
        assert "scratch" in action.lower()


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

    def test_preference_fit_mismatch(self):
        from app.services.recommendation_engine import RecommendationEngine
        engine = RecommendationEngine.__new__(RecommendationEngine)
        score = engine._preference_fit({"resource_type": "article"}, {"preferred_learning_style": "video"})
        assert score == 0.5


class TestQuizScoring:
    def test_score_calculation(self):
        questions = [
            {"correct_answer": 0, "skill_tested": "Python"},
            {"correct_answer": 1, "skill_tested": "JavaScript"},
            {"correct_answer": 2, "skill_tested": "React"},
            {"correct_answer": 0, "skill_tested": "Node.js"},
            {"correct_answer": 3, "skill_tested": "CSS"},
        ]
        answers = [0, 1, 0, 0, 3]  # 4/5 correct
        correct = sum(1 for q, a in zip(questions, answers) if q["correct_answer"] == a)
        score = correct / len(questions)
        assert score == 0.8

    def test_weak_strong_identification(self):
        questions = [
            {"correct_answer": 0, "skill_tested": "Python"},
            {"correct_answer": 1, "skill_tested": "JavaScript"},
            {"correct_answer": 2, "skill_tested": "React"},
        ]
        answers = [0, 0, 2]  # Python correct, JS wrong, React correct
        weak = []
        strong = []
        for q, a in zip(questions, answers):
            if a == q["correct_answer"]:
                strong.append(q["skill_tested"])
            else:
                weak.append(q["skill_tested"])
        assert "Python" in strong
        assert "React" in strong
        assert "JavaScript" in weak


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

    def test_clean_json_plain(self):
        from app.services.ai_service import AIService
        ai = AIService.__new__(AIService)
        text = '{"key": "value"}'
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

    def test_empty(self):
        from app.providers.youtube import YouTubeProvider
        yt = YouTubeProvider.__new__(YouTubeProvider)
        assert yt._parse_duration("") == ""
