import { useState } from 'react'

import { Card, SecondaryLink, SectionHeading, StatusChip, WordChip } from '../components/ui'

const feedback = [
  ['Vocabulary context', 'A fixed reference point', 'Correct'],
  ['Grammar lens', 'While estimates vary…', 'Review wording'],
  ['Logic check', 'To reduce random variation', 'Correct'],
  ['Output rewrite', 'A stable anchor helps…', 'Saved'],
]

export function HistoryDetailPage() {
  const [tab, setTab] = useState<'lesson' | 'answers' | 'summary'>('lesson')

  return (
    <div className="pt-1">
      <div className="flex flex-wrap items-center gap-3">
        <SecondaryLink to="/app/history">Back to History</SecondaryLink>
        <StatusChip>Owner-only</StatusChip>
      </div>
      <div className="mt-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[28px] font-semibold tracking-[-0.03em]">Estimating with stable anchors</h1>
          <p className="mt-1 max-w-2xl text-sm leading-5 text-ink-muted">Completed today at 09:24. Generated lesson, submitted answers, feedback, and summary are preserved as a read-only record.</p>
        </div>
        <div className="flex gap-2 text-xs"><span className="rounded-md bg-surface-muted px-2.5 py-1.5">B2</span><StatusChip>Completed</StatusChip></div>
      </div>

      <div className="mt-4 grid grid-cols-3 rounded-lg border border-line bg-white p-2 lg:hidden">
        {(['lesson', 'answers', 'summary'] as const).map((item) => <button className={`rounded-md px-2 py-2 text-xs font-medium capitalize ${tab === item ? 'bg-lexis-soft text-lexis' : 'text-ink-muted'}`} key={item} onClick={() => setTab(item)} type="button">{item}</button>)}
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.94fr)]">
        <div className={tab !== 'lesson' ? 'hidden lg:grid lg:gap-4' : 'grid gap-4'}>
          <Card className="p-5">
            <div className="flex items-start justify-between"><SectionHeading subtitle="Read-only generated content">Generated lesson</SectionHeading><StatusChip>Detail ready</StatusChip></div>
            <article className="mt-5 rounded-lg border border-[#e7e2d7] bg-[#fffdf8] p-5">
              <h2 className="text-xl font-semibold">A Better Way to Estimate</h2>
              <p className="mt-3 text-sm leading-6 text-ink-muted">A stable anchor gives a team a shared reference point. Useful estimates remain open to revision as new criteria and context become available.</p>
              <div className="mt-4 flex flex-wrap gap-2">{['estimate', 'anchor', 'segment', 'context'].map((word) => <WordChip key={word}>{word}</WordChip>)}</div>
            </article>
            <div className="mt-4 rounded-lg bg-surface-muted p-4">
              <div className="flex items-center justify-between"><strong className="text-sm">Source sync snapshot</strong><StatusChip>Valid</StatusChip></div>
              <p className="mt-2 text-xs text-ink-muted">Maimemo · synced today 09:12 · 24 new / 8 review</p>
            </div>
            <div className="mt-4 rounded-lg border border-line p-4">
              <strong className="text-sm">Read-only grammar lens</strong>
              <p className="mt-2 text-xs leading-5 text-ink-muted">“While” introduces a contrast between a stable reference and a changing estimate.</p>
            </div>
          </Card>
        </div>

        <div className="grid content-start gap-4">
          <Card className={`p-5 ${tab !== 'answers' && tab !== 'lesson' ? 'hidden lg:block' : ''}`}>
            <div className="flex items-start justify-between"><SectionHeading subtitle="Submitted values and coach feedback">Attempt answers</SectionHeading><StatusChip>Completed</StatusChip></div>
            <div className="mt-4 divide-y divide-line">
              {feedback.map(([title, answer, state]) => <div className="py-3" key={title}><div className="flex items-center justify-between gap-3"><strong className="text-xs">{title}</strong><span className="text-[11px] text-lexis">{state}</span></div><p className="mt-1 text-xs text-ink-muted">{answer}</p></div>)}
            </div>
          </Card>
          <Card className={`p-5 ${tab !== 'summary' && tab !== 'lesson' ? 'hidden lg:block' : ''}`}>
            <div className="flex items-start justify-between"><SectionHeading>Final summary</SectionHeading><StatusChip>Saved</StatusChip></div>
            <p className="mt-4 text-sm leading-6 text-ink-muted">Strong vocabulary comprehension. Review contrast clauses before the next lesson.</p>
            <div className="mt-5 space-y-2 text-xs text-ink-muted"><p>• Completed attempts remain read-only.</p><p>• Incomplete attempts reopen in Lesson Player.</p></div>
          </Card>
        </div>
      </div>
    </div>
  )
}
