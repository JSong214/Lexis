import { Link } from 'react-router'

import { Card, PageTitle, ProgressBar, SectionHeading, StatusChip } from '../components/ui'
import { useLessonHistoryQuery } from '../features/lessons/lessons'

export function HistoryPage() {
  const history = useLessonHistoryQuery()

  if (history.isPending) {
    return <Card className="p-8"><StatusChip tone="default">Loading history</StatusChip><p className="mt-4 text-sm text-ink-muted">Reading your owner-only lesson records…</p></Card>
  }

  if (history.isError || !history.data) {
    return <Card className="p-8"><StatusChip tone="danger">History unavailable</StatusChip><p className="mt-4 text-sm text-ink-muted">{history.error instanceof Error ? history.error.message : 'Lesson history could not be loaded.'}</p></Card>
  }

  const completedCount = history.data.filter((item) => item.attemptStatus === 'completed').length
  const draftCount = history.data.filter((item) => item.attemptStatus === 'draft').length
  const completionRate = history.data.length === 0
    ? 0
    : Math.round((completedCount / history.data.length) * 100)

  return (
    <div className="pt-3">
      <PageTitle subtitle="Review completed lessons, saved feedback, and resumable attempts.">Learning History</PageTitle>

      <div className="mt-5 grid gap-4 lg:grid-cols-[minmax(0,1.7fr)_320px]">
        <Card className="overflow-hidden">
          <div className="border-b border-line p-5">
            <SectionHeading subtitle="Owner-only lesson records">Recent lessons</SectionHeading>
          </div>
          <div className="divide-y divide-line">
            {history.data.length === 0 && <div className="p-8 text-center text-sm text-ink-muted">No lessons yet. Generate one from Workspace.</div>}
            {history.data.map((lesson) => {
              const status = lesson.attemptStatus === 'completed'
                ? 'Completed'
                : lesson.attemptStatus === 'draft'
                  ? 'In progress'
                  : 'Not started'
              return (
                <Link className="grid gap-3 p-5 no-underline transition hover:bg-surface-muted/60 sm:grid-cols-[1fr_auto] sm:items-center" key={lesson.id} to={`/app/history/${lesson.id}`}>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="font-semibold tracking-[-0.015em]">{lesson.title}</h2>
                      <span className="rounded-md bg-surface-muted px-2 py-1 text-[11px] text-ink-muted">{lesson.cefrLevel}</span>
                    </div>
                    <p className="mt-2 text-xs text-ink-muted">
                      {new Date(lesson.createdAt).toLocaleString()} · {lesson.correctCount} correct · {lesson.answeredCount}/{lesson.exerciseCount} answered
                    </p>
                  </div>
                  <StatusChip tone={status === 'Completed' ? 'success' : 'warning'}>{status}</StatusChip>
                </Link>
              )
            })}
          </div>
        </Card>

        <div className="grid content-start gap-4">
          <Card className="p-5">
            <SectionHeading subtitle="Calculated from saved ContextLesson records.">Learning continuity</SectionHeading>
            <div className="mt-5 flex items-end justify-between">
              <strong className="text-3xl text-lexis">{history.data.length}</strong>
              <span className="text-xs text-ink-muted">lessons created</span>
            </div>
            <div className="mt-4"><ProgressBar value={completionRate} /></div>
            <p className="mt-3 text-xs leading-5 text-ink-muted">{completedCount} completed. {draftCount} resumable draft{draftCount === 1 ? '' : 's'}.</p>
          </Card>
          <Card className="p-5">
            <SectionHeading subtitle="Based on persisted exercise feedback.">Saved evidence</SectionHeading>
            <p className="mt-4 text-sm leading-6 text-ink-muted">Open any lesson to review its generated content, submitted answers, immediate feedback, and final summary.</p>
          </Card>
        </div>
      </div>
    </div>
  )
}
