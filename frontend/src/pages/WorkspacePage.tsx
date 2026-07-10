import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router'

import { Card, MetricTile, PageTitle, PrimaryButton, ProgressBar, SectionHeading, StatusChip, WordChip } from '../components/ui'
import { vocabularyGroups } from '../data/mock-data'
import { useHealthQuery } from '../features/system/health'

export function WorkspacePage() {
  const navigate = useNavigate()
  const healthQuery = useHealthQuery()
  const [selectedWords, setSelectedWords] = useState<string[]>(['anchor', 'estimate', 'ambiguous'])
  const previewWords = useMemo(() => vocabularyGroups.flatMap((group) => group.words).slice(0, 6), [])

  function toggleWord(word: string) {
    setSelectedWords((current) => current.includes(word) ? current.filter((item) => item !== word) : [...current, word])
  }

  return (
    <div>
      <PageTitle subtitle="Confirm sync, adjust today’s words, then generate one valid lesson.">Course Workbench</PageTitle>

      <div className="mt-3 grid gap-3 md:mt-4 md:gap-4 lg:mt-1 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.98fr)] lg:grid-rows-[154px_76px_248px] lg:gap-5">
        <Card className="order-1 p-3 md:p-4 lg:hidden lg:col-start-2 lg:row-start-1 lg:p-5">
          <div className="flex items-start justify-between gap-3">
            <SectionHeading subtitle="Latest sync 09:12. Snapshot ready.">Maimemo connected</SectionHeading>
            <StatusChip tone={healthQuery.isError ? 'danger' : 'success'}>{healthQuery.isError ? 'Offline' : 'Ready'}</StatusChip>
          </div>
        </Card>

        <Card className="order-2 p-3 md:p-4 lg:col-start-1 lg:row-start-1 lg:p-5">
          <div className="flex items-start justify-between gap-4">
            <div><h2 className="text-lg font-semibold">Vocabulary profile</h2><p className="mt-1 hidden text-xs text-ink-muted md:block">Latest Maimemo snapshot is normalized and ready.</p></div>
            <div className="hidden md:block"><StatusChip>Ready</StatusChip></div>
          </div>
          <div className="mt-3 grid grid-cols-3 gap-3 md:mt-4 md:grid-cols-4">
            <MetricTile label="New words" note="from sync" value="24" />
            <MetricTile label="Review" note="needs context" value="8" />
            <MetricTile label="Mastered sample" note="context only" value="12" />
            <div className="hidden md:block"><MetricTile label="Mastered count" note="reference" value="3.4k" /></div>
          </div>
        </Card>

        <Card className="order-3 p-3 md:p-4 lg:col-start-2 lg:row-start-1 lg:row-span-2 lg:p-5">
          <div className="flex items-start justify-between">
            <SectionHeading subtitle="Lesson generated. Reading is in progress.">Course completion</SectionHeading>
            <strong className="text-2xl text-lexis">1/3</strong>
          </div>
          <div className="mt-2"><ProgressBar value={62} /></div>
          <div className="mt-2 flex gap-2 overflow-hidden text-[10px] md:text-[11px] lg:hidden">
            <span className="shrink-0 rounded-md bg-lexis-soft px-2 py-1 text-lexis">Lesson done</span>
            <span className="shrink-0 rounded-md bg-surface-muted px-2 py-1">Reading now</span>
            <span className="shrink-0 rounded-md bg-warning-soft px-2 py-1 text-warning">Exercise next</span>
          </div>          <div className="mt-3 hidden gap-1.5 lg:grid">
            <div className="grid grid-cols-[1fr_82px_58px] items-center rounded-md bg-lexis-soft px-3 py-2 text-[11px]"><strong>Lesson</strong><span className="text-ink-muted">Generated</span><span className="text-lexis">Done</span></div>
            <div className="grid grid-cols-[1fr_82px_58px] items-center rounded-md bg-surface-muted px-3 py-2 text-[11px]"><strong>Reading</strong><span className="text-ink-muted">2 / 4 parts</span><span className="text-warning">Active</span></div>
            <div className="grid grid-cols-[1fr_82px_58px] items-center rounded-md bg-surface-muted px-3 py-2 text-[11px]"><strong>Exercise</strong><span className="text-ink-muted">Not started</span><span className="text-warning">Next</span></div>
          </div>
        </Card>

        <Card className="order-4 p-3 md:p-4 lg:col-start-1 lg:row-start-2 lg:row-span-2 lg:p-5">
          <div className="flex items-start justify-between gap-4">
            <div><h2 className="text-lg font-semibold"><span className="md:hidden">Word package preview</span><span className="hidden md:inline">Word package adjustment</span></h2><p className="mt-1 hidden text-xs leading-5 text-ink-muted md:block">Remove unsuitable words or mark 1–3 focus candidates.</p></div>
            <span className="shrink-0 rounded-md bg-lexis-soft px-2 py-1 text-[11px] text-lexis">{selectedWords.length} focus</span>
          </div>
          <div className="mt-5 hidden space-y-7 md:block">
            {vocabularyGroups.map((group) => (
              <div key={group.title}>
                <div className="mb-2.5 flex justify-between text-xs"><strong>{group.title}</strong><span className="text-ink-muted">{group.note}</span></div>
                <div className="flex flex-wrap gap-2">{group.words.map((word) => <WordChip active={selectedWords.includes(word)} key={word} onClick={() => toggleWord(word)}>{word}</WordChip>)}</div>
              </div>
            ))}
          </div>
          <div className="mt-3 flex flex-wrap gap-2 md:hidden">
            {previewWords.map((word) => <WordChip active={selectedWords.includes(word)} key={word} onClick={() => toggleWord(word)}>{word}</WordChip>)}
          </div>
        </Card>

        <Card className="order-5 p-3 md:p-4 lg:col-start-2 lg:row-start-3 lg:p-5">
          <div className="hidden md:block"><StatusChip>Ready to generate</StatusChip></div>
          <div className="md:mt-3"><SectionHeading subtitle="Uses the latest snapshot plus current word adjustments.">Lesson generation</SectionHeading></div>
          <dl className="mt-3 hidden grid-cols-[110px_1fr] gap-y-1 text-xs md:grid">
            <dt className="text-ink-muted">CEFR level</dt><dd className="font-semibold">B2</dd>
            <dt className="text-ink-muted">Goal</dt><dd className="font-semibold">IELTS reading</dd>
            <dt className="text-ink-muted">Reading length</dt><dd className="font-semibold">120–150 words</dd>
            <dt className="text-ink-muted">Unknown words</dt><dd className="font-semibold">&lt;= 5 + Chinese aid</dd>
          </dl>
          <div className="mt-3 flex gap-2 text-[11px] md:hidden"><span className="rounded-md bg-surface-muted px-2 py-1">CEFR B2</span><span className="rounded-md bg-surface-muted px-2 py-1">Goal IELTS</span><span className="rounded-md bg-surface-muted px-2 py-1">Unknown ≤5</span></div>
          <PrimaryButton className="mt-3 w-full md:mt-2" disabled={selectedWords.length === 0} onClick={() => navigate('/app/lessons/demo')}>Generate lesson</PrimaryButton>
        </Card>
      </div>
    </div>
  )
}
