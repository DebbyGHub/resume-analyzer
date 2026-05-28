import { useState, useRef, useEffect } from "react";

import { ChatWindow } from "../components/interview/ChatWindow";
import { ChatMessage } from "../components/interview/ChatMessage";
import { InterviewInput } from "../components/interview/InterviewInput";
import { InterviewFeedback } from "../components/interview/InterviewFeedback";

import { SessionHeader } from "../components/interview/SessionHeader";
import { TypingIndicator } from "../components/interview/TypingIndicator";
import { InterviewSummary } from "../components/interview/InterviewSummary";

import { useLocation } from "react-router-dom";

import type { QualityBreakdown } from "../components/interview/InterviewSummary";

import {
  evaluateInterviewAnswer,
  getInterviewQuestions,
  type InterviewQuestion,
} from "../api/interview.api";

// ─── Types ────────────────────────────────────────────────────────────────────

interface EvaluationResult {
  similarity_score: number;
  confidence_score: number;
  final_score: number;
  quality: "excellent" | "good" | "average" | "weak";
  flags: string[];
}

interface Message {
  id: string;
  role: "ai" | "user";
  content: string;
  timestamp: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function now(): string {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function uid(): string {
  return Math.random().toString(36).slice(2, 9);
}

function buildSummary(
  evaluations: EvaluationResult[],
  questions: InterviewQuestion[],
) {
  if (evaluations.length === 0) return null;

  const avgScore =
    evaluations.reduce((s, e) => s + e.final_score, 0) / evaluations.length;

  const breakdown: QualityBreakdown = {
    excellent: 0,
    good: 0,
    average: 0,
    weak: 0,
  };

  for (const e of evaluations) {
    breakdown[e.quality] = (breakdown[e.quality] ?? 0) + 1;
  }

  const topicScores: Record<string, number[]> = {};

  evaluations.forEach((e, i) => {
    const topic = questions[i]?.topic ?? "General";

    if (!topicScores[topic]) {
      topicScores[topic] = [];
    }

    topicScores[topic].push(e.final_score);
  });

  const topicAvg = Object.entries(topicScores).map(([t, scores]) => ({
    topic: t,
    avg: scores.reduce((a, b) => a + b, 0) / scores.length,
  }));

  topicAvg.sort((a, b) => b.avg - a.avg);

  const pct = Math.round(avgScore * 100);

  const recommendation =
    pct >= 85
      ? "Outstanding performance. You demonstrated strong conceptual clarity across all topics."
      : pct >= 70
        ? "Solid performance overall. Consider deepening your weaker topics before your next interview."
        : pct >= 50
          ? "A reasonable attempt. Focus on building more complete, well-structured answers."
          : "There's room for improvement. Review the flagged topics and practice giving concise, technical answers.";

  return {
    averageScore: avgScore,
    qualityBreakdown: breakdown,
    strongestCategory: topicAvg[0]?.topic,
    weakestCategory:
      topicAvg.length > 1 ? topicAvg[topicAvg.length - 1].topic : undefined,
    recommendation,
  };
}

// ─── InterviewPage ────────────────────────────────────────────────────────────


interface InterviewPageProps {
  extractedSkills: string[];
  jobTitle?: string;
  companyName?: string;
  matchedKeywords: string[];
  missingKeywords: string[];
}

export function InterviewPage({
  extractedSkills: propExtractedSkills,
  jobTitle: propJobTitle,
  matchedKeywords: propMatchedKeywords,
  missingKeywords: propMissingKeywords,
}: InterviewPageProps) {
  const location = useLocation();

  const {
    extractedSkills = propExtractedSkills ?? [],
    jobTitle = propJobTitle,
    matchedKeywords = propMatchedKeywords ?? [],
    missingKeywords = propMissingKeywords ?? [],
  } = location.state ?? {};
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [questionsLoading, setQuestionsLoading] = useState(true);

  const [questionIndex, setQuestionIndex] = useState(0);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");

  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);

  const [evaluations, setEvaluations] = useState<EvaluationResult[]>([]);

  const [loading, setLoading] = useState(false);
  const [completed, setCompleted] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);

  const currentQuestion = questions[questionIndex];

  const hasSkills = extractedSkills.length > 0;

  const [showIntro, setShowIntro] = useState(hasSkills);

  const isLastQuestion = questionIndex === questions.length - 1;

  // ── Load questions from backend ────────────────────────────────

  useEffect(() => {
    if (!hasSkills) {
      setQuestionsLoading(false);
      return;
    }

    async function loadQuestions() {
      const response = await getInterviewQuestions({
        skills: extractedSkills,
        jobTitle,
        matchedKeywords,
        missingKeywords,
      });
      if (!response.ok) {
        console.error(response.error);
        setQuestionsLoading(false);
        return;
      }

      setQuestions(response.data);

      setQuestionsLoading(false);
    }

    loadQuestions();
  }, [hasSkills, extractedSkills, jobTitle, matchedKeywords, missingKeywords]);

