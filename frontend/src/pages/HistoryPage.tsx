import { Link } from 'react-router'

import { Card, PageTitle, ProgressBar, SectionHeading, StatusChip } from '../components/ui'
import { lessonHistory } from '../data/mock-data'

export function HistoryPage() {
  return (
    <div className="pt-3">
      <PageTitle subtitle="Review completed lessons, saved feedback, and resumable attempts.">Learning History</PageTitle>

      <div className="mt-5 grid gap-4 lg:grid-cols-[minmax(0,1.7fr)_320px]">
        <Card className="overflow-hidden">
          <div className="border-b border-line p-5">
            <SectionHeading subtitle="Owner-only lesson records">Recent lessons</SectionHeading>
          </div>
          <div className="divide-y divide-line">
            {lessonHistory.map((lesson) => (
              <Link className="grid gap-3 p-5 no-underline transition hover:bg-surface-muted/60 sm:grid-cols-[1fr_auto] sm:items-center" key={lesson.id} to={`/app/history/${lesson.id}`}>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="font-semibold tracking-[-0.015em]">{lesson.title}</h2>
                    <span className="rounded-md bg-surface-muted px-2 py-1 text-[11px] text-ink-muted">{lesson.level}</span>
                  </div>
                  <p className="mt-2 text-xs text-ink-muted">{lesson.date} · {lesson.score}</p>
                </div>
                <StatusChip tone={lesson.status === 'Completed' ? 'success' : 'warning'}>{lesson.status}</StatusChip>
              </Link>
            ))}
          </div>
        </Card>

        <div className="grid content-start gap-4">
          <Card className="p-5">
            <SectionHeading subtitle="A lightweight view of recent continuity.">This week</SectionHeading>
            <div className="mt-5 flex items-end justify-between">
              <strong className="text-3xl text-lexis">3</strong>
              <span className="text-xs text-ink-muted">lessons created</span>
            </div>
            <div className="mt-4"><ProgressBar value={75} /></div>
            <p className="mt-3 text-xs leading-5 text-ink-muted">Two lessons completed. One attempt can still resume.</p>
          </Card>
          <Card className="p-5">
            <SectionHeading subtitle="Based on saved exercise feedback.">Review signal</SectionHeading>
            <p className="mt-4 text-sm leading-6 text-ink-muted">Grammar lens remains the strongest candidate for the next focused review.</p>
          </Card>
        </div>
      </div>
    </div>
  )
}
