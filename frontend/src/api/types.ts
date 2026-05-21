export interface AppState {
  total_chapters: number
  current_chapter: number
  completed_chapters: number[]
  scores_per_chapter: Record<string, number>
  last_exam: ExamAttempt | null
  all_done: boolean
}

export interface ExamAttempt {
  date: string
  score: number
  passed: boolean
}

export interface ChapterSummary {
  id: number
  title: string
  locked: boolean
  completed: boolean
  score: number | null
  chunk_count: number
  chunk_index: number
}

export interface ChapterDetail {
  id: number
  title: string
  content_chunks: string[]
  chunk_index: number
  chunk_count: number
}

export interface QuizQuestion {
  id: string
  question: string
  options: Record<string, string>
  image_url?: string | null
}

export interface QuizResponse {
  chapter_id: number
  questions: QuizQuestion[]
  total: number
}

export interface PerQuestion {
  id: string
  question: string
  options: Record<string, string>
  image_url?: string | null
  chosen: string
  correct: string
  explanation: string | null
  is_correct: boolean
}

export interface QuizResult {
  score: number
  passed: boolean
  correct_count: number
  total: number
  per_question: PerQuestion[]
  chapter_completed: boolean
}

export interface ExamResponse {
  exam_id: string
  questions: QuizQuestion[]
  total: number
  note: string | null
}

export interface ExamResult {
  score: number
  passed: boolean
  correct_count: number
  total: number
  per_question: PerQuestion[]
}
