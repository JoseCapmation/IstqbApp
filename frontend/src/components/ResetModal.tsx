import { useState } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Dialog } from './ui/Dialog'
import { Button } from './ui/Button'
import { useResetProgress } from '../api/hooks'
import { useToast } from './ui/Toast'
import { useNavigate } from 'react-router-dom'

interface ResetModalProps {
  open: boolean
  onClose: () => void
}

export function ResetModal({ open, onClose }: ResetModalProps) {
  const [typed, setTyped] = useState('')
  const reset = useResetProgress()
  const { show } = useToast()
  const navigate = useNavigate()

  const isConfirmed = typed === 'RESET' || typed.toLowerCase() === 'yes'

  function handleReset() {
    reset.mutate(undefined, {
      onSuccess: () => {
        show('All progress has been reset.', 'success')
        setTyped('')
        onClose()
        navigate('/')
      },
      onError: () => {
        show('Failed to reset progress. Please try again.', 'error')
      },
    })
  }

  function handleClose() {
    setTyped('')
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} title="Reset All Progress">
      <div className="flex flex-col gap-4">
        <div className="flex items-start gap-3 rounded-xl bg-amber-50 border border-amber-200 p-4">
          <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
          <p className="text-sm text-amber-800">
            This will permanently clear all chapter completion, quiz scores, exam history, and reading
            checkpoints. This action cannot be undone.
          </p>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Type <strong>RESET</strong> or <strong>yes</strong> to confirm
          </label>
          <input
            type="text"
            value={typed}
            onChange={(e) => setTyped(e.target.value)}
            placeholder="RESET"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:border-capmation-navy-800 focus:outline-none focus:ring-1 focus:ring-capmation-navy-800"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && isConfirmed) handleReset()
            }}
            autoFocus
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={handleReset}
            disabled={!isConfirmed}
            loading={reset.isPending}
          >
            Reset Progress
          </Button>
        </div>
      </div>
    </Dialog>
  )
}
