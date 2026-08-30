"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { UserSkill, SkillGap } from "@/lib/types";
import { Target, TrendingUp, AlertTriangle } from "lucide-react";

const GAP_COLORS = {
  none: "bg-lime",
  low: "bg-green-500",
  medium: "bg-yellow-500",
  high: "bg-orange-500",
  critical: "bg-red-500",
};

export default function SkillsPage() {
  const { user } = useAuth();
  const [skills, setSkills] = useState<UserSkill[]>([]);
  const [gaps, setGaps] = useState<SkillGap[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      Promise.all([
        api.getSkills().then((s) => setSkills(Array.isArray(s) ? s : [])).catch(() => {}),
        api.getSkillGaps(user.id).then((g) => setGaps(Array.isArray(g) ? g : [])).catch(() => {}),
      ]).finally(() => setLoading(false));
    }
  }, [user]);

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-8 bg-night rounded w-32" />
        <div className="grid md:grid-cols-2 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="h-32 bg-night rounded-xl" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Skills</h1>
        <p className="text-sm text-muted-foreground mt-1">Your skill development and gaps</p>
      </div>

      {/* Skill Gaps */}
      {gaps.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-pink-accent" />
            Skill Gaps
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {gaps.map((gap) => (
              <div key={gap.skill_id} className="bg-night border border-hairline rounded-xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold">{gap.skill_name}</h3>
                  <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${
                    gap.gap === "critical" ? "bg-red-500/20 text-red-400" :
                    gap.gap === "high" ? "bg-orange-500/20 text-orange-400" :
                    gap.gap === "medium" ? "bg-yellow-500/20 text-yellow-400" :
                    "bg-green-500/20 text-green-400"
                  }`}>
                    {gap.gap} gap
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Current: <span className="capitalize">{gap.current_level}</span></span>
                    <span>Target: <span className="capitalize">{gap.target_level}</span></span>
                  </div>
                  <div className="w-full h-2 bg-[#362d59] rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${GAP_COLORS[gap.gap] || "bg-lime"}`}
                      style={{ width: `${(1 - ["none", "low", "medium", "high", "critical"].indexOf(gap.gap) / 4) * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">{gap.recommended_action}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Empty state */}
      {gaps.length === 0 && skills.length === 0 && (
        <div className="text-center py-16 bg-night border border-hairline rounded-xl">
          <Target className="h-12 w-12 text-lime mx-auto mb-4" />
          <h3 className="text-lg font-bold mb-2">No skills tracked yet</h3>
          <p className="text-sm text-muted-foreground">Complete your profile and generate a roadmap to see your skill map.</p>
        </div>
      )}
    </div>
  );
}
