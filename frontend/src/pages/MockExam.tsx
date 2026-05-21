import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { clsx } from 'clsx'
import {
  GraduationCap,
  CheckCircle2,
  XCircle,
  ChevronRight,
  ArrowLeft,
  Trophy,
  AlertCircle,
} from 'lucide-react'
import { useExam, useSubmitExam } from '../api/hooks'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Progress } from '../components/ui/Progress'
import { Badge } from '../components/ui/Badge'
import { useToast } from '../components/ui/Toast'
import { FormattedText } from '../components/FormattedText'
import type { PerQuestion, QuizQuestion } from '../api/types'
import { useQueryClient } from '@tanstack/react-query'
import { KEYS } from '../api/hooks'

type Phase = 'prestart' | 'exam' | 'results'

export function MockExam() {
  const [phase, setPhase] = useState<Phase>('prestart')
  const [currentQ, setCurrentQ] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<{
    score: number
    passed: boolean
    correct_count: number
    total: number
    per_question: PerQuestion[]
  } | null>(null)

  const { data: exam, isLoading } = useExam()
  const submitMut = useSubmitExam()
  const { show } = useToast()
  const qc = useQueryClient()
  const navigate = useNavigate()

  if (phase === 'prestart') {
    return (
      <PreStart
        onStart={() => setPhase('exam')}
        note={exam?.note ?? null}
        loading={isLoading}
      />
    )
  }

  if (!exam) return null

  if (phase === 'results' && result) {
    return (
      <ResultsView
        result={result}
        onRestart={() => {
          qc.removeQueries({ queryKey: KEYS.exam })
          setPhase('prestart')
          setCurrentQ(0)
          setAnswers({})
          setResult(null)
        }}
        onDashboard={() => navigate('/')}
      />
    )
  }

  const questions: QuizQuestion[] = exam.questions
  const total = questions.length
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
        { exam_id: exam!.exam_id, answers },
        {
          onSuccess: (data) => {
            setResult(data)
            setPhase('results')
          },
          onError: () => show('Failed to submit exam. Please try again.', 'error'),
        },
      )
    } else {
      setCurrentQ((prev) => prev + 1)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center justify-between mb-1">
          <Badge variant="amber">Mock Exam</Badge>
          <span className="text-sm text-slate-500">
            {currentQ + 1} / {total}
          </span>
        </div>
        <Progress value={pct} color="amber" className="mt-2" />
      </div>

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
                  ? 'border-amber-500 bg-amber-50 text-amber-800'
                  : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700',
              )}
            >
              <span
                className={clsx(
                  'flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold',
                  chosen === letter ? 'bg-amber-500 text-white' : 'bg-slate-200 text-slate-600',
                )}
              >
                {letter}
              </span>
              <FormattedText>{text}</FormattedText>
            </button>
          ))}
        </div>
      </Card>

      <div className="flex justify-between gap-4">
        <Button
          variant="secondary"
          onClick={() => setCurrentQ((prev) => Math.max(0, prev - 1))}
          disabled={currentQ === 0}
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
        <Button
          onClick={goNext}
          disabled={!chosen}
          loading={submitMut.isPending}
          className="bg-amber-500 hover:bg-amber-600"
        >
          {isLast ? 'Submit Exam' : 'Next'}
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

function PreStart({
  onStart,
  note,
  loading,
}: {
  onStart: () => void
  note: string | null
  loading: boolean
}) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Mock Exam</h1>
        <p className="mt-1 text-slate-500">Test your readiness for the ISTQB CTFL certification</p>
      </div>

      <Card>
        <div className="flex flex-col items-center gap-6 text-center py-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-amber-100">
            <GraduationCap className="h-8 w-8 text-amber-600" />
          </div>
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-slate-800">Ready to be tested?</h2>
            <p className="text-slate-500 max-w-sm text-sm">
              You will answer 40 questions drawn from all chapters. No per-question feedback until the
              very end. You need <strong>65%</strong> to pass.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-6 w-full max-w-sm">
            <InfoPill label="Questions" value="40" />
            <InfoPill label="Pass score" value="65%" />
            <InfoPill label="Feedback" value="End only" />
          </div>
          {note && (
            <div className="flex items-start gap-2 rounded-xl bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-800 text-left w-full">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-amber-500" />
              {note}
            </div>
          )}
          <Button
            size="lg"
            onClick={onStart}
            loading={loading}
            className="bg-amber-500 hover:bg-amber-600 text-white px-8"
          >
            Start Exam
          </Button>
        </div>
      </Card>
    </div>
  )
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

function InfoPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col items-center gap-1 rounded-xl bg-slate-50 border border-slate-200 px-3 py-3">
      <span className="font-bold text-slate-800 text-lg">{value}</span>
      <span className="text-xs text-slate-500">{label}</span>
    </div>
  )
}

function ResultsView({
  result,
  onRestart,
  onDashboard,
}: {
  result: {
    score: number
    passed: boolean
    correct_count: number
    total: number
    per_question: PerQuestion[]
  }
  onRestart: () => void
  onDashboard: () => void
}) {
  const [expanded, setExpanded] = useState<string | null>(null)

  return (
    <div className="space-y-6">
      {/* Score banner */}
      <Card
        className={clsx(
          'text-center',
          result.passed ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50',
        )}
      >
        <div className="flex flex-col items-center gap-3 py-4">
          {result.passed ? (
            <Trophy className="h-14 w-14 text-emerald-500" />
          ) : (
            <XCircle className="h-14 w-14 text-red-400" />
          )}
          <div>
            <div
              className={clsx(
                'text-5xl font-bold',
                result.passed ? 'text-emerald-700' : 'text-red-600',
              )}
            >
              {result.score}%
            </div>
            <div
              className={clsx(
                'text-xl font-semibold mt-2',
                result.passed ? 'text-emerald-700' : 'text-red-600',
              )}
            >
              {result.passed ? 'PASSED' : 'NOT PASSED'}
            </div>
            <div className="text-sm text-slate-500 mt-2">
              {result.correct_count} / {result.total} correct · 65% required to pass
            </div>
          </div>
        </div>
      </Card>

      {/* Review */}
      <div className="space-y-3">
        <h2 className="font-semibold text-slate-800">Question Review</h2>
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
              <div className="border-t border-slate-100 px-4 pb-4 space-y-2 mt-0">
                {pq.image_url && <div className="mt-3"><QuestionDiagram src={pq.image_url} /></div>}
                <div className="space-y-1.5 pt-3">
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
        <Button variant="secondary" onClick={onDashboard}>
          <ArrowLeft className="h-4 w-4" />
          Dashboard
        </Button>
        <Button onClick={onRestart} className="bg-amber-500 hover:bg-amber-600 text-white">
          Try Again
        </Button>
      </div>
    </div>
  )
}
