"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { DashboardData, LearningPath } from "@/lib/types";
import { BookOpen, Target, Flame, Clock, Route, ArrowRight, Brain } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      api.getDashboardData(user.id).then((d) => setData(d as DashboardData)).catch(console.error).finally(() => setLoading(false));
    }
  }, [user]);

  if (loading) return <DashboardSkeleton />;

  const progress = data?.progress;
  const path = data?.learning_path;

  return (
    <div className="space-y-8">
      {/* Greeting */}
      <div>
        <h1 className="text-2xl font-bold">Good {getGreeting()}, {user?.email?.split("@")[0] || "Learner"}</h1>
        <p className="text-sm text-muted-foreground mt-1">Let&apos;s make progress toward your goal.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard icon={<Route className="h-5 w-5" />} label="Overall" value={`${progress?.overall_percentage || 0}%`} />
        <StatCard icon={<Target className="h-5 w-5" />} label="Skills Mastered" value={String(data?.skills?.filter((s) => s.current_level === "advanced").length || 0)} />
        <StatCard icon={<Flame className="h-5 w-5" />} label="Streak" value={`${progress?.current_streak || 0} days`} />
        <StatCard icon={<Clock className="h-5 w-5" />} label="Hours Learned" value={String(progress?.hours_learned || 0)} />
        <StatCard icon={<BookOpen className="h-5 w-5" />} label="Current Phase" value={getCurrentPhase(path)} />
      </div>

      {/* Continue Learning */}
      {path && path.segments.length > 0 ? (
        <ContinueLearningCard segment={path.segments.find((s) => s.status === "in_progress") || path.segments[0]} />
      ) : (
        <EmptyRoadmapCard />
      )}

      {/* Skill Development + Roadmap Preview */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-night border border-hairline rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Skill Development</h2>
          {data?.skills && data.skills.length > 0 ? (
            <div className="space-y-3">
              {data.skills.slice(0, 6).map((skill, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-sm font-medium capitalize">{skill.skill_name || skill.skill_id}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-[#362d59] rounded-full">
                      <div
                        className="h-1.5 bg-lime rounded-full"
                        style={{ width: `${skill.confidence * 20}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground capitalize">{skill.current_level}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Complete your profile to see your skill map.</p>
          )}
        </div>

        <div className="bg-night border border-hairline rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Roadmap Preview</h2>
          {path ? (
            <div className="space-y-3">
              {path.segments.slice(0, 5).map((segment, idx) => (
                <div key={segment.id} className="flex items-center gap-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    segment.status === "completed" ? "bg-lime text-[#150f23]" :
                    segment.status === "in_progress" ? "bg-[#6a5fc1] text-white" :
                    "bg-[#362d59] text-muted-foreground"
                  }`}>
                    {idx + 1}
                  </div>
                  <span className={`text-sm ${segment.status === "locked" ? "text-muted-foreground" : "font-medium"}`}>
                    {segment.title}
                  </span>
                </div>
              ))}
              <Link href="/roadmap" className="text-sm text-[#6a5fc1] hover:underline mt-2 inline-block">
                View full roadmap
              </Link>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Your learning journey starts here.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-night border border-hairline rounded-xl p-4">
      <div className="flex items-center gap-2 mb-2 text-muted-foreground">{icon}<span className="text-xs font-medium">{label}</span></div>
      <div className="text-xl font-bold">{value}</div>
    </div>
  );
}

function ContinueLearningCard({ segment }: { segment: { id: string; title: string; estimated_duration?: string } }) {
  return (
    <div className="bg-gradient-to-r from-[#422082] to-[#362d59] border border-[#6a5fc1] rounded-xl p-6">
      <p className="text-xs font-medium uppercase tracking-wide text-lime mb-2">Continue Learning</p>
      <h3 className="text-lg font-bold mb-1">{segment.title}</h3>
      {segment.estimated_duration && (
        <p className="text-sm text-muted-foreground mb-4">{segment.estimated_duration} estimated</p>
      )}
      <Link
        href={`/learn/${segment.id}`}
        className="inline-flex items-center gap-2 bg-lime text-[#150f23] px-5 py-2 rounded-md text-sm font-bold uppercase tracking-wide hover:opacity-90 transition-opacity"
      >
        Continue <ArrowRight className="h-4 w-4" />
      </Link>
    </div>
  );
}

function EmptyRoadmapCard() {
  return (
    <div className="bg-night border border-hairline rounded-xl p-8 text-center">
      <Brain className="h-12 w-12 text-lime mx-auto mb-4" />
      <h3 className="text-lg font-bold mb-2">No roadmap yet</h3>
      <p className="text-sm text-muted-foreground mb-4">Tell me what you want to achieve, and I&apos;ll build your first learning path.</p>
      <Link
        href="/onboarding"
        className="inline-flex items-center gap-2 bg-lime text-[#150f23] px-5 py-2 rounded-md text-sm font-bold uppercase tracking-wide hover:opacity-90 transition-opacity"
      >
        Get Started <ArrowRight className="h-4 w-4" />
      </Link>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-8 bg-night rounded w-64" />
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        {[...Array(5)].map((_, i) => <div key={i} className="h-24 bg-night rounded-xl" />)}
      </div>
      <div className="h-40 bg-night rounded-xl" />
    </div>
  );
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "morning";
  if (hour < 17) return "afternoon";
  return "evening";
}

function getCurrentPhase(path: LearningPath | null | undefined) {
  if (!path) return "N/A";
  const current = path.segments.find((s: { status: string; sequence: number }) => s.status === "in_progress");
  return current ? `Phase ${current.sequence}` : "Not started";
}
