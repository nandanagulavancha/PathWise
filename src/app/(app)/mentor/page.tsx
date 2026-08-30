"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { Send, Brain, User, Trash2 } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const SUGGESTED_QUESTIONS = [
  "What should I study next?",
  "Why was this topic recommended?",
  "Explain my current progress",
  "How do prerequisites connect?",
  "Help me understand this concept",
];

export default function MentorPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || !user) return;

    const userMsg: Message = { role: "user", content: text.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.chatWithMentor(user.id, text.trim(), conversationId) as { response: string; conversation_id: string };
      setConversationId(res.conversation_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.response }]);
    } catch (e) {
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I encountered an error. Please try again." }]);
    }
    setLoading(false);
  };

  const clearChat = () => {
    setMessages([]);
    setConversationId(undefined);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-hairline">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-lime/10 rounded-full flex items-center justify-center">
            <Brain className="h-5 w-5 text-lime" />
          </div>
          <div>
            <h1 className="text-lg font-bold">Pathwise Mentor</h1>
            <p className="text-xs text-muted-foreground">Your personalized AI learning assistant</p>
          </div>
        </div>
        {messages.length > 0 && (
          <button onClick={clearChat} className="text-xs text-muted-foreground hover:text-white flex items-center gap-1">
            <Trash2 className="h-3.5 w-3.5" /> Clear
          </button>
        )}
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto py-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <Brain className="h-16 w-16 text-lime/30 mx-auto mb-4" />
            <h2 className="text-lg font-semibold mb-2">Ask your AI mentor anything</h2>
            <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
              I know your profile, goals, roadmap, and progress. Ask me about your learning journey.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-xs bg-[#362d59] border border-hairline px-3 py-2 rounded-lg hover:border-[#6a5fc1] transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
            {msg.role === "assistant" && (
              <div className="w-8 h-8 bg-lime/10 rounded-full flex items-center justify-center flex-shrink-0">
                <Brain className="h-4 w-4 text-lime" />
              </div>
            )}
            <div className={`max-w-[80%] rounded-xl px-4 py-3 text-sm ${
              msg.role === "user"
                ? "bg-[#6a5fc1] text-white"
                : "bg-night border border-hairline"
            }`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
            {msg.role === "user" && (
              <div className="w-8 h-8 bg-[#362d59] rounded-full flex items-center justify-center flex-shrink-0">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 bg-lime/10 rounded-full flex items-center justify-center">
              <Brain className="h-4 w-4 text-lime animate-pulse" />
            </div>
            <div className="bg-night border border-hairline rounded-xl px-4 py-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="pt-4 border-t border-hairline">
        <form
          onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
          className="flex gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask your mentor anything..."
            className="flex-1 bg-night border border-hairline rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#6a5fc1]"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="bg-lime text-[#150f23] px-4 py-3 rounded-lg disabled:opacity-50 transition-opacity"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
