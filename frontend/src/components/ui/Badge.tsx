import { clsx } from 'clsx'
import type { HTMLAttributes } from 'react'

type BadgeVariant = 'green' | 'indigo' | 'slate' | 'amber' | 'red'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
}

const variants: Record<BadgeVariant, string> = {
  green: 'bg-emerald-100 text-emerald-700',
  indigo: 'bg-capmation-navy-100 text-capmation-navy-800',
  slate: 'bg-slate-100 text-slate-600',
  amber: 'bg-amber-100 text-amber-700',
  red: 'bg-red-100 text-red-700',
}

export function Badge({ variant = 'slate', className, children, ...props }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        variants[variant],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  )
}
