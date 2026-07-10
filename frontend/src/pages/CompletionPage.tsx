import { Link } from 'react-router'

import { Card, MetricTile, PrimaryButton, ProgressBar, SecondaryLink, SectionHeading, StatusChip, WordChip } from '../components/ui'

const feedback = [
  ['Vocabulary context', 'Correct', 'The selected meaning matches the article.'],
  ['Grammar lens', 'Review', 'Revisit the contrast structure with “while”.'],
  ['Output rewrite', 'Saved', 'Your sentence is stored with this attempt.'],
]

export function CompletionPage() {
  return (
    <div className="pt-1">
      <div className="flex flex-wrap items-center gap-4 border-b border-line pb-4">
        <SecondaryLink to="/app/workspace">Back to Workspace</SecondaryLink>
        <div className="mr-auto">
          <h1 className="text-xl font-semibold">Lesson complete</h1>
          <p className="mt-1 text-xs text-ink-muted">Estimating with stable anchors · B2</p>
        </div>
        <StatusChip>Summary saved</StatusChip>
      </div>
      <div className="mt-3"><ProgressBar value={100} /></div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.94fr)]">
        <div className="grid gap-4">
          <Card className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div><span className="text-xs font-semibold uppercase tracking-[0.08em] text-lexis">Attempt complete</span><h2 className="mt-2 text-2xl font-semibold tracking-[-0.025em]">Your lesson is saved to History.</h2></div>
              <StatusChip>History ready</StatusChip>
            </div>
            <p className="mt-3 text-sm leading-6 text-ink-muted">Feedback, vocabulary updates, and the final summary are now attached to this lesson attempt.</p>
            <div className="mt-5 grid grid-cols-3 gap-3">
              <MetricTile label="Exercises" value="3 / 4" />
              <MetricTile label="Summary" value="Saved" />
              <MetricTile label="Mastery" value="+3" />
            </div>
          </Card>

          <Card className="p-5">
            <div className="flex items-start justify-between"><SectionHeading>Final summary</SectionHeading><StatusChip>Ready</StatusChip></div>
            <p className="mt-4 text-sm leading-6 text-ink-muted">You understood how stable anchors reduce random variation and used the key vocabulary in context.</p>
            <dl className="mt-5 grid gap-3 text-sm">
              <div className="grid grid-cols-[90px_1fr] gap-3"><dt className="font-semibold text-lexis">Strength</dt><dd className="text-ink-muted">Vocabulary meaning and main-idea reasoning.</dd></div>
              <div className="grid grid-cols-[90px_1fr] gap-3"><dt className="font-semibold text-warning">Review</dt><dd className="text-ink-muted">Contrast clauses introduced by “while”.</dd></div>
              <div className="grid grid-cols-[90px_1fr] gap-3"><dt className="font-semibold">Next focus</dt><dd className="text-ink-muted">Use “criteria” and “validate” in one short rewrite.</dd></div>
            </dl>
          </Card>

          <Card className="p-5">
            <SectionHeading subtitle="Saved with the completed attempt.">Exercise feedback recap</SectionHeading>
            <div className="mt-4 divide-y divide-line">
              {feedback.map(([title, state, note]) => <div className="grid gap-2 py-3 text-sm sm:grid-cols-[150px_80px_1fr]" key={title}><strong>{title}</strong><span className="text-lexis">{state}</span><span className="text-ink-muted">{note}</span></div>)}
            </div>
          </Card>
        </div>

        <div className="grid content-start gap-4">
          <Card className="p-5">
            <div className="flex items-start justify-between"><SectionHeading>Context mastery update</SectionHeading><StatusChip>Updated</StatusChip></div>
            <p className="mt-3 text-sm leading-6 text-ink-muted">Three focus words received new evidence from this attempt.</p>
            <div className="mt-4 flex flex-wrap gap-2">{['estimate', 'anchor', 'segment'].map((word) => <WordChip key={word}>{word}</WordChip>)}</div>
            <div className="mt-5 space-y-2 text-xs text-ink-muted">
              <p className="rounded-lg bg-surface-muted p-3"><strong className="text-ink">estimate</strong> · fuzzy → practicing</p>
              <p className="rounded-lg bg-surface-muted p-3"><strong className="text-ink">anchor</strong> · practicing → stable</p>
              <p className="rounded-lg bg-surface-muted p-3"><strong className="text-ink">segment</strong> · new evidence saved</p>
            </div>
          </Card>
          <Card className="p-5">
            <SectionHeading subtitle="Open the saved lesson and feedback any time.">Next action</SectionHeading>
            <Link to="/app/history/lesson-2026-07-10"><PrimaryButton className="mt-5 w-full">Open History</PrimaryButton></Link>
          </Card>
        </div>
      </div>
    </div>
  )
}
