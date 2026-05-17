import { useState, useRef, useEffect } from "react";

import { ChatWindow } from "../components/interview/ChatWindow";
import { ChatMessage } from "../components/interview/ChatMessage";
import { InterviewInput } from "../components/interview/InterviewInput";
import { InterviewFeedback } from "../components/interview/InterviewFeedback";

import { SessionHeader } from "../components/interview/SessionHeader";
import { TypingIndicator } from "../components/interview/TypingIndicator";
import { InterviewSummary } from "../components/interview/InterviewSummary";

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

export function InterviewPage() {
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

  const isLastQuestion = questionIndex === questions.length - 1;

  // ── Load questions from backend ────────────────────────────────

  useEffect(() => {
    async function loadQuestions() {
      const response = await getInterviewQuestions();

      if (!response.ok) {
        console.error(response.error);
        setQuestionsLoading(false);
        return;
      }

      setQuestions(response.data);

      if (response.data.length > 0) {
        setMessages([
          {
            id: uid(),
            role: "ai",
            content: response.data[0].question,
            timestamp: now(),
          },
        ]);
      }

      setQuestionsLoading(false);
    }

    loadQuestions();
  }, []);

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

  // ── Main UI ────────────────────────────────────────────────────

  return (
    <ChatWindow
      header={
        <SessionHeader
          title="Technical Interview"
          topic={currentQuestion.topic}
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
