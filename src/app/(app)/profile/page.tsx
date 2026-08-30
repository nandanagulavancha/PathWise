"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { User, RefreshCw, Settings, Loader2 } from "lucide-react";

export default function ProfilePage() {
  const { user } = useAuth();
  const router = useRouter();
  const [regenerating, setRegenerating] = useState(false);

  const handleRegenerate = async () => {
    if (!user?.id) return;
    setRegenerating(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      // Get active goal
      const goalsRes = await fetch(`${API_URL}/api/roadmap/${user.id}`);
      if (goalsRes.ok) {
        const path = await goalsRes.json();
        if (path?.goal_id) {
          // Trigger regeneration
          await fetch(`${API_URL}/api/roadmap/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ goal_id: path.goal_id }),
          });
        }
      }
      router.push("/dashboard");
    } catch (err) {
      console.error("Regeneration failed:", err);
    }
    setRegenerating(false);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Profile</h1>
        <p className="text-sm text-muted-foreground mt-1">Manage your learning profile and preferences</p>
      </div>

      <div className="bg-night border border-hairline rounded-xl p-6 space-y-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-[#362d59] rounded-full flex items-center justify-center">
            <User className="h-8 w-8 text-muted-foreground" />
          </div>
          <div>
            <h2 className="font-semibold">{user?.email}</h2>
            <p className="text-xs text-muted-foreground">Learner</p>
          </div>
        </div>

        <div className="grid gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Email</label>
            <input
              type="email"
              value={user?.email || ""}
              disabled
              className="w-full bg-[#1f1633] border border-hairline rounded-md px-3 py-2.5 text-sm opacity-60"
            />
          </div>
        </div>
      </div>

      <div className="bg-night border border-hairline rounded-xl p-6">
        <h3 className="font-semibold mb-4">Actions</h3>
        <div className="space-y-3">
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="w-full text-left p-4 rounded-lg border border-hairline hover:border-[#6a5fc1] transition-colors disabled:opacity-50"
          >
            <div className="flex items-center gap-2">
              {regenerating ? <Loader2 className="h-4 w-4 animate-spin text-lime" /> : <RefreshCw className="h-4 w-4 text-lime" />}
              <p className="text-sm font-medium">Regenerate My Learning Path</p>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5 ml-6">
              {regenerating ? "Generating new roadmap..." : "Create a new roadmap based on your updated profile"}
            </p>
          </button>
          <button
            onClick={() => router.push("/onboarding")}
            className="w-full text-left p-4 rounded-lg border border-hairline hover:border-[#6a5fc1] transition-colors"
          >
            <div className="flex items-center gap-2">
              <Settings className="h-4 w-4 text-[#6a5fc1]" />
              <p className="text-sm font-medium">Update Onboarding</p>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5 ml-6">Change your interests, skills, and goals</p>
          </button>
        </div>
      </div>
    </div>
  );
}
