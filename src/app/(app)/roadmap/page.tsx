"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { LearningPath, LearningSegment } from "@/lib/types";
import { CheckCircle2, Circle, Lock, AlertCircle, Clock, ChevronDown, ChevronRight } from "lucide-react";
import Link from "next/link";

const STATUS_CONFIG = {
  completed: { icon: CheckCircle2, color: "text-lime", bg: "bg-lime/10", label: "Completed" },
  in_progress: { icon: Circle, color: "text-[#6a5fc1]", bg: "bg-[#6a5fc1]/10", label: "In Progress" },
  upcoming: { icon: Circle, color: "text-muted-foreground", bg: "bg-[#362d59]", label: "Upcoming" },
  needs_review: { icon: AlertCircle, color: "text-pink-accent", bg: "bg-[#fa7faa]/10", label: "Needs Review" },
  locked: { icon: Lock, color: "text-muted-foreground/50", bg: "bg-[#362d59]/50", label: "Locked" },
};

export default function RoadmapPage() {
  const { user } = useAuth();
  const [path, setPath] = useState<LearningPath | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [unlockAll, setUnlockAll] = useState(false);

  useEffect(() => {
    if (user) {
      api.getRoadmap(user.id).then((p) => setPath(p as LearningPath)).catch(() => {}).finally(() => setLoading(false));
    }
  }, [user]);

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-8 bg-night rounded w-48" />
        {[...Array(5)].map((_, i) => <div key={i} className="h-24 bg-night rounded-xl" />)}
      </div>
    );
  }

  if (!path) {
    return (
      <div className="text-center py-16">
        <h2 className="text-xl font-bold mb-2">No roadmap yet</h2>
        <p className="text-muted-foreground mb-4">Complete onboarding to generate your personalized roadmap.</p>
        <Link href="/onboarding" className="bg-lime text-[#150f23] px-5 py-2 rounded-md text-sm font-bold uppercase tracking-wide">
          Get Started
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{path.title}</h1>
          <p className="text-sm text-muted-foreground mt-1">{path.description}</p>
          {path.estimated_duration && (
            <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
              <Clock className="h-3.5 w-3.5" />
              <span>Estimated: {path.estimated_duration}</span>
            </div>
          )}
        </div>
        {/* Lock/Unlock toggle */}
        <button
          onClick={() => setUnlockAll(!unlockAll)}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium border transition-colors ${
            unlockAll ? "border-lime bg-lime/10 text-lime" : "border-hairline text-muted-foreground hover:border-[#6a5fc1]"
          }`}
        >
          {unlockAll ? <Circle className="h-3.5 w-3.5" /> : <Lock className="h-3.5 w-3.5" />}
          {unlockAll ? "Free Access" : "Sequential"}
        </button>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-5 top-0 bottom-0 w-px bg-[#362d59]" />

        <div className="space-y-4">
          {path.segments.map((segment, idx) => {
            const effectiveStatus = unlockAll && segment.status === "locked" ? "upcoming" : segment.status;
            const config = STATUS_CONFIG[effectiveStatus] || STATUS_CONFIG.locked;
            const Icon = config.icon;
            const isExpanded = expanded === segment.id;

            return (
              <div key={segment.id} className="relative pl-12">
                {/* Node */}
                <div className={`absolute left-3 w-5 h-5 rounded-full ${config.bg} flex items-center justify-center`}>
                  <Icon className={`h-3.5 w-3.5 ${config.color}`} />
                </div>

                <div className={`bg-night border border-hairline rounded-xl p-5 transition-colors ${
                  segment.status === "in_progress" ? "border-[#6a5fc1]" : ""
                }`}>
                  <button
                    onClick={() => setExpanded(isExpanded ? null : segment.id)}
                    className="w-full text-left flex items-center justify-between"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-muted-foreground">Phase {idx + 1}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${config.bg} ${config.color}`}>
                          {config.label}
                        </span>
                      </div>
                      <h3 className="text-base font-semibold mt-1">{segment.title}</h3>
                      {segment.estimated_duration && (
                        <p className="text-xs text-muted-foreground mt-0.5">{segment.estimated_duration}</p>
                      )}
                    </div>
                    {isExpanded ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
                  </button>

                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-hairline space-y-3">
                      {segment.overview && <p className="text-sm text-muted-foreground">{segment.overview}</p>}
                      {segment.skills && segment.skills.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-muted-foreground mb-1">Skills</p>
                          <div className="flex flex-wrap gap-1">
                            {segment.skills.map((s) => (
                              <span key={s} className="text-xs bg-[#362d59] px-2 py-1 rounded">{s}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {effectiveStatus !== "locked" && (
                        <Link
                          href={`/learn/${segment.id}`}
                          className="inline-block bg-lime text-[#150f23] px-4 py-2 rounded-md text-xs font-bold uppercase tracking-wide mt-2"
                        >
                          {effectiveStatus === "completed" ? "Review" : "Start Learning"}
                        </Link>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
