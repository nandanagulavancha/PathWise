const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_URL;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `API error: ${res.status}`);
    }

    return res.json();
  }

  // Goals
  async analyzeGoal(rawGoal: string) {
    return this.request("/api/goals/analyze", {
      method: "POST",
      body: JSON.stringify({ raw_goal: rawGoal }),
    });
  }

  async completeOnboarding(data: unknown, userId: string) {
    return this.request(`/api/goals/onboarding?user_id=${userId}`, {
      method: "POST",
      body: JSON.stringify({ ...data as object, user_id: userId }),
    });
  }

  // Roadmap
  async generateRoadmap(goalId: string) {
    return this.request("/api/roadmap/generate", {
      method: "POST",
      body: JSON.stringify({ goal_id: goalId }),
    });
  }

  async getRoadmap(userId: string) {
    return this.request(`/api/roadmap/${userId}`);
  }

  // Skills
  async getSkills(category?: string) {
    const params = category ? `?category=${category}` : "";
    return this.request(`/api/skills/${params}`);
  }

  async getSkillGaps(userId: string) {
    return this.request(`/api/skills/gap/${userId}`);
  }

  // Resources
  async searchResources(query: string, options?: { skill?: string; difficulty?: string; provider?: string }) {
    const params = new URLSearchParams({ query });
    if (options?.skill) params.set("skill", options.skill);
    if (options?.difficulty) params.set("difficulty", options.difficulty);
    if (options?.provider) params.set("provider", options.provider);
    return this.request(`/api/resources/search?${params}`);
  }

  async getResourceExplanation(resourceId: string, userId: string) {
    return this.request(`/api/resources/${resourceId}/explanation?user_id=${userId}`);
  }

  // Quiz
  async generateQuiz(segmentId: string) {
    return this.request("/api/quiz/generate", {
      method: "POST",
      body: JSON.stringify({ segment_id: segmentId }),
    });
  }

  async submitQuiz(quizId: string, answers: number[], userId?: string) {
    const params = userId ? `?user_id=${userId}` : "";
    return this.request(`/api/quiz/submit${params}`, {
      method: "POST",
      body: JSON.stringify({ quiz_id: quizId, answers }),
    });
  }

  // Progress
  async getProgress(userId: string) {
    return this.request(`/api/progress/${userId}`);
  }

  async getDashboardData(userId: string) {
    return this.request(`/api/progress/dashboard/${userId}`);
  }

  async markComplete(userId: string, segmentId?: string, resourceId?: string) {
    const params = new URLSearchParams({ user_id: userId });
    if (segmentId) params.set("segment_id", segmentId);
    if (resourceId) params.set("resource_id", resourceId);
    return this.request(`/api/progress/complete?${params}`, { method: "POST" });
  }

  // Feedback
  async submitFeedback(userId: string, data: { resource_id?: string; segment_id?: string; type: string; text?: string }) {
    return this.request(`/api/feedback/?user_id=${userId}`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Mentor
  async chatWithMentor(userId: string, message: string, conversationId?: string) {
    return this.request(`/api/mentor/chat?user_id=${userId}`, {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  }

  // Recommendations
  async getRecommendations(userId: string, limit = 10) {
    return this.request(`/api/recommendations/${userId}?limit=${limit}`);
  }

  async getNextActions(userId: string) {
    return this.request(`/api/recommendations/${userId}/next-actions`);
  }
}

export const api = new ApiClient();
