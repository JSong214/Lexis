import { SignOut } from '@phosphor-icons/react'
import { NavLink, Outlet, useNavigate } from 'react-router'

import { Brand, StatusChip } from '../components/ui'
import { useCurrentUserQuery, useLogoutMutation } from '../features/auth/auth'
import { useAutoSyncMaimemo, useMaimemoConnectionQuery } from '../features/maimemo/maimemo'
import { useHealthQuery } from '../features/system/health'

const navigation = [
  { label: 'Workspace', to: '/app/workspace' },
  { label: 'History', to: '/app/history' },
  { label: 'Settings', to: '/app/settings/connection' },
]

export function AppShell() {
  const navigate = useNavigate()
  const healthQuery = useHealthQuery()
  const currentUser = useCurrentUserQuery()
  const connection = useMaimemoConnectionQuery()
  useAutoSyncMaimemo(connection.data?.configured ?? false)
  const logoutMutation = useLogoutMutation()
  const healthLabel = healthQuery.isPending ? 'Connecting' : healthQuery.isError ? 'API offline' : 'API connected'

  function handleLogout() {
    logoutMutation.mutate(undefined, {
      onSuccess: () => navigate('/login', { replace: true }),
    })
  }

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <header className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-6 pt-6 md:px-8">
        <Brand />
        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <p className="max-w-52 truncate text-xs font-semibold">{currentUser.data?.email}</p>
            <p className="mt-1 text-[11px] text-ink-muted">{logoutMutation.isError ? 'Sign out failed' : 'Private session'}</p>
          </div>
          <div className="hidden md:block"><StatusChip tone={healthQuery.isError ? 'danger' : 'success'}>{healthLabel}</StatusChip></div>
          <button aria-label="Log out" className="grid size-10 place-items-center rounded-lg border border-line bg-white text-ink-muted transition hover:bg-surface-muted hover:text-ink disabled:opacity-50" disabled={logoutMutation.isPending} onClick={handleLogout} title="Log out" type="button">
            <SignOut aria-hidden="true" size={18} />
          </button>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl px-6 pb-28 pt-6 md:px-8"><Outlet /></main>
      <nav aria-label="Primary navigation" className="fixed inset-x-6 bottom-3 z-50 mx-auto grid max-w-[480px] grid-cols-3 rounded-xl border border-line bg-white/95 p-2 shadow-[0_12px_36px_rgba(17,20,23,0.08)] backdrop-blur md:bottom-5">
        {navigation.map((item) => (
          <NavLink className={({ isActive }) => `flex h-11 flex-col items-center justify-center gap-1 rounded-lg text-[11px] font-medium transition ${isActive ? 'bg-lexis-soft text-lexis' : 'text-ink-muted hover:bg-surface-muted'}`} key={item.to} to={item.to}>
            {({ isActive }) => <><span className={`size-1.5 rounded-full ${isActive ? 'bg-lexis' : 'bg-[#a9b4ae]'}`} aria-hidden="true" />{item.label}</>}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
