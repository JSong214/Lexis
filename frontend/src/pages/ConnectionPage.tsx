import { ShieldCheck } from '@phosphor-icons/react'
import { type FormEvent } from 'react'
import { toast } from 'sonner'

import { Card, MetricTile, PageTitle, PrimaryButton, SectionHeading, StatusChip } from '../components/ui'
import {
  type CefrLevel,
  type LearningGoal,
  useCurrentUserQuery,
  useUpdatePreferencesMutation,
} from '../features/auth/auth'
import {
  useMaimemoConnectionQuery,
  useSaveMaimemoConnectionMutation,
  useSyncMaimemoMutation,
  useVocabularyProfileQuery,
} from '../features/maimemo/maimemo'

const CEFR_LEVELS: CefrLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const LEARNING_GOALS: LearningGoal[] = [
  'General English',
  'CET-4',
  'CET-6',
  'IELTS',
  'TOEFL',
  'Postgraduate Entrance English',
  'Academic English',
  'Workplace English',
]

export function ConnectionPage() {
  const currentUser = useCurrentUserQuery()
  const updatePreferences = useUpdatePreferencesMutation()
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
  const preferencesError = updatePreferences.error instanceof Error
    ? updatePreferences.error.message
    : ''

  function handlePreferencesSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    updatePreferences.mutate({
      cefr_level: String(formData.get('cefrLevel')) as CefrLevel,
      learning_goal: String(formData.get('learningGoal')) as LearningGoal,
    }, {
      onSuccess: () => toast.success('Learning profile saved'),
      onError: (mutationError) => toast.error(mutationError instanceof Error ? mutationError.message : 'Learning profile could not be saved.'),
    })
  }

  function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = event.currentTarget
    const secret = String(new FormData(form).get('secret') ?? '').trim()
    saveConnection.mutate(secret, {
      onSuccess: () => {
        form.reset()
        toast.success('Maimemo connection saved')
      },
      onError: (mutationError) => toast.error(mutationError instanceof Error ? mutationError.message : 'Maimemo connection could not be saved.'),
    })
  }

  return (
    <div className="pt-3">
      <PageTitle subtitle="Manage your learning profile and connected vocabulary source.">Settings</PageTitle>
      <Card className="mt-5 p-5 md:p-8">
        <div className="flex items-start justify-between gap-4">
          <SectionHeading subtitle="These preferences set the difficulty and goal for every new lesson.">Learning profile</SectionHeading>
          <StatusChip tone={updatePreferences.isSuccess ? 'success' : 'default'}>{updatePreferences.isSuccess ? 'Saved' : 'Account settings'}</StatusChip>
        </div>
        {currentUser.data && (
          <form className="mt-6" key={`${currentUser.data.cefr_level}-${currentUser.data.learning_goal}`} onSubmit={handlePreferencesSave}>
            <div className="grid gap-4 md:grid-cols-3">
              <label className="grid gap-2 text-xs font-semibold">
                Email
                <input className="h-12 rounded-lg border border-line bg-surface-muted px-4 text-sm font-normal text-ink-muted" disabled value={currentUser.data.email} />
              </label>
              <label className="grid gap-2 text-xs font-semibold">
                CEFR level
                <select className="h-12 rounded-lg border border-line bg-white px-4 text-sm font-normal outline-none focus:border-lexis" defaultValue={currentUser.data.cefr_level} disabled={updatePreferences.isPending} name="cefrLevel">
                  {CEFR_LEVELS.map((level) => <option key={level} value={level}>{level}</option>)}
                </select>
              </label>
              <label className="grid gap-2 text-xs font-semibold">
                Learning goal
                <select className="h-12 rounded-lg border border-line bg-white px-4 text-sm font-normal outline-none focus:border-lexis" defaultValue={currentUser.data.learning_goal} disabled={updatePreferences.isPending} name="learningGoal">
                  {LEARNING_GOALS.map((goal) => <option key={goal} value={goal}>{goal}</option>)}
                </select>
              </label>
            </div>
            <div className="mt-4 flex justify-end">
              <PrimaryButton className="w-full sm:w-auto" disabled={updatePreferences.isPending} type="submit">{updatePreferences.isPending ? 'Saving…' : 'Save learning profile'}</PrimaryButton>
            </div>
          </form>
        )}
        {currentUser.isPending && <p className="mt-6 text-sm text-ink-muted">Loading account settings…</p>}
        {preferencesError && <p className="mt-4 rounded-lg bg-danger-soft p-3 text-xs text-danger" role="alert">{preferencesError}</p>}
      </Card>
      <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.95fr)]">
        <Card className="p-5 md:p-8">
          <div className="flex items-start justify-between gap-4">
            <SectionHeading subtitle="Uses the read-only Maimemo Open API with your encrypted token.">Connection setup</SectionHeading>
            <StatusChip tone={configured ? 'success' : 'warning'}>{configured ? 'Configured' : 'Setup required'}</StatusChip>
          </div>
          <form className="mt-6" onSubmit={handleSave}>
            <label className="grid gap-2 text-xs font-semibold">
              Maimemo Open API token
              <input autoComplete="off" className="h-12 rounded-lg border border-line px-4 text-sm font-normal outline-none placeholder:text-[#98a0a6] focus:border-lexis" disabled={saveConnection.isPending} name="secret" placeholder={connection.data?.secretSaved ? 'Encrypted token already saved' : 'Paste your Maimemo Open API token'} type="password" />
            </label>
            <div className="mt-4 flex justify-end">
              <PrimaryButton className="w-full sm:w-auto" disabled={saveConnection.isPending} type="submit">{saveConnection.isPending ? 'Saving…' : 'Save Maimemo connection'}</PrimaryButton>
            </div>
          </form>
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-surface-muted p-3 text-xs text-ink-muted">
            <ShieldCheck className="shrink-0 text-lexis" size={19} />
            The token is encrypted at rest, used only by the backend, and never returned by the API.
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
            <MetricTile label="Tracked" value={(profile.data?.trackedWordCount ?? 0).toLocaleString()} />
          </div>
          <button className="mt-6 h-10 w-full rounded-lg border border-line bg-white text-sm font-semibold transition hover:bg-surface-muted disabled:opacity-50" disabled={!configured || syncMaimemo.isPending} onClick={() => syncMaimemo.mutate(undefined, {
            onSuccess: (syncedProfile) => toast.success('Maimemo synced · ' + (syncedProfile.newWords.length + syncedProfile.fuzzyWords.length) + ' focus words'),
            onError: (mutationError) => toast.error(mutationError instanceof Error ? mutationError.message : 'Maimemo sync failed.'),
          })} type="button">
            {syncMaimemo.isPending ? 'Syncing…' : 'Sync Maimemo now'}
          </button>
          <p className="mt-3 text-center text-[11px] text-ink-muted">{profile.data ? 'Latest profile saved to your account' : 'No successful sync yet'}</p>
        </Card>
      </div>
    </div>
  )
}
