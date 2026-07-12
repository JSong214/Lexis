import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router'

import { useGenerateLessonMutation } from '../features/lessons/lessons'
import { ApiError } from '../lib/api-client'
import { Card, MetricTile, PageTitle, PrimaryButton, SectionHeading, StatusChip, WordChip } from '../components/ui'
import {
  useMaimemoConnectionQuery,
  useSyncMaimemoMutation,
  useVocabularyProfileQuery,
} from '../features/maimemo/maimemo'

export function WorkspacePage() {
  const navigate = useNavigate()
  const generateLesson = useGenerateLessonMutation()
  const connection = useMaimemoConnectionQuery()
  const profile = useVocabularyProfileQuery()
  const syncMaimemo = useSyncMaimemoMutation()
  const [selectedWords, setSelectedWords] = useState<string[]>([])

  useEffect(() => {
    if (profile.data && selectedWords.length === 0) {
      setSelectedWords([...profile.data.newWords, ...profile.data.fuzzyWords].slice(0, 3))
    }
  }, [profile.data, selectedWords.length])

  const vocabularyGroups = useMemo(() => profile.data ? [
    { title: 'New Words', note: 'Course focus candidates', words: profile.data.newWords },
    { title: 'Fuzzy / Review Words', note: 'Worth practicing in context', words: profile.data.fuzzyWords },
    { title: 'Mastered Sample', note: 'Context material', words: profile.data.masteredWordsSample },
  ] : [], [profile.data])

  function toggleWord(word: string) {
    setSelectedWords((current) => current.includes(word)
      ? current.filter((item) => item !== word)
      : [...current, word])
  }

  const profileMissing = profile.error instanceof ApiError && profile.error.status === 404
  const configured = connection.data?.configured ?? false

  if (profile.isPending || connection.isPending) {
    return <Card className="p-8"><StatusChip tone="default">Loading workspace</StatusChip><p className="mt-4 text-sm text-ink-muted">Checking your latest vocabulary profile…</p></Card>
  }

  if (!profile.data) {
    return (
      <div>
        <PageTitle subtitle="Create one normalized vocabulary profile before generating a lesson.">Course Workbench</PageTitle>
        <Card className="mt-6 p-6 md:p-10">
          <StatusChip tone={configured ? 'warning' : 'default'}>{configured ? 'Sync required' : 'Connection required'}</StatusChip>
          <h2 className="mt-5 text-2xl font-semibold">{configured ? 'Your connection is ready for its first sync.' : 'Connect a vocabulary source to begin.'}</h2>
          <p className="mt-3 max-w-xl text-sm leading-6 text-ink-muted">
            {profileMissing ? 'Lexis could not find a saved vocabulary profile for this account.' : 'The profile API is currently unavailable.'}
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            {configured
              ? <PrimaryButton disabled={syncMaimemo.isPending} onClick={() => syncMaimemo.mutate()}>{syncMaimemo.isPending ? 'Syncing…' : 'Sync mock vocabulary'}</PrimaryButton>
              : <Link className="inline-flex min-h-11 items-center rounded-lg bg-lexis px-5 text-sm font-semibold text-white" to="/app/settings/connection">Open connection settings</Link>}
          </div>
          {syncMaimemo.error instanceof Error && <p className="mt-4 text-xs text-danger">{syncMaimemo.error.message}</p>}
        </Card>
      </div>
    )
  }

  return (
    <div>
      <PageTitle subtitle="Review the latest synchronized words and prepare the next lesson.">Course Workbench</PageTitle>
      <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.95fr)]">
        <div className="grid gap-5">
          <Card className="p-5">
            <div className="flex items-start justify-between gap-4">
              <SectionHeading subtitle="Saved from the latest MockMaimemoSyncProvider snapshot.">Vocabulary profile</SectionHeading>
              <StatusChip>Ready</StatusChip>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
              <MetricTile label="New words" note="from sync" value={String(profile.data.newWords.length)} />
              <MetricTile label="Review" note="needs context" value={String(profile.data.fuzzyWords.length)} />
              <MetricTile label="Mastered sample" note="context only" value={String(profile.data.masteredWordsSample.length)} />
              <MetricTile label="Mastered count" note="reference" value={profile.data.masteredWordCount.toLocaleString()} />
            </div>
          </Card>
          <Card className="p-5">
            <div className="flex items-start justify-between gap-4">
              <SectionHeading subtitle="Choose the words that should receive extra attention in the lesson.">Word package adjustment</SectionHeading>
              <span className="rounded-md bg-lexis-soft px-2 py-1 text-[11px] text-lexis">{selectedWords.length} focus</span>
            </div>
            <div className="mt-6 space-y-6">
              {vocabularyGroups.map((group) => (
                <div key={group.title}>
                  <div className="mb-2 flex justify-between gap-4 text-xs"><strong>{group.title}</strong><span className="text-ink-muted">{group.note}</span></div>
                  <div className="flex flex-wrap gap-2">{group.words.map((word) => <WordChip active={selectedWords.includes(word)} key={word} onClick={() => toggleWord(word)}>{word}</WordChip>)}</div>
                </div>
              ))}
            </div>
          </Card>
        </div>
        <div className="grid content-start gap-5">
          <Card className="p-5">
            <SectionHeading subtitle="Refreshes this account's snapshot and vocabulary profile.">Maimemo sync</SectionHeading>
            <p className="mt-4 text-xs text-ink-muted">Provider: MockMaimemoSyncProvider</p>
            <button className="mt-5 h-10 w-full rounded-lg border border-line bg-white text-sm font-semibold hover:bg-surface-muted disabled:opacity-50" disabled={syncMaimemo.isPending} onClick={() => syncMaimemo.mutate()} type="button">{syncMaimemo.isPending ? 'Syncing…' : 'Sync again'}</button>
          </Card>
          <Card className="p-5">
            <StatusChip>Schema validated</StatusChip>
            <SectionHeading subtitle="Uses the configured LLMProvider and validates the structured ContextLesson before saving.">Lesson generation</SectionHeading>
            <PrimaryButton className="mt-5 w-full" disabled={selectedWords.length === 0 || generateLesson.isPending} onClick={() => generateLesson.mutate({ cefrLevel: 'B2', examGoal: 'IELTS reading', selectedWords }, { onSuccess: (lesson) => navigate('/app/lessons/' + lesson.id) })}>{generateLesson.isPending ? 'Generating…' : 'Generate lesson'}</PrimaryButton>
          </Card>
        </div>
      </div>
    </div>
  )
}
