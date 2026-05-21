/**
 * Smart formatter for ISTQB question text and theory chunks.
 *
 * Inserts line breaks before enumeration markers and final question stems so
 * that composite questions render clearly in the browser without touching the
 * source JSON. The function is idempotent: text that already contains newlines
 * (e.g. theory chunks) passes through with only minor whitespace cleanup.
 */

/** Question stem openers that should be separated from the preceding list. */
const STEM_PATTERNS = [
  'Which of the following',
  'Which one of the following',
  'Which BEST',
  'Which of these',
  'What is the BEST',
  'What BEST',
  'Identify the',
  'Select the',
  'Which test case',
  'What test case',
  'What test technique',
  'What technique',
  'What type of',
  'What is the MOST',
  'What is the LEAST',
  'What would',
  'How many',
  'How would',
]

/**
 * Lowercase roman numerals that appear as list markers in ISTQB questions
 * (i. ii. iii. iv. v. vi. vii. viii. ix. x.).
 * We use an explicit alternation ordered longest-first to avoid i matching ii.
 */
const ROMAN_RE = /(?:viii|vii|vi|iv|ix|iii|ii|i|x)\./

/**
 * Format raw question/chunk text for readable display.
 *
 * - If the text already contains newlines it is returned as-is (theory chunks
 *   are already paragraph-wrapped in the JSON).
 * - Otherwise, inserts `\n\n` before list markers and question stems.
 */
export function formatLongText(input: string): string {
  if (!input) return input

  const trimmed = input.trim()

  // Already formatted — don't double-process.
  if (trimmed.includes('\n')) return trimmed

  let text = trimmed

  // 1. Numeric list items: "1. Foo 2. Bar" → "1. Foo\n\n2. Bar"
  //    Only break when preceded by word/text chars (letters, digits, brackets, commas).
  //    Excludes math operators like /, *, +, =, (, ) so formulas like "/ 4. Text"
  //    are not incorrectly split.
  text = text.replace(/([a-zA-Z\d\]:),;]) (\d+)\. /g, '$1\n\n$2. ')

  // 2. Uppercase single-letter list markers: "A. Foo B. Bar"
  //    Preceded by a lowercase letter, digit, colon, or closing bracket/paren.
  //    This covers both mid-sentence ("improve B.") and post-colon ("descriptions: A.").
  text = text.replace(/([a-z\d\]:)])\s+([A-Z])\. /g, '$1\n\n$2. ')

  // 3. Lowercase roman numeral list items: "i. Foo ii. Bar"
  //    We require the token to be preceded by a non-newline char + space so we
  //    don't reprocess items we already separated in earlier steps.
  const romanGlobal = new RegExp(`([^\\n]) (${ROMAN_RE.source}) `, 'g')
  text = text.replace(romanGlobal, '$1\n\n$2 ')

  // 3b. Bullet-point list items: "• Foo • Bar" → "• Foo\n\n• Bar"
  text = text.replace(/([^\n]) (•) /g, '$1\n\n$2 ')

  // 4. Section dividers: "And the following X" separates two sub-lists.
  text = text.replace(/ (And the following\b)/g, '\n\n$1')

  // 4b. Labeled criteria / steps: "AC1: ... AC2: ..." or "R1 R2 R3" style.
  //     Match patterns like "AC1:", "R1:", "TC1:", "Step 1:", "C1:", "US1:".
  //     Break before each label when it appears mid-sentence (preceded by a
  //     non-newline character).
  text = text.replace(/([^\n]) ([A-Z]{1,3}\d+[:)] )/g, '$1\n\n$2')

  // 4c. "Acceptance Criteria:" header — put on its own line.
  text = text.replace(/([^\n]) (Acceptance Criteria:)/g, '$1\n\n$2\n')

  // 4d. Numbered step labels "Step 1:" / "Step 2:" etc.
  text = text.replace(/([^\n]) (Step \d+:)/g, '$1\n\n$2')

  // 5. Final question stem openers ("Which of the following BEST...").
  //    Also inserts a period if the preceding sentence doesn't end with one.
  for (const stem of STEM_PATTERNS) {
    // If preceded by a word char without terminal punctuation → add period + newlines.
    text = text.replace(
      new RegExp(`([a-zA-Z0-9]) (${escapeRe(stem)}\\b)`),
      '$1.\n\n$2',
    )
    // If already has terminal punctuation but no newline → add newlines only.
    text = text.replace(
      new RegExp(`([.!?]) (${escapeRe(stem)}\\b)`),
      '$1\n\n$2',
    )
  }

  // 6. Collapse 3+ consecutive newlines down to two.
  text = text.replace(/\n{3,}/g, '\n\n')

  return text.trim()
}

/**
 * Append a period to text that doesn't end with terminal punctuation.
 * Only applied when the text is long enough to be a sentence (≥ minLength
 * chars), so short option fragments like "ii, v" are left untouched.
 */
export function ensureTerminalPunctuation(
  text: string,
  { minLength = 30 }: { minLength?: number } = {},
): string {
  const trimmed = text.trim()
  if (trimmed.length < minLength) return trimmed
  if ('.?!:'.includes(trimmed.slice(-1))) return trimmed
  return trimmed + '.'
}

/** Escape a literal string for use inside a RegExp. */
function escapeRe(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
