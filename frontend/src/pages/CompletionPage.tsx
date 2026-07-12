import { Link, useParams } from 'react-router'

import {
  Card,
  MetricTile,
  PrimaryButton,
  ProgressBar,
  SecondaryLink,
  SectionHeading,
  StatusChip,
  WordChip,
} from '../components/ui'
import {
  useLessonCompletionQuery,
  useLessonQuery,
} from '../features/lessons/lessons'

const exerciseLabels = {
  vocabulary_context: 'Vocabulary context',
  syntax: 'Syntax understanding',
  paragraph_logic: 'Paragraph logic',
  output: 'Output practice',
}

export function CompletionPage() {
  const { lessonId } = useParams()
  const lesson = useLessonQuery(lessonId)
  const completion = useLessonCompletionQuery(lessonId)

  if (lesson.isPending || completion.isPending) {
    return <Card className="p-8"><StatusChip tone="default">Loading summary</StatusChip><p className="mt-4 text-sm text-ink-muted">Reading the completed LessonAttempt…</p></Card>
  }

  if (lesson.isError || completion.isError || !lesson.data || !completion.data) {
    const error = lesson.error ?? completion.error
    return <Card className="p-8"><StatusChip tone="danger">Summary unavailable</StatusChip><p className="mt-4 text-sm text-ink-muted">{error instanceof Error ? error.message : 'The completed attempt could not be loaded.'}</p><Link className="mt-5 inline-block text-sm font-semibold text-lexis" to={`/app/lessons/${lessonId}`}>Back to lesson</Link></Card>
  }

  const lessonData = lesson.data
  const { attempt, masteryUpdates } = completion.data
  const correctCount = attempt.feedback.filter((item) => item.isCorrect).length

  return (
    <div className="pt-1">
      <div className="flex flex-wrap items-center gap-4 border-b border-line pb-4">
        <SecondaryLink to="/app/workspace">Back to Workspace</SecondaryLink>
        <div className="mr-auto">
          <h1 className="text-xl font-semibold">Lesson complete</h1>
          <p className="mt-1 text-xs text-ink-muted">{lessonData.content.title} · {lessonData.cefrLevel}</p>
        </div>
        <StatusChip>Summary saved</StatusChip>
      </div>
      <div className="mt-3"><ProgressBar value={100} /></div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.94fr)]">
        <div className="grid gap-4">
          <Card className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div><span className="text-xs font-semibold uppercase tracking-[0.08em] text-lexis">Attempt complete</span><h2 className="mt-2 text-2xl font-semibold tracking-[-0.025em]">Your learning record is saved.</h2></div>
              <StatusChip>History ready</StatusChip>
            </div>
            <p className="mt-3 text-sm leading-6 text-ink-muted">Answers, immediate feedback, the final summary, and context mastery evidence now belong to this attempt.</p>
            <div className="mt-5 grid grid-cols-3 gap-3">
              <MetricTile label="Exercises" value={`${correctCount} / ${attempt.feedback.length}`} />
              <MetricTile label="Summary" value="Saved" />
              <MetricTile label="Mastery" value={`+${masteryUpdates.length}`} />
            </div>
          </Card>

          <Card className="p-5">
            <div className="flex items-start justify-between"><SectionHeading>Final summary</SectionHeading><StatusChip>Ready</StatusChip></div>
            <p className="mt-4 text-sm leading-7 text-ink-muted">{attempt.finalSummary}</p>
          </Card>

          <Card className="p-5">
            <SectionHeading subtitle="Saved with the completed attempt.">Exercise feedback recap</SectionHeading>
            <div className="mt-4 divide-y divide-line">
              {attempt.feedback.map((item) => (
                <div className="grid gap-2 py-3 text-sm sm:grid-cols-[150px_80px_1fr]" key={item.id}>
                  <strong>{exerciseLabels[item.exerciseType]}</strong>
                  <span className={item.isCorrect ? 'text-lexis' : 'text-warning'}>{item.isCorrect ? 'Correct' : 'Review'}</span>
                  <span className="text-ink-muted">{item.feedbackText}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="grid content-start gap-4">
          <Card className="p-5">
            <div className="flex items-start justify-between"><SectionHeading>Context mastery update</SectionHeading><StatusChip>Updated</StatusChip></div>
            <p className="mt-3 text-sm leading-6 text-ink-muted">{masteryUpdates.length} focus words received evidence from this completed attempt.</p>
            <div className="mt-4 flex flex-wrap gap-2">{masteryUpdates.map((item) => <WordChip key={item.word}>{item.word}</WordChip>)}</div>
            <div className="mt-5 space-y-2 text-xs text-ink-muted">
              {masteryUpdates.map((item) => (
                <p className="rounded-lg bg-surface-muted p-3" key={item.word}>
                  <strong className="text-ink">{item.word}</strong> · {item.status} · {item.exposureCount} exposure
                </p>
              ))}
            </div>
          </Card>
          <Card className="p-5">
            <SectionHeading subtitle="Open the saved lesson and feedback any time.">Next action</SectionHeading>
            <Link to={`/app/history/${lessonId}`}><PrimaryButton className="mt-5 w-full">Open History</PrimaryButton></Link>
          </Card>
        </div>
      </div>
    </div>
  )
}
