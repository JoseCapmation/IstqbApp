import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Menu, X, ChevronRight, Home } from 'lucide-react'
import { Sidebar } from './Sidebar'
import { clsx } from 'clsx'

function Breadcrumbs() {
  const location = useLocation()
  const segments = location.pathname.split('/').filter(Boolean)

  const labels: Record<string, string> = {
    chapter: 'Chapter',
    quiz: 'Quiz',
    exam: 'Mock Exam',
  }

  if (segments.length === 0) return <span className="text-slate-500 text-sm">Dashboard</span>

  return (
    <nav className="flex items-center gap-1 text-sm text-slate-500">
      <Home className="h-3.5 w-3.5" />
      {segments.map((seg, i) => (
        <span key={i} className="flex items-center gap-1">
          <ChevronRight className="h-3.5 w-3.5" />
          <span className={clsx(i === segments.length - 1 ? 'text-slate-800 font-medium' : '')}>
            {labels[seg] ?? seg}
          </span>
        </span>
      ))}
    </nav>
  )
}

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Desktop sidebar */}
      <div className="hidden md:flex md:shrink-0">
        <Sidebar />
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div
            className="absolute inset-0 bg-black/30 backdrop-blur-sm"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="relative z-50 h-full w-64">
            <Sidebar mobile onClose={() => setSidebarOpen(false)} />
          </div>
        </div>
      )}

      {/* Main */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Topbar */}
        <header className="flex h-14 items-center gap-4 border-b border-slate-200 bg-white px-4 md:px-6 shrink-0">
          <button
            className="md:hidden rounded-lg p-1.5 text-slate-500 hover:bg-slate-100"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open sidebar"
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
          <Breadcrumbs />
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-4xl px-4 py-8 md:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
