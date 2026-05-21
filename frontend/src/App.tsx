import { type ReactNode } from 'react'
import { BrowserRouter, Navigate, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ToastProvider } from './components/ui/Toast'
import { AppLayout } from './components/layout/AppLayout'
import { Dashboard } from './pages/Dashboard'
import { ChapterReader } from './pages/ChapterReader'
import { ChapterQuiz } from './pages/ChapterQuiz'
import { MockExam } from './pages/MockExam'
import LoginPage from './pages/LoginPage'
import { getUser } from './lib/session'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 10_000,
    },
  },
})

function RequireAuth({ children }: { children: ReactNode }) {
  const user = getUser()
  return user ? <>{children}</> : <Navigate to="/login" replace />
}

export { queryClient }

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              element={
                <RequireAuth>
                  <AppLayout />
                </RequireAuth>
              }
            >
              <Route path="/" element={<Dashboard />} />
              <Route path="/chapter/:id" element={<ChapterReader />} />
              <Route path="/chapter/:id/quiz" element={<ChapterQuiz />} />
              <Route path="/exam" element={<MockExam />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </QueryClientProvider>
  )
}
