import { useNavigate, useParams } from 'react-router-dom'
import { useState } from 'react'
import { clsx } from 'clsx'
import { CheckCircle2, XCircle, ChevronRight, RefreshCw, ArrowLeft, Trophy } from 'lucide-react'
import { useQuiz, useSubmitQuiz } from '../api/hooks'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Progress } from '../components/ui/Progress'
import { Badge } from '../components/ui/Badge'
import { useToast } from '../components/ui/Toast'
import { FormattedText } from '../components/FormattedText'
import type { PerQuestion, QuizQuestion } from '../api/types'
import { useQueryClient } from '@tanstack/react-query'
import { KEYS } from '../api/hooks'

function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-slate-200 ${className ?? ''}`} />
}

function QuestionDiagram({ src }: { src: string }) {
  return (
    <div className="my-4 rounded-xl border border-slate-200 bg-slate-50 p-3 overflow-x-auto">
      <img
        src={src}
        alt="Question diagram"
        className="max-w-full h-auto mx-auto block"
        style={{ maxHeight: '480px' }}
      />
    </div>
  )
}

export function ChapterQuiz() {
  const { id } = useParams<{ id: string }>()
  const chapterId = Number(id)
  const navigate = useNavigate()
  const { show } = useToast()
  const qc = useQueryClient()

  const { data: quiz, isLoading } = useQuiz(chapterId)
  const submitMut = useSubmitQuiz()

  const [currentQ, setCurrentQ] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<{
    score: number
    passed: boolean
    correct_count: number
    total: number
    per_question: PerQuestion[]
    chapter_completed: boolean
  } | null>(null)

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-12 w-32" />
      </div>
    )
  }

  if (!quiz) return <div className="text-slate-500">No questions available.</div>

  const questions: QuizQuestion[] = quiz.questions
  const total = questions.length

  if (result) {
    return (
      <ResultView
        result={result}
        onRetry={() => {
          qc.removeQueries({ queryKey: KEYS.quiz(chapterId) })
          setResult(null)
          setCurrentQ(0)
          setAnswers({})
        }}
        onBack={() => navigate(`/chapter/${chapterId}`)}
      />
    )
  }

  const q = questions[currentQ]
  const pct = ((currentQ + 1) / total) * 100
  const chosen = answers[q.id]
  const isLast = currentQ === total - 1

  function select(letter: string) {
    setAnswers((prev) => ({ ...prev, [q.id]: letter }))
  }

  function goNext() {
    if (isLast) {
      submitMut.mutate(
        { chapterId, answers },
        {
          onSuccess: (data) => {
            setResult(data)
            if (data.chapter_completed) {
              show(`Chapter completed! Score: ${data.score}%`, 'success')
            }
          },
          onError: () => show('Failed to submit quiz. Please try again.', 'error'),
        },
      )
    } else {
      setCurrentQ((prev) => prev + 1)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Badge variant="indigo">Chapter {chapterId} — Quiz</Badge>
        <div className="mt-2 flex items-center justify-between text-sm text-slate-500">
          <span>
            Question {currentQ + 1} of {total}
          </span>
          <span>{Math.round(pct)}% complete</span>
        </div>
        <Progress value={pct} className="mt-2" />
      </div>

      {/* Question */}
      <Card>
        <p className="text-slate-800 font-medium leading-relaxed mb-4">
          <FormattedText ensurePunctuation>{q.question}</FormattedText>
        </p>
        {q.image_url && <QuestionDiagram src={q.image_url} />}
        <div className="space-y-3 mt-4">
          {Object.entries(q.options).map(([letter, text]) => (
            <button
              key={letter}
              onClick={() => select(letter)}
              className={clsx(
                'w-full flex items-start gap-3 rounded-xl border-2 px-4 py-3 text-left text-sm transition-all',
                chosen === letter
                  ? 'border-capmation-lime-500 bg-capmation-lime-50 text-capmation-navy-900'
                  : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700',
              )}
            >
              <span
                className={clsx(
                  'flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold',
                  chosen === letter ? 'bg-capmation-lime-500 text-white' : 'bg-slate-200 text-slate-600',
                )}
              >
                {letter}
              </span>
              <FormattedText>{text}</FormattedText>
            </button>
          ))}
        </div>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between gap-4">
        <Button
          variant="secondary"
          onClick={() => setCurrentQ((prev) => Math.max(0, prev - 1))}
          disabled={currentQ === 0}
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
        <Button onClick={goNext} disabled={!chosen} loading={submitMut.isPending}>
          {isLast ? 'Submit Quiz' : 'Next'}
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

function ResultView({
  result,
  onRetry,
  onBack,
}: {
  result: {
    score: number
    passed: boolean
    correct_count: number
    total: number
    per_question: PerQuestion[]
    chapter_completed: boolean
  }
  onRetry: () => void
  onBack: () => void
}) {
  const [expanded, setExpanded] = useState<string | null>(null)
  const navigate = useNavigate()

  return (
    <div className="space-y-6">
      {/* Score banner */}
      <Card
        className={clsx(
          'text-center',
          result.passed ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50',
        )}
      >
        <div className="flex flex-col items-center gap-3">
          {result.passed ? (
            <Trophy className="h-12 w-12 text-emerald-500" />
          ) : (
            <XCircle className="h-12 w-12 text-red-400" />
          )}
          <div>
            <div
              className={clsx(
                'text-4xl font-bold',
                result.passed ? 'text-emerald-700' : 'text-red-600',
              )}
            >
              {result.score}%
            </div>
            <div
              className={clsx(
                'text-lg font-semibold mt-1',
                result.passed ? 'text-emerald-700' : 'text-red-600',
              )}
            >
              {result.passed ? 'Passed!' : 'Not Passed'}
            </div>
            <div className="text-sm text-slate-500 mt-1">
              {result.correct_count} / {result.total} correct · 70% required
            </div>
          </div>
        </div>
      </Card>

      {/* Per-question review */}
      <div className="space-y-3">
        <h2 className="font-semibold text-slate-800">Review</h2>
        {result.per_question.map((pq) => (
          <Card key={pq.id} padding={false}>
            <button
              className="w-full flex items-start gap-3 p-4 text-left"
              onClick={() => setExpanded((prev) => (prev === pq.id ? null : pq.id))}
            >
              {pq.is_correct ? (
                <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
              )}
              <FormattedText className="text-sm text-slate-700 flex-1">{pq.question}</FormattedText>
              <ChevronRight
                className={clsx(
                  'h-4 w-4 text-slate-400 shrink-0 mt-0.5 transition-transform',
                  expanded === pq.id && 'rotate-90',
                )}
              />
            </button>
            {expanded === pq.id && (
              <div className="border-t border-slate-100 px-4 pb-4 space-y-3">
                {pq.image_url && <div className="mt-3"><QuestionDiagram src={pq.image_url} /></div>}
                <div className="space-y-1.5 mt-3">
                  {Object.entries(pq.options).map(([letter, text]) => (
                    <div
                      key={letter}
                      className={clsx(
                        'flex items-start gap-2 rounded-lg px-3 py-2 text-sm',
                        letter === pq.correct
                          ? 'bg-emerald-50 text-emerald-800 font-medium'
                          : letter === pq.chosen && !pq.is_correct
                          ? 'bg-red-50 text-red-700'
                          : 'text-slate-600',
                      )}
                    >
                      <span className="font-bold shrink-0">{letter}.</span>
                      <FormattedText className="flex-1">{text}</FormattedText>
                      {letter === pq.correct && (
                        <CheckCircle2 className="h-4 w-4 text-emerald-500 ml-auto shrink-0 mt-0.5" />
                      )}
                      {letter === pq.chosen && !pq.is_correct && (
                        <XCircle className="h-4 w-4 text-red-400 ml-auto shrink-0 mt-0.5" />
                      )}
                    </div>
                  ))}
                </div>
                {pq.explanation && (
                  <div className="rounded-lg bg-slate-50 border border-slate-200 p-3 text-sm text-slate-600">
                    <span className="font-medium text-slate-700">Explanation: </span>
                    {pq.explanation}
                  </div>
                )}
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        <Button variant="secondary" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" />
          Back to Chapter
        </Button>
        {!result.passed && (
          <Button variant="ghost" onClick={onRetry}>
            <RefreshCw className="h-4 w-4" />
            Retry Quiz
          </Button>
        )}
        {result.chapter_completed && (
          <Button onClick={() => navigate('/')}>
            Back to Dashboard
          </Button>
        )}
      </div>
    </div>
  )
}
