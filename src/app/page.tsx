import Link from "next/link";
import { ArrowRight, Brain, Target, Route, MessageCircle, BarChart3, Sparkles } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-canvas">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <Brain className="h-8 w-8 text-lime" />
          <span className="text-xl font-bold tracking-tight">Pathwise AI</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Log In
          </Link>
          <Link
            href="/signup"
            className="bg-lime text-[#150f23] px-4 py-2 rounded-md text-sm font-bold uppercase tracking-wide hover:opacity-90 transition-opacity"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 pt-24 pb-32 text-center">
        <h1 className="text-5xl md:text-7xl lg:text-[88px] font-bold leading-[1.1] tracking-tight mb-8">
          Your learning path should{" "}
          <span className="highlight-chip">adapt</span>{" "}
          to you.
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-12 leading-relaxed">
          Pathwise AI turns your goals, skills and learning behavior into a personalized
          roadmap that evolves as you learn.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/signup"
            className="bg-lime text-[#150f23] px-8 py-3 rounded-md text-sm font-bold uppercase tracking-wide hover:opacity-90 transition-opacity inline-flex items-center gap-2"
          >
            Build My Learning Path <ArrowRight className="h-4 w-4" />
          </Link>
          <a
            href="#how-it-works"
            className="border border-[rgba(255,255,255,0.18)] bg-[rgba(255,255,255,0.05)] px-8 py-3 rounded-md text-sm font-medium uppercase tracking-wide hover:bg-[rgba(255,255,255,0.1)] transition-colors"
          >
            See How It Works
          </a>
        </div>
      </section>

      {/* Features */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-6 pb-32">
        <div className="text-center mb-16">
          <p className="text-sm font-medium uppercase tracking-wide text-lime mb-4">How It Works</p>
          <h2 className="text-3xl md:text-5xl font-bold">
            Your AI learning mentor
          </h2>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard
            icon={<Target className="h-6 w-6 text-lime" />}
            title="Personalized Learning"
            description="Tell us your goals in natural language. Our AI understands what you want to achieve and builds a path just for you."
          />
          <FeatureCard
            icon={<Brain className="h-6 w-6 text-lime" />}
            title="AI Skill Gap Analysis"
            description="We analyze your current skills against your target role, identifying exactly what you need to learn and in what order."
          />
          <FeatureCard
            icon={<Route className="h-6 w-6 text-lime" />}
            title="Adaptive Roadmaps"
            description="Your roadmap evolves based on your quiz performance, feedback, and learning pace. Never static, always personalized."
          />
          <FeatureCard
            icon={<Sparkles className="h-6 w-6 text-lime" />}
            title="AI Reflection Quizzes"
            description="Generated from your actual learning material, quizzes identify weak areas and adapt your path accordingly."
          />
          <FeatureCard
            icon={<BarChart3 className="h-6 w-6 text-lime" />}
            title="Progress Intelligence"
            description="Track skill mastery, not just resource completion. See exactly how your abilities grow over time."
          />
          <FeatureCard
            icon={<MessageCircle className="h-6 w-6 text-lime" />}
            title="AI Mentor"
            description="Ask your personal AI mentor anything about your learning journey. It knows your profile, progress, and goals."
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-hairline py-8 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-lime" />
            <span className="text-sm font-medium">Pathwise AI</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Learn what matters. In the right order. At your pace.
          </p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-night border border-hairline rounded-xl p-6 hover:border-[#6a5fc1] transition-colors">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
    </div>
  );
}