  // ── Auto-scroll ────────────────────────────────────────────────

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading, evaluation]);

  // ── Submit answer ──────────────────────────────────────────────

  async function handleSubmit() {
    if (!currentQuestion) return;

    const trimmed = inputValue.trim();

    if (!trimmed || loading) return;

    const userMsg: Message = {
      id: uid(),
      role: "user",
      content: trimmed,
      timestamp: now(),
    };

    setMessages((prev) => [...prev, userMsg]);

    setInputValue("");
    setLoading(true);
    setEvaluation(null);

    let result: EvaluationResult;

    const response = await evaluateInterviewAnswer({
      ideal_answer: currentQuestion.ideal_answer,
      candidate_answer: trimmed,
    });

    if (!response.ok) {
      result = {
        similarity_score: 0,
        confidence_score: 0,
        final_score: 0,
        quality: "weak",
        flags: ["evaluation_error"],
      };
    } else {
      result = response.data;
    }

    setLoading(false);

    setEvaluation(result);

    setEvaluations((prev) => [...prev, result]);

    setTimeout(() => {
      if (isLastQuestion) {
        setCompleted(true);
      } else {
        const next = questions[questionIndex + 1];

        setMessages((prev) => [
          ...prev,
          {
            id: uid(),
            role: "ai",
            content: next.question,
            timestamp: now(),
          },
        ]);

        setQuestionIndex((qi) => qi + 1);

        setEvaluation(null);
      }
    }, 1800);
  }

  // ── Loading state ──────────────────────────────────────────────

  if (questionsLoading) {
    return (
      <div className="min-h-screen bg-surface-base flex items-center justify-center">
        <TypingIndicator label="Loading interview questions…" />
      </div>
    );
  }

  if (!hasSkills) {
    return (
      <div className="min-h-screen bg-surface-base flex items-center justify-center">
        <div className="max-w-xl text-center px-6">
          <h1 className="text-3xl font-semibold mb-4">Resume Required</h1>

          <p className="text-text-muted text-lg">
            Upload your resume first to begin a personalized AI interview.
          </p>
        </div>
      </div>
    );
  }

  // ── Empty state ────────────────────────────────────────────────

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-surface-base flex items-center justify-center text-text-muted">
        Failed to load interview questions.
      </div>
    );
  }

  // ── Summary ────────────────────────────────────────────────────

  if (completed) {
    const summary = buildSummary(evaluations, questions);

    return (
      <div className="min-h-screen bg-surface-base">
        <InterviewSummary
          totalQuestions={questions.length}
          averageScore={summary?.averageScore ?? 0}
          strongestCategory={summary?.strongestCategory}
          weakestCategory={summary?.weakestCategory}
          qualityBreakdown={summary?.qualityBreakdown}
          recommendation={summary?.recommendation}
        />
      </div>
    );
  }

  if (showIntro) {
    return (
      <div className="min-h-screen bg-surface-base flex items-center justify-center px-6">
        <div className="relative overflow-hidden max-w-2xl w-full rounded-[2rem] border border-white/10 bg-gradient-to-br from-white/[0.06] to-white/[0.02] backdrop-blur-2xl p-10 shadow-xl">
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute -top-24 -right-24 h-72 w-72 rounded-full bg-accent-glow blur-3xl opacity-40" />

            <div className="absolute -bottom-24 -left-24 h-64 w-64 rounded-full bg-violet-500/10 blur-3xl opacity-30" />
          </div>
          <h1 className="text-5xl font-semibold tracking-tight mb-4">
            AI Technical Interview
          </h1>

          <p className="text-text-secondary text-lg leading-relaxed mb-8 max-w-xl">
            Your interview has been personalized using your resume, target role,
            and technical profile.
          </p>

          {jobTitle && (
            <div className="mb-8">
              <div className="text-xs uppercase tracking-[0.2em] text-text-muted mb-2">
                Target Role
              </div>

              <div className="inline-flex items-center rounded-full border border-accent/20 bg-accent/10 px-4 py-2 text-accent font-medium">
                {jobTitle}
              </div>
            </div>
          )}

          <div className="mb-8">
            <h2 className="text-sm uppercase tracking-wide text-text-muted mb-4">
              Interview Focus Areas
            </h2>

            <div className="flex flex-wrap gap-3">
              {extractedSkills.slice(0, 8).map((skill: string) => (
                <div
                  key={skill}
                  className="px-4 py-2 rounded-full bg-accent/10 border border-accent/20 text-accent backdrop-blur-md"
                >
                  {skill}
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => {
              setShowIntro(false);

              if (questions.length > 0) {
                setMessages([
                  {
                    id: uid(),
                    role: "ai",
                    content: questions[0].question,
                    timestamp: now(),
                  },
                ]);
              }
            }}
            className="w-full py-4 rounded-2xl bg-accent text-white font-medium shadow-lg hover:shadow-xl hover:scale-[1.01] transition-all duration-300"
          >
            Start Interview
          </button>
        </div>
      </div>
    );
  }

  // ── Main UI ────────────────────────────────────────────────────

  return (
    <ChatWindow
      header={
        <SessionHeader
          title="Technical Interview"
          topic={currentQuestion?.topic ?? "Interview"}
          currentQuestion={questionIndex + 1}
          totalQuestions={questions.length}
          status="active"
        />
      }
      messages={
        <div
          ref={scrollRef}
          className="flex flex-col gap-4 px-6 py-6 overflow-y-auto flex-1"
        >
          {messages.map((m) => (
            <ChatMessage
              key={m.id}
              role={m.role}
              content={m.content}
              timestamp={m.timestamp}
              status={m.role === "user" ? "sent" : undefined}
            />
          ))}
        </div>
      }
      typingIndicator={loading ? <TypingIndicator /> : undefined}
      feedback={
        evaluation ? (
          <InterviewFeedback
            similarityScore={evaluation.similarity_score}
            confidenceScore={evaluation.confidence_score}
            finalScore={evaluation.final_score}
            quality={evaluation.quality}
            flags={evaluation.flags}
          />
        ) : undefined
      }
      input={
        <InterviewInput
          value={inputValue}
          onChange={setInputValue}
          onSubmit={handleSubmit}
          loading={loading}
          disabled={loading || !!evaluation}
          maxLength={1000}
        />
      }
    />
  );
}
