import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  fetchChapter,
  fetchChapters,
  fetchExam,
  fetchQuiz,
  fetchState,
  resetProgress,
  restartChapter,
  saveChunkIndex,
  submitExam,
  submitQuiz,
} from './client'

export const KEYS = {
  state: ['state'] as const,
  chapters: ['chapters'] as const,
  chapter: (id: number) => ['chapter', id] as const,
  quiz: (id: number) => ['quiz', id] as const,
  exam: ['exam'] as const,
}

export function useAppState() {
  return useQuery({ queryKey: KEYS.state, queryFn: fetchState })
}

export function useChapters() {
  return useQuery({ queryKey: KEYS.chapters, queryFn: fetchChapters })
}

export function useChapter(id: number) {
  return useQuery({ queryKey: KEYS.chapter(id), queryFn: () => fetchChapter(id) })
}

export function useQuiz(chapterId: number) {
  return useQuery({
    queryKey: KEYS.quiz(chapterId),
    queryFn: () => fetchQuiz(chapterId),
    staleTime: 0,
    gcTime: 0,
  })
}

export function useExam() {
  return useQuery({
    queryKey: KEYS.exam,
    queryFn: fetchExam,
    staleTime: 0,
    gcTime: 0,
  })
}

export function useSaveChunkIndex() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, index }: { id: number; index: number }) =>
      saveChunkIndex(id, index),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: KEYS.chapter(id) })
      qc.invalidateQueries({ queryKey: KEYS.chapters })
    },
  })
}

export function useRestartChapter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => restartChapter(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: KEYS.chapter(id) })
      qc.invalidateQueries({ queryKey: KEYS.chapters })
    },
  })
}

export function useSubmitQuiz() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      chapterId,
      answers,
    }: {
      chapterId: number
      answers: Record<string, string>
    }) => submitQuiz(chapterId, answers),
    onSuccess: (data, { chapterId }) => {
      if (data.chapter_completed) {
        qc.invalidateQueries({ queryKey: KEYS.state })
        qc.invalidateQueries({ queryKey: KEYS.chapters })
        qc.invalidateQueries({ queryKey: KEYS.chapter(chapterId) })
        qc.removeQueries({ queryKey: KEYS.quiz(chapterId) })
      }
    },
  })
}

export function useSubmitExam() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ exam_id, answers }: { exam_id: string; answers: Record<string, string> }) =>
      submitExam(exam_id, answers),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEYS.state })
      qc.removeQueries({ queryKey: KEYS.exam })
    },
  })
}

export function useResetProgress() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: resetProgress,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEYS.state })
      qc.invalidateQueries({ queryKey: KEYS.chapters })
    },
  })
}
