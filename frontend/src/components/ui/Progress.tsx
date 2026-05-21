import { clsx } from 'clsx'

interface ProgressProps {
  value: number // 0–100
  className?: string
  color?: 'navy' | 'lime' | 'emerald' | 'amber'
}

const colorClass: Record<NonNullable<ProgressProps['color']>, string> = {
  navy:    'bg-capmation-navy-800',
  lime:    'bg-capmation-lime-500',
  emerald: 'bg-emerald-500',
  amber:   'bg-amber-400',
}

export function Progress({ value, className, color = 'navy' }: ProgressProps) {
  const pct = Math.min(100, Math.max(0, value))
  return (
    <div
      role="progressbar"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      className={clsx('h-2 w-full overflow-hidden rounded-full bg-slate-200', className)}
    >
      <div
        className={clsx('h-full rounded-full transition-all duration-500', colorClass[color])}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

interface ProgressRingProps {
  value: number // 0–100
  size?: number
  strokeWidth?: number
  label?: string
  sublabel?: string
  /** Set to true when the ring sits on a dark background — uses white text. */
  onDark?: boolean
}

export function ProgressRing({
  value,
  size = 120,
  strokeWidth = 10,
  label,
  sublabel,
  onDark,
}: ProgressRingProps) {
  const r = (size - strokeWidth) / 2
  const circ = 2 * Math.PI * r
  const pct = Math.min(100, Math.max(0, value))
  const dash = (pct / 100) * circ

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#9bc53d"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${circ}`}
          className="transition-all duration-700"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        {label && (
          <span className={clsx('text-xl font-bold', onDark ? 'text-white' : 'text-slate-800')}>
            {label}
          </span>
        )}
        {sublabel && (
          <span className={clsx('text-xs', onDark ? 'text-white/70' : 'text-slate-500')}>
            {sublabel}
          </span>
        )}
      </div>
    </div>
  )
}
