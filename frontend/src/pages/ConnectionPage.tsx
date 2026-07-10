import { ShieldCheck } from '@phosphor-icons/react'
import { type FormEvent, useState } from 'react'

import { Card, MetricTile, PageTitle, PrimaryButton, SectionHeading, StatusChip } from '../components/ui'

export function ConnectionPage() {
  const [connected, setConnected] = useState(true)
  const [syncing, setSyncing] = useState(false)

  function saveConnection(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const secret = String(new FormData(event.currentTarget).get('secret') ?? '')
    if (secret.trim()) setConnected(true)
  }

  function syncNow() {
    setSyncing(true)
    window.setTimeout(() => setSyncing(false), 650)
  }

  return (
    <div className="pt-3">
      <PageTitle subtitle="Securely connect your vocabulary source before generating a lesson.">Maimemo Connection</PageTitle>
      <div className="mt-5 grid gap-4 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.95fr)]">
        <Card className="p-5 md:p-8">
          <div className="flex items-start justify-between gap-4">
            <SectionHeading subtitle="The secret is submitted to the API and never returned to this browser.">Connection setup</SectionHeading>
            <StatusChip>Encrypted</StatusChip>
          </div>
          <form className="mt-6" onSubmit={saveConnection}>
            <label className="grid gap-2 text-xs font-semibold">
              Maimemo secret
              <input className="h-12 rounded-lg border border-line px-4 text-sm font-normal outline-none placeholder:text-[#98a0a6] focus:border-lexis" name="secret" placeholder={connected ? '••••••••••••••••' : 'Paste your Maimemo secret'} type="password" />
            </label>
            <div className="mt-4 flex justify-end">
              <PrimaryButton className="w-full sm:w-auto" type="submit">Save connection</PrimaryButton>
            </div>
          </form>
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-surface-muted p-3 text-xs text-ink-muted">
            <ShieldCheck className="shrink-0 text-lexis" size={19} />
            Secret values are encrypted at rest and excluded from API responses.
          </div>
        </Card>

        <Card className="p-5 md:p-6">
          <div className="flex items-start justify-between gap-3">
            <SectionHeading subtitle="Latest vocabulary snapshot">Sync readiness</SectionHeading>
            <StatusChip tone={connected ? 'success' : 'warning'}>{connected ? 'Sync ready' : 'Not connected'}</StatusChip>
          </div>
          <div className="mt-6 grid grid-cols-3 gap-3">
            <MetricTile label="New words" value="24" />
            <MetricTile label="Review" value="8" />
            <MetricTile label="Mastered" value="3.4k" />
          </div>
          <button className="mt-6 h-10 w-full rounded-lg border border-line bg-white text-sm font-semibold transition hover:bg-surface-muted disabled:opacity-50" disabled={!connected || syncing} onClick={syncNow} type="button">
            {syncing ? 'Syncing…' : 'Sync now'}
          </button>
          <p className="mt-3 text-center text-[11px] text-ink-muted">Last successful sync · Today 09:12</p>
        </Card>
      </div>
    </div>
  )
}
