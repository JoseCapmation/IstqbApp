import { useNavigate, useParams } from 'react-router-dom'
import { ChevronLeft, ChevronRight, RotateCcw, BookOpen, PenLine } from 'lucide-react'
import { useChapter } from '../api/hooks'
import { useSaveChunkIndex, useRestartChapter } from '../api/hooks'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Progress } from '../components/ui/Progress'
import { Badge } from '../components/ui/Badge'
import { FormattedText } from '../components/FormattedText'
import { useState } from 'react'

function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-slate-200 ${className ?? ''}`} />
}

export function ChapterReader() {
  const { id } = useParams<{ id: string }>()
  const chapterId = Number(id)
  const navigate = useNavigate()

  const { data: chapter, isLoading } = useChapter(chapterId)
  const saveChunk = useSaveChunkIndex()
  const restartMut = useRestartChapter()
  const [confirming, setConfirming] = useState(false)

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-72 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    )
  }

  if (!chapter) return <div className="text-slate-500">Chapter not found.</div>

  const chunks = chapter.content_chunks
  const total = chunks.length
  // chunk_index represents "how many chunks have been read", so current page = chunk_index
  // (page 0 = first unread chunk, capped at total-1 once all read)
  const currentIdx = Math.min(chapter.chunk_index, total - 1)
  const pct = total > 0 ? ((currentIdx + 1) / total) * 100 : 100
  const isLast = currentIdx === total - 1
  const allRead = chapter.chunk_index >= total

  function goNext() {
    const nextIdx = currentIdx + 1
    saveChunk.mutate({ id: chapterId, index: nextIdx })
  }

  function goPrev() {
    const prevIdx = Math.max(0, currentIdx - 1)
    saveChunk.mutate({ id: chapterId, index: prevIdx })
  }

  function handleRestart() {
    restartMut.mutate(chapterId, {
      onSuccess: () => setConfirming(false),
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="indigo">Chapter {chapter.id}</Badge>
          </div>
          <h1 className="text-2xl font-bold text-slate-800">{chapter.title}</h1>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => (confirming ? handleRestart() : setConfirming(true))}
          loading={restartMut.isPending}
          className="shrink-0 text-slate-500"
        >
          <RotateCcw className="h-4 w-4" />
          {confirming ? 'Confirm restart' : 'Restart'}
        </Button>
      </div>

      {/* Progress */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs text-slate-500">
          <span>Reading progress</span>
          <span>
            Part {currentIdx + 1} of {total}
          </span>
        </div>
        <Progress value={pct} />
      </div>

      {/* Content */}
      <Card>
        <div className="flex items-center gap-2 mb-4 text-xs text-slate-400 font-medium uppercase tracking-wide">
          <BookOpen className="h-3.5 w-3.5" />
          Part {currentIdx + 1} / {total}
        </div>
        <div className="prose prose-slate max-w-none">
          <p className="text-slate-700 leading-relaxed">
            <FormattedText>{chunks[currentIdx]}</FormattedText>
          </p>
        </div>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between gap-4">
        <Button
          variant="secondary"
          onClick={goPrev}
          disabled={currentIdx === 0}
          loading={saveChunk.isPending}
        >
          <ChevronLeft className="h-4 w-4" />
          Previous
        </Button>

        {isLast || allRead ? (
          <Button onClick={() => navigate(`/chapter/${chapterId}/quiz`)}>
            <PenLine className="h-4 w-4" />
            Start Quiz
          </Button>
        ) : (
          <Button onClick={goNext} loading={saveChunk.isPending}>
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Also offer quiz skip if not first chunk */}
      {!isLast && !allRead && currentIdx > 0 && (
        <div className="text-center">
          <button
            className="text-sm text-capmation-navy-700 hover:underline"
            onClick={() => navigate(`/chapter/${chapterId}/quiz`)}
          >
            Skip reading and go to quiz
          </button>
        </div>
      )}
    </div>
  )
}
