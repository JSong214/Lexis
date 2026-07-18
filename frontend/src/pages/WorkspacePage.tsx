import { useEffect, useMemo, useRef, useState } from 'react'
import { ArrowClockwise } from '@phosphor-icons/react'
import { Link, useNavigate } from 'react-router'
import { toast } from 'sonner'

import { Card, MetricTile, PageTitle, PrimaryButton, SectionHeading, StatusChip, WordChip } from '../components/ui'
import { useCurrentUserQuery } from '../features/auth/auth'
import { useGenerateLessonMutation } from '../features/lessons/lessons'
import {
  type TopicProposal,
  type TopicProposalResult,
  useTopicProposalsMutation,
} from '../features/lessons/topic-planning'
import {
  useMaimemoConnectionQuery,
  useSyncMaimemoMutation,
  useVocabularyProfileQuery,
} from '../features/maimemo/maimemo'
import { ApiError } from '../lib/api-client'

const anchorRanges = {
  A1: [2, 3],
  A2: [2, 3],
  B1: [3, 4],
  B2: [3, 4],
  C1: [4, 5],
  C2: [4, 5],
} as const

function proposalAnchors(proposal: TopicProposal) {
  return proposal.wordUsages
    .filter((usage) => usage.role === 'anchor')
    .map((usage) => usage.word)
}

