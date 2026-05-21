import { getUser } from '../lib/session'
import type {
  AppState,
  ChapterDetail,
  ChapterSummary,
  ExamResponse,
  ExamResult,
  QuizResponse,
  QuizResult,
} from './types'

const BASE = '/api'

/** Append ?user=<username> for all progress-aware requests. */
function userParam(): string {
  const u = getUser()
  return u ? `?user=${encodeURIComponent(u)}` : ''
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${text}`)
  }
  return res.json() as Promise<T>
}

// Auth (no user param needed — these endpoints manage users themselves)
export const checkUser = (username: string) =>
  request<{ exists: boolean }>(`/users/${encodeURIComponent(username)}`)
export const createUser = (username: string) =>
  request<{ ok: boolean; username: string }>('/users', {
    method: 'POST',
    body: JSON.stringify({ username }),
  })

// State
export const fetchState = () => request<AppState>(`/state${userParam()}`)
export const resetProgress = () =>
  request<{ ok: boolean }>(`/progress/reset${userParam()}`, { method: 'POST' })

// Chapters
export const fetchChapters = () => request<ChapterSummary[]>(`/chapters${userParam()}`)
export const fetchChapter = (id: number) => request<ChapterDetail>(`/chapters/${id}${userParam()}`)
export const saveChunkIndex = (id: number, index: number) =>
  request<{ ok: boolean; chunk_index: number }>(`/chapters/${id}/chunk${userParam()}`, {
    method: 'POST',
    body: JSON.stringify({ index }),
  })
export const restartChapter = (id: number) =>
  request<{ ok: boolean }>(`/chapters/${id}/restart${userParam()}`, { method: 'POST' })

// Quiz
export const fetchQuiz = (chapterId: number) =>
  request<QuizResponse>(`/chapters/${chapterId}/quiz${userParam()}`)
export const submitQuiz = (chapterId: number, answers: Record<string, string>) =>
  request<QuizResult>(`/chapters/${chapterId}/quiz/submit${userParam()}`, {
    method: 'POST',
    body: JSON.stringify({ answers }),
  })

// Exam
export const fetchExam = () => request<ExamResponse>(`/exam${userParam()}`)
export const submitExam = (exam_id: string, answers: Record<string, string>) =>
  request<ExamResult>(`/exam/submit${userParam()}`, {
    method: 'POST',
    body: JSON.stringify({ exam_id, answers }),
  })
