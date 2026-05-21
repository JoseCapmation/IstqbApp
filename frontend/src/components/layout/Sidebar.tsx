import { Link, useLocation, useNavigate } from 'react-router-dom'
import { clsx } from 'clsx'
import { BookOpen, GraduationCap, RotateCcw, CheckCircle2, Lock, Circle, LogOut } from 'lucide-react'
import { useChapters } from '../../api/hooks'
import { useState } from 'react'
import { ResetModal } from '../ResetModal'
import { getUser, clearUser } from '../../lib/session'
import { queryClient } from '../../App'

interface SidebarProps {
  mobile?: boolean
  onClose?: () => void
}

export function Sidebar({ mobile, onClose }: SidebarProps) {
  const { data: chapters } = useChapters()
  const location = useLocation()
  const navigate = useNavigate()
  const [resetOpen, setResetOpen] = useState(false)
  const currentUser = getUser()

  function handleLogout() {
    clearUser()
    queryClient.clear()
    navigate('/login', { replace: true })
  }

  const isActive = (path: string) => location.pathname === path

  return (
    <>
      <aside
        className={clsx(
          'flex h-full w-64 flex-col bg-white border-r border-slate-200',
          mobile && 'shadow-xl',
        )}
      >
        {/* Capmation logo bar */}
        <div className="bg-capmation-navy-800 px-4 py-3 flex items-center">
          <img src="/capmation-logo.png" alt="Capmation" className="h-8" />
        </div>
        {/* App title */}
        <div className="px-5 pt-3 pb-3 border-b border-slate-100">
          <div className="font-bold text-slate-800 leading-tight">ISTQB CTFL Trainer</div>
          <div className="text-xs text-slate-500">Foundation Level</div>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {/* Dashboard */}
          <SidebarLink
            to="/"
            icon={<BookOpen className="h-4 w-4" />}
            active={isActive('/')}
            onClick={onClose}
          >
            Dashboard
          </SidebarLink>

          {/* Chapters */}
          {chapters && chapters.length > 0 && (
            <div className="mt-4">
              <div className="px-3 mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
                Chapters
              </div>
              <div className="space-y-0.5">
                {chapters.map((ch) => {
                  const path = `/chapter/${ch.id}`
                  const active = location.pathname.startsWith(path)
                  return (
                    <Link
                      key={ch.id}
                      to={ch.locked ? '#' : path}
                      onClick={ch.locked ? undefined : onClose}
                      className={clsx(
                        'flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors',
                        active && !ch.locked
                          ? 'bg-capmation-lime-50 text-capmation-navy-800 font-medium'
                          : 'text-slate-600 hover:bg-slate-50 hover:text-slate-800',
                        ch.locked && 'opacity-50 cursor-not-allowed',
                      )}
                    >
                      {ch.completed ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                      ) : ch.locked ? (
                        <Lock className="h-4 w-4 shrink-0" />
                      ) : (
                        <Circle className="h-4 w-4 shrink-0 text-capmation-navy-600" />
                      )}
                      <span className="truncate">{ch.title}</span>
                      {ch.score !== null && (
                        <span className="ml-auto text-xs text-emerald-600 font-medium shrink-0">
                          {ch.score}%
                        </span>
                      )}
                    </Link>
                  )
                })}
              </div>
            </div>
          )}
        </nav>

        {/* Bottom actions */}
        <div className="border-t border-slate-100 px-3 py-3 space-y-0.5">
          <SidebarLink
            to="/exam"
            icon={<GraduationCap className="h-4 w-4" />}
            active={isActive('/exam')}
            onClick={onClose}
          >
            Mock Exam
          </SidebarLink>
          <button
            onClick={() => setResetOpen(true)}
            className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-red-500 hover:bg-red-50 transition-colors"
          >
            <RotateCcw className="h-4 w-4 shrink-0" />
            Reset Progress
          </button>
        </div>

        {/* User / logout */}
        {currentUser && (
          <div className="border-t border-slate-100 px-4 py-3 flex items-center justify-between">
            <div className="min-w-0">
              <p className="text-xs text-slate-400">Logged in as</p>
              <p className="text-sm font-semibold text-capmation-navy-800 truncate">{currentUser}</p>
            </div>
            <button
              onClick={handleLogout}
              title="Log out"
              className="ml-2 p-1.5 rounded-md text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors shrink-0"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        )}
      </aside>

      <ResetModal open={resetOpen} onClose={() => setResetOpen(false)} />
    </>
  )
}

function SidebarLink({
  to,
  icon,
  active,
  children,
  onClick,
}: {
  to: string
  icon: React.ReactNode
  active: boolean
  children: React.ReactNode
  onClick?: () => void
}) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className={clsx(
        'flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors',
        active
          ? 'bg-capmation-lime-50 text-capmation-navy-800 font-medium'
          : 'text-slate-600 hover:bg-slate-50 hover:text-slate-800',
      )}
    >
      {icon}
      {children}
    </Link>
  )
}
