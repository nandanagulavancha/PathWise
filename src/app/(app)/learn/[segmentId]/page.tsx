"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { LearningSegment, LearningPath, Resource } from "@/lib/types";
import { BookOpen, Play, CheckCircle2, ExternalLink, ThumbsUp, ThumbsDown, MessageCircle } from "lucide-react";
import Link from "next/link";

export default function LearnSegmentPage() {
  const { segmentId } = useParams();
  const { user } = useAuth();
  const [segment, setSegment] = useState<LearningSegment | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "resources" | "quiz">("overview");

  useEffect(() => {
    if (user && segmentId) {
      // Fetch segment data via roadmap
      api.getRoadmap(user.id).then((path: unknown) => {
        const p = path as LearningPath | null;
        if (p && p.segments) {
          const seg = p.segments.find((s) => s.id === segmentId);
          if (seg) setSegment(seg);
        }
      }).catch(console.error).finally(() => setLoading(false));
    }
  }, [user, segmentId]);

  if (loading) {
    return <div className="animate-pulse space-y-4"><div className="h-8 bg-night rounded w-64" /><div className="h-48 bg-night rounded-xl" /></div>;
  }

  if (!segment) {
    return <div className="text-center py-16"><p className="text-muted-foreground">Segment not found.</p></div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-lime mb-1">Phase {segment.sequence}</p>
        <h1 className="text-2xl font-bold">{segment.title}</h1>
        {segment.estimated_duration && (
          <p className="text-sm text-muted-foreground mt-1">{segment.estimated_duration} estimated</p>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-night rounded-lg p-1 border border-hairline">
        {(["overview", "resources", "quiz"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium capitalize transition-colors ${
              activeTab === tab ? "bg-[#362d59] text-white" : "text-muted-foreground hover:text-white"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "overview" && (
        <div className="bg-night border border-hairline rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-lime" /> Overview
          </h2>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {segment.overview || "Overview will be generated when you start this segment."}
          </p>
          {segment.skills && segment.skills.length > 0 && (
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-2">Skills you will develop:</p>
              <div className="flex flex-wrap gap-2">
                {segment.skills.map((s) => (
                  <span key={s} className="text-xs bg-[#362d59] border border-hairline px-3 py-1 rounded-full">{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "resources" && (
        <div className="space-y-4">
          {segment.resources && segment.resources.length > 0 ? (
            segment.resources.map((resource, idx) => (
              <div key={resource.id}>
                <ResourceCard resource={resource} userId={user?.id || ""} segmentId={segment.id} resourceIndex={idx} />
              </div>
            ))
          ) : (
            <div className="bg-night border border-hairline rounded-xl p-8 text-center">
              <p className="text-sm text-muted-foreground">Resources will be loaded when this segment is active.</p>
            </div>
          )}
        </div>
      )}

      {activeTab === "quiz" && (
        <div className="bg-night border border-hairline rounded-xl p-8 text-center">
          <h3 className="text-lg font-semibold mb-2">Full Reflection Quiz</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Test your understanding of the entire segment: {segment.title}
          </p>
          <Link
            href={`/quiz/${segment.id}`}
            className="inline-flex items-center gap-2 bg-lime text-[#150f23] px-5 py-2 rounded-md text-sm font-bold uppercase tracking-wide"
          >
            Start Full Quiz
          </Link>
        </div>
      )}
    </div>
  );
}

function ResourceCard({ resource, userId, segmentId, resourceIndex }: { resource: Resource; userId: string; segmentId: string; resourceIndex: number }) {
  const [completed, setCompleted] = useState(false);
  const [showQuiz, setShowQuiz] = useState(false);
  const [quizQuestion, setQuizQuestion] = useState<{ question: string; options: string[]; correct_answer: number; explanation: string } | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [answered, setAnswered] = useState(false);
  const [loadingQuiz, setLoadingQuiz] = useState(false);

  const handleComplete = async () => {
    try {
      await api.markComplete(userId, undefined, resource.id);
      setCompleted(true);
      // Generate a quick quiz question for this resource
      setLoadingQuiz(true);
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/quiz/quick`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ resource_title: resource.title, segment_id: segmentId }),
        });
        if (res.ok) {
          const data = await res.json();
          if (data.question) {
            setQuizQuestion(data);
            setShowQuiz(true);
          }
        }
      } catch {}
      setLoadingQuiz(false);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAnswer = (idx: number) => {
    setSelectedAnswer(idx);
    setAnswered(true);
  };

  return (
    <div className="bg-night border border-hairline rounded-xl p-5 space-y-4">
      <div className="flex gap-4">
        {resource.thumbnail && (
          <img src={resource.thumbnail} alt="" className="w-32 h-20 object-cover rounded-lg flex-shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="text-sm font-semibold line-clamp-2">{resource.title}</h3>
              <p className="text-xs text-muted-foreground mt-1">
                {(resource.metadata?.channel as string) || resource.provider} {resource.duration && `· ${resource.duration}`}
              </p>
            </div>
            {completed && <CheckCircle2 className="h-5 w-5 text-lime flex-shrink-0" />}
          </div>
          <div className="flex items-center gap-2 mt-3">
            <a
              href={resource.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs bg-[#362d59] px-3 py-1.5 rounded-md hover:bg-[#422082] transition-colors"
            >
              <Play className="h-3 w-3" /> Open <ExternalLink className="h-3 w-3" />
            </a>
            {!completed && (
              <button
                onClick={handleComplete}
                className="text-xs text-muted-foreground hover:text-lime transition-colors"
              >
                Mark Complete
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Mini Quiz after completion */}
      {loadingQuiz && (
        <div className="pt-3 border-t border-hairline">
          <p className="text-xs text-muted-foreground animate-pulse">Generating quick quiz...</p>
        </div>
      )}
      {showQuiz && quizQuestion && (
        <div className="pt-3 border-t border-hairline space-y-3">
          <p className="text-xs font-medium text-lime uppercase tracking-wide">Quick Check</p>
          <p className="text-sm font-medium">{quizQuestion.question}</p>
          <div className="space-y-2">
            {quizQuestion.options.map((opt, idx) => (
              <button
                key={idx}
                onClick={() => !answered && handleAnswer(idx)}
                disabled={answered}
                className={`w-full text-left px-3 py-2 rounded-lg text-xs border transition-colors ${
                  answered && idx === quizQuestion.correct_answer
                    ? "border-lime bg-lime/10 text-lime"
                    : answered && idx === selectedAnswer && idx !== quizQuestion.correct_answer
                    ? "border-red-500 bg-red-500/10 text-red-400"
                    : selectedAnswer === idx
                    ? "border-lime bg-lime/10"
                    : "border-hairline hover:border-[#6a5fc1]"
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
          {answered && (
            <p className="text-xs text-muted-foreground">{quizQuestion.explanation}</p>
          )}
        </div>
      )}
    </div>
  );
}
