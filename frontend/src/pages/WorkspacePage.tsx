import { useEffect, useMemo, useState } from 'react'
import { ArrowClockwise } from '@phosphor-icons/react'
import { Link, useNavigate } from 'react-router'
import { toast } from 'sonner'

import { useCurrentUserQuery } from '../features/auth/auth'
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
  const currentUser = useCurrentUserQuery()
  const generateLesson = useGenerateLessonMutation()
  const connection = useMaimemoConnectionQuery()
  const profile = useVocabularyProfileQuery()
  const syncMaimemo = useSyncMaimemoMutation()
  const [selectedWords, setSelectedWords] = useState<string[]>([])

  const snapshotWords = useMemo(() => {
    if (!profile.data) {
      return []
    }
    if (profile.data.snapshotWords.length > 0) {
      return profile.data.snapshotWords
    }
    return [
      ...profile.data.newWords.map((word) => ({ word, sourceCategory: 'new' as const })),
      ...profile.data.fuzzyWords.map((word) => ({ word, sourceCategory: 'fuzzy' as const })),
      ...profile.data.practiceWords.map((word) => ({ word, sourceCategory: 'practice' as const })),
    ]
  }, [profile.data])

  const availableWords = useMemo(() => Array.from(new Set(
    snapshotWords
      .filter(({ sourceCategory }) => sourceCategory !== 'mastered_sample')
      .map(({ word }) => word),
  )), [snapshotWords])

  useEffect(() => {
    if (availableWords.length === 0) {
      return
    }

    const availableWordKeys = new Set(
      availableWords.map((word) => word.trim().toLowerCase()),
    )
    setSelectedWords((current) => {
      const retainedWords = current.filter((word) =>
        availableWordKeys.has(word.trim().toLowerCase()),
      )
      return retainedWords.length > 0 ? retainedWords : availableWords.slice(0, 3)
    })
  }, [availableWords])

  const vocabularyGroups = useMemo(() => snapshotWords.length > 0 ? [
    { title: 'New Words', note: 'Course focus candidates', words: snapshotWords.filter(({ sourceCategory }) => sourceCategory === 'new').map(({ word }) => word).sort((left, right) => left.localeCompare(right, 'en', { sensitivity: 'base' })) },
    { title: 'Fuzzy / Review Words', note: 'Worth practicing in context', words: snapshotWords.filter(({ sourceCategory }) => sourceCategory === 'fuzzy').map(({ word }) => word).sort((left, right) => left.localeCompare(right, 'en', { sensitivity: 'base' })) },
    { title: 'Practice Words', note: 'Today excluding new and review', words: snapshotWords.filter(({ sourceCategory }) => sourceCategory === 'practice').map(({ word }) => word).sort((left, right) => left.localeCompare(right, 'en', { sensitivity: 'base' })) },
  ] : [], [snapshotWords])

  function toggleWord(word: string) {
    setSelectedWords((current) => current.includes(word)
      ? current.filter((item) => item !== word)
      : [...current, word])
  }

  function handleSync() {
    syncMaimemo.mutate(undefined, {
      onSuccess: (syncedProfile) => toast.success('Maimemo synced · ' + (syncedProfile.newWords.length + syncedProfile.fuzzyWords.length) + ' focus words'),
      onError: (mutationError) => toast.error(mutationError instanceof Error ? mutationError.message : 'Maimemo sync failed.'),
    })
  }

  function handleGenerateLesson() {
    if (!currentUser.data) return
    if (selectedWords.length === 0) {
      toast.error('需要至少选择一个单词')
      return
    }

    const latestWordKeys = new Set(availableWords.map((word) => word.trim().toLowerCase()))
    const validSelectedWords = selectedWords.filter((word) =>
      latestWordKeys.has(word.trim().toLowerCase()),
    )
    if (validSelectedWords.length === 0) {
      setSelectedWords(availableWords.slice(0, 3))
      toast.error('词汇已同步，请重新选择最新词汇')
      return
    }
    if (validSelectedWords.length !== selectedWords.length) {
      setSelectedWords(validSelectedWords)
    }

    generateLesson.mutate({ cefrLevel: currentUser.data.cefr_level, examGoal: currentUser.data.learning_goal, selectedWords: validSelectedWords }, {
      onSuccess: (lesson) => {
        toast.success('Lesson generated')
        navigate('/app/lessons/' + lesson.id)
      },
      onError: (mutationError) => toast.error(mutationError instanceof Error ? mutationError.message : 'Lesson generation failed.'),
    })
  }

  const profileMissing = profile.error instanceof ApiError && profile.error.status === 404
  const configured = connection.data?.configured ?? false

  if (profile.isPending || connection.isPending || currentUser.isPending) {
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
              ? <PrimaryButton disabled={syncMaimemo.isPending} onClick={handleSync}>{syncMaimemo.isPending ? 'Syncing…' : 'Sync Maimemo now'}</PrimaryButton>
              : <Link className="inline-flex min-h-11 items-center rounded-lg bg-lexis px-5 text-sm font-semibold text-white" to="/app/settings/connection">Open connection settings</Link>}
          </div>
          {syncMaimemo.error instanceof Error && <p className="mt-4 text-xs text-danger">{syncMaimemo.error.message}</p>}
        </Card>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <PageTitle subtitle="Review the latest synchronized words and prepare the next lesson.">Course Workbench</PageTitle>
        <button aria-label="Refresh Maimemo" className="inline-flex size-10 shrink-0 items-center justify-center rounded-lg border border-line bg-white text-ink-muted transition hover:bg-surface-muted hover:text-ink disabled:opacity-50 lg:hidden" disabled={syncMaimemo.isPending} onClick={handleSync} title="Refresh Maimemo" type="button">
          <ArrowClockwise aria-hidden="true" className={syncMaimemo.isPending ? 'animate-spin' : undefined} size={18} />
        </button>
      </div>
      <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.95fr)]">
        <div className="grid gap-5">
          <Card className="p-5">
            <div className="flex items-start justify-between gap-4">
              <SectionHeading subtitle="Saved from the latest read-only Maimemo Open API snapshot.">Vocabulary profile</SectionHeading>
              <StatusChip>Ready</StatusChip>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-3">
              <MetricTile label="New words" note="from sync" value={String(profile.data.newWords.length)} />
              <MetricTile label="Review" note="needs context" value={String(profile.data.fuzzyWords.length)} />
              <MetricTile label="Practice words" note="today excluding new/review" value={String(profile.data.practiceWords.length)} />
              <MetricTile label="Tracked words" note="Maimemo records" value={profile.data.trackedWordCount.toLocaleString()} />
              <MetricTile label="Today" note="finished / total" value={`${profile.data.dailyFinishedCount} / ${profile.data.dailyTotalCount}`} />
              <MetricTile label="Study time" note="today" value={`${Math.round(profile.data.dailyStudyTimeMs / 60000)} min`} />
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
          <Card className="hidden p-5 lg:block">
            <SectionHeading subtitle="Refreshes this account's snapshot and vocabulary profile.">Maimemo sync</SectionHeading>
            <p className="mt-4 text-xs text-ink-muted">Provider: {connection.data?.provider ?? 'maimemo'}</p>
            <button className="mt-5 h-10 w-full rounded-lg border border-line bg-white text-sm font-semibold hover:bg-surface-muted disabled:opacity-50" disabled={syncMaimemo.isPending} onClick={handleSync} type="button">{syncMaimemo.isPending ? 'Syncing…' : 'Sync again'}</button>
          </Card>
          <Card className="p-5">
            <StatusChip>Schema validated</StatusChip>
            <SectionHeading subtitle="Uses the configured LLMProvider and validates the structured ContextLesson before saving.">Lesson generation</SectionHeading>
            <p className="mt-4 text-xs text-ink-muted">{currentUser.data ? `${currentUser.data.cefr_level} · ${currentUser.data.learning_goal}` : 'Learning profile unavailable'}</p>
            <PrimaryButton className="mt-5 w-full" disabled={!currentUser.data || generateLesson.isPending} onClick={handleGenerateLesson}>{generateLesson.isPending ? 'Generating…' : 'Generate lesson'}</PrimaryButton>
          </Card>
        </div>
      </div>
    </div>
  )
}
