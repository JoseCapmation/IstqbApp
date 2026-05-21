import { useNavigate } from 'react-router-dom'
import { BookOpen, GraduationCap, ArrowRight, CheckCircle2, Clock, Trophy } from 'lucide-react'
import { useAppState, useChapters } from '../api/hooks'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Progress, ProgressRing } from '../components/ui/Progress'

function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-slate-200 ${className ?? ''}`} />
}

export function Dashboard() {
  const { data: state, isLoading: stateLoading } = useAppState()
  const { data: chapters, isLoading: chaptersLoading } = useChapters()
  const navigate = useNavigate()

  const loading = stateLoading || chaptersLoading

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-48 w-full" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (!state || !chapters) return null

  const pct = state.total_chapters > 0 ? (state.completed_chapters.length / state.total_chapters) * 100 : 0
  const activeChapter = chapters.find((c) => !c.completed && !c.locked)
  const lastExam = state.last_exam

  return (
    <div className="space-y-6">
      {/* Hero */}
      <Card className="bg-gradient-to-br from-capmation-navy-700 to-capmation-navy-900 text-white border-none shadow-lg">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-3">
            <Badge variant="indigo" className="bg-white/20 text-white border-white/10">
              ISTQB CTFL Foundation
            </Badge>
            <h1 className="text-2xl font-bold">Welcome back</h1>
            <p className="text-capmation-lime-100 text-sm max-w-sm">
              {state.all_done
                ? 'All chapters complete! Take the mock exam to test your readiness.'
                : `Keep going — ${state.total_chapters - state.completed_chapters.length} chapter${state.total_chapters - state.completed_chapters.length !== 1 ? 's' : ''} remaining.`}
            </p>
            {activeChapter && !state.all_done && (
              <Button
                variant="white"
                onClick={() => navigate(`/chapter/${activeChapter.id}`)}
              >
                Continue — {activeChapter.title}
                <ArrowRight className="h-4 w-4" />
              </Button>
            )}
            {state.all_done && (
              <Button
                variant="white"
                onClick={() => navigate('/exam')}
              >
                Take Mock Exam
                <GraduationCap className="h-4 w-4" />
              </Button>
            )}
          </div>
          <div className="shrink-0">
            <ProgressRing
              value={pct}
              size={120}
              strokeWidth={10}
              label={`${state.completed_chapters.length}/${state.total_chapters}`}
              sublabel="chapters"
              onDark
            />
          </div>
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          icon={<CheckCircle2 className="h-5 w-5 text-emerald-500" />}
          label="Chapters Done"
          value={`${state.completed_chapters.length} / ${state.total_chapters}`}
          bg="bg-emerald-50"
        />
        <StatCard
          icon={<Clock className="h-5 w-5 text-capmation-navy-800" />}
          label="Current Chapter"
          value={`Chapter ${state.current_chapter}`}
          bg="bg-capmation-navy-100"
        />
        <StatCard
          icon={<Trophy className="h-5 w-5 text-amber-500" />}
          label="Last Exam"
          value={lastExam ? `${lastExam.score}% — ${lastExam.passed ? 'PASS' : 'FAIL'}` : 'No attempts yet'}
          bg="bg-amber-50"
          badge={lastExam ? (lastExam.passed ? 'green' : 'red') : undefined}
        />
      </div>

      {/* Chapter list */}
      <Card padding={false}>
        <div className="border-b border-slate-100 px-6 py-4">
          <h2 className="font-semibold text-slate-800">All Chapters</h2>
        </div>
        <div className="divide-y divide-slate-100">
          {chapters.map((ch) => {
            const chunkPct = ch.chunk_count > 0 ? (ch.chunk_index / ch.chunk_count) * 100 : 0
            return (
              <div
                key={ch.id}
                className="flex items-center gap-4 px-6 py-4 hover:bg-slate-50 transition-colors"
              >
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-xl text-sm font-semibold shrink-0 ${
                    ch.completed
                      ? 'bg-emerald-100 text-emerald-700'
                      : ch.locked
                      ? 'bg-slate-100 text-slate-400'
                      : 'bg-capmation-navy-100 text-capmation-navy-800'
                  }`}
                >
                  {ch.id}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-sm font-medium ${ch.locked ? 'text-slate-400' : 'text-slate-800'}`}
                    >
                      {ch.title}
                    </span>
                    {ch.completed && <Badge variant="green">Completed</Badge>}
                    {ch.locked && <Badge variant="slate">Locked</Badge>}
                    {!ch.completed && !ch.locked && <Badge variant="indigo">In Progress</Badge>}
                  </div>
                  {!ch.locked && ch.chunk_count > 0 && (
                    <div className="mt-1.5 flex items-center gap-2">
                      <Progress
                        value={chunkPct}
                        className="flex-1 h-1.5"
                        color={ch.completed ? 'emerald' : 'navy'}
                      />
                      <span className="text-xs text-slate-400 shrink-0">
                        {ch.chunk_index}/{ch.chunk_count}
                      </span>
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  {ch.score !== null && (
                    <span className="text-sm font-medium text-emerald-600">{ch.score}%</span>
                  )}
                  {!ch.locked && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/chapter/${ch.id}`)}
                    >
                      {ch.completed ? 'Review' : 'Go'}
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </Card>

      {/* Quick actions */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-capmation-navy-100 shrink-0">
            <BookOpen className="h-6 w-6 text-capmation-navy-800" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-slate-800">Practice Quiz</h3>
            <p className="text-sm text-slate-500">Jump straight into a chapter quiz (skip reading)</p>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              const ch = chapters.find((c) => !c.locked)
              if (ch) navigate(`/chapter/${ch.id}/quiz`)
            }}
          >
            Start
          </Button>
        </Card>
        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100 shrink-0">
            <GraduationCap className="h-6 w-6 text-amber-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-slate-800">Mock Exam</h3>
            <p className="text-sm text-slate-500">40 questions · 65% to pass · no feedback until end</p>
          </div>
          <Button variant="secondary" size="sm" onClick={() => navigate('/exam')}>
            Start
          </Button>
        </Card>
      </div>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
  bg,
  badge,
}: {
  icon: React.ReactNode
  label: string
  value: string
  bg: string
  badge?: 'green' | 'red'
}) {
  return (
    <Card className="flex items-center gap-4">
      <div className={`flex h-11 w-11 items-center justify-center rounded-xl shrink-0 ${bg}`}>{icon}</div>
      <div>
        <div className="text-xs text-slate-500">{label}</div>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="font-semibold text-slate-800 text-sm">{value}</span>
          {badge && <Badge variant={badge}>{badge === 'green' ? 'PASS' : 'FAIL'}</Badge>}
        </div>
      </div>
    </Card>
  )
}
