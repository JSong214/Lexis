import { useState } from 'react'
import { Link, useParams } from 'react-router'

import { Card, SecondaryLink, SectionHeading, StatusChip, WordChip } from '../components/ui'
import {
  useLessonAttemptQuery,
  useLessonQuery,
} from '../features/lessons/lessons'

const exerciseLabels = {
  vocabulary_context: 'Vocabulary context',
  syntax: 'Syntax understanding',
  paragraph_logic: 'Paragraph logic',
  output: 'Output practice',
}

export function HistoryDetailPage() {
  const { lessonId } = useParams()
  const [tab, setTab] = useState<'lesson' | 'answers' | 'summary'>('lesson')
  const lesson = useLessonQuery(lessonId)
  const attempt = useLessonAttemptQuery(lessonId)

  if (lesson.isPending || attempt.isPending) {
    return <Card className="p-8"><StatusChip tone="default">Loading record</StatusChip><p className="mt-4 text-sm text-ink-muted">Reading the saved lesson and attempt…</p></Card>
  }

  if (lesson.isError || attempt.isError || !lesson.data) {
    const error = lesson.error ?? attempt.error
    return <Card className="p-8"><StatusChip tone="danger">Record unavailable</StatusChip><p className="mt-4 text-sm text-ink-muted">{error instanceof Error ? error.message : 'The history record could not be loaded.'}</p><Link className="mt-5 inline-block text-sm font-semibold text-lexis" to="/app/history">Back to History</Link></Card>
  }

  const lessonData = lesson.data
  const attemptData = attempt.data
  const attemptStatus = attemptData?.status === 'completed'
    ? 'Completed'
    : attemptData?.status === 'draft'
      ? 'In progress'
      : 'Not started'

  return (
    <div className="pt-1">
      <div className="flex flex-wrap items-center gap-3">
        <SecondaryLink to="/app/history">Back to History</SecondaryLink>
        <StatusChip>Owner-only</StatusChip>
        {attemptData?.status !== 'completed' && <SecondaryLink to={`/app/lessons/${lessonId}`}>Resume lesson</SecondaryLink>}
      </div>
      <div className="mt-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[28px] font-semibold tracking-[-0.03em]">{lessonData.content.title}</h1>
          <p className="mt-1 max-w-2xl text-sm leading-5 text-ink-muted">
            Generated {new Date(lessonData.createdAt).toLocaleString()}. Course content and owner-only learning evidence are preserved together.
          </p>
        </div>
        <div className="flex gap-2 text-xs"><span className="rounded-md bg-surface-muted px-2.5 py-1.5">{lessonData.cefrLevel}</span><StatusChip tone={attemptStatus === 'Completed' ? 'success' : 'warning'}>{attemptStatus}</StatusChip></div>
      </div>

      <div className="mt-4 grid grid-cols-3 rounded-lg border border-line bg-white p-2 lg:hidden">
        {(['lesson', 'answers', 'summary'] as const).map((item) => <button className={`rounded-md px-2 py-2 text-xs font-medium capitalize ${tab === item ? 'bg-lexis-soft text-lexis' : 'text-ink-muted'}`} key={item} onClick={() => setTab(item)} type="button">{item}</button>)}
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.94fr)]">
        <div className={tab !== 'lesson' ? 'hidden lg:grid lg:gap-4' : 'grid gap-4'}>
          <Card className="p-5">
            <div className="flex items-start justify-between"><SectionHeading subtitle="Read-only generated ContextLesson">Generated lesson</SectionHeading><StatusChip>Detail ready</StatusChip></div>
            <article className="mt-5 rounded-lg border border-[#e7e2d7] bg-[#fffdf8] p-5">
              <h2 className="text-xl font-semibold">{lessonData.content.title}</h2>
              <p className="mt-3 text-sm leading-7 text-ink-muted">{lessonData.content.readingText}</p>
              <div className="mt-4 flex flex-wrap gap-2">{lessonData.content.targetWords.map((word) => <WordChip key={word}>{word}</WordChip>)}</div>
            </article>
            <div className="mt-4 rounded-lg bg-surface-muted p-4">
              <div className="flex items-center justify-between"><strong className="text-sm">Source sync snapshot</strong><StatusChip>Valid</StatusChip></div>
              <p className="mt-2 text-xs text-ink-muted">Snapshot {lessonData.snapshotId} · provider {lessonData.provider}</p>
            </div>
            <div className="mt-4 rounded-lg border border-line p-4">
              <strong className="text-sm">Read-only grammar analysis</strong>
              <ul className="mt-2 grid gap-2 text-xs leading-5 text-ink-muted">{lessonData.content.grammarAnalysis.map((item) => <li key={item}>{item}</li>)}</ul>
            </div>
          </Card>
        </div>

        <div className="grid content-start gap-4">
          <Card className={`p-5 ${tab !== 'answers' && tab !== 'lesson' ? 'hidden lg:block' : ''}`}>
            <div className="flex items-start justify-between"><SectionHeading subtitle="Submitted values and immediate feedback">Attempt answers</SectionHeading><StatusChip tone={attemptData ? 'success' : 'default'}>{attemptData ? `${attemptData.feedback.length} saved` : 'None'}</StatusChip></div>
            <div className="mt-4 divide-y divide-line">
              {!attemptData?.feedback.length && <p className="py-4 text-xs text-ink-muted">No answers have been submitted.</p>}
              {attemptData?.feedback.map((item) => (
                <div className="py-3" key={item.id}>
                  <div className="flex items-center justify-between gap-3"><strong className="text-xs">{exerciseLabels[item.exerciseType]}</strong><span className={`text-[11px] ${item.isCorrect ? 'text-lexis' : 'text-warning'}`}>{item.isCorrect ? 'Correct' : 'Review'}</span></div>
                  <p className="mt-1 text-xs text-ink-muted">{item.answer}</p>
                  <p className="mt-2 text-xs leading-5 text-ink-muted">{item.feedbackText}</p>
                </div>
              ))}
            </div>
          </Card>
          <Card className={`p-5 ${tab !== 'summary' && tab !== 'lesson' ? 'hidden lg:block' : ''}`}>
            <div className="flex items-start justify-between"><SectionHeading>Final summary</SectionHeading><StatusChip tone={attemptData?.finalSummary ? 'success' : 'default'}>{attemptData?.finalSummary ? 'Saved' : 'Pending'}</StatusChip></div>
            <p className="mt-4 text-sm leading-6 text-ink-muted">{attemptData?.finalSummary ?? 'Complete all four exercises to create and save the final summary.'}</p>
            <div className="mt-5 space-y-2 text-xs text-ink-muted"><p>• Completed attempts remain read-only in History.</p><p>• Draft attempts reopen in the Lesson page.</p></div>
          </Card>
        </div>
      </div>
    </div>
  )
}
