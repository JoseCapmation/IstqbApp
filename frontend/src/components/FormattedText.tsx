import { clsx } from 'clsx'
import { formatLongText, ensureTerminalPunctuation } from '../lib/formatText'

interface FormattedTextProps {
  children: string
  className?: string
  /** When true, appends a period if the text is missing terminal punctuation. */
  ensurePunctuation?: boolean
}

/**
 * Renders formatted question / theory text.
 *
 * - Runs `formatLongText` to insert line breaks before enumeration markers
 *   and question stems.
 * - `whitespace-pre-line` makes the browser honour `\n` while still wrapping
 *   long lines naturally.
 * - Optionally appends a terminal period via `ensurePunctuation` (used for
 *   question stems, not for option fragments).
 */
export function FormattedText({ children, className, ensurePunctuation }: FormattedTextProps) {
  let text = formatLongText(children)
  if (ensurePunctuation) {
    text = ensureTerminalPunctuation(text)
  }
  return <span className={clsx('whitespace-pre-line', className)}>{text}</span>
}
