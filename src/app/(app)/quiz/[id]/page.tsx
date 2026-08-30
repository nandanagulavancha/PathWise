"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { CheckCircle2, XCircle, ArrowRight } from "lucide-react";

interface QuizData {
  quiz_id: string;
  title: string;
  questions: { id: string; question: string; options: string[]; skill_tested: string; difficulty: string }[];
}

interface QuizResultData {
  score: number;
  total_questions: number;
  correct_answers: number;
  weak_concepts: string[];
  strong_concepts: string[];
  recommended_action: string;
  details: { question: string; your_answer: number; correct_answer: number; correct: boolean; explanation: string }[];
}

export default function QuizPage() {
  const { id: segmentId } = useParams();
  const { user } = useAuth();
  const router = useRouter();
  const [quiz, setQuiz] = useState<QuizData | null>(null);
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [result, setResult] = useState<QuizResultData | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (segmentId) {
      api.generateQuiz(segmentId as string)
        .then((q) => setQuiz(q as QuizData))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [segmentId]);

  const handleAnswer = () => {
    if (selected === null) return;
    const newAnswers = [...answers, selected];
    setAnswers(newAnswers);
    setSelected(null);

    if (quiz && currentQ < quiz.questions.length - 1) {
      setCurrentQ(currentQ + 1);
    } else {
      // Submit
      submitQuiz(newAnswers);
    }
  };

  const submitQuiz = async (finalAnswers: number[]) => {
    if (!quiz) return;
    setSubmitting(true);
    try {
      const res = await api.submitQuiz(quiz.quiz_id, finalAnswers, user?.id);
      setResult(res as QuizResultData);
    } catch (e) {
      console.error(e);
    }
    setSubmitting(false);
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto animate-pulse space-y-4">
        <div className="h-8 bg-night rounded w-48" />
        <div className="h-64 bg-night rounded-xl" />
      </div>
    );
  }

  if (!quiz || quiz.questions.length === 0) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <p className="text-muted-foreground">Unable to generate quiz. Try again later.</p>
      </div>
    );
  }

  if (result) {
    return <QuizResults result={result} onBack={() => router.push(`/learn/${segmentId}`)} />;
  }

  const question = quiz.questions[currentQ];
  const difficultyColor = question.difficulty === "easy" ? "text-green-400 bg-green-400/10" :
    question.difficulty === "hard" ? "text-red-400 bg-red-400/10" : "text-yellow-400 bg-yellow-400/10";

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <p className="text-xs font-medium text-muted-foreground">{quiz.title}</p>
        <div className="flex items-center justify-between mt-2">
          <h1 className="text-lg font-bold">Question {currentQ + 1} of {quiz.questions.length}</h1>
          <span className={`text-xs px-2 py-1 rounded capitalize font-medium ${difficultyColor}`}>{question.difficulty}</span>
        </div>
        {/* Progress */}
        <div className="w-full h-1.5 bg-night rounded-full mt-3">
          <div className="h-1.5 bg-lime rounded-full transition-all" style={{ width: `${((currentQ + 1) / quiz.questions.length) * 100}%` }} />
        </div>
        {/* Difficulty indicator */}
        <div className="flex gap-1 mt-2">
          {quiz.questions.map((q, i) => (
            <div key={i} className={`h-1 flex-1 rounded-full ${
              i < currentQ ? "bg-lime" :
              i === currentQ ? (q.difficulty === "easy" ? "bg-green-400" : q.difficulty === "hard" ? "bg-red-400" : "bg-yellow-400") :
              "bg-[#362d59]"
            }`} />
          ))}
        </div>
      </div>

      <div className="bg-night border border-hairline rounded-xl p-6 space-y-6">
        <p className="text-base font-medium">{question.question}</p>
        <div className="space-y-3">
          {question.options.map((option, idx) => (
            <button
              key={idx}
              onClick={() => setSelected(idx)}
              className={`w-full text-left p-4 rounded-lg border transition-colors text-sm ${
                selected === idx
                  ? "border-lime bg-lime/10"
                  : "border-hairline hover:border-[#6a5fc1]"
              }`}
            >
              <span className="font-medium mr-2">{String.fromCharCode(65 + idx)}.</span>
              {option}
            </button>
          ))}
        </div>

        <button
          onClick={handleAnswer}
          disabled={selected === null || submitting}
          className="w-full bg-lime text-[#150f23] py-3 rounded-md text-sm font-bold uppercase tracking-wide disabled:opacity-50 transition-opacity"
        >
          {currentQ < quiz.questions.length - 1 ? "Next Question" : "Submit Quiz"}
        </button>
      </div>
    </div>
  );
}

function QuizResults({ result, onBack }: { result: QuizResultData; onBack: () => void }) {
  const scorePercent = Math.round(result.score * 100);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-night border border-hairline rounded-xl p-8 text-center">
        <div className={`text-5xl font-bold mb-2 ${scorePercent >= 80 ? "text-lime" : scorePercent >= 50 ? "text-yellow-400" : "text-pink-accent"}`}>
          {scorePercent}%
        </div>
        <p className="text-sm text-muted-foreground">
          {result.correct_answers} of {result.total_questions} correct
        </p>
      </div>

      <div className="bg-night border border-hairline rounded-xl p-6 space-y-4">
        <h3 className="font-semibold">Recommended Action</h3>
        <p className="text-sm text-muted-foreground">{result.recommended_action}</p>

        {result.strong_concepts.length > 0 && (
          <div>
            <p className="text-xs font-medium text-lime mb-1">Strong</p>
            <div className="flex flex-wrap gap-1">
              {result.strong_concepts.map((c) => (
                <span key={c} className="text-xs bg-lime/10 text-lime px-2 py-1 rounded">{c}</span>
              ))}
            </div>
          </div>
        )}

        {result.weak_concepts.length > 0 && (
          <div>
            <p className="text-xs font-medium text-pink-accent mb-1">Needs Work</p>
            <div className="flex flex-wrap gap-1">
              {result.weak_concepts.map((c) => (
                <span key={c} className="text-xs bg-[#fa7faa]/10 text-pink-accent px-2 py-1 rounded">{c}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {result.details && (
        <div className="space-y-3">
          {result.details.map((d, idx) => (
            <div key={idx} className="bg-night border border-hairline rounded-xl p-4">
              <div className="flex items-start gap-2">
                {d.correct ? <CheckCircle2 className="h-4 w-4 text-lime mt-0.5" /> : <XCircle className="h-4 w-4 text-pink-accent mt-0.5" />}
                <div>
                  <p className="text-sm font-medium">{d.question}</p>
                  <p className="text-xs text-muted-foreground mt-1">{d.explanation}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={onBack}
        className="w-full bg-lime text-[#150f23] py-3 rounded-md text-sm font-bold uppercase tracking-wide flex items-center justify-center gap-2"
      >
        Continue Learning <ArrowRight className="h-4 w-4" />
      </button>
    </div>
  );
}
