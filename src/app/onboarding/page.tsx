"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Brain, ArrowRight, ArrowLeft, Check } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { ExperienceLevel, OnboardingData } from "@/lib/types";

const INTERESTS = [
  "Web Development", "Mobile Development", "AI/ML", "Data Science",
  "Cybersecurity", "Cloud", "DevOps", "UI/UX", "Programming",
  "Databases", "Blockchain", "Game Development",
];

const EXPERIENCE_LEVELS: { value: ExperienceLevel; label: string; description: string }[] = [
  { value: "beginner", label: "Beginner", description: "New to programming or this field" },
  { value: "intermediate", label: "Intermediate", description: "Some experience, built small projects" },
  { value: "advanced", label: "Advanced", description: "Professional experience, complex projects" },
];

export default function OnboardingPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<OnboardingData>({
    profile: {
      name: "",
      experience_level: "beginner",
      occupation: "",
      preferred_language: "English",
      weekly_hours: 10,
      preferred_learning_style: "video",
    },
    interests: [],
    skills: [],
    previous_learning: [],
    goal: "",
    preferences: {},
  });

  const totalSteps = 7;

  const updateProfile = (field: string, value: unknown) => {
    setData((prev) => ({
      ...prev,
      profile: { ...prev.profile, [field]: value },
    }));
  };

  const handleNext = () => {
    if (step < totalSteps) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const [generatingStep, setGeneratingStep] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!user?.id) {
      setError("Not authenticated. Please go back and sign in first.");
      return;
    }
    setError("");
    setLoading(true);
    setGeneratingStep("Saving your profile...");
    try {
      await api.completeOnboarding(data, user.id);
      setGeneratingStep("Your roadmap is being generated in the background...");
      // Wait briefly then redirect — roadmap generates in background
      setTimeout(() => {
        setGeneratingStep("Redirecting to your dashboard...");
        router.push("/dashboard");
      }, 2000);
    } catch (err) {
      console.error("Onboarding failed:", err);
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
      setGeneratingStep("");
      setLoading(false);
    }
  };

  if (loading && generatingStep) {
    return (
      <div className="min-h-screen bg-canvas flex flex-col items-center justify-center px-4">
        <Brain className="h-12 w-12 text-lime animate-pulse mb-6" />
        <h2 className="text-xl font-bold mb-2">Building your personalized path</h2>
        <p className="text-sm text-muted-foreground mb-6">{generatingStep}</p>
        <div className="w-64 h-1.5 bg-night rounded-full overflow-hidden">
          <div className="h-full bg-lime rounded-full animate-[pulse_2s_ease-in-out_infinite] w-2/3" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-canvas flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <Brain className="h-10 w-10 text-lime mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">Let&apos;s personalize your learning</h1>
          <p className="text-sm text-muted-foreground">Step {step} of {totalSteps}</p>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-night rounded-full h-1.5 mb-8">
          <div
            className="bg-lime h-1.5 rounded-full transition-all duration-300"
            style={{ width: `${(step / totalSteps) * 100}%` }}
          />
        </div>

        {/* Steps */}
        <div className="bg-night border border-hairline rounded-xl p-8">
          {step === 1 && (
            <StepAboutYou data={data} updateProfile={updateProfile} />
          )}
          {step === 2 && (
            <StepInterests data={data} setData={setData} />
          )}
          {step === 3 && (
            <StepSkills data={data} setData={setData} />
          )}
          {step === 4 && (
            <StepPreviousLearning data={data} setData={setData} />
          )}
          {step === 5 && (
            <StepGoal data={data} setData={setData} />
          )}
          {step === 6 && (
            <StepPreferences data={data} updateProfile={updateProfile} setData={setData} />
          )}
          {step === 7 && (
            <StepConfirmation data={data} />
          )}
        </div>

        {/* Navigation */}
        {error && (
          <div className="mt-4 bg-destructive/10 border border-destructive/30 rounded-md p-3 text-sm text-red-400">
            {error}
          </div>
        )}
        <div className="flex justify-between mt-6">
          <button
            onClick={handleBack}
            disabled={step === 1}
            className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-white disabled:opacity-30 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" /> Back
          </button>

          {step < totalSteps ? (
            <button
              onClick={handleNext}
              className="flex items-center gap-2 bg-lime text-[#150f23] px-6 py-2.5 rounded-md text-sm font-bold uppercase tracking-wide hover:opacity-90 transition-opacity"
            >
              Continue <ArrowRight className="h-4 w-4" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="flex items-center gap-2 bg-lime text-[#150f23] px-6 py-2.5 rounded-md text-sm font-bold uppercase tracking-wide hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              {loading ? "Building your path..." : "Generate My Roadmap"}
              {!loading && <Check className="h-4 w-4" />}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function StepAboutYou({ data, updateProfile }: { data: OnboardingData; updateProfile: (f: string, v: unknown) => void }) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">About You</h2>
      <div>
        <label className="block text-sm font-medium mb-1.5">Display Name</label>
        <input
          type="text"
          value={data.profile.name}
          onChange={(e) => updateProfile("name", e.target.value)}
          className="w-full bg-[#1f1633] border border-hairline rounded-md px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#6a5fc1]"
          placeholder="How should we address you?"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1.5">Current Occupation</label>
        <input
          type="text"
          value={data.profile.occupation || ""}
          onChange={(e) => updateProfile("occupation", e.target.value)}
          className="w-full bg-[#1f1633] border border-hairline rounded-md px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#6a5fc1]"
          placeholder="e.g. Student, Software Developer, Product Manager"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-3">Experience Level</label>
        <div className="space-y-2">
          {EXPERIENCE_LEVELS.map((level) => (
            <button
              key={level.value}
              onClick={() => updateProfile("experience_level", level.value)}
              className={`w-full text-left p-4 rounded-lg border transition-colors ${
                data.profile.experience_level === level.value
                  ? "border-lime bg-[#362d59]"
                  : "border-hairline hover:border-[#6a5fc1]"
              }`}
            >
              <div className="font-medium text-sm">{level.label}</div>
              <div className="text-xs text-muted-foreground mt-0.5">{level.description}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function StepInterests({ data, setData }: { data: OnboardingData; setData: React.Dispatch<React.SetStateAction<OnboardingData>> }) {
  const [custom, setCustom] = useState("");

  const toggle = (interest: string) => {
    setData((prev) => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter((i) => i !== interest)
        : [...prev.interests, interest],
    }));
  };

  const addCustom = () => {
    if (custom.trim() && !data.interests.includes(custom.trim())) {
      setData((prev) => ({ ...prev, interests: [...prev.interests, custom.trim()] }));
      setCustom("");
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">What are you interested in?</h2>
      <p className="text-sm text-muted-foreground">Select all that apply</p>
      <div className="flex flex-wrap gap-2">
        {INTERESTS.map((interest) => (
          <button
            key={interest}
            onClick={() => toggle(interest)}
            className={`px-4 py-2 rounded-full text-sm font-medium border transition-colors ${
              data.interests.includes(interest)
                ? "bg-lime text-[#150f23] border-lime"
                : "border-hairline hover:border-[#6a5fc1]"
            }`}
          >
            {interest}
          </button>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={custom}
          onChange={(e) => setCustom(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addCustom()}
          className="flex-1 bg-[#1f1633] border border-hairline rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#6a5fc1]"
          placeholder="Add custom interest..."
        />
        <button onClick={addCustom} className="px-4 py-2 bg-[#362d59] rounded-md text-sm font-medium hover:bg-[#422082] transition-colors">
          Add
        </button>
      </div>
    </div>
  );
}

function StepSkills({ data, setData }: { data: OnboardingData; setData: React.Dispatch<React.SetStateAction<OnboardingData>> }) {
  const [allSkills, setAllSkills] = useState<{ id: string; name: string; category: string }[]>([]);
  const [filter, setFilter] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");

  useEffect(() => {
    api.getSkills().then((s) => {
      if (Array.isArray(s)) setAllSkills(s);
    }).catch(() => {});
  }, []);

  const categories = ["All", ...Array.from(new Set(allSkills.map((s) => s.category).filter(Boolean)))];

  const filtered = allSkills.filter((s) => {
    const matchesFilter = s.name.toLowerCase().includes(filter.toLowerCase());
    const matchesCategory = selectedCategory === "All" || s.category === selectedCategory;
    return matchesFilter && matchesCategory;
  });

  const isSelected = (skillId: string) => data.skills.some((s) => s.skill_id === skillId);

  const toggleSkill = (skill: { id: string; name: string }) => {
    if (isSelected(skill.id)) {
      setData((prev) => ({ ...prev, skills: prev.skills.filter((s) => s.skill_id !== skill.id) }));
    } else {
      setData((prev) => ({
        ...prev,
        skills: [...prev.skills, { skill_id: skill.id, current_level: "beginner" as ExperienceLevel, confidence: 3 }],
      }));
    }
  };

  const updateLevel = (skillId: string, level: ExperienceLevel) => {
    setData((prev) => ({
      ...prev,
      skills: prev.skills.map((s) => s.skill_id === skillId ? { ...s, current_level: level } : s),
    }));
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Your Existing Skills</h2>
      <p className="text-sm text-muted-foreground">Select skills you already know and set your level</p>

      <input
        type="text"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        className="w-full bg-[#1f1633] border border-hairline rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#6a5fc1]"
        placeholder="Search skills..."
      />

      <div className="flex gap-2 flex-wrap">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
              selectedCategory === cat ? "bg-lime text-[#150f23] border-lime" : "border-hairline hover:border-[#6a5fc1]"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="max-h-48 overflow-y-auto space-y-1 pr-1">
        {filtered.slice(0, 30).map((skill) => (
          <button
            key={skill.id}
            onClick={() => toggleSkill(skill)}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between ${
              isSelected(skill.id) ? "bg-[#362d59] border border-lime" : "border border-hairline hover:border-[#6a5fc1]"
            }`}
          >
            <span>{skill.name}</span>
            <span className="text-xs text-muted-foreground">{skill.category}</span>
          </button>
        ))}
      </div>

      {data.skills.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-2">Selected ({data.skills.length}):</p>
          <div className="space-y-2">
            {data.skills.map((skill) => {
              const info = allSkills.find((s) => s.id === skill.skill_id);
              return (
                <div key={skill.skill_id} className="flex items-center justify-between bg-[#1f1633] border border-hairline rounded-lg px-3 py-2">
                  <span className="text-sm font-medium">{info?.name || skill.skill_id}</span>
                  <select
                    value={skill.current_level}
                    onChange={(e) => updateLevel(skill.skill_id, e.target.value as ExperienceLevel)}
                    className="bg-[#150f23] border border-hairline rounded px-2 py-1 text-xs"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function StepPreviousLearning({ data, setData }: { data: OnboardingData; setData: React.Dispatch<React.SetStateAction<OnboardingData>> }) {
  const [item, setItem] = useState("");

  const add = () => {
    if (item.trim()) {
      setData((prev) => ({ ...prev, previous_learning: [...prev.previous_learning, item.trim()] }));
      setItem("");
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Previous Learning</h2>
      <p className="text-sm text-muted-foreground">Courses, certifications, or projects you&apos;ve completed</p>

      <div className="flex gap-2">
        <input
          type="text"
          value={item}
          onChange={(e) => setItem(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && add()}
          className="flex-1 bg-[#1f1633] border border-hairline rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#6a5fc1]"
          placeholder="e.g. CS50, freeCodeCamp JavaScript..."
        />
        <button onClick={add} className="px-4 py-2 bg-[#362d59] rounded-md text-sm font-medium hover:bg-[#422082] transition-colors">Add</button>
      </div>

      {data.previous_learning.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {data.previous_learning.map((item, idx) => (
            <span key={idx} className="px-3 py-1.5 bg-[#362d59] rounded-full text-xs font-medium flex items-center gap-2">
              {item}
              <button
                onClick={() => setData((prev) => ({ ...prev, previous_learning: prev.previous_learning.filter((_, i) => i !== idx) }))}
                className="text-muted-foreground hover:text-red-400"
              >
                x
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function StepGoal({ data, setData }: { data: OnboardingData; setData: React.Dispatch<React.SetStateAction<OnboardingData>> }) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">What do you want to achieve?</h2>
      <p className="text-sm text-muted-foreground">
        Describe your learning goal in your own words. Be as specific as you like.
      </p>
      <textarea
        value={data.goal}
        onChange={(e) => setData((prev) => ({ ...prev, goal: e.target.value }))}
        rows={5}
        className="w-full bg-[#1f1633] border border-hairline rounded-md px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#6a5fc1] resize-none"
        placeholder="e.g. I want to become a full-stack developer and build production-ready applications within 6 months."
      />
      <p className="text-xs text-muted-foreground">
        The more detail you provide, the better your AI mentor can personalize your learning path.
      </p>
    </div>
  );
}

function StepPreferences({ data, updateProfile, setData }: { data: OnboardingData; updateProfile: (f: string, v: unknown) => void; setData: React.Dispatch<React.SetStateAction<OnboardingData>> }) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Learning Preferences</h2>

      <div>
        <label className="block text-sm font-medium mb-1.5">Preferred Language</label>
        <input
          type="text"
          value={data.profile.preferred_language}
          onChange={(e) => updateProfile("preferred_language", e.target.value)}
          className="w-full bg-[#1f1633] border border-hairline rounded-md px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#6a5fc1]"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5">Weekly Study Hours</label>
        <input
          type="number"
          value={data.profile.weekly_hours}
          onChange={(e) => updateProfile("weekly_hours", parseInt(e.target.value) || 5)}
          min={1}
          max={60}
          className="w-full bg-[#1f1633] border border-hairline rounded-md px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#6a5fc1]"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-3">Preferred Learning Format</label>
        <div className="grid grid-cols-2 gap-2">
          {["Video", "Article", "Interactive", "Project-based"].map((format) => (
            <button
              key={format}
              onClick={() => updateProfile("preferred_learning_style", format.toLowerCase())}
              className={`p-3 rounded-lg border text-sm font-medium transition-colors ${
                data.profile.preferred_learning_style === format.toLowerCase()
                  ? "border-lime bg-[#362d59]"
                  : "border-hairline hover:border-[#6a5fc1]"
              }`}
            >
              {format}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function StepConfirmation({ data }: { data: OnboardingData }) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Here&apos;s what I understand about you</h2>
      <p className="text-sm text-muted-foreground">Review before we generate your personalized roadmap</p>

      <div className="space-y-4">
        <SummaryItem label="Name" value={data.profile.name || "Not set"} />
        <SummaryItem label="Level" value={data.profile.experience_level} />
        <SummaryItem label="Occupation" value={data.profile.occupation || "Not specified"} />
        <SummaryItem label="Interests" value={data.interests.join(", ") || "None selected"} />
        <SummaryItem
          label="Skills"
          value={data.skills.map((s) => `${s.skill_id.replace(/-/g, " ")} (${s.current_level})`).join(", ") || "None added"}
        />
        <SummaryItem label="Goal" value={data.goal || "Not set"} />
        <SummaryItem label="Weekly hours" value={`${data.profile.weekly_hours} hours`} />
        <SummaryItem label="Format" value={data.profile.preferred_learning_style || "Not specified"} />
      </div>
    </div>
  );
}

function SummaryItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 bg-[#1f1633] rounded-lg p-3 border border-hairline">
      <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</span>
      <span className="text-sm capitalize">{value}</span>
    </div>
  );
}
