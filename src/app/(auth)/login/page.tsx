"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Brain } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { signIn } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const { error } = await signIn(email, password);
    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      router.push("/dashboard");
    }
  };

  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-6">
            <Brain className="h-8 w-8 text-lime" />
            <span className="text-xl font-bold">Pathwise AI</span>
          </Link>
          <h1 className="text-2xl font-bold mb-2">Welcome back</h1>
          <p className="text-sm text-muted-foreground">Continue your learning journey</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-destructive/10 border border-destructive/30 rounded-md p-3 text-sm text-red-400">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-1.5">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-night border border-hairline rounded-md px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-link"
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-night border border-hairline rounded-md px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-link"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-lime text-[#150f23] py-2.5 rounded-md text-sm font-bold uppercase tracking-wide hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            {loading ? "Signing in..." : "Log In"}
          </button>
        </form>

        <div className="flex justify-between text-sm text-muted-foreground mt-6">
          <Link href="/reset-password" className="text-[#6a5fc1] hover:underline">Forgot password?</Link>
          <Link href="/signup" className="text-[#6a5fc1] hover:underline">Create account</Link>
        </div>
      </div>
    </div>
  );
}
