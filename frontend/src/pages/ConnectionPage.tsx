import { ShieldCheck } from '@phosphor-icons/react'
import { type FormEvent } from 'react'

import { Card, MetricTile, PageTitle, PrimaryButton, SectionHeading, StatusChip } from '../components/ui'
import {
  useMaimemoConnectionQuery,
  useSaveMaimemoConnectionMutation,
  useSyncMaimemoMutation,
  useVocabularyProfileQuery,
} from '../features/maimemo/maimemo'

export function ConnectionPage() {
  const connection = useMaimemoConnectionQuery()
  const profile = useVocabularyProfileQuery()
  const saveConnection = useSaveMaimemoConnectionMutation()
  const syncMaimemo = useSyncMaimemoMutation()
  const configured = connection.data?.configured ?? false
  const error = saveConnection.error instanceof Error
    ? saveConnection.error.message
    : syncMaimemo.error instanceof Error
      ? syncMaimemo.error.message
      : ''

  function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = event.currentTarget
    const secret = String(new FormData(form).get('secret') ?? '').trim()
    saveConnection.mutate(secret, { onSuccess: () => form.reset() })
  }

  return (
    <div className="pt-3">
      <PageTitle subtitle="Connect a vocabulary source, then create a normalized profile from one sync.">Maimemo Connection</PageTitle>
      <div className="mt-5 grid gap-4 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.95fr)]">
        <Card className="p-5 md:p-8">
          <div className="flex items-start justify-between gap-4">
            <SectionHeading subtitle="Mock mode is active while the real Maimemo adapter is being verified.">Connection setup</SectionHeading>
            <StatusChip tone={configured ? 'success' : 'warning'}>{configured ? 'Configured' : 'Setup required'}</StatusChip>
          </div>
          <form className="mt-6" onSubmit={handleSave}>
            <label className="grid gap-2 text-xs font-semibold">
              Maimemo secret <span className="font-normal text-ink-muted">(optional in mock mode)</span>
              <input autoComplete="off" className="h-12 rounded-lg border border-line px-4 text-sm font-normal outline-none placeholder:text-[#98a0a6] focus:border-lexis" disabled={saveConnection.isPending} name="secret" placeholder={connection.data?.secretSaved ? 'Encrypted secret already saved' : 'Leave empty to use mock data'} type="password" />
            </label>
            <div className="mt-4 flex justify-end">
              <PrimaryButton className="w-full sm:w-auto" disabled={saveConnection.isPending} type="submit">{saveConnection.isPending ? 'Saving…' : 'Save mock connection'}</PrimaryButton>
            </div>
          </form>
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-surface-muted p-3 text-xs text-ink-muted">
            <ShieldCheck className="shrink-0 text-lexis" size={19} />
            Secret values are encrypted at rest and never returned by the API.
          </div>
          {error && <p className="mt-4 rounded-lg bg-danger-soft p-3 text-xs text-danger" role="alert">{error}</p>}
        </Card>

        <Card className="p-5 md:p-6">
          <div className="flex items-start justify-between gap-3">
            <SectionHeading subtitle="Latest normalized snapshot">Sync readiness</SectionHeading>
            <StatusChip tone={profile.data ? 'success' : configured ? 'warning' : 'default'}>{profile.data ? 'Profile ready' : configured ? 'Ready to sync' : 'Not connected'}</StatusChip>
          </div>
          <div className="mt-6 grid grid-cols-3 gap-3">
            <MetricTile label="New words" value={String(profile.data?.newWords.length ?? 0)} />
            <MetricTile label="Review" value={String(profile.data?.fuzzyWords.length ?? 0)} />
            <MetricTile label="Mastered" value={(profile.data?.masteredWordCount ?? 0).toLocaleString()} />
          </div>
          <button className="mt-6 h-10 w-full rounded-lg border border-line bg-white text-sm font-semibold transition hover:bg-surface-muted disabled:opacity-50" disabled={!configured || syncMaimemo.isPending} onClick={() => syncMaimemo.mutate()} type="button">
            {syncMaimemo.isPending ? 'Syncing…' : 'Sync mock vocabulary'}
          </button>
          <p className="mt-3 text-center text-[11px] text-ink-muted">{profile.data ? 'Latest profile saved to your account' : 'No successful sync yet'}</p>
        </Card>
      </div>
    </div>
  )
}