export function WorkspacePage() {
  const navigate = useNavigate()
  const currentUser = useCurrentUserQuery()
  const connection = useMaimemoConnectionQuery()
  const profile = useVocabularyProfileQuery()
  const syncMaimemo = useSyncMaimemoMutation()
  const planTopics = useTopicProposalsMutation()
  const generateLesson = useGenerateLessonMutation()
  const [selectedWords, setSelectedWords] = useState<string[]>([])
  const [proposalResult, setProposalResult] = useState<TopicProposalResult | null>(null)
  const [selectedProposalId, setSelectedProposalId] = useState<string | null>(null)
  const [anchorWords, setAnchorWords] = useState<string[]>([])
  const proposalSectionRef = useRef<HTMLDivElement>(null)

  const snapshotWords = useMemo(() => {
    if (!profile.data) return []
    if (profile.data.snapshotWords.length > 0) return profile.data.snapshotWords
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
    if (availableWords.length === 0) return
    const availableKeys = new Set(availableWords.map((word) => word.toLowerCase()))
    setSelectedWords((current) => {
      const retained = current.filter((word) => availableKeys.has(word.toLowerCase()))
      return retained.length > 0 ? retained : availableWords.slice(0, 8)
    })
    setProposalResult(null)
    setSelectedProposalId(null)
    setAnchorWords([])
  }, [availableWords])

  const vocabularyGroups = useMemo(() => [
    { title: 'New Words', note: 'Course candidates', category: 'new' },
    { title: 'Fuzzy / Review Words', note: 'Worth revisiting', category: 'fuzzy' },
    { title: 'Practice Words', note: 'Available for transfer', category: 'practice' },
  ].map((group) => ({
    ...group,
    words: snapshotWords
      .filter(({ sourceCategory }) => sourceCategory === group.category)
      .map(({ word }) => word)
      .sort((left, right) => left.localeCompare(right, 'en', { sensitivity: 'base' })),
  })), [snapshotWords])

  const selectedProposal = proposalResult?.proposals.find(
    (proposal) => proposal.id === selectedProposalId,
  ) ?? null
  const level = currentUser.data?.cefr_level ?? 'B2'
  const [minimumAnchors, maximumAnchors] = anchorRanges[level]
  const anchorError = selectedProposal && (
    anchorWords.length < 1 || anchorWords.length > maximumAnchors
  )
    ? `${level} allows 1–${maximumAnchors} Anchor words.`
    : null
  const anchorRecommendation = selectedProposal
    && anchorWords.length > 0
    && anchorWords.length < minimumAnchors
    ? `${minimumAnchors}–${maximumAnchors} Anchor words are recommended for ${level}, but you may continue with ${anchorWords.length}.`
    : null

  function resetPlanning() {
    setProposalResult(null)
    setSelectedProposalId(null)
    setAnchorWords([])
  }

  function toggleWord(word: string) {
    setSelectedWords((current) => current.includes(word)
      ? current.filter((item) => item !== word)
      : [...current, word])
    resetPlanning()
  }

  function validSelectedWords() {
    if (selectedWords.length === 0) {
      toast.error('需要至少选择一个候选词')
      return null
    }
    const availableKeys = new Set(availableWords.map((word) => word.toLowerCase()))
    const valid = selectedWords.filter((word) => availableKeys.has(word.toLowerCase()))
    if (valid.length === 0) {
      setSelectedWords(availableWords.slice(0, 8))
      resetPlanning()
      toast.error('词汇已同步，请重新选择最新词汇')
      return null
    }
    if (valid.length !== selectedWords.length) {
      setSelectedWords(valid)
      resetPlanning()
    }
    return valid
  }

  function handleSync() {
    syncMaimemo.mutate(undefined, {
      onSuccess: (result) => {
        resetPlanning()
        toast.success('Maimemo synced · ' + (result.newWords.length + result.fuzzyWords.length) + ' focus words')
      },
      onError: (error) => toast.error(error instanceof Error ? error.message : 'Maimemo sync failed.'),
    })
  }

  function showTopicChoices(result: TopicProposalResult) {
    setProposalResult(result)
    setSelectedProposalId(null)
    setAnchorWords([])
    requestAnimationFrame(() => {
      proposalSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }

  async function findTopics() {
    if (!currentUser.data) return
    const words = validSelectedWords()
    if (!words) return
    const request = {
      cefrLevel: currentUser.data.cefr_level,
      examGoal: currentUser.data.learning_goal,
    }

    try {
      const result = await planTopics.mutateAsync({ ...request, selectedWords: words })
      showTopicChoices(result)
    } catch {
      // The mutation exposes the API error below the action card.
    }
  }

  function chooseProposal(proposal: TopicProposal) {
    setSelectedProposalId(proposal.id)
    setAnchorWords(proposalAnchors(proposal))
  }

  function toggleAnchor(word: string) {
    setAnchorWords((current) => {
      if (current.includes(word)) return current.filter((item) => item !== word)
      if (current.length >= maximumAnchors) return current
      return [...current, word]
    })
  }

  function generateSelectedLesson() {
    if (!currentUser.data || !selectedProposal || anchorError) return
    const words = validSelectedWords()
    if (!words) return
    generateLesson.mutate({
      cefrLevel: currentUser.data.cefr_level,
      examGoal: currentUser.data.learning_goal,
      selectedWords: words,
      proposalId: selectedProposal.id,
      anchorWords,
    }, {
      onSuccess: (lesson) => {
        toast.success('Lesson generated')
        navigate('/app/lessons/' + lesson.id)
      },
      onError: (error) => toast.error(error instanceof Error ? error.message : 'Lesson generation failed.'),
    })
  }

  const configured = connection.data?.configured ?? false
  const profileMissing = profile.error instanceof ApiError && profile.error.status === 404

  if (profile.isPending || connection.isPending || currentUser.isPending) {
    return <Card className="p-8"><StatusChip>Loading workspace</StatusChip><p className="mt-4 text-sm text-ink-muted">Checking your latest vocabulary profile…</p></Card>
  }

  if (!profile.data) {
    return (
      <div>
        <PageTitle subtitle="Create a vocabulary profile before planning a knowledge lesson.">Course Workbench</PageTitle>
        <Card className="mt-6 p-6 md:p-10">
          <StatusChip tone={configured ? 'warning' : 'default'}>{configured ? 'Sync required' : 'Connection required'}</StatusChip>
          <h2 className="mt-5 text-2xl font-semibold">{configured ? 'Your connection is ready for its first sync.' : 'Connect a vocabulary source to begin.'}</h2>
          <p className="mt-3 text-sm text-ink-muted">{profileMissing ? 'No vocabulary profile exists for this account.' : 'The profile API is unavailable.'}</p>
          <div className="mt-6">
            {configured
              ? <PrimaryButton disabled={syncMaimemo.isPending} onClick={handleSync}>{syncMaimemo.isPending ? 'Syncing…' : 'Sync Maimemo now'}</PrimaryButton>
              : <Link className="inline-flex min-h-11 items-center rounded-lg bg-lexis px-5 text-sm font-semibold text-white" to="/app/settings/connection">Open connection settings</Link>}
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <PageTitle subtitle="Choose candidates, compare knowledge topics, then generate one focused lesson.">Course Workbench</PageTitle>
        <button aria-label="Refresh Maimemo" className="inline-flex size-10 items-center justify-center rounded-lg border border-line bg-white text-ink-muted lg:hidden" disabled={syncMaimemo.isPending} onClick={handleSync} type="button">
          <ArrowClockwise className={syncMaimemo.isPending ? 'animate-spin' : undefined} size={18} />
        </button>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.95fr)]">
        <div className="grid gap-5">
          <Card className="p-5">
            <div className="flex items-start justify-between gap-4">
              <SectionHeading subtitle="Saved from the latest read-only Maimemo snapshot.">Vocabulary profile</SectionHeading>
              <StatusChip>Ready</StatusChip>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-3">
              <MetricTile label="New words" note="from sync" value={String(profile.data.newWords.length)} />
              <MetricTile label="Review" note="needs context" value={String(profile.data.fuzzyWords.length)} />
              <MetricTile label="Practice" note="available today" value={String(profile.data.practiceWords.length)} />
              <MetricTile label="Tracked" note="Maimemo records" value={profile.data.trackedWordCount.toLocaleString()} />
              <MetricTile label="Today" note="finished / total" value={`${profile.data.dailyFinishedCount} / ${profile.data.dailyTotalCount}`} />
              <MetricTile label="Study time" note="today" value={`${Math.round(profile.data.dailyStudyTimeMs / 60000)} min`} />
            </div>
          </Card>

          <Card className="p-5">
            <div className="flex items-start justify-between gap-4">
              <SectionHeading subtitle="Candidates are not forced into one lesson. Unrelated words can be deferred.">Candidate words</SectionHeading>
              <span className="rounded-md bg-lexis-soft px-2 py-1 text-[11px] text-lexis">{selectedWords.length} selected</span>
            </div>
            <div className="mt-6 space-y-6">
              {vocabularyGroups.map((group) => (
                <div key={group.title}>
                  <div className="mb-2 flex justify-between gap-4 text-xs"><strong>{group.title}</strong><span className="text-ink-muted">{group.note}</span></div>
                  <div className="flex flex-wrap gap-2">
                    {group.words.map((word) => <WordChip active={selectedWords.includes(word)} key={word} onClick={() => toggleWord(word)}>{word}</WordChip>)}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {proposalResult && (
            <div className="scroll-mt-5" ref={proposalSectionRef}>
              <Card className="p-5">
              <div className="flex items-start justify-between gap-4">
                <SectionHeading subtitle="Choose one topic before generating the lesson. No topic is selected automatically.">Choose a topic</SectionHeading>
                <StatusChip tone={selectedProposal ? 'success' : 'warning'}>{selectedProposal ? 'Topic selected' : 'Selection required'}</StatusChip>
              </div>
              {proposalResult.notice && <p className="mt-4 rounded-lg border border-lexis/20 bg-lexis-soft p-3 text-xs leading-5 text-ink-muted">{proposalResult.notice}</p>}
              <div className="mt-5 grid gap-3">
                {proposalResult.proposals.map((proposal) => (
                  <button
                    aria-pressed={proposal.id === selectedProposalId}
                    className={`rounded-lg border p-4 text-left transition ${proposal.id === selectedProposalId ? 'border-lexis bg-lexis-soft' : 'border-line hover:border-lexis/40'}`}
                    key={proposal.id}
                    onClick={() => chooseProposal(proposal)}
                    type="button"
                  >
                    <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-lexis">{proposal.contentMode.replaceAll('_', ' ')}</p>
                    <h3 className="mt-1 text-base font-semibold">{proposal.title}</h3>
                    <p className="mt-3 text-sm font-medium">{proposal.coreQuestion}</p>
                    <p className="mt-2 text-xs leading-5 text-ink-muted">{proposal.relationExplanation}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {proposalAnchors(proposal).map((word) => <span className="rounded-md bg-white px-2 py-1 text-[11px] text-lexis" key={word}>{word} · Anchor</span>)}
                      {proposal.deferredWords.map((word) => <span className="rounded-md bg-surface-muted px-2 py-1 text-[11px] text-ink-muted" key={word}>{word} · Deferred</span>)}
                    </div>
                  </button>
                ))}
              </div>
              {proposalResult.unmatchedWords.length > 0 && <p className="mt-4 text-xs text-warning">Not covered by the curated lexical source: {proposalResult.unmatchedWords.join(', ')}</p>}
              </Card>
            </div>
          )}
        </div>

        <div className="grid content-start gap-5">
          <Card className="hidden p-5 lg:block">
            <SectionHeading subtitle="Refresh the account snapshot and vocabulary profile.">Maimemo sync</SectionHeading>
            <p className="mt-4 text-xs text-ink-muted">Provider: {connection.data?.provider ?? 'maimemo'}</p>
            <button className="mt-5 h-10 w-full rounded-lg border border-line bg-white text-sm font-semibold hover:bg-surface-muted" disabled={syncMaimemo.isPending} onClick={handleSync} type="button">{syncMaimemo.isPending ? 'Syncing…' : 'Sync again'}</button>
          </Card>

          <Card className="p-5">
            <StatusChip tone={selectedProposal ? 'success' : 'warning'}>{selectedProposal ? 'Topic selected' : 'Topic required'}</StatusChip>
            <SectionHeading subtitle="Lexis validates word senses and relations before asking the LLM to write.">Knowledge lesson</SectionHeading>
            <p className="mt-4 text-xs text-ink-muted">{currentUser.data ? `${currentUser.data.cefr_level} · ${currentUser.data.learning_goal}` : 'Learning profile unavailable'}</p>

            {!selectedProposal ? (
              <>
                <p className="mt-4 text-xs leading-5 text-ink-muted">{proposalResult ? 'Topic choices are ready. Select one in the Choose a topic section before generating the lesson.' : 'Find 2–3 focused learning topics based on the selected words.'}</p>
                <PrimaryButton className="mt-5 w-full" disabled={!currentUser.data || planTopics.isPending} onClick={findTopics}>{planTopics.isPending ? 'Finding topics…' : proposalResult ? 'Refresh topic choices' : 'Find topic proposals'}</PrimaryButton>
              </>
            ) : (
              <>
                <div className="mt-5 rounded-lg border border-line p-4">
                  <h3 className="text-sm font-semibold">{selectedProposal.title}</h3>
                  <p className="mt-2 text-xs leading-5 text-ink-muted">{selectedProposal.coreKnowledge}</p>
                </div>
                <div className="mt-5">
                  <div className="flex justify-between gap-3 text-xs">
                    <strong>Anchor words</strong>
                    <span className="text-ink-muted">{anchorWords.length} selected · recommended {minimumAnchors}–{maximumAnchors}</span>
                  </div>
                  <p className="mt-2 text-xs leading-5 text-ink-muted">Only words with a validated relation can be promoted.</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {selectedProposal.wordUsages
                      .filter((usage) => usage.senseId && (usage.role === 'anchor' || usage.role === 'support'))
                      .map((usage) => <WordChip active={anchorWords.includes(usage.word)} key={usage.word} onClick={() => toggleAnchor(usage.word)}>{usage.word}</WordChip>)}
                  </div>
                  {anchorError && <p className="mt-3 text-xs text-warning">{anchorError}</p>}
                  {anchorRecommendation && <p className="mt-3 text-xs text-ink-muted">{anchorRecommendation}</p>}
                </div>
                <button className="mt-5 h-10 w-full rounded-lg border border-line bg-white text-sm font-semibold hover:bg-surface-muted" disabled={planTopics.isPending} onClick={findTopics} type="button">{planTopics.isPending ? 'Refreshing…' : 'Refresh proposals'}</button>
                <PrimaryButton className="mt-3 w-full" disabled={!currentUser.data || generateLesson.isPending || Boolean(anchorError)} onClick={generateSelectedLesson}>{generateLesson.isPending ? 'Generating lesson…' : 'Generate selected lesson'}</PrimaryButton>
              </>
            )}

            {planTopics.isError && !proposalResult && <p className="mt-4 text-xs leading-5 text-danger">Topic planning could not complete. {planTopics.error instanceof Error ? planTopics.error.message : 'Topic planning failed.'}</p>}
            {generateLesson.isError && <p className="mt-4 text-xs text-danger">{generateLesson.error instanceof Error ? generateLesson.error.message : 'Lesson generation failed.'}</p>}
          </Card>
        </div>
      </div>
    </div>
  )
}
