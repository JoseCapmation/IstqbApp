import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { checkUser, createUser } from '../api/client'
import { setUser } from '../lib/session'

type Stage = 'idle' | 'checking' | 'confirm_create' | 'creating' | 'error'

export default function LoginPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [stage, setStage] = useState<Stage>('idle')
  const [errorMsg, setErrorMsg] = useState('')

  const trimmed = username.trim()

  async function handleContinue(e: FormEvent) {
    e.preventDefault()
    if (!trimmed) return
    setStage('checking')
    setErrorMsg('')

    try {
      const { exists } = await checkUser(trimmed)
      if (exists) {
        setUser(trimmed)
        navigate('/', { replace: true })
      } else {
        setStage('confirm_create')
      }
    } catch {
      setErrorMsg('Could not reach the server. Is the backend running?')
      setStage('error')
    }
  }

  async function handleCreate() {
    setStage('creating')
    setErrorMsg('')
    try {
      await createUser(trimmed)
      setUser(trimmed)
      navigate('/', { replace: true })
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err)
      setErrorMsg(msg)
      setStage('error')
    }
  }

  const busy = stage === 'checking' || stage === 'creating'

  return (
    <div className="min-h-screen bg-capmation-navy-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo / header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center bg-capmation-navy-800 rounded-2xl px-6 py-3 mb-4">
            <img src="/capmation-logo.png" alt="Capmation" className="h-10" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">ISTQB CTFL Trainer</h1>
          <p className="text-slate-300 text-sm mt-1">by Capmation</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-xl font-semibold text-capmation-navy-900 mb-1">Welcome back</h2>
          <p className="text-slate-500 text-sm mb-6">
            Enter your username to continue — or create one to get started.
          </p>

          <form onSubmit={handleContinue} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-slate-700 mb-1">
                Username
              </label>
              <input
                id="username"
                type="text"
                autoComplete="username"
                autoFocus
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value)
                  if (stage === 'confirm_create' || stage === 'error') setStage('idle')
                }}
                disabled={busy}
                placeholder="e.g. joseM"
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-900 placeholder-slate-400
                           focus:outline-none focus:ring-2 focus:ring-capmation-navy-500 focus:border-transparent
                           disabled:opacity-50 text-sm"
              />
            </div>

            {/* Error banner */}
            {stage === 'error' && errorMsg && (
              <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                {errorMsg}
              </p>
            )}

            {/* Confirm create panel */}
            {stage === 'confirm_create' && (
              <div className="bg-capmation-navy-50 border border-capmation-navy-200 rounded-lg px-4 py-3 space-y-3">
                <p className="text-sm text-capmation-navy-800">
                  No account found for <span className="font-semibold">"{trimmed}"</span>.
                  Create a new account?
                </p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={handleCreate}
                    disabled={busy}
                    className="flex-1 bg-capmation-navy-700 hover:bg-capmation-navy-800 text-white text-sm font-medium
                               py-2 rounded-lg transition-colors disabled:opacity-50"
                  >
                    Yes, create account
                  </button>
                  <button
                    type="button"
                    onClick={() => { setStage('idle'); setUsername('') }}
                    disabled={busy}
                    className="flex-1 border border-slate-300 text-slate-600 hover:bg-slate-50 text-sm font-medium
                               py-2 rounded-lg transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {stage !== 'confirm_create' && (
              <button
                type="submit"
                disabled={busy || !trimmed}
                className="w-full bg-capmation-lime-400 hover:bg-capmation-lime-500 text-capmation-navy-900
                           font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-50 text-sm"
              >
                {busy ? 'Please wait…' : 'Continue'}
              </button>
            )}
          </form>
        </div>
      </div>
    </div>
  )
}
